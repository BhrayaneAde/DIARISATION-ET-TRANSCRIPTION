# 🎤 Interview Transcription & Diarisation

Une application web moderne pour la transcription automatique et l'identification des locuteurs dans les fichiers audio. Parfait pour les interviews, réunions, podcasts et débats.

## ✨ Fonctionnalités

- 🎯 **Transcription automatique** avec Whisper (OpenAI)
- 👥 **Diarisation intelligente** - Identification des locuteurs
- 💬 **Interface chat moderne** - Affichage style messagerie
- 🌍 **Détection automatique** de la langue (français prioritaire)
- 📊 **Analyse détaillée** - Temps de parole par personne
- 🎤 **Détection mono/multi-locuteurs** automatique
- 📱 **Interface responsive** avec drag & drop

## 🚀 Installation

### Prérequis

- **Python 3.11 ou 3.12** (⚠️ Éviter Python 3.13)
- **Git** pour cloner le projet
- **Token Hugging Face** (gratuit)

### 1. Cloner le projet

```bash
git clone https://github.com/BhrayaneAde/DIARISATION-ET-TRANSCRIPTION.git
cd DIARISATION-ET-TRANSCRIPTION
```

### 2. Créer l'environnement virtuel

```bash
# Créer l'environnement
python -m venv venv

# Activer (Windows)
venv\Scripts\activate

# Activer (Linux/Mac)
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
# Mettre à jour pip
python -m pip install --upgrade pip

# Installer les packages
pip install -r requirements.txt

# Installer FFmpeg
python install_ffmpeg.py
```

### 4. Configuration Hugging Face

1. Créer un compte sur [Hugging Face](https://huggingface.co)
2. Aller dans **Settings** → **Access Tokens**
3. Créer un nouveau token
4. Créer le fichier `.env` :

```bash
# Créer le fichier .env
echo HF_AUTH_TOKEN=votre_token_ici > .env
```

### 5. Lancer l'application

```bash
# Démarrer le serveur
python main_app.py
```

🌐 **Accéder à l'interface :** http://localhost:5002

## 📋 Utilisation

### Interface Web

1. **Glissez-déposez** votre fichier audio ou cliquez pour sélectionner
2. **Formats supportés** : `.m4a`, `.wav`, `.mp3`, `.mp4` (max 500MB)
3. **Cliquez** sur "Démarrer l'analyse"
4. **Attendez** le traitement (barre de progression)
5. **Consultez** les résultats en format chat

### Types de Contenu

- **📻 Monologue** : Podcast solo, présentation → Affichage unifié
- **💬 Dialogue** : Interview, débat → Chat alterné avec couleurs
- **👥 Multi-locuteurs** : Réunion → Identification automatique

## 🛠️ Dépannage

### Erreurs Communes

**❌ "Diarisation non disponible"**
```bash
# Vérifier le token HF
echo $HF_AUTH_TOKEN  # Linux/Mac
echo %HF_AUTH_TOKEN%  # Windows

# Recharger le token
set HF_AUTH_TOKEN=votre_token
python main_app.py
```

**❌ "FFmpeg introuvable"**
```bash
# FFmpeg est inclus dans le projet
set PATH=%PATH%;%CD%
python main_app.py
```

**❌ Erreurs Python 3.13**
```bash
# Utiliser Python 3.11 ou 3.12
python --version
# Si 3.13, installer Python 3.11/3.12
```

### Performance

- **CPU** : Fonctionne sur CPU (plus lent mais accessible)
- **GPU** : Modifier `device="cuda"` dans le code pour accélération
- **Mémoire** : 8GB RAM recommandés pour les gros fichiers

## 📁 Structure du Projet

```
DIARISATION-ET-TRANSCRIPTION/
├── main_app.py              # 🚀 Application principale
├── install_ffmpeg.py        # 📦 Installation FFmpeg
├── requirements.txt         # 📦 Dépendances
├── .env                     # 🔑 Token Hugging Face
├── uploads/                # 📁 Fichiers uploadés
├── output/                 # 📄 Résultats générés
└── README.md               # 📖 Documentation
```

## 🔧 Technologies

- **[Whisper](https://github.com/openai/whisper)** - Transcription (OpenAI)
- **[Pyannote.audio](https://github.com/pyannote/pyannote-audio)** - Diarisation
- **[Flask](https://flask.palletsprojects.com/)** - Serveur web
- **HTML/CSS/JavaScript** - Interface utilisateur

## 📊 Formats de Sortie

### Chat Interface
- Bulles colorées par locuteur
- Timestamps précis
- Avatars personnalisés

### Analyse Détaillée
- Temps de parole par personne
- Nombre de segments
- Répartition temporelle

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit (`git commit -m 'Ajout fonctionnalité'`)
4. Push (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

- **Issues** : [GitHub Issues](https://github.com/BhrayaneAde/DIARISATION-ET-TRANSCRIPTION/issues)
- **Documentation** : Ce README
- **Exemples** : Dossier `examples/` (à venir)

---

**Développé avec ❤️ pour la communauté open source**