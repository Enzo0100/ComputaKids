from flask import Flask, request, jsonify, render_template, send_from_directory
from app.groq_model import GroqModel
from app.teaching_assistant import TeachingAssistant
import os

app = Flask(__name__, 
    template_folder='transcricao/templates',
    static_folder='transcricao/static'
)

# Configuração do modelo Groq
api_key = "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"  # Substituir pela chave da API Groq
groq_model = GroqModel(api_key=api_key)
assistant = TeachingAssistant(groq_model)

@app.route('/')
def index():
    """Renderiza a página principal do jogo."""
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    """Processa a mensagem do usuário e retorna a resposta."""
    data = request.json
    user_question = data.get('question')
    level = data.get('level', 0)
    is_consult_mode = data.get('isConsultMode', False)
    
    if not user_question:
        return jsonify({"error": "Pergunta não fornecida"}), 400
        
    try:
        if is_consult_mode:
            # No modo consulta, usamos o explain_concept diretamente
            response = assistant.explain_concept(user_question)
        else:
            # No modo jogo, usamos o process_question normal
            response = assistant.process_question(user_question, level)
        return jsonify(response)
    except Exception as e:
        print(f"Erro ao processar pergunta: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/start_level/<int:level>', methods=['GET'])
def start_level(level):
    """Inicia um novo nível do jogo."""
    try:
        response = assistant.start_level(level)
        return jsonify(response)
    except Exception as e:
        print(f"Erro ao iniciar nível: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/next_question/<int:level>', methods=['GET'])
def next_question(level):
    """Obtém a próxima pergunta do nível atual."""
    try:
        response = assistant.next_question()
        return jsonify(response)
    except Exception as e:
        print(f"Erro ao obter próxima pergunta: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/progress', methods=['GET'])
def get_progress():
    """Obtém o progresso atual do jogo."""
    try:
        progress = assistant.get_progress()
        return jsonify(progress)
    except Exception as e:
        print(f"Erro ao obter progresso: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Processa o áudio enviado e retorna a transcrição."""
    if 'audio' not in request.files:
        return jsonify({"error": "Nenhum arquivo de áudio fornecido"}), 400
        
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400
        
    try:
        import whisper
        import tempfile

        # Salvar o arquivo de áudio temporariamente
        with tempfile.NamedTemporaryFile(delete=False) as temp_audio_file:
            audio_file.save(temp_audio_file.name)
            temp_audio_path = temp_audio_file.name

        # Carregar o modelo Whisper
        model = whisper.load_model("base")

        # Transcrever o áudio em português
        result = model.transcribe(temp_audio_path, language='pt')

        # Retornar a transcrição
        return jsonify({
            "transcription": result['text']
        }), 200
    except Exception as e:
        print(f"Erro na transcrição: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
