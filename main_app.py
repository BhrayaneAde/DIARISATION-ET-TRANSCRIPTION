from flask import Flask, request, jsonify, render_template_string
import whisper
import os
from pathlib import Path
from pyannote.audio import Pipeline
from datetime import timedelta
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)

# Load models once at startup
print("🔄 Chargement des modèles...")
whisper_model = whisper.load_model("large-v3")

# Load diarization pipeline with error handling
try:
    from dotenv import load_dotenv
    load_dotenv()
    hf_token = os.environ.get("HF_AUTH_TOKEN")
    print(f"🔑 Token HF: {hf_token[:10]}..." if hf_token else "❌ Pas de token HF")
    
    if not hf_token:
        raise ValueError("HF_AUTH_TOKEN not found in environment")
    
    print("🔄 Chargement du pipeline de diarisation...")
    diarization_pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization", 
        use_auth_token=hf_token
    )
    print("✅ Modèles chargés avec diarisation!")
except Exception as e:
    print(f"⚠️ Diarisation non disponible: {e}")
    print("Utilisation du mode alternatif (attribution automatique)")
    diarization_pipeline = None
    print("✅ Modèle Whisper chargé (sans diarisation)!")

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎤 Transcription & Diarisation Avancée</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .upload-card { background: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); margin-bottom: 30px; }
        .file-drop { border: 3px dashed #667eea; border-radius: 10px; padding: 40px; text-align: center; cursor: pointer; transition: all 0.3s; }
        .file-drop:hover { border-color: #764ba2; background: #f8f9ff; }
        .file-drop.dragover { border-color: #4CAF50; background: #e8f5e8; }
        .upload-btn { background: linear-gradient(45deg, #667eea, #764ba2); color: white; border: none; padding: 15px 30px; border-radius: 25px; font-size: 16px; cursor: pointer; margin-top: 20px; }
        .upload-btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .upload-btn:disabled { background: #ccc; cursor: not-allowed; transform: none; }
        .progress { width: 100%; height: 25px; background: #f0f0f0; border-radius: 15px; overflow: hidden; margin: 20px 0; display: none; }
        .progress-bar { height: 100%; background: linear-gradient(45deg, #4CAF50, #45a049); width: 0%; transition: width 0.3s; border-radius: 15px; }
        .results { background: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); display: none; }
        .chat-container { background: #f8f9fa; border-radius: 15px; padding: 20px; margin-bottom: 20px; max-height: 500px; overflow-y: auto; }
        .chat-message { margin-bottom: 15px; display: flex; align-items: flex-start; }
        .chat-message.speaker-0 { justify-content: flex-start; }
        .chat-message.speaker-1 { justify-content: flex-end; }
        .chat-bubble { max-width: 70%; padding: 12px 16px; border-radius: 18px; position: relative; word-wrap: break-word; }
        .chat-bubble.speaker-0 { background: linear-gradient(135deg, #667eea, #764ba2); color: white; margin-right: auto; }
        .chat-bubble.speaker-1 { background: linear-gradient(135deg, #f093fb, #f5576c); color: white; margin-left: auto; }
        .chat-bubble.speaker-2 { background: linear-gradient(135deg, #4facfe, #00f2fe); color: white; }
        .chat-avatar { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; margin: 0 10px; }
        .chat-avatar.speaker-0 { background: linear-gradient(135deg, #667eea, #764ba2); }
        .chat-avatar.speaker-1 { background: linear-gradient(135deg, #f093fb, #f5576c); }
        .chat-avatar.speaker-2 { background: linear-gradient(135deg, #4facfe, #00f2fe); }
        .chat-timestamp { font-size: 0.8em; opacity: 0.7; margin-top: 5px; }
        .speaker-name { font-size: 0.9em; font-weight: bold; margin-bottom: 5px; opacity: 0.9; }
        .speakers-section { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .speaker-card { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; border-radius: 10px; }
        .speaker-card.speaker-0 { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .speaker-card.speaker-1 { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
        .speaker-card.speaker-2 { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
        .speaker-segments { max-height: 200px; overflow-y: auto; margin-top: 10px; }
        .segment { background: rgba(255,255,255,0.2); padding: 10px; margin: 5px 0; border-radius: 5px; }
        .timestamp { font-size: 0.9em; opacity: 0.8; }
        .status { padding: 15px; border-radius: 10px; margin: 20px 0; text-align: center; font-weight: bold; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .info { background: #d1ecf1; color: #0c5460; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎤 Transcription & Diarisation</h1>
            <p>Intelligence artificielle pour interviews multi-locuteurs</p>
        </div>

        <div class="upload-card">
            <div class="file-drop" id="fileDrop" onclick="document.getElementById('audioFile').click()">
                <input type="file" id="audioFile" accept="audio/*" style="display: none;" onchange="handleFileSelect(this)">
                <h3>📁 Glissez votre fichier audio ici</h3>
                <p>ou cliquez pour sélectionner</p>
                <p><small>Formats: .m4a, .wav, .mp3, .mp4 | Max: 500MB</small></p>
            </div>
            <div id="fileName" style="margin-top: 15px; font-weight: bold; color: #667eea;"></div>
            <button class="upload-btn" id="uploadBtn" onclick="startTranscription()" disabled>
                🚀 Démarrer l'analyse
            </button>
            <div class="progress" id="progress">
                <div class="progress-bar" id="progressBar"></div>
            </div>
            <div id="status"></div>
        </div>

        <div class="results" id="results">
            <h2>💬 Conversation</h2>
            <div class="chat-container" id="chatContainer"></div>
            
            <h2>👥 Analyse par Locuteur</h2>
            <div class="speakers-section" id="speakersSection"></div>
        </div>
    </div>

    <script>
        let selectedFile = null;

        // Drag & Drop
        const fileDrop = document.getElementById('fileDrop');
        fileDrop.addEventListener('dragover', (e) => {
            e.preventDefault();
            fileDrop.classList.add('dragover');
        });
        fileDrop.addEventListener('dragleave', () => {
            fileDrop.classList.remove('dragover');
        });
        fileDrop.addEventListener('drop', (e) => {
            e.preventDefault();
            fileDrop.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                document.getElementById('audioFile').files = files;
                handleFileSelect(document.getElementById('audioFile'));
            }
        });

        function handleFileSelect(input) {
            selectedFile = input.files[0];
            if (selectedFile) {
                document.getElementById('fileName').textContent = `📎 ${selectedFile.name} (${(selectedFile.size/1024/1024).toFixed(1)} MB)`;
                document.getElementById('uploadBtn').disabled = false;
            }
        }

        function startTranscription() {
            if (!selectedFile) return;

            const formData = new FormData();
            formData.append('audio', selectedFile);

            document.getElementById('uploadBtn').disabled = true;
            document.getElementById('uploadBtn').textContent = '⏳ Analyse en cours...';
            document.getElementById('progress').style.display = 'block';
            document.getElementById('results').style.display = 'none';

            // Simulate progress
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += Math.random() * 5;
                if (progress > 95) progress = 95;
                document.getElementById('progressBar').style.width = progress + '%';
            }, 1000);

            fetch('/process', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                clearInterval(progressInterval);
                document.getElementById('progressBar').style.width = '100%';
                
                if (data.success) {
                    displayResults(data);
                    document.getElementById('status').innerHTML = '<div class="status success">✅ Analyse terminée avec succès!</div>';
                } else {
                    document.getElementById('status').innerHTML = `<div class="status error">❌ ${data.error}</div>`;
                }
            })
            .catch(error => {
                clearInterval(progressInterval);
                document.getElementById('status').innerHTML = `<div class="status error">❌ Erreur: ${error.message}</div>`;
            })
            .finally(() => {
                document.getElementById('uploadBtn').disabled = false;
                document.getElementById('uploadBtn').textContent = '🚀 Démarrer l\\'analyse';
                setTimeout(() => document.getElementById('progress').style.display = 'none', 1000);
            });
        }

        function displayResults(data) {
            // Chat-style conversation
            const chatContainer = document.getElementById('chatContainer');
            chatContainer.innerHTML = '';
            
            // Get speaker names and assign colors
            const speakerNames = Object.keys(data.speakers);
            const speakerColors = {};
            speakerNames.forEach((speaker, index) => {
                speakerColors[speaker] = index;
            });
            
            // Check if mono-speaker
            const isMonoSpeaker = speakerNames.length === 1 || speakerNames.some(name => name.includes('ORATEUR_PRINCIPAL'));
            
            // Display messages in chat format
            data.segments.forEach(segment => {
                const messageDiv = document.createElement('div');
                const speakerIndex = speakerColors[segment.speaker] || 0;
                
                if (isMonoSpeaker) {
                    // Mode mono-locuteur: tous les messages à gauche
                    messageDiv.className = `chat-message speaker-0`;
                } else {
                    // Mode multi-locuteurs: alternance gauche/droite
                    messageDiv.className = `chat-message speaker-${speakerIndex}`;
                }
                
                const avatarDiv = document.createElement('div');
                avatarDiv.className = `chat-avatar speaker-${speakerIndex}`;
                avatarDiv.textContent = isMonoSpeaker ? '🎤' : segment.speaker.charAt(segment.speaker.length - 1);
                
                const bubbleDiv = document.createElement('div');
                bubbleDiv.className = `chat-bubble speaker-${speakerIndex}`;
                
                const speakerDisplayName = isMonoSpeaker ? 'Orateur' : segment.speaker;
                
                bubbleDiv.innerHTML = `
                    <div class="speaker-name">${speakerDisplayName}</div>
                    <div>${segment.text}</div>
                    <div class="chat-timestamp">${segment.start}</div>
                `;
                
                // Pour mono-locuteur, toujours avatar à gauche
                if (isMonoSpeaker || speakerIndex % 2 === 0) {
                    messageDiv.appendChild(avatarDiv);
                    messageDiv.appendChild(bubbleDiv);
                } else {
                    messageDiv.appendChild(bubbleDiv);
                    messageDiv.appendChild(avatarDiv);
                }
                
                chatContainer.appendChild(messageDiv);
            });
            
            // Speakers analysis
            const speakersSection = document.getElementById('speakersSection');
            speakersSection.innerHTML = '';
            
            Object.entries(data.speakers).forEach(([speaker, info], index) => {
                const speakerCard = document.createElement('div');
                speakerCard.className = `speaker-card speaker-${index}`;
                
                speakerCard.innerHTML = `
                    <h3>🎭 ${speaker}</h3>
                    <p><strong>Temps de parole:</strong> ${info.duration}</p>
                    <p><strong>Segments:</strong> ${info.segments.length}</p>
                    <div class="speaker-segments">
                        ${info.segments.map(seg => `
                            <div class="segment">
                                <div class="timestamp">[${seg.start} - ${seg.end}]</div>
                                <div>${seg.text}</div>
                            </div>
                        `).join('')}
                    </div>
                `;
                
                speakersSection.appendChild(speakerCard);
            });
            
            document.getElementById('results').style.display = 'block';
            
            // Auto-scroll to bottom of chat
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/process', methods=['POST'])
def process_audio():
    try:
        file = request.files['audio']
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        print(f"🎵 Traitement de {filepath}...")
        
        # 1. Transcription avec Whisper
        print("📝 Transcription...")
        # Auto-détection de la langue ou français par défaut
        result = whisper_model.transcribe(filepath, language=None)  # Auto-detect
        detected_language = result.get('language', 'fr')
        print(f"🌍 Langue détectée: {detected_language}")
        
        # Si pas français, re-transcrire en français
        if detected_language != 'fr':
            print("🔄 Re-transcription en français...")
            result = whisper_model.transcribe(filepath, language="fr")
        
        # 2. Diarisation avec pyannote (si disponible)
        if diarization_pipeline:
            print("👥 Identification des locuteurs...")
            diarization = diarization_pipeline(filepath)
        else:
            print("⚠️ Diarisation non disponible - attribution automatique")
            diarization = None
        
        # 3. Fusion des résultats
        print("🔗 Fusion des données...")
        segments_with_speakers = []
        
        # Détection du nombre de locuteurs basée sur la diarisation
        unique_speakers = set()
        if diarization:
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                unique_speakers.add(speaker)
            num_speakers = len(unique_speakers)
            
            if num_speakers == 1:
                print(f"🎤 MONO-LOCUTEUR détecté: {list(unique_speakers)[0]}")
            else:
                print(f"👥 {num_speakers} LOCUTEURS détectés: {list(unique_speakers)}")
        else:
            # Sans diarisation, on assume 2 locuteurs (stéréo)
            num_speakers = 2
            print("👥 Mode STÉRÉO: 2 locuteurs assumés (pas de diarisation)")
        
        for i, segment in enumerate(result["segments"]):
            seg_start = segment["start"]
            seg_end = segment["end"]
            
            # Trouver le locuteur pour ce segment
            if diarization:
                speaker_label = "Locuteur_Inconnu"
                for turn, _, speaker in diarization.itertracks(yield_label=True):
                    if turn.start <= seg_start <= turn.end or turn.start <= seg_end <= turn.end:
                        speaker_label = speaker
                        break
                
                # Si vraiment 1 seul locuteur détecté, renommer
                if num_speakers == 1:
                    speaker_label = "ORATEUR_PRINCIPAL"
            else:
                # Sans diarisation: mode stéréo (2 locuteurs)
                speaker_label = f"SPEAKER_{i % 2:02d}"
            
            segments_with_speakers.append({
                "start": str(timedelta(seconds=int(seg_start))),
                "end": str(timedelta(seconds=int(seg_end))),
                "text": segment["text"].strip(),
                "speaker": speaker_label
            })
        
        # 4. Analyse par locuteur
        speakers_analysis = {}
        for segment in segments_with_speakers:
            speaker = segment["speaker"]
            if speaker not in speakers_analysis:
                speakers_analysis[speaker] = {
                    "segments": [],
                    "total_duration": 0
                }
            
            speakers_analysis[speaker]["segments"].append(segment)
            # Calculer durée approximative
            start_parts = segment["start"].split(":")
            end_parts = segment["end"].split(":")
            start_seconds = int(start_parts[0])*3600 + int(start_parts[1])*60 + int(start_parts[2])
            end_seconds = int(end_parts[0])*3600 + int(end_parts[1])*60 + int(end_parts[2])
            speakers_analysis[speaker]["total_duration"] += (end_seconds - start_seconds)
        
        # Formater les durées
        for speaker in speakers_analysis:
            duration = speakers_analysis[speaker]["total_duration"]
            speakers_analysis[speaker]["duration"] = str(timedelta(seconds=duration))
        
        # 5. Transcript complet
        full_transcript = "\n".join([
            f"[{seg['start']} - {seg['end']}] {seg['speaker']}: {seg['text']}"
            for seg in segments_with_speakers
        ])
        
        print("✅ Traitement terminé!")
        
        return jsonify({
            'success': True,
            'full_transcript': full_transcript,
            'speakers': speakers_analysis,
            'segments': segments_with_speakers
        })
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5002)