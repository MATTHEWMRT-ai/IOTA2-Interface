import streamlit as st
import subprocess
import os
import re
import shutil

# --- FIXED CONFIGURATION ---
PIXI_EXE = "/home/kheobs/.pixi/bin/pixi"
OUTPUT_FOLDER = "/media/kheobs/DATA/IOTA2_TEST_ZONE/IOTA2_Outputs/Results_classif"

# Page configuration
st.set_page_config(page_title="IOTA2 Expert Panel", layout="wide")
st.title("🛰️ IOTA2 - Classification Interface")

# --- SIDEBAR ---
st.sidebar.header("📁 File Configuration")

def get_file_path(uploaded_file, text_path):
    if uploaded_file is not None:
        save_path = os.path.join("/tmp", uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return save_path
    return text_path

u_cfg = st.sidebar.file_uploader("Upload .cfg", type=["cfg"])
p_cfg = st.sidebar.text_input("Path to .cfg", "/media/kheobs/DATA/IOTA2_TEST_ZONE/i2_tutorial_classification.cfg")

u_col = st.sidebar.file_uploader("Upload colorFile.txt", type=["txt"])
p_col = st.sidebar.text_input("Path to colors", "/media/kheobs/DATA/IOTA2_TEST_ZONE/colorFile.txt")

u_nom = st.sidebar.file_uploader("Upload nomenclature", type=["txt"])
p_nom = st.sidebar.text_input("Path to nomenclature", "/media/kheobs/DATA/IOTA2_TEST_ZONE/nomenclature23.txt")

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Algorithm Parameters")
scheduler_choice = st.sidebar.radio("Execution mode", ["debug"])
nb_trees = st.sidebar.slider("Number of trees (nbtrees)", 10, 500, 100, 10)
train_ratio = st.sidebar.slider("Training ratio (%)", 1, 100, 10, 5) / 100

final_config_orig = get_file_path(u_cfg, p_cfg)
final_color = get_file_path(u_col, p_col)
final_nom = get_file_path(u_nom, p_nom)

BASE_FINAL = os.path.join(OUTPUT_FOLDER, "final")
matrix_path = os.path.join(BASE_FINAL, "Confusion_Matrix_Classif_Seed_0.png")
map_path = os.path.join(BASE_FINAL, "Classif_Seed_0_ColorIndexed.tif")
preview_path = os.path.join(BASE_FINAL, "Color_Preview.png")

# --- TECHNICAL FUNCTIONS ---

def prepare_iota_config(path, trees, ratio, nomenclature, color):
    if not os.path.exists(path): return None
    with open(path, 'r') as f:
        content = f.read()
    if "classifier.rf.nbtrees" in content:
        content = re.sub(r"('classifier.rf.nbtrees'\s*:\s*)\d+", rf"\g<1>{trees}", content)
    else:
        content = content.replace("'classifier.rf.min'", f"'classifier.rf.nbtrees': {trees}, 'classifier.rf.min'")
    content = re.sub(r"('strategy.percent.p'\s*:\s*)[0-9.]+", rf"\g<1>{ratio}", content)
    content = re.sub(r"(nomenclature_path\s*:\s*).*?\n", rf"\g<1>'{nomenclature}'\n", content)
    content = re.sub(r"(color_table\s*:\s*).*?\n", rf"\g<1>'{color}'\n", content)
    custom_path = "/tmp/iota2_auto_config.cfg"
    with open(custom_path, 'w') as f:
        f.write(content)
    return custom_path

def convert_to_png(tif, png, c_file):
    if not os.path.exists(tif): return False
    try:
        tmp = tif.replace(".tif", "_tmp.tif")
        subprocess.run(["gdaldem", "color-relief", tif, c_file, tmp, "-alpha"], check=True)
        subprocess.run(["gdal_translate", "-of", "PNG", tmp, png], check=True)
        if os.path.exists(tmp): os.remove(tmp)
        return True
    except: return False

# --- ACTION ZONE ---

st.info(f"🚀 **Config:** {scheduler_choice} | 🌳 {nb_trees} trees | 📊 Ratio {int(train_ratio*100)}%")

col_btn1, col_btn2 = st.columns(2)

with col_btn2:
    # RESET BUTTON: ONLY performs cleanup
    if st.button("♻️ RESET (Clean folders)", use_container_width=True, type="primary"):
        with st.status("Deep cleaning in progress...", expanded=True) as status:
            if os.path.exists(OUTPUT_FOLDER):
                shutil.rmtree(OUTPUT_FOLDER, ignore_errors=True)
            
            tmp_cfg = "/tmp/iota2_auto_config.cfg"
            if os.path.exists(tmp_cfg):
                os.remove(tmp_cfg)
                
            os.makedirs(OUTPUT_FOLDER, exist_ok=True)
            status.update(label="Folders cleaned. Ready for a new calculation!", state="complete")
        st.toast("System reset", icon="🧹")

with col_btn1:
    # RUN BUTTON: Performs preparation and calculation
    if st.button("🚀 RUN CALCULATION", use_container_width=True):
        work_cfg = prepare_iota_config(final_config_orig, nb_trees, train_ratio, final_nom, final_color)
        
        if work_cfg:
            cmd = [PIXI_EXE, "run", "Iota2.py", "-config", work_cfg, "-scheduler_type", scheduler_choice, "-restart"]
            
            with st.expander("IOTA2 Calculation Logs", expanded=True):
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in process.stdout:
                    st.text(line.strip())
                process.wait()
            
            # Smart check (if the map exists, it's good)
            if os.path.exists(map_path) or process.returncode == 0:
                st.success("✅ Calculation completed successfully!")
                convert_to_png(map_path, preview_path, final_color)
                st.balloons()
            else:
                st.error("Finished or error, check the logs.")

st.markdown("---")

# --- RESULTS ---
st.header("📊 Results")
c1, c2 = st.columns(2)
W = 700

with c1:
    st.subheader("📈 Confusion Matrix")
    if os.path.exists(matrix_path):
        st.image(matrix_path, width=W)
    else:
        st.warning("Matrix not found.")

with c2:
    st.subheader("🗺️ Map")
    if os.path.exists(map_path) and not os.path.exists(preview_path):
        convert_to_png(map_path, preview_path, final_color)
    if os.path.exists(preview_path):
        st.image(preview_path, width=W)
    else:
        st.info("The map will appear here.")
