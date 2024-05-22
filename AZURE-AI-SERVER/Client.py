import socket
import logging

# Configuración de logging
logging.basicConfig(filename='client.log', level=logging.INFO)

# Configuración del cliente sin SSL
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = 'localhost'
port = 12345

try:
    client_socket.connect((host, port))
    logging.info(f"Conectado al servidor {host} en el puerto {port}.")
except Exception as e:
    logging.error(f"No se pudo conectar al servidor: {e}")
    exit(1)

# Lista para almacenar el historial de mensajes
message_history = []

try:
    while True:
        message = input("Tú: ")
        if message.lower() == 'byee':
            client_socket.sendall(message.encode('utf-8'))  # Asegúrate de enviar "byee" al servidor
            client_socket.close()
            logging.info("Cliente desconectado por solicitud del usuario.")
            break
        
        # Añadir el mensaje del usuario al historial
        message_history.append({"role": "user", "content": message})
        
        # Preparar el contexto con los últimos dos mensajes del cliente y del bot
        context = ""
        if len(message_history) >= 4:
            context += f"Pregunta anterior del cliente: {message_history[-4]['content']}\n"
            context += f"Respuesta anterior del bot: {message_history[-3]['content']}\n"
            context += f"Pregunta actual del cliente: {message_history[-2]['content']}\n"
        elif len(message_history) >= 2:
            context += f"Pregunta anterior del cliente: {message_history[-2]['content']}\n"
        
        context += f"Pregunta actual del cliente: {message_history[-1]['content']}\n"
        
        try:
            client_socket.sendall(context.encode('utf-8'))  # Enviar el contexto al servidor
            response = client_socket.recv(1024).decode('utf-8')
            print("Bot:", response)
            logging.info("Mensaje enviado y respuesta recibida.")
            
            # Añadir la respuesta del bot al historial
            message_history.append({"role": "assistant", "content": response})
            
        except Exception as e:
            logging.error(f"Error en la comunicación: {e}")
            break
finally:
    client_socket.close()
    logging.info("Conexión del cliente cerrada.")