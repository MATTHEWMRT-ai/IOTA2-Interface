import streamlit as st
import subprocess
import os
import re
import glob
import platform

# ==========================================
# PATH CONFIGURATION
# ==========================================
PIXI_EXE = "XXXXX/.pixi/bin/pixi"
IOTA2_DIR = "XXXXXX/iota2"
SCRIPT_REL_PATH = "iota2/Iota2.py"

st.set_page_config(page_title="IOTA2 Control Panel", layout="wide")
st.title("🛰️ IOTA2 - Control Panel")
st.markdown("---")

# --- SIDEBAR ---
st.sidebar.header("📁 Configuration Files")

def get_file_path(uploaded_file, text_path):
    if uploaded_file is not None:
        save_path = os.path.join("/tmp", uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return save_path
    return text_path

u_cfg = st.sidebar.file_uploader("Upload Main .cfg", type=["cfg"])
p_cfg = st.sidebar.text_input("Path to Main .cfg", "XXXXXXXXXXXXXXXX/i2_classification.cfg")

u_col = st.sidebar.file_uploader("Upload colorFile.txt", type=["txt"])
p_col = st.sidebar.text_input("Path to colors", "XXXXXXXXXXXXXXX/colorFile.txt")

u_nom = st.sidebar.file_uploader("Upload nomenclature", type=["txt"])
p_nom = st.sidebar.text_input("Path to nomenclature", "XXXXXXXXXX/nomenclature23.txt")

# --- NOUVEAU : Fichier de ressources Dask ---
st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Dask Resources Config")
u_res = st.sidebar.file_uploader("Upload config_ressources.cfg", type=["cfg"])
p_res = st.sidebar.text_input("Path to config_ressources", "XXXXXXXXXXXXXXXX/config_ressources_example.cfg")

# --- Dossier sensor_data ---
st.sidebar.markdown("---")
st.sidebar.subheader("🛰️ Sensor Data")
p_sensor = st.sidebar.text_input("Path to sensor_data folder", "XXXXXXXXXXXXX/sensor_data")

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Settings & Hardware")
st.sidebar.info("💡 Make sure your resource config matches your parallel tasks!")

scheduler_choice = st.sidebar.selectbox("Execution Mode", ["localCluster", "debug"])

if scheduler_choice == "localCluster":
    st.sidebar.success("🛡️ localCluster selected: 'ulimit' and 'exports' applied securely.")

output_folder = st.sidebar.text_input("Output Folder", "XXXXXXXXXXXX/IOTA2_output")

# --- NOUVEAU : Paramètres de parallélisation ---
st.sidebar.markdown("---")
st.sidebar.subheader("🚀Performance")
nb_tasks = st.sidebar.number_input("Number of Parallel Tasks (-nb_parallel_tasks)", min_value=1, max_value=64, value=4, step=1)

ram_limit = st.sidebar.slider(
    "OTB Max RAM Hint (MB)", 
    min_value=128, 
    max_value=32000, 
    value=8192, 
    step=512, 
    help="Limits internal RAM per OTB process. 8192 = 8GB."
)

# --- PATH VARIABLES RESOLUTION ---
final_config_orig = get_file_path(u_cfg, p_cfg)
final_color = get_file_path(u_col, p_col)
final_nom = get_file_path(u_nom, p_nom)
final_res = get_file_path(u_res, p_res)  # Résolution du fichier de ressources
BASE_FINAL = os.path.join(output_folder, "final")
matrix_path = os.path.join(BASE_FINAL, "Confusion_Matrix_Classif_Seed_0.png")

# --- TECHNICAL FUNCTIONS ---
def prepare_iota_config(path, nomenclature, color, out_folder):
    if not os.path.exists(path): return None
    with open(path, 'r') as f:
        content = f.read()
    
    content = re.sub(r"(nomenclature_path\s*:\s*).*?\n", rf"\g<1>'{nomenclature}'\n", content)
    content = re.sub(r"(color_table\s*:\s*).*?\n", rf"\g<1>'{color}'\n", content)
    content = re.sub(r"(output_path\s*:\s*).*?\n", rf"\g<1>'{out_folder}'\n", content)
    content = re.sub(r"(remove_output_path\s*:\s*).*?\n", r"\g<1>True\n", content)
    
    custom_path = "/tmp/iota2_auto_config.cfg"
    with open(custom_path, 'w') as f:
        f.write(content)
    return custom_path

def purge_stacks(sensor_path):
    if not os.path.exists(sensor_path):
        return 0
        
    files = glob.glob(os.path.join(sensor_path, "**/*_STACK.tif"), recursive=True) + \
            glob.glob(os.path.join(sensor_path, "**/*_BINARY_MASK.tif"), recursive=True)
    for f in files:
        try: os.remove(f)
        except: pass
    return len(files)

# --- SECTION 1 : STANDARD PROCESSING ---
st.header("1. Standard Processing (Training / Test)")
col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 LAUNCH IOTA2 (HPC Mode)", use_container_width=True):
        work_cfg = prepare_iota_config(final_config_orig, final_nom, final_color, output_folder)
        if work_cfg:
            my_env = os.environ.copy()
            my_env["PYTHONPATH"] = f"{IOTA2_DIR}:{my_env.get('PYTHONPATH', '')}"
            my_env["PATH"] = f"{IOTA2_DIR}/iota2:{my_env.get('PATH', '')}"
            my_env["PYTHONNOUSERSITE"] = "1"
            my_env["OTB_MAX_RAM_HINT"] = str(ram_limit)
            
            # --- MISE À JOUR DE LA COMMANDE D'EXÉCUTION ---
            if scheduler_choice == "localCluster":
                bash_command = (
                    "ulimit -n 65535 && "
                    f"export PATH=\"{IOTA2_DIR}/iota2:$PATH\" && "
                    f"export PYTHONPATH=\"{IOTA2_DIR}:$PYTHONPATH\" && "
                    f"export OTB_MAX_RAM_HINT={ram_limit} && "
                    f"{PIXI_EXE} run python {SCRIPT_REL_PATH} "
                    f"-config {work_cfg} "
                    f"-config_ressources {final_res} "
                    f"-nb_parallel_tasks {nb_tasks} "
                    f"-scheduler_type {scheduler_choice}"
                )
                cmd = ["bash", "-c", bash_command]
            else:
                cmd = [
                    PIXI_EXE, "run", "python", SCRIPT_REL_PATH, 
                    "-config", work_cfg,
                    "-config_ressources", final_res,
                    "-nb_parallel_tasks", str(nb_tasks),
                    "-scheduler_type", scheduler_choice
                ]
            
            with st.expander("Live Logs", expanded=True):
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=IOTA2_DIR, env=my_env)
                for line in process.stdout: st.text(line.strip())
                process.wait()

with col2:
    if st.button("🧹 MANUAL RESET & PURGE (Sensor Data)", use_container_width=True, type="primary"):
        nb = purge_stacks(p_sensor)
        st.success(f"Disk cleaned: {nb} old _STACK / _BINARY_MASK files deleted from {p_sensor}.")

st.markdown("---")

# --- SECTION 2 : RESULTS ---
st.header("2. Results")

def create_map_preview(tif_path, png_path):
    if os.path.exists(png_path) and os.path.getmtime(png_path) > os.path.getmtime(tif_path):
        return True
    
    with st.spinner("🖼️ Generating map preview from heavy .tif..."):
        try:
            cmd = [PIXI_EXE, "run", "gdal_translate", "-of", "PNG", "-outsize", "800", "0", tif_path, png_path]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            st.error(f"Error generating preview: {e}")
            return False

col_res1, col_res2 = st.columns(2)

with col_res1:
    st.subheader("Confusion Matrix")
    if os.path.exists(matrix_path):
        st.image(matrix_path, caption="Latest Confusion Matrix", use_container_width=True)
    else:
        st.info("Waiting for the confusion matrix to be generated...")

with col_res2:
    st.subheader("Classification Map")
    final_tifs = glob.glob(os.path.join(BASE_FINAL, "*Classif*.tif"))
    
    if final_tifs:
        main_tif = final_tifs[0] 
        preview_path = os.path.join(BASE_FINAL, "map_preview.png")
        
        if create_map_preview(main_tif, preview_path):
            st.image(preview_path, caption="Final Classification Map (Preview)", use_container_width=True)
            
            if st.button("📂 Open Results Folder"):
                subprocess.Popen(["xdg-open", BASE_FINAL]) # 'xdg-open' au lieu de 'explorer.exe' pour Linux
    else:
        st.info("Waiting for the final .tif classification map...")
