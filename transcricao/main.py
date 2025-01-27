from flask import Flask, request, jsonify, render_template, send_from_directory
from app.groq_model import GroqModel
from app.teaching_assistant import TeachingAssistant
import os
import whisper
import tempfile

app = Flask(__name__)

# Configuração do modelo Groq
api_key = "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"  # Substituir pela chave da API Groq
groq_model = GroqModel(api_key=api_key)
assistant = TeachingAssistant(groq_model)

@app.route('/')
def index():
    """Renderiza a página principal do jogo."""
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve arquivos estáticos."""
    return send_from_directory('static', path)

@app.route('/ask', methods=['POST'])
def ask():
    """Processa a mensagem do usuário e retorna a resposta."""
    data = request.json
    user_question = data.get('question')
    level = data.get('level', 0)
    
    if not user_question:
        return jsonify({"error": "Pergunta não fornecida"}), 400
        
    try:
        response = assistant.process_question(user_question, level)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/start_level/<int:level>', methods=['GET'])
def start_level(level):
    """Inicia um novo nível do jogo."""
    try:
        response = assistant.start_level(level)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/next_question/<int:level>', methods=['GET'])
def next_question(level):
    """Obtém a próxima pergunta do nível atual."""
    try:
        response = assistant.next_question()
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/progress', methods=['GET'])
def get_progress():
    """Obtém o progresso atual do jogo."""
    try:
        progress = assistant.get_progress()
        return jsonify(progress)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

print("Iniciando carregamento do modelo Whisper...")
try:
    # Carrega o modelo Whisper (faça isso fora da rota para evitar recarregar a cada requisição)
    whisper_model = whisper.load_model("base")
    print("Modelo Whisper carregado com sucesso!")
except Exception as e:
    print(f"Erro ao carregar modelo Whisper: {str(e)}")
    whisper_model = None

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Processa o áudio enviado e retorna a transcrição."""
    print("Recebendo requisição de transcrição...")
    
    if whisper_model is None:
        return jsonify({"error": "Modelo de transcrição não está disponível"}), 500
    
    if 'audio' not in request.files:
        return jsonify({"error": "Nenhum arquivo de áudio fornecido"}), 400
        
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400
    
    print(f"Arquivo de áudio recebido: {audio_file.filename}")
    
    try:
        # Cria um arquivo temporário para salvar o áudio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
            print(f"Salvando áudio em arquivo temporário: {temp_audio.name}")
            audio_file.save(temp_audio.name)
            
            # Converte o áudio para o formato correto usando ffmpeg
            converted_file = temp_audio.name + '_converted.wav'
            print(f"Convertendo áudio para WAV: {converted_file}")
            os.system(f'ffmpeg -i {temp_audio.name} -ar 16000 -ac 1 -c:a pcm_s16le {converted_file}')
            
            print("Iniciando transcrição...")
            # Realiza a transcrição
            result = whisper_model.transcribe(converted_file)
            
            # Remove os arquivos temporários
            os.unlink(temp_audio.name)
            os.unlink(converted_file)
            print("Arquivos temporários removidos")
            
            if not result or 'text' not in result:
                print("Erro: Resultado da transcrição está vazio ou inválido")
                return jsonify({"error": "Falha ao transcrever o áudio"}), 500
            
            print(f"Transcrição realizada com sucesso: {result['text']}")
            
            # Retorna o texto transcrito
            return jsonify({
                "success": True,
                "transcription": result["text"]
            })
    except Exception as e:
        print(f"Erro durante a transcrição: {str(e)}")
        return jsonify({"error": f"Erro na transcrição: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
