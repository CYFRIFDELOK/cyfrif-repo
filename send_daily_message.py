import schedule
import time
import asyncio
from telegram import Bot
from telegram.error import TelegramError

# List of bot tokens
TOKEN_LIST = [
    '7742670843:AAFywfGGhJU247I4czKr64s9s61a_PbZ9xI',  # Bot 1 token
    '8026415050:AAGqcTPCBxXWFTyQ6FvoypbmIwDeEZIVIrc',  # Bot 2 token
]

# List of user IDs you want to send the message to
user_ids = [7571595447, 1024322210]  # Replace with actual Telegram user IDs

# Message you want to send
message = "this is cyfrif ."

# Correct image path (Windows style path)
image_path = r'C:\py\F.jpg.png'  # Path to your image file

# Function to send the message and image using different bots
async def send_daily_message():
    for token in TOKEN_LIST:
        bot = Bot(token=token)
        for user_id in user_ids:
            try:
                # Attempt to send the message asynchronously using await
                await bot.send_message(chat_id=user_id, text=message)
                # Send the image
                with open(image_path, 'rb') as photo_file:
                    await bot.send_photo(chat_id=user_id, photo=photo_file)
                print(f"Message and image sent to {user_id} using bot {token}")
            except TelegramError as e:
                # Handle Telegram errors
                if "chat not found" in str(e):  # Check if the error is about the chat not being found
                    print(f"User {user_id} has not started the bot or is blocking it.")
                else:
                    print(f"Failed to send message to {user_id} using bot {token}: {e}")

# Schedule the message to be sent at 19:39 PM every day
def schedule_messages():
    schedule.every().day.at("10:00").do(run_async_task)
    print("Scheduled message at 10:00 AM every day.")

# Function to run the asynchronous task (this will be called by the scheduler)
def run_async_task():
    try:
        asyncio.run(send_daily_message())
    except Exception as e:
        print(f"Error in running the async task: {e}")

# Keep the script running
def run_schedule():
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)  # Sleep for 1 second to keep checking the schedule
        except KeyboardInterrupt:
            print("Program interrupted. Exiting...")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

if __name__ == "__main__":
    schedule_messages()
    run_schedule()









