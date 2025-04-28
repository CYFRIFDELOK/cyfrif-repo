import sys
import time
import pywhatkit as kit
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QVBoxLayout

def send_whatsapp_messages(phone_numbers, message):
    """
    Sends a WhatsApp message to multiple recipients.
    
    :param phone_numbers: List of phone numbers (strings).
    :param message: The message to send.
    """
    if not phone_numbers or not message:
        print("❌ No recipients or empty message!")
        return

    for phone in phone_numbers:
        phone = phone.strip()
        if phone:
            try:
                print(f"📩 Sending to: {phone} | Message: {message}")
                kit.sendwhatmsg_instantly(f"+{phone}", message, wait_time=10, tab_close=False)
                print(f"✅ Message sent to {phone}")
                time.sleep(7)  # Delay to avoid rate limits
            except Exception as e:
                print(f"❌ Error sending to {phone}: {e}")

    print("✅ All messages sent successfully!")

class WhatsAppSenderUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("WhatsApp Bulk Sender")
        self.setGeometry(100, 100, 400, 250)
        
        layout = QVBoxLayout()
        
        self.phone_label = QLabel("Enter phone numbers (comma-separated):")
        layout.addWidget(self.phone_label)
        self.phone_input = QLineEdit()
        layout.addWidget(self.phone_input)
        
        self.message_label = QLabel("Enter message:")
        layout.addWidget(self.message_label)
        self.message_input = QTextEdit()
        layout.addWidget(self.message_input)
        
        self.send_button = QPushButton("Send Messages")
        self.send_button.clicked.connect(self.send_messages)
        layout.addWidget(self.send_button)
        
        self.setLayout(layout)
    
    def send_messages(self):
        phone_numbers = self.phone_input.text().split(',')
        message = self.message_input.toPlainText()
        send_whatsapp_messages(phone_numbers, message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WhatsAppSenderUI()
    window.show()
    sys.exit(app.exec_())

















