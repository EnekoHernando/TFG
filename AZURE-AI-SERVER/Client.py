import socket
import logging

class ChatClient:
    def __init__(self, host='localhost', port=12345):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.username = ""
        self.connected = False
        logging.basicConfig(filename='client.log', level=logging.INFO)

    def connect(self, username):
        try:
            self.client_socket.connect((self.host, self.port))
            self.username = username
            self.client_socket.sendall(username.encode('utf-8'))
            self.connected = True
            logging.info(f"Conectado al servidor {self.host} en el puerto {self.port}.")
        except Exception as e:
            logging.error(f"No se pudo conectar al servidor: {e}")
            self.connected = False

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