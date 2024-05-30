import socket
import logging
import openai
import threading
import time
from openai import AzureOpenAI
import os
import sys
import json

# Configurar la codificación predeterminada a UTF-8
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Nombre del archivo de log
log_filename = 'server.log'

# Borrar el archivo de log existente si ya existe
if os.path.exists(log_filename):
    os.remove(log_filename)

# Configuración de logging
logging.basicConfig(filename=log_filename, level=logging.INFO, encoding='utf-8')

# Configuración de la API de Azure OpenAI
openai.api_type = "azure"
openai.api_version = "2024-02-15-preview"
openai.api_base = os.getenv("AzureApiBase")
openai.api_key = os.getenv("AzureApiKey")
deployment_id = os.getenv("deploymentid")

# Configuración del endpoint de Azure Search
search_endpoint = os.getenv("AzureSearchEndpoint")
search_key = os.getenv("AzureSearchKey")
session=""

# Configuración del diccionario de índices y sus contextos
indices_context = {
    "cyc": "Contexto para CYC",
    "eticacivica": "Contexto para Ética Cívica",
    "prog1": "Contexto para Prog1",
    "sapresumenesyejeneko": "Contexto para Sap Resumenes y Ejercicios NEKO",
    "sapresumenesyejerprofe": "Contexto para Sap Resumenes y Ejercicios Profe",
    "sistemasinformacion": "Contexto para Sistemas de Información"
}

class ChatbotHandler:
    def __init__(self, username, index_name):
        self.username = username
        self.index_name = index_name
        self.client = AzureOpenAI(api_version="2024-02-15-preview",
                                  azure_endpoint=os.getenv("AzureApiBase"),
                                  api_key=os.getenv("AzureApiKey"))
        
        self.user_dir = os.path.join("Conversaciones", username)
        if not os.path.exists(self.user_dir):
            os.makedirs(self.user_dir)
        self.conversation_file = os.path.join(self.user_dir, "conversation.txt")
        
        # Eliminar todos los archivos en el directorio del usuario
        for file in os.listdir(self.user_dir):
            file_path = os.path.join(self.user_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

    def chatbot(self, input_text):
        last_messages = self.read_last_messages(6)
        message_text = [{"role": "user", "content": msg} for msg in last_messages]
        message_text.append({"role": "user", "content": input_text})
        logging.info(f'chatbot function, input text: {input_text}')
        try:
            logging.info(f'Completion')
            completion = self.client.chat.completions.create(
                messages=message_text,
                model=deployment_id,
                extra_body={"data_sources": [
                    {
                        "type": "azure_search",
                        "parameters": {
                            "endpoint": search_endpoint,
                            "index_name": self.index_name,
                            "semantic_configuration": "default",
                            "query_type": "simple",
                            "fields_mapping": {},
                            "in_scope": True,
                            "role_information": indices_context[self.index_name],
                            "filter": None,
                            "strictness": 3,
                            "top_n_documents": 5,
                            "authentication": {
                                "type": "api_key",
                                "key": search_key
                            },
                        "key": search_key,
                        "indexName": self.index_name
                        }
                    }]},
                temperature=0.75,
                top_p=1,
                max_tokens=2000,
                stop=None,
                
            )
            
            logging.info(f'Completion finished')
            return completion.choices[0].message.content if completion.choices else "No response"
        except Exception as e:
            logging.error(f"Error during API call: {e}")
            return "Error while processing your request."

    def read_last_messages(self, num_messages):
        if not os.path.exists(self.conversation_file):
            return []
        with open(self.conversation_file, "r", encoding='utf-8') as file:
            lines = file.readlines()
        
        messages = []
        user_msg, bot_msg = None, None
        for line in reversed(lines):
            if line.startswith("User: "):
                user_msg = line[len("User: "):].strip()
            elif line.startswith("Bot: "):
                bot_msg = line[len("Bot: "):].strip()
            if user_msg and bot_msg:
                messages.append(user_msg)
                messages.append(bot_msg)
                user_msg, bot_msg = None, None
            if len(messages) >= num_messages:
                break
        return list(reversed(messages[:num_messages]))

    def save_conversation(self, message, response):
        with open(self.conversation_file, "a", encoding='utf-8') as file:
            file.write(f"User: {message}\n")
            file.write(f"Bot: {response}\n")

def handle_client(client_socket, addr):
    logging.info(f'Conectado con {addr}')
    print(f"Conexión establecida con {addr}")

    try:
        # Enviar la lista de índices al cliente
        indices_json = json.dumps(indices_context)
        client_socket.sendall(indices_json.encode('utf-8'))

        data = client_socket.recv(1024).decode('utf-8').strip()
        user_data = json.loads(data)
        username = user_data.get("username")
        selected_index = user_data.get("selected_index")

        logging.info(f'Usuario {username} conectado desde {addr}')
        client_socket.sendall(f"Bienvenido {username}!\n".encode('utf-8'))
        
        if selected_index in indices_context:
            logging.info(f'Índice seleccionado por el cliente: {selected_index}')
        else:
            logging.error(f'Índice inválido seleccionado: {selected_index}')
            client_socket.sendall("Índice inválido seleccionado.\n".encode('utf-8'))
            client_socket.close()
            return

        chatbot_handler = ChatbotHandler(username, selected_index)

        while True:
            input_text = client_socket.recv(1024).decode('utf-8')
            if not input_text:
                print(f"No se recibió más información de {addr}")
                break
            logging.info(f'Mensaje recibido de {username}: {input_text}')
            print(f"Mensaje recibido de {addr}: '{input_text}'")

            if input_text.lower() == "bye":
                logging.info(f'Conexión con {addr} cerrada por el cliente.')
                print(f"Cliente {addr} ha enviado 'bye'. Cerrando conexión.")
                break

            start_time = time.time()
            response = chatbot_handler.chatbot(input_text)
            end_time = time.time()
            response_time = end_time - start_time
            logging.info(f'Tiempo de respuesta: {response_time:.2f} segundos')
            print(f"Tiempo de respuesta: {response_time:.2f} segundos")

            logging.info(f'Respuesta preparada: {response}')
            print(f"Enviando respuesta a {addr}: '{response}'")
            try:
                client_socket.sendall(response.encode('utf-8'))
                logging.info(f'Respuesta enviada a {addr}')
            except UnicodeEncodeError as e:
                logging.error(f"Error al enviar respuesta a {addr}: {e}")
                client_socket.sendall("Error al procesar la respuesta.\n".encode('utf-8'))

            chatbot_handler.save_conversation(input_text, response)
    except Exception as e:
        logging.error(f"Error al manejar la conexión del cliente {addr}: {e}")
    finally:
        client_socket.close()
        logging.info(f"Conexión con el cliente {addr} cerrada.")
        print(f"Conexión con {addr} ha sido cerrada.")

# Configuración del servidor sin SSL
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = 'localhost'
port = 12345
server_socket.bind((host, port))
server_socket.listen(5)
logging.info(f"Servidor escuchando en {host}:{port} sin SSL...")
print(f"Servidor iniciado y escuchando en {host}:{port}")

try:
    while True:
        client_socket, addr = server_socket.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_handler.start()
except KeyboardInterrupt:
    logging.info("Servidor cerrado por interrupción del teclado.")
    print("Servidor cerrado por interrupción del teclado.")
finally:
    server_socket.close()
    logging.info("Socket del servidor cerrado.")
    print("Socket del servidor cerrado.")




#indices_context[self.index_name]