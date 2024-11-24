import os
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to generate AI response
async def chat_with_ai(prompt: str) -> str:
    try:
        # Using gpt-3.5-turbo instead of gpt-4
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Updated model
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {str(e)}"

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to the AI bot! Send me a message and I'll reply using AI.")

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    ai_response = await chat_with_ai(user_message)
    await update.message.reply_text(ai_response)

# Main function to run the bot
def main():
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
