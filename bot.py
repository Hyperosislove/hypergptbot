import os
import logging
import requests
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Configure logging for debugging and monitoring
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Securely fetch API keys from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Store in a .env file or server config
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Store securely
GEMINI_API_URL = "https://api.gemini.google/v1/chat"  # Update with correct endpoint

# Function to query Gemini API
async def chat_with_gemini(prompt: str) -> str:
    try:
        headers = {
            "Authorization": f"Bearer {GEMINI_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "gemini-large",  # Specify model version (e.g., gemini-small, gemini-medium)
            "messages": [{"role": "user", "content": prompt}],
        }
        response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to Gemini API: {e}")
        return "Sorry, I couldn't connect to the Gemini AI right now. Please try again later."
    except KeyError:
        logger.error("Unexpected response format from Gemini API.")
        return "Sorry, I couldn't understand the response from the AI. Please try again."

# /start command to welcome users
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("User started the bot.")
    await update.message.reply_text(
        "Welcome to the Gemini AI Bot! Send me any message, and I'll reply using Gemini AI."
    )

# Message handler for user messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"Received message from user: {user_message}")
    
    # Send user message to Gemini and get response
    ai_response = await chat_with_gemini(user_message)
    await update.message.reply_text(ai_response)

# /help command for assistance
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "I am a bot powered by Gemini AI. You can ask me any question or have a conversation with me!"
    )

# Error handler for unexpected exceptions
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception while handling an update: {context.error}")
    if update.effective_message:
        await update.effective_message.reply_text(
            "An unexpected error occurred. Please try again later."
        )

# Main function to initialize the bot
def main():
    try:
        if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
            raise ValueError("API keys are missing. Set them in environment variables.")

        # Build the bot application
        app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

        # Add command and message handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # Add error handler
        app.add_error_handler(error_handler)

        logger.info("Bot is running...")
        app.run_polling()

    except Exception as e:
        logger.critical(f"Failed to start the bot: {e}")

if __name__ == "__main__":
    main()
