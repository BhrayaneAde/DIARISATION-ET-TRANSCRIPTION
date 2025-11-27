#!/usr/bin/env python3
"""
Script d'installation automatique de FFmpeg
Télécharge et configure FFmpeg pour le projet
"""

import os
import requests
import zipfile
import shutil
from pathlib import Path

def download_ffmpeg():
    """Télécharge et installe FFmpeg"""
    print("📥 Téléchargement de FFmpeg...")
    
    # URL de téléchargement FFmpeg Windows
    url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    
    # Télécharger
    response = requests.get(url, stream=True)
    with open("ffmpeg.zip", "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print("📦 Extraction...")
    
    # Extraire
    with zipfile.ZipFile("ffmpeg.zip", 'r') as zip_ref:
        zip_ref.extractall(".")
    
    # Trouver le dossier extrait
    for item in os.listdir("."):
        if item.startswith("ffmpeg-") and os.path.isdir(item):
            ffmpeg_dir = item
            break
    
    # Copier ffmpeg.exe
    src = os.path.join(ffmpeg_dir, "bin", "ffmpeg.exe")
    if os.path.exists(src):
        shutil.copy2(src, "ffmpeg.exe")
        print("✅ FFmpeg installé avec succès!")
    
    # Nettoyer
    os.remove("ffmpeg.zip")
    shutil.rmtree(ffmpeg_dir)
    
    print("🎉 Installation terminée!")

if __name__ == "__main__":
    if not os.path.exists("ffmpeg.exe"):
        download_ffmpeg()
    else:
        print("✅ FFmpeg déjà installé!")