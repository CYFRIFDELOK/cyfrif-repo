import sys
import asyncio
import os
from threading import Thread
from telegram import Bot
from telegram.error import TelegramError
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QMessageBox, QTimeEdit, QFileDialog
)
from PyQt5.QtCore import QTime, QTimer, Qt


class TelegramScheduler(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Telegram Scheduled Messenger")
        self.setGeometry(100, 100, 500, 500)

        layout = QVBoxLayout()

        # Input for Bot Token
        self.label_token = QLabel("Enter Bot Tokens (one per line):")
        layout.addWidget(self.label_token)
        self.input_token = QTextEdit()
        layout.addWidget(self.input_token)

        # Input for multiple chat IDs
        self.label_ids = QLabel("Enter Chat IDs (comma-separated):")
        layout.addWidget(self.label_ids)
        self.input_ids = QTextEdit()
        layout.addWidget(self.input_ids)

        # Input for message
        self.label_msg = QLabel("Enter Message:")
        layout.addWidget(self.label_msg)
        self.input_msg = QTextEdit()
        layout.addWidget(self.input_msg)

        # Image selection
        self.label_img = QLabel("Select Image (optional):")
        layout.addWidget(self.label_img)
        self.input_img = QTextEdit()
        layout.addWidget(self.input_img)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_image)
        layout.addWidget(self.browse_button)

        # Time picker
        self.label_time = QLabel("Select Time:")
        layout.addWidget(self.label_time)
        self.time_picker = QTimeEdit()
        self.time_picker.setTime(QTime.currentTime())
        layout.addWidget(self.time_picker)

        # Send button
        self.send_button = QPushButton("Schedule Message")
        self.send_button.clicked.connect(self.schedule_message)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def browse_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.gif)")
        if file_path:
            self.input_img.setText(file_path)

    def schedule_message(self):
        selected_time = self.time_picker.time()
        current_time = QTime.currentTime()
        time_diff = current_time.msecsTo(selected_time)

        if time_diff <= 0:
            QMessageBox.warning(self, "Warning", "Please select a future time.")
            return

        QTimer.singleShot(time_diff, self.send_message)
        QMessageBox.information(self, "Scheduled", f"Message scheduled for {selected_time.toString()}")

    def send_message(self):
        bot_tokens = self.input_token.toPlainText().strip().split("\n")
        chat_ids = self.input_ids.toPlainText().strip().replace("\n", "").split(",")
        message = self.input_msg.toPlainText().strip()
        image_path = self.input_img.toPlainText().strip()

        if not bot_tokens or not chat_ids or not message:
            QMessageBox.warning(self, "Warning", "Please enter bot tokens, chat IDs, and a message.")
            return

        valid_chat_ids = [chat_id.strip() for chat_id in chat_ids if chat_id.strip().isdigit()]
        if not valid_chat_ids:
            QMessageBox.warning(self, "Warning", "No valid chat IDs provided.")
            return

        # Start a thread for each bot token to handle sending the message
        for bot_token in bot_tokens:
            bot_token = bot_token.strip()
            if bot_token:
                bot = Bot(token=bot_token)
                thread = Thread(target=self.run_async_send, args=(bot, valid_chat_ids, message, image_path, bot_token))
                thread.start()

    def run_async_send(self, bot, chat_ids, message, image_path, bot_token):
        print(f"Sending messages for bot: {bot_token}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.send_telegram_messages(bot, chat_ids, message, image_path, bot_token))
        loop.close()

    async def send_telegram_messages(self, bot, chat_ids, message, image_path, bot_token):
        print(f"Sending to {len(chat_ids)} chat IDs...")
        tasks = [self.send_single_message(bot, chat_id, message, image_path) for chat_id in chat_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        success_count = sum(1 for r in results if r is True)
        failed_count = sum(1 for r in results if isinstance(r, Exception))

        # Safely update the UI from the main thread using QTimer
        QTimer.singleShot(0, lambda: self.show_result_message(bot_token, success_count, failed_count))

    async def send_single_message(self, bot, chat_id, message, image_path):
        try:
            await bot.send_message(chat_id=chat_id, text=message)
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as img_file:
                    await bot.send_photo(chat_id=chat_id, photo=img_file)
            return True
        except TelegramError as e:
            print(f"Failed to send to {chat_id}: {e}")
            return e

    def show_result_message(self, bot_token, success_count, failed_count):
        print(f"Results: {success_count} sent, {failed_count} failed")
        QMessageBox.information(
            self, "Result",
            f"Bot Token: {bot_token}\nMessage sent to {success_count} users.\nFailed: {failed_count}"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TelegramScheduler()
    window.show()
    sys.exit(app.exec_())
