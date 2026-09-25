import os
import subprocess
import shutil
import uuid
from flask import Flask, request, send_file, render_template, jsonify
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def apply_gifski_fps_drop(input_path, output_path, target_bytes):
    # This algorithm guarantees perfect colors by extracting frames and asking gifski to re-encode them
    # at a lower framerate (dropping frames) until it hits the target file size.
    frames_dir = output_path + "_frames"
    os.makedirs(frames_dir, exist_ok=True)
    
    img = Image.open(input_path)
    frame_count = img.n_frames
    original_duration = img.info.get('duration', 100) # ms
    img_width = img.width
    
    # Try different keep_steps to hit the size.
    # keep_step = 2 means keep 1 out of 2 frames
    for keep_step in [2, 3, 4, 5, 6, 8]:
        new_duration = original_duration * keep_step
        fps = 1000 / new_duration if new_duration > 0 else 10
        
        kept_frames = []
        for i in range(0, frame_count, keep_step):
            img.seek(i)
            # convert to RGBA to ensure perfect quality
            frame_img = img.convert("RGBA")
            frame_path = os.path.join(frames_dir, f"frame_{i:04d}.png")
            frame_img.save(frame_path)
            kept_frames.append(frame_path)
            
        # gifski by default resizes images > 800x600. Force width to preserve resolution.
        cmd = ["gifski", "-o", output_path, "--fps", str(int(fps)), "--quality", "90", "-W", str(img_width)] + kept_frames
        subprocess.run(cmd, check=True)
        
        size = os.path.getsize(output_path)
        if size <= target_bytes:
            shutil.rmtree(frames_dir)
            return {"final_kb": size / 1024, "method": f"Drop FPS (1/{keep_step}) via Gifski ✨"}
            
    # if all failed, just return the lowest one
    shutil.rmtree(frames_dir)
    return {"final_kb": os.path.getsize(output_path) / 1024, "method": f"Drop FPS (1/{keep_step}) [LIMITE]", "warning": True}


def compress_gif_logic(input_path, output_path, target_kb, **kwargs):
    target_bytes = target_kb * 1024
    mode = kwargs.get('compression_mode', 'scale_100')
    
    if mode == 'drop_fps':
        return apply_gifski_fps_drop(input_path, output_path, target_bytes)
    
    # Base step: reduce to a global 256 color palette.
    base_output = output_path + ".base.gif"
    
    # If mode is scale_80 or scale_50, scale it immediately at the base step to save time
    scale_arg = []
    if mode == 'scale_80':
        scale_arg = ["--scale=0.8"]
    elif mode == 'scale_50':
        scale_arg = ["--scale=0.5"]
        
    cmd = ["gifsicle", "-O3", "--colors=256"] + scale_arg + [input_path, "-o", base_output]
    subprocess.run(cmd, check=True)
    base_size = os.path.getsize(base_output)
    
    if base_size <= target_bytes:
        shutil.copy2(base_output, output_path)
        os.remove(base_output)
        return {"final_kb": os.path.getsize(output_path) / 1024, "method": f"Lossless ({mode})"}
        
    # Configurações de Qualidade (Hard Caps) para evitar destruição do GIF
    MAX_LOSSY = 80
    MIN_COLORS = 128
    
    min_lossy = 10
    max_lossy = MAX_LOSSY
    best_lossy = None
    best_valid_size = float('inf')
    temp_output = output_path + ".tmp.gif"
    valid_file_found = False
    
    while min_lossy <= max_lossy:
        mid_lossy = (min_lossy + max_lossy) // 2
        cmd = ["gifsicle", "-O3", f"--lossy={mid_lossy}", base_output, "-o", temp_output]
        subprocess.run(cmd, check=True)
        size = os.path.getsize(temp_output)
        
        if size <= target_bytes:
            best_lossy = mid_lossy
            best_valid_size = size
            shutil.copy2(temp_output, output_path)
            valid_file_found = True
            max_lossy = mid_lossy - 5
        else:
            min_lossy = mid_lossy + 5
            
    if valid_file_found:
        os.remove(base_output)
        if os.path.exists(temp_output):
            os.remove(temp_output)
        return {"final_kb": best_valid_size / 1024, "method": f"Lossy {best_lossy} ({mode})"}
        
    # Cores
    min_colors = MIN_COLORS
    max_colors = 255
    best_colors = None
    
    while min_colors <= max_colors:
        mid_colors = (min_colors + max_colors) // 2
        cmd = ["gifsicle", "-O3", f"--lossy={MAX_LOSSY}", f"--colors={mid_colors}", base_output, "-o", temp_output]
        subprocess.run(cmd, check=True)
        size = os.path.getsize(temp_output)
        
        if size <= target_bytes:
            best_colors = mid_colors
            best_valid_size = size
            shutil.copy2(temp_output, output_path)
            valid_file_found = True
            min_colors = mid_colors + 5
        else:
            max_colors = mid_colors - 5
            
    os.remove(base_output)
    
    if valid_file_found:
        if os.path.exists(temp_output):
            os.remove(temp_output)
        return {"final_kb": best_valid_size / 1024, "method": f"Lossy {MAX_LOSSY} + Colors {best_colors} ({mode})"}
    else:
        # Failsafe
        cmd = ["gifsicle", "-O3", f"--lossy={MAX_LOSSY}", f"--colors={MIN_COLORS}"] + scale_arg + [input_path, "-o", output_path]
        subprocess.run(cmd, check=True)
        
        final_size = os.path.getsize(output_path) / 1024
        if os.path.exists(temp_output):
            os.remove(temp_output)
            
        return {
            "final_kb": final_size, 
            "method": f"Lossy {MAX_LOSSY} + Colors {MIN_COLORS} ({mode}) [LIMITE ALCANÇADO]",
            "warning": True
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress_endpoint():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400
        
    try:
        target_kb = float(request.form.get('target_kb', 1000))
        compression_mode = request.form.get('compression_mode', 'scale_100')
    except ValueError:
        return jsonify({"error": "Peso alvo inválido"}), 400

    filename = str(uuid.uuid4()) + ".gif"
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(OUTPUT_FOLDER, "compressed_" + filename)
    
    file.save(input_path)
    
    original_kb = os.path.getsize(input_path) / 1024
    
    try:
        result_meta = compress_gif_logic(input_path, output_path, target_kb, compression_mode=compression_mode)
        
        return jsonify({
            "success": True,
            "original_kb": original_kb,
            "final_kb": result_meta["final_kb"],
            "method": result_meta["method"],
            "warning": result_meta.get("warning", False),
            "download_url": f"/download/{os.path.basename(output_path)}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name="compressed.gif")
    return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)
