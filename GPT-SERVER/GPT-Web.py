import os
import logging
import threading
from llama_index.core import StorageContext, load_index_from_storage
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

# Configuración de logging
logging.basicConfig(filename='server.log', level=logging.INFO)
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAIKEY")

def read_last_messages(user_dir, num_messages=4):
    conversation_file = os.path.join(user_dir, "conversation.txt")
    if not os.path.exists(conversation_file):
        return ""
    with open(conversation_file, "r", encoding='utf-8') as file:
        lines = file.readlines()

    messages = []
    user_msg, bot_msg = None, None
    for line in reversed(lines):
        if line.startswith("Cliente: "):
            user_msg = line.strip()
        elif line.startswith("Bot: "):
            bot_msg = line.strip()
        if user_msg and bot_msg:
            messages.append(user_msg)
            messages.append(bot_msg)
            user_msg, bot_msg = None, None
        if len(messages) >= num_messages * 2:
            break
    return "\n".join(reversed(messages))

def save_conversation(username, message, response):
    user_dir = os.path.join("conversaciones", username)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    conversation_file = os.path.join(user_dir, "conversation.txt")
    with open(conversation_file, "a", encoding='utf-8') as file:
        file.write(f"Cliente: {message}\n")
        file.write(f"Bot: {response}\n")

def clear_conversation(username):
    user_dir = os.path.join("conversaciones", username)
    conversation_file = os.path.join(user_dir, "conversation.txt")
    if os.path.exists(conversation_file):
        os.remove(conversation_file)

def chatbot(input_text, index_path, username):
    logging.info(f"Recibido texto: {input_text}")
    storage_context = StorageContext.from_defaults(persist_dir=index_path)
    new_index = load_index_from_storage(storage_context)
    new_query_engine = new_index.as_query_engine()

    # Leer los últimos 4 mensajes de la conversación del usuario
    user_dir = os.path.join("conversaciones", username)
    context = read_last_messages(user_dir)
    
    # Construir el mensaje para el bot
    if context:
        prompt = f"Contexto:\n{context}\n\nPregunta:\nCliente: {input_text}"
    else:
        prompt = f"Pregunta:\nCliente: {input_text}"
    
    response = new_query_engine.query(prompt)
    logging.info(f"Texto de respuesta: {response}")
    return response.response

app = Flask(__name__)
CORS(app)

clients = {}

@app.route('/connect', methods=['POST'])
def connect():
    data = request.json
    username = data.get('username')
    index = data.get('index')
    session_id = str(uuid.uuid4())
    clients[session_id] = {"username": username, "index": index}
    
    # Limpiar la conversación al conectar
    clear_conversation(username)
    
    return jsonify({"message": "Connected", "session_id": session_id})

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    session_id = data.get('session_id')
    message = data.get('message')
    if session_id in clients:
        username = clients[session_id]["username"]
        index_path = os.path.join("indices", clients[session_id]["index"])
        response = chatbot(message, index_path, username)
        save_conversation(username, message, response)
        return jsonify({"response": response})
    else:
        return jsonify({"error": "Invalid session_id"}), 400

@app.route('/get_indices', methods=['GET'])
def get_indices():
    indices_dir = "indices"
    indices = [d for d in os.listdir(indices_dir) if os.path.isdir(os.path.join(indices_dir, d))]
    return jsonify({"indices": indices})

def run_flask():
    app.run(host='0.0.0.0', port=5000)

flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

try:
    logging.info('Ya se puede conectar al servidor')
    print("Ya se puede conectar al servidor")
except KeyboardInterrupt:
    logging.info("Servidor cerrado por interrupción del teclado.")
finally:
    logging.info("Servidor cerrado.")