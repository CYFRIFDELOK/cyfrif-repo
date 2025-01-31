import asyncio
from telegram import Bot
from telegram.error import TelegramError

# List of bot tokens
TOKEN_LIST = [
    '7742670843:AAFywfGGhJU247I4czKr64s9s61a_PbZ9xI',  # Bot 1 token
    '8026415050:AAGqcTPCBxXWFTyQ6FvoypbmIwDeEZIVIrc',  # Bot 2 token
    # Add more tokens here
]

# Create asynchronous function to get updates for each bot
async def get_chat_ids_for_bots():
    for token in TOKEN_LIST:
        bot = Bot(token=token)
        
        try:
            updates = await bot.get_updates()

            if not updates:
                print(f"No updates found for bot with token {token}")
                continue

            # Loop through each update and print user info
            for update in updates:
                if update.message:
                    chat_id = update.message.chat.id  # Chat ID
                    username = update.message.from_user.username  # Username
                    message_text = update.message.text if update.message.text else "No text"

                    print(f"Bot Token: {token}")
                    print(f"User ID: {chat_id}")
                    print(f"Username: {username}")
                    print(f"Message Text: {message_text}")
                else:
                    print("No message found in update.")
        except TelegramError as e:
            print(f"Error fetching updates for bot with token {token}: {e}")

# Run the asynchronous function using asyncio
asyncio.run(get_chat_ids_for_bots())



