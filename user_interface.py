import sys
import time
import asyncio
import pywhatkit as kit
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QVBoxLayout,
                             QTabWidget, QTimeEdit, QMessageBox, QFileDialog)
from PyQt5.QtCore import QTimer, QTime
from telegram import Bot, InputFile
from telegram.error import TelegramError

class MessagingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.image_path = None  # Store selected image path

        # Telegram scheduler
        self.telegram_timer = QTimer(self)
        self.telegram_timer.timeout.connect(self.check_telegram_schedule)
        self.telegram_timer.start(1000)
        self.scheduled_time = None

        # WhatsApp scheduler
        self.whatsapp_timer = QTimer(self)
        self.whatsapp_timer.timeout.connect(self.check_whatsapp_schedule)
        self.whatsapp_timer.start(1000)
        self.whatsapp_scheduled_time = None

    def initUI(self):
        self.setWindowTitle("Messaging App - WhatsApp & Telegram")
        self.setGeometry(100, 100, 500, 650)

        self.tabs = QTabWidget()
        self.whatsapp_tab = self.create_whatsapp_tab()
        self.telegram_tab = self.create_telegram_tab()

        self.tabs.addTab(self.whatsapp_tab, "WhatsApp")
        self.tabs.addTab(self.telegram_tab, "Telegram")

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def create_whatsapp_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.whatsapp_phone_input = QLineEdit()
        self.whatsapp_phone_input.setPlaceholderText("Enter phone numbers (comma-separated)")
        layout.addWidget(self.whatsapp_phone_input)

        self.whatsapp_message_input = QTextEdit()
        self.whatsapp_message_input.setPlaceholderText("Enter message")
        layout.addWidget(self.whatsapp_message_input)

        self.whatsapp_image_button = QPushButton("Select Image")
        self.whatsapp_image_button.clicked.connect(self.select_image)
        layout.addWidget(self.whatsapp_image_button)

        self.whatsapp_time_picker = QTimeEdit()
        self.whatsapp_time_picker.setTime(QTime.currentTime())
        layout.addWidget(self.whatsapp_time_picker)

        self.whatsapp_send_button = QPushButton("Schedule WhatsApp Messages")
        self.whatsapp_send_button.clicked.connect(self.schedule_whatsapp_message)
        layout.addWidget(self.whatsapp_send_button)

        tab.setLayout(layout)
        return tab

    def create_telegram_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.telegram_token_input = QTextEdit()
        self.telegram_token_input.setPlaceholderText("Enter Telegram Bot Token(s) (one per line)")
        layout.addWidget(self.telegram_token_input)

        self.telegram_id_input = QTextEdit()
        self.telegram_id_input.setPlaceholderText("Enter Chat IDs (comma-separated)")
        layout.addWidget(self.telegram_id_input)

        self.telegram_message_input = QTextEdit()
        self.telegram_message_input.setPlaceholderText("Enter Telegram message")
        layout.addWidget(self.telegram_message_input)

        self.telegram_image_button = QPushButton("Select Image")
        self.telegram_image_button.clicked.connect(self.select_image)
        layout.addWidget(self.telegram_image_button)

        self.telegram_time_picker = QTimeEdit()
        self.telegram_time_picker.setTime(QTime.currentTime())
        layout.addWidget(self.telegram_time_picker)

        self.telegram_send_button = QPushButton("Schedule Telegram Message")
        self.telegram_send_button.clicked.connect(self.schedule_telegram_message)
        layout.addWidget(self.telegram_send_button)

        tab.setLayout(layout)
        return tab

    def select_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.image_path = file_path
            QMessageBox.information(self, "Image Selected", f"Image selected: {file_path}")

    def schedule_whatsapp_message(self):
        self.whatsapp_scheduled_time = self.whatsapp_time_picker.time().toString("HH:mm")
        QMessageBox.information(self, "Scheduled", f"WhatsApp message scheduled for {self.whatsapp_scheduled_time}")

    def check_whatsapp_schedule(self):
        if self.whatsapp_scheduled_time and QTime.currentTime().toString("HH:mm") == self.whatsapp_scheduled_time:
            print("✅ Scheduled WhatsApp message is being sent now!")
            self.send_whatsapp_messages()
            self.whatsapp_scheduled_time = None

    def send_whatsapp_messages(self):
        phone_numbers = self.whatsapp_phone_input.text().split(',')
        message = self.whatsapp_message_input.toPlainText()

        for phone in phone_numbers:
            phone = phone.strip()
            if phone:
                try:
                    if self.image_path:
                        kit.sendwhats_image(f"+{phone}", self.image_path, caption=message, wait_time=10, tab_close=False)
                    else:
                        kit.sendwhatmsg_instantly(f"+{phone}", message, wait_time=10, tab_close=False)
                    time.sleep(10)
                except Exception as e:
                    print(f"Error sending to {phone}: {e}")
        print("✅ All WhatsApp messages sent!")

    def schedule_telegram_message(self):
        self.scheduled_time = self.telegram_time_picker.time().toString("HH:mm")
        QMessageBox.information(self, "Scheduled", f"Telegram message scheduled for {self.scheduled_time}")

    def check_telegram_schedule(self):
        if self.scheduled_time and QTime.currentTime().toString("HH:mm") == self.scheduled_time:
            print("✅ Scheduled Telegram message is being sent now!")
            asyncio.run(self.send_telegram_messages())
            self.scheduled_time = None

    async def send_telegram_messages(self):
        bot_tokens = self.telegram_token_input.toPlainText().strip().split("\n")
        chat_ids = self.telegram_id_input.toPlainText().strip().replace("\n", "").split(",")
        message = self.telegram_message_input.toPlainText().strip()

        if not bot_tokens or not chat_ids:
            QMessageBox.warning(self, "Warning", "Please enter bot tokens and chat IDs.")
            return

        for bot_token in bot_tokens:
            bot = Bot(token=bot_token.strip())
            for chat_id in chat_ids:
                try:
                    if self.image_path:
                        with open(self.image_path, "rb") as img:
                            await bot.send_photo(chat_id=chat_id.strip(), photo=InputFile(img), caption=message)
                    else:
                        await bot.send_message(chat_id=chat_id.strip(), text=message)
                    await asyncio.sleep(2)
                except TelegramError as e:
                    print(f"Error sending to {chat_id}: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MessagingApp()
    window.show()
    sys.exit(app.exec_())

