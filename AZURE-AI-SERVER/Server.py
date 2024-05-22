import socket
import logging
import openai
import threading
import time
from openai import AzureOpenAI
import os
import requests

# Nombre del archivo de log
log_filename = 'server.log'

# Borrar el archivo de log existente si ya existe
if os.path.exists(log_filename):
    os.remove(log_filename)

# Configuración de logging
logging.basicConfig(filename=log_filename, level=logging.INFO)

# Configuración de la API de Azure OpenAI
openai.api_type = "azure"
openai.api_version = "2024-02-15-preview"
openai.api_base = os.getenv("AzureApiBase")
openai.api_key = os.getenv("AzureApiKey")
deployment_id = os.getenv("deployment_id")

# Configuración del endpoint de Azure Search
search_endpoint = os.getenv("AzureSearchEndpoint")
search_key = os.getenv("AzureSearchKey")
search_index_name = "cyc"
session=""

client = AzureOpenAI(api_version="2024-02-15-preview",
azure_endpoint=os.getenv("AzureApiBase"),
api_key=os.getenv("AzureApiKey"))

def chatbot(input_text):
    message_text = [{"role": "user", "content": input_text}]
    logging.info(f'chatbot function, input text: {input_text}')
    try:
        logging.info(f'Completition')
        completion = client.chat.completions.create(
            messages=message_text,
            model=deployment_id,
            extra_body={"data_sources":[
                {
                    "type": "azure_search",
                    "parameters": {
                        "endpoint": search_endpoint,
                        "index_name": search_index_name,
                        "semantic_configuration": "default",
                        "query_type": "simple",
                        "fields_mapping": {},
                        "in_scope": True,
                        "role_information": "Eres un asistente de AI que tiene que ayudar a estudiantes de programación con python.",
                        "filter": None,
                        "strictness": 3,
                        "top_n_documents": 5,
                        "authentication": {
                            "type": "api_key",
                            "key": search_key
                        },
                    "key":search_key,
                    "indexName": search_index_name
                    }
                }]},
            temperature=0.75,
            top_p=1,
            max_tokens=2000,
            stop=None,
            
        )
        
        logging.info(f'Completition finished')
        return completion.choices[0].message.content if completion.choices else "No response"
    except Exception as e:
        logging.error(f"Error during API call: {e}")
        return "Error while processing your request."

def handle_client(client_socket, addr):
    logging.info(f'Conectado con {addr}')
    print(f"Conexión establecida con {addr}")

    try:
        while True:  # Mantener la conexión abierta para múltiples mensajes
            input_text = client_socket.recv(1024).decode('utf-8')
            if not input_text:
                print(f"No se recibió más información de {addr}")
                break  # Salir del bucle si no se recibe información
            logging.info(f'Mensaje recibido: {input_text}')
            print(f"Mensaje recibido de {addr}: '{input_text}'")

            if input_text.lower() == "bye":
                logging.info(f'Conexión con {addr} cerrada por el cliente.')
                print(f"Cliente {addr} ha enviado 'bye'. Cerrando conexión.")
                break  # Salir del bucle interno si el cliente dice "bye"

            start_time = time.time()  # Registrar el tiempo de inicio
            response = chatbot(input_text)
            end_time = time.time()  # Registrar el tiempo de finalización
            response_time = end_time - start_time  # Calcular el tiempo de respuesta
            logging.info(f'Tiempo de respuesta: {response_time:.2f} segundos')
            print(f"Tiempo de respuesta: {response_time:.2f} segundos")

            logging.info(f'Respuesta preparada: {response}')
            print(f"Enviando respuesta a {addr}: '{response}'")
            client_socket.sendall(response.encode('utf-8'))
            logging.info(f'Respuesta enviada a {addr}')
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