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




def extract_frames_dynamic(input_path, frames_dir, threshold):
    img = Image.open(input_path)
    frame_count = img.n_frames
    original_duration = img.info.get('duration', 100) # ms
    fps = 1000 / original_duration if original_duration > 0 else 10
    img_width = img.width
    
    kept_frames = []
    import numpy as np
    
    img.seek(0)
    prev_frame_img = img.convert("RGBA")
    prev_path = os.path.join(frames_dir, f"frame_{0:04d}.png")
    prev_frame_img.save(prev_path)
    kept_frames.append(prev_path)
    
    prev_arr = np.array(prev_frame_img).astype(float)
    
    for i in range(1, frame_count):
        img.seek(i)
        curr_frame_img = img.convert("RGBA")
        curr_arr = np.array(curr_frame_img).astype(float)
        
        mse = np.mean((prev_arr - curr_arr) ** 2)
        
        if mse < threshold:
            kept_frames.append(kept_frames[-1])
        else:
            curr_path = os.path.join(frames_dir, f"frame_{i:04d}.png")
            curr_frame_img.save(curr_path)
            kept_frames.append(curr_path)
            prev_arr = curr_arr
            
    unique_count = len(set(kept_frames))
    return kept_frames, fps, img_width, unique_count, frame_count

def run_hybrid_stage_dynamic(input_path, output_path, target_bytes, frames_dir, threshold, max_lossy, min_colors, quality=90):
    kept_frames, fps, img_width, unique_count, frame_count = extract_frames_dynamic(input_path, frames_dir, threshold)
    if not kept_frames:
        return False, float('inf'), max_lossy, 0
        
    unique_pct = unique_count / frame_count
        
    gifski_out = output_path + f".thresh_{threshold}_q{quality}.gif"
    cmd = ["gifski", "-o", gifski_out, "--fps", str(int(fps)), "--quality", str(quality), "-W", str(img_width)] + kept_frames
    subprocess.run(cmd, check=True)
    
    temp_out = output_path + ".tmp.gif"
    
    def get_gifsicle_cmd(lossy):
        c = ["gifsicle", "-O3", gifski_out, "-o", temp_out]
        if min_colors < 256:
            c.insert(2, f"--colors={min_colors}")
        if lossy > 0:
            c.insert(2, f"--lossy={lossy}")
        return c
    
    cmd_lossless = get_gifsicle_cmd(0)
    subprocess.run(cmd_lossless, check=True)
    size_lossless = os.path.getsize(temp_out)
    if size_lossless <= target_bytes:
        shutil.copy2(temp_out, output_path)
        if os.path.exists(gifski_out): os.remove(gifski_out)
        if os.path.exists(temp_out): os.remove(temp_out)
        return True, size_lossless, 0, unique_pct 
    
    cmd_max = get_gifsicle_cmd(max_lossy)
    subprocess.run(cmd_max, check=True)
    if os.path.getsize(temp_out) > target_bytes:
        shutil.copy2(temp_out, output_path)
        size = os.path.getsize(output_path)
        if os.path.exists(gifski_out): os.remove(gifski_out)
        if os.path.exists(temp_out): os.remove(temp_out)
        return False, size, max_lossy, unique_pct
    
    min_l = 1
    max_l = max_lossy
    best_lossy = None
    best_size = float('inf')
    valid_found = False
    
    while min_l <= max_l:
        mid_l = (min_l + max_l) // 2
        cmd = get_gifsicle_cmd(mid_l)
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
        return True, best_size, best_lossy, unique_pct
    else:
        return False, os.path.getsize(output_path), max_lossy, unique_pct

def generate_profiles():
    profiles = []
    
    # Ultra-dense thresholds to eliminate "cliffs" in file size
    dense_thresholds = [0, 2, 5, 10, 15, 20, 30, 40, 50, 65, 80, 100, 125, 150, 175, 200, 225, 250, 275, 300, 350, 400, 450, 500, 600, 700, 800, 1000, 1200, 1600, 2000, 2400, 3200]
    
    # Phase 1: Maximum Quality (Local Colormaps preserved)
    for t in [0, 10]:
        profiles.append({"thresh": t, "colors": 256, "max_l": 200, "quality": 100})
        
    # Phase 2: Standard Quality (Local Colormaps preserved)
    for t in dense_thresholds:
        profiles.append({"thresh": t, "colors": 256, "max_l": 200, "quality": 90})
        
    # Phase 3: Lower Colors (Global Colormaps forced)
    for t in dense_thresholds[dense_thresholds.index(100):]:  # Start from 100
        profiles.append({"thresh": t, "colors": 192, "max_l": 200, "quality": 90})
        
    # Phase 4: Extreme compression
    for t in dense_thresholds[dense_thresholds.index(400):]:  # Start from 400
        profiles.append({"thresh": t, "colors": 128, "max_l": 200, "quality": 80})
        
    return profiles

PROGRESS_DICT = {}

@app.route('/progress/<task_id>')
def get_progress(task_id):
    return jsonify({"message": PROGRESS_DICT.get(task_id, "")})

def compress_gif_logic(input_path, output_path, target_kb, task_id=None, **kwargs):
    target_bytes = target_kb * 1024
    frames_dir = output_path + "_frames_tmp"
    os.makedirs(frames_dir, exist_ok=True)
    
    profiles = generate_profiles()
    
    def set_progress(msg):
        if task_id:
            PROGRESS_DICT[task_id] = msg
            
    try:
        set_progress("Iniciando Busca Binária de Perfis Otimizados...")
        low = 0
        high = len(profiles) - 1
        best_profile_idx = None
        best_result = None
        
        best_filepath = output_path + ".best.gif"
        
        while low <= high:
            mid = (low + high) // 2
            p = profiles[mid]
            
            set_progress(f"Avaliando Perfil {mid+1}/{len(profiles)} (Tolerância {p['thresh']})...")
            
            success, size, lossy, unique_pct = run_hybrid_stage_dynamic(
                input_path, output_path, target_bytes, frames_dir, 
                threshold=p["thresh"], max_lossy=p["max_l"], min_colors=p["colors"], quality=p["quality"]
            )
            
            if success:
                best_profile_idx = mid
                best_result = (size, lossy, unique_pct, p)
                if os.path.exists(output_path):
                    shutil.copy2(output_path, best_filepath)
                high = mid - 1
            else:
                low = mid + 1
                
        if best_profile_idx is not None:
            size, lossy, unique_pct, p = best_result
            if os.path.exists(best_filepath):
                shutil.move(best_filepath, output_path)
            
            if p["quality"] == 100: name = "Qualidade Máxima"
            elif p["colors"] == 256: name = "Qualidade Alta (Paleta Nativa)"
            elif p["colors"] == 192: name = "Qualidade Média"
            else: name = "Qualidade Baixa"
            
            lossy_str = f"Lossy {lossy}" if lossy > 0 else "Lossless"
            fps_str = f"Únicos {int(unique_pct*100)}%"
            
            set_progress("Finalizado!")
            return {"final_kb": size / 1024, "method": f"{name} ({fps_str}) + {lossy_str}"}
            
        set_progress("Extremo!")
        return {"final_kb": os.path.getsize(output_path) / 1024, "method": f"Extremo (Cores 128, Únicos <5%)", "warning": True}
        
    finally:
        if os.path.exists(frames_dir):
            shutil.rmtree(frames_dir)
        if os.path.exists(best_filepath):
            try: os.remove(best_filepath)
            except: pass

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
        task_id = request.form.get("task_id", None)
        result_meta = compress_gif_logic(input_path, temp_output, target_kb, task_id=task_id)
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
