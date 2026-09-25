import os
import subprocess
import shutil
import uuid
import re
import zipfile
import time
from io import BytesIO
from flask import Flask, request, send_file, render_template, jsonify, after_this_request
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Limite de 50MB por arquivo

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def cleanup_old_files():
    """Remove arquivos na pasta outputs mais velhos que 1 hora."""
    now = time.time()
    for f in os.listdir(OUTPUT_FOLDER):
        f_path = os.path.join(OUTPUT_FOLDER, f)
        if os.path.isfile(f_path):
            if os.stat(f_path).st_mtime < now - 3600:  # 1 hora
                try: os.remove(f_path)
                except: pass

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'gif'

def extract_frames(input_path, frames_dir, keep_step):
    img = Image.open(input_path)
    frame_count = img.n_frames
    original_duration = img.info.get('duration', 100) # ms
    new_duration = original_duration * keep_step
    fps = 1000 / new_duration if new_duration > 0 else 10
    img_width = img.width
    
    kept_frames = []
    for i in range(0, frame_count, keep_step):
        img.seek(i)
        frame_img = img.convert("RGBA")
        frame_path = os.path.join(frames_dir, f"frame_{i:04d}.png")
        frame_img.save(frame_path)
        kept_frames.append(frame_path)
        
    return kept_frames, fps, img_width

def run_hybrid_stage(input_path, output_path, target_bytes, frames_dir, keep_step, max_lossy, min_colors):
    kept_frames, fps, img_width = extract_frames(input_path, frames_dir, keep_step)
    if not kept_frames:
        return False, float('inf'), max_lossy
        
    gifski_out = output_path + f".step_{keep_step}.gif"
    cmd = ["gifski", "-o", gifski_out, "--fps", str(int(fps)), "--quality", "90", "-W", str(img_width)] + kept_frames
    subprocess.run(cmd, check=True)
    
    temp_out = output_path + ".tmp.gif"
    
    cmd_lossless = ["gifsicle", "-O3", f"--colors={min_colors}", gifski_out, "-o", temp_out]
    subprocess.run(cmd_lossless, check=True)
    size_lossless = os.path.getsize(temp_out)
    if size_lossless <= target_bytes:
        shutil.copy2(temp_out, output_path)
        if os.path.exists(gifski_out): os.remove(gifski_out)
        if os.path.exists(temp_out): os.remove(temp_out)
        return True, size_lossless, 0 
    
    cmd_max = ["gifsicle", "-O3", f"--lossy={max_lossy}", f"--colors={min_colors}", gifski_out, "-o", temp_out]
    subprocess.run(cmd_max, check=True)
    if os.path.getsize(temp_out) > target_bytes:
        shutil.copy2(temp_out, output_path)
        size = os.path.getsize(output_path)
        if os.path.exists(gifski_out): os.remove(gifski_out)
        if os.path.exists(temp_out): os.remove(temp_out)
        return False, size, max_lossy
    
    min_l = 10
    max_l = max_lossy
    best_lossy = None
    best_size = float('inf')
    valid_found = False
    
    while min_l <= max_l:
        mid_l = (min_l + max_l) // 2
        cmd = ["gifsicle", "-O3", f"--lossy={mid_l}", f"--colors={min_colors}", gifski_out, "-o", temp_out]
        subprocess.run(cmd, check=True)
        size = os.path.getsize(temp_out)
        
        if size <= target_bytes:
            best_lossy = mid_l
            best_size = size
            shutil.copy2(temp_out, output_path)
            valid_found = True
            max_l = mid_l - 1
        else:
            min_l = mid_l + 1
            
    if os.path.exists(gifski_out): os.remove(gifski_out)
    if os.path.exists(temp_out): os.remove(temp_out)
    
    if valid_found:
        return True, best_size, best_lossy
    else:
        return False, os.path.getsize(output_path), max_lossy


def compress_gif_logic(input_path, output_path, target_kb, **kwargs):
    target_bytes = target_kb * 1024
    frames_dir = output_path + "_frames_tmp"
    os.makedirs(frames_dir, exist_ok=True)
    
    keep_steps = [1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 30]
    
    try:
        for ks in keep_steps:
            max_l = 80 if ks <= 2 else (100 if ks <= 4 else 120)
            min_c = 255 if ks <= 2 else (192 if ks <= 4 else 128)
            
            success, size, lossy = run_hybrid_stage(input_path, output_path, target_bytes, frames_dir, ks, max_lossy=max_l, min_colors=min_c)
            
            if success:
                if ks == 1: name = "Original"
                elif ks <= 2: name = "Fluidez Alta"
                elif ks <= 4: name = "Fluidez Média"
                elif ks <= 8: name = "Fluidez Baixa"
                else: name = "Extremo"
                
                lossy_str = f"Lossy {lossy}" if lossy > 0 else "Lossless"
                fps_str = "FPS 100%" if ks == 1 else f"FPS 1/{ks}"
                
                return {"final_kb": size / 1024, "method": f"{name} ({fps_str}) + {lossy_str}"}
                
        return {"final_kb": os.path.getsize(output_path) / 1024, "method": f"Slideshow Extremo (FPS 1/{keep_steps[-1]})", "warning": True}
        
    finally:
        if os.path.exists(frames_dir):
            shutil.rmtree(frames_dir)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress_endpoint():
    cleanup_old_files()

    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400
        
    if not allowed_file(file.filename):
        return jsonify({"error": "Apenas arquivos .gif são permitidos"}), 400
        
    try:
        target_kb = float(request.form.get('target_kb', 1000))
    except ValueError:
        return jsonify({"error": "Peso alvo inválido"}), 400

    # Handle filename parsing
    original_filename = secure_filename(file.filename)
    # Remove leading digits and underscore
    clean_name = re.sub(r'^\d+_', '', original_filename)
    
    unique_id = str(uuid.uuid4())[:8]
    input_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_{clean_name}")
    temp_output = os.path.join(OUTPUT_FOLDER, f"temp_{unique_id}_{clean_name}")
    
    file.save(input_path)
    original_kb = os.path.getsize(input_path) / 1024
    
    try:
        result_meta = compress_gif_logic(input_path, temp_output, target_kb)
        final_kb = result_meta["final_kb"]
        
        # New filename format: [FINAL_KB]_[UUID]_clean_name.gif
        final_name = f"{int(final_kb)}_{unique_id}_{clean_name}"
        final_output = os.path.join(OUTPUT_FOLDER, final_name)
        
        # Rename temp_output to final_output
        if os.path.exists(temp_output):
            os.rename(temp_output, final_output)
        
        return jsonify({
            "success": True,
            "original_kb": original_kb,
            "final_kb": final_kb,
            "method": result_meta["method"],
            "warning": result_meta.get("warning", False),
            "download_url": f"/download/{final_name}",
            "filename": final_name
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

@app.route('/download/<filename>')
def download_file(filename):
    filename = secure_filename(filename)
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    
    if not os.path.abspath(file_path).startswith(os.path.abspath(OUTPUT_FOLDER)):
        return "Caminho inválido", 400
        
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

@app.route('/download_zip', methods=['POST'])
def download_zip():
    data = request.json
    filenames = data.get('filenames', [])
    
    if not filenames:
        return jsonify({"error": "Nenhum arquivo especificado"}), 400
        
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for fname in filenames:
            fname = secure_filename(fname)
            file_path = os.path.join(OUTPUT_FOLDER, fname)
            
            if os.path.abspath(file_path).startswith(os.path.abspath(OUTPUT_FOLDER)) and os.path.exists(file_path):
                zf.write(file_path, fname)
                
    memory_file.seek(0)
    return send_file(memory_file, download_name="gifs_comprimidos.zip", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
