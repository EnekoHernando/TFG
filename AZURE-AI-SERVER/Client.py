import socket
import logging
import json

class ChatClient:
    def __init__(self, host='localhost', port=12345):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.username = ""
        self.index = ""
        self.connected = False
        logging.basicConfig(filename='client.log', level=logging.INFO)

    def connect(self):
        try:
            self.client_socket.connect((self.host, self.port))
            self.connected = True
            logging.info(f"Conectado al servidor {self.host} en el puerto {self.port}.")
        except Exception as e:
            logging.error(f"No se pudo conectar al servidor: {e}")
            self.connected = False

    def send_user_data(self, username, index):
        try:
            self.username = username
            self.index = index
            user_data = json.dumps({"username": username, "selected_index": index})
            self.client_socket.sendall(user_data.encode('utf-8'))
        except Exception as e:
            logging.error(f"Error al enviar datos de usuario: {e}")

    def receive_indices(self):
        try:
            data = self.client_socket.recv(4096)  # Aumentar el buffer si es necesario
            indices_context = json.loads(data.decode('utf-8'))
            return indices_context
        except Exception as e:
            logging.error(f"Error al recibir la lista de índices: {e}")
            return {}

    def recv_message(self, buffer_size=1024, timeout=1):
        try:
            self.client_socket.settimeout(timeout)
            data = self.client_socket.recv(buffer_size)
            return data.decode('utf-8')
        except socket.timeout:
            return ""
        except Exception as e:
            logging.error(f"Error en la recepción de datos: {e}")
            self.connected = False
            return ""

    def send_message(self, message):
        if self.connected:
            try:
                self.client_socket.sendall(message.encode('utf-8'))
                if message.lower() == 'bye':
                    self.client_socket.close()
                    logging.info("Cliente desconectado por solicitud del usuario.")
                    self.connected = False
                else:
                    response = self.recv_message()
                    logging.info("Mensaje enviado y respuesta recibida.")
                    return response
            except Exception as e:
                logging.error(f"Error en la comunicación: {e}")
                self.connected = False
        return None

    def close(self):
        self.client_socket.close()
        logging.info("Conexión del cliente cerrada.")