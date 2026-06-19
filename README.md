# 🌍 Interface d'Analyse Spatiale - Occupation du Sol (Cambodge)

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![GDAL](https://img.shields.io/badge/GDAL-000000?style=for-the-badge&logo=qgis&logoColor=white)

## 📖 Description du Projet
Cette application interactive développée avec **Streamlit** permet de générer et visualiser les résultats de classification de l'occupation du sol (Land Cover) générés par la chaîne de traitement **IOTA2** (modèle Random Forest). 

Le projet se concentre sur le territoire du **Cambodge** et intègre des données optiques (Sentinel-2) ainsi que des features externes (Distance à la mer, Densité de bâtiments, MNT) pour différencier avec précision 12 classes environnementales (Mangrove, Forêt, Agriculture, Tissu urbain, etc.).

---

## 🛠️ Prérequis et Installation

### 1. Cloner le dépôt
git clone [https://github.com/ton-nom/iota2-cambodia-streamlit.git](https://github.com/ton-nom/iota2-cambodia-streamlit.git)
cd iota2-cambodia-streamlit

2. Créer un environnement virtuel (Recommandé)
Bash

python3 -m venv venv
source venv/bin/activate  # Sur Linux/Mac
# venv\Scripts\activate   # Sur Windows

3. Installer les dépendances

Assurez-vous d'avoir GDAL correctement configuré sur votre système avant d'installer les paquets Python.
Bash

pip install -r requirements.txt

Contenu type du requirements.txt :

    streamlit
    geopandas
    rasterio
    folium
    streamlit-folium
    matplotlib
    numpy

🚀 Démarrer l'Application

Une fois les dépendances installées, lancez le serveur Streamlit avec la commande suivante :
Bash

streamlit run app.py

L'interface s'ouvrira automatiquement dans votre navigateur par défaut à l'adresse http://localhost:8501.
📂 Structure du Répertoire
Plaintext

📁 iota2-cambodia-streamlit/
│
├── 📄 app.py                  # Script principal de l'interface Streamlit
├── 📄 requirements.txt        # Liste des dépendances Python
├── 📄 README.md               # Ce fichier
│
├── 📁 data/                   # Dossier contenant les données (ignoré par Git)
│   ├── 📁 features_externes/  # Tuiles de distance mer, densité, etc.
│   ├── 📁 model_results/      # Raster finaux de IOTA2
│   └── 📄 nomenclature.txt    # Correspondance Code/Classe (ex: 5 = Shrubland)
│
└── 📁 utils/                  # Scripts utilitaires
    └── 📄 raster_tools.py     # Fonctions de lecture/conversion avec Rasterio

🧠 Contexte Technique (Modélisation)

Les données visualisées par cette application sont le fruit d'un pipeline de Data Engineering strict :

    Découpage chirurgical : Tuilage (ex: T48PUV) en blocs de 10980x10980 pixels.

    Apprentissage : Modèle Random Forest entraîné sur des points de vérité terrain (Shapefiles) minutieusement répartis pour éviter les biais géographiques.
    
📝 Auteur

Kheobs - Initial work Matthew MARTINE
