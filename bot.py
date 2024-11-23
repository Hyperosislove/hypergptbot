import os
import openai
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Fetch sensitive info from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set the OpenAI API key
openai.api_key = OPENAI_API_KEY

# Initialize Telegram bot client with time synchronization enabled
bot = Client("chatgpt_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, sync_time=True)

# Store user conversations in memory (or use a database for production)
user_conversations = {}

# Function to get GPT-3/4 response and maintain conversation context
async def get_gpt_response(user_id, query):
    # Check if user has a conversation history
    conversation_history = user_conversations.get(user_id, [])
    
    # Append user's query to the conversation history
    conversation_history.append({"role": "user", "content": query})
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # You can use "gpt-3.5-turbo" for lower cost
            messages=conversation_history,
            max_tokens=150,
            temperature=0.7  # Adjust for randomness (0-1 range)
        )

        # Get the assistant's response and append it to the conversation history
        assistant_reply = response.choices[0].message["content"].strip()
        conversation_history.append({"role": "assistant", "content": assistant_reply})

        # Save the conversation history back
        user_conversations[user_id] = conversation_history

        return assistant_reply
    except Exception as e:
        logging.error(f"Error while getting response from OpenAI: {e}")
        return "Sorry, something went wrong. Please try again later."

# Function to create inline keyboard with buttons
def create_keyboard():
    buttons = [
        [InlineKeyboardButton("Ask Another Question", callback_data="ask_question")],
        [InlineKeyboardButton("Menu", callback_data="menu")]
    ]
    return InlineKeyboardMarkup(buttons)

@bot.on_message(filters.command("start"))
async def start(client, message: Message):
    text = (
        "🌟 **ChatGPT Bot** 🌟\n\n"
        "Hello! I am your AI-powered assistant. Ask me anything and I will do my best to help you! 😄\n\n"
        "Just type your message and I will respond. You can also click the button below to ask another question or return to the menu.\n\n"
        "👇👇👇👇👇👇👇👇👇👇"
    )
    await message.reply(text, reply_markup=create_keyboard())

@bot.on_message(filters.text & ~filters.command("start"))
async def chat(client, message: Message):
    user_message = message.text
    user_id = message.from_user.id

    # Get GPT response for the user query
    gpt_response = await get_gpt_response(user_id, user_message)

    # Send the response back to the user
    await message.reply(gpt_response, reply_markup=create_keyboard())

@bot.on_callback_query(filters.regex("ask_question"))
async def ask_question(client, callback_query):
    await callback_query.message.edit(
        text="You can now ask a new question. Type it below and I will respond!",
        reply_markup=create_keyboard()
    )

@bot.on_callback_query(filters.regex("menu"))
async def menu(client, callback_query):
    await callback_query.message.edit(
        text="Welcome to the menu! Choose an option below.",
        reply_markup=create_keyboard()
    )

@bot.on_message(filters.command("clear"))
async def clear_conversation(client, message: Message):
    user_id = message.from_user.id
    if user_id in user_conversations:
        del user_conversations[user_id]
        await message.reply("Your conversation history has been cleared!")
    else:
        await message.reply("You don't have any conversation history yet.")

if __name__ == "__main__":
    bot.run()
