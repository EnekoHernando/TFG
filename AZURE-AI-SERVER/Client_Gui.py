import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QInputDialog, QMessageBox
from Client import ChatClient  # Importamos la lógica del cliente
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

class ChatClientThread(QThread):
    message_received = pyqtSignal(str)

    def __init__(self, client):
        super().__init__()
        self.client = client

    def run(self):
        while self.client.connected:
            response = self.client.recv_message()
            if response:
                self.message_received.emit(response)

class ChatClientGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.client = ChatClient()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Chat Client')
        self.resize(800, 600)  # Ajustar el tamaño de la ventana

        main_layout = QVBoxLayout()
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        main_layout.addWidget(self.chat_display)
        
        input_layout = QHBoxLayout()
        
        self.text_input = QLineEdit()
        input_layout.addWidget(self.text_input)
        
        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        main_layout.addLayout(input_layout)
        
        self.setLayout(main_layout)

        self.connect_to_server()

    def connect_to_server(self):
        username, ok = QInputDialog.getText(self, 'Nombre de usuario', 'Ingrese su nombre de usuario:')
        if ok:
            self.client.connect(username)
            if self.client.connected:
                self.chat_thread = ChatClientThread(self.client)
                self.chat_thread.message_received.connect(self.display_message)
                self.chat_thread.start()
            else:
                self.display_error("No se pudo conectar al servidor.")
                self.close()

    @pyqtSlot(str)
    def display_message(self, message):
        self.chat_display.append(f'Bot: {message}')

    def display_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)
        self.close()

    def send_message(self):
        message = self.text_input.text()
        if message:
            self.chat_display.append(f'User: {message}')
            response = self.client.send_message(message)
            if response:
                self.chat_display.append(f'Bot: {response}')
            self.text_input.clear()

    def closeEvent(self, event):
        self.client.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client_gui = ChatClientGUI()
    client_gui.show()
    sys.exit(app.exec_())