import socket
import logging

# Configuración de logging
logging.basicConfig(filename='client.log', level=logging.INFO)

# Configuración del cliente sin SSL
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = 'localhost'
port = 12345
client_socket.connect((host, port))
logging.info(f"Conectado al servidor {host} en el puerto {port}.")

try:
    while True:
        message = input("Tú: ")
        if message.lower() == 'bye':
            client_socket.close()
            logging.info("Cliente desconectado por solicitud del usuario.")
            break
        try:
            client_socket.sendall(message.encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            print("Bot:", response)
            logging.info(f"Mensaje enviado y respuesta recibida.")
        except Exception as e:
            logging.error(f"Error en la comunicación: {e}")
            client_socket.close()
            break
finally:
    client_socket.close()
    logging.info("Conexión del cliente cerrada.")
