import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QInputDialog, QMessageBox, QComboBox, QDialog, QLabel, QFormLayout
from PyQt5.QtGui import QTextCursor, QColor
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt
from Client import ChatClient

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

class UserInputDialog(QDialog):
    def __init__(self, indices, parent=None):
        super(UserInputDialog, self).__init__(parent)
        self.setWindowTitle("Ingresar Información")

        layout = QFormLayout()
        
        self.username_input = QLineEdit(self)
        layout.addRow("Nombre de usuario:", self.username_input)
        
        self.index_combo = QComboBox(self)
        self.index_combo.addItems(indices)
        layout.addRow("Seleccione un índice:", self.index_combo)

        self.button_box = QHBoxLayout()
        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        self.button_box.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.reject)
        self.button_box.addWidget(self.cancel_button)

        layout.addRow(self.button_box)
        
        self.setLayout(layout)

    def get_inputs(self):
        return self.username_input.text(), self.index_combo.currentText()

class ChatClientGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.client = ChatClient()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Chat Client')
        self.resize(800, 600)

        main_layout = QVBoxLayout()
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: #2e2e2e; color: white;")
        main_layout.addWidget(self.chat_display)
        
        input_layout = QHBoxLayout()
        
        self.text_input = QLineEdit()
        self.text_input.setStyleSheet("background-color: #1e1e1e; color: white;")
        input_layout.addWidget(self.text_input)
        
        self.send_button = QPushButton('Send')
        self.send_button.setStyleSheet("background-color: #444; color: white;")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        main_layout.addLayout(input_layout)
        
        self.setLayout(main_layout)

        self.connect_to_server()

    def connect_to_server(self):
        self.client.connect()  # Conectar sin enviar nada todavía para obtener la lista de índices
        if self.client.connected:
            indices_context = self.client.receive_indices()
            if indices_context:
                dialog = UserInputDialog(indices_context.keys(), self)
                if dialog.exec() == QDialog.Accepted:
                    username, selected_index = dialog.get_inputs()
                    self.client.send_user_data(username, selected_index)
                    if self.client.connected:
                        self.chat_thread = ChatClientThread(self.client)
                        self.chat_thread.message_received.connect(self.display_message)
                        self.chat_thread.start()
                    else:
                        self.display_error("No se pudo conectar al servidor.")
                        self.close()
                else:
                    self.close()
            else:
                self.display_error("No se pudo obtener la lista de índices.")
                self.close()
        else:
            self.display_error("No se pudo conectar al servidor.")
            self.close()

    @pyqtSlot(str)
    def display_message(self, message):
        self.append_message("Bot", message, None)

    def display_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)
        self.close()

    def send_message(self):
        message = self.text_input.text()
        if message:
            self.append_message("User", message, QColor(90, 90, 90))
            response = self.client.send_message(message)
            if response:
                self.append_message("Bot", response, None)
            self.text_input.clear()

    def append_message(self, sender, message, color):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)

        if sender == "User":
            color_name = color.name()
            # Reemplaza los saltos de línea y tabulaciones por sus equivalentes en HTML
            message = message.replace('\n', '<br>')
            message = message.replace('\t', '&emsp;')
            html_message = f"""
            <div style="
                display: flex;
                justify-content: flex-end;
                clear: both;
            ">
                <div style="
                    background-color: {color_name};
                    color: white;
                    padding: 10px 15px;
                    border-radius: 15px;
                    margin: 10px 0;
                    width: fit-content;
                    max-width: 75%;
                    text-align: left;
                ">
                    {message}
                </div>
            </div>
            <div style="clear: both;"></div>
            """
        else:
            # Reemplaza los saltos de línea y tabulaciones por sus equivalentes en HTML
            message = message.replace('\n', '<br>')
            message = message.replace('\t', '&emsp;')
            html_message = f"""
            <div style="
                display: flex;
                justify-content: flex-start;
                clear: both;
            ">
                <div style="
                    color: white;
                    padding: 10px 15px;
                    margin: 10px 0;
                    width: fit-content;
                    max-width: 75%;
                    text-align: left;
                ">
                    {message}
                </div>
            </div>
            <div style="clear: both;"></div>
            """

        cursor.insertHtml(html_message)
        cursor.insertBlock()

        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()

    def closeEvent(self, event):
        self.client.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client_gui = ChatClientGUI()
    client_gui.show()
    sys.exit(app.exec_())