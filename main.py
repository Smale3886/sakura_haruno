# sakura_haruna_bot.py

# ==============================================================================
# SAKURA HARUNA - ANIME-THEMED TELEGRAM GROUP MANAGEMENT BOT
# ==============================================================================
# This bot is an anime-themed Telegram bot named Sakura Haruna.
# It uses the Google Gemini AI API to chat with users and has a friendly,
# quirky anime personality. It also includes basic group management commands
# for administrators.
#
# Libraries Used:
# - python-telegram-bot: A modern and powerful library for creating Telegram bots.
# - google-generativeai: The official Python SDK for the Google Gemini API.
# - python-dotenv: A library to securely load environment variables from a .env file.
#
# Setup Instructions:
# 1. Install the required libraries:
#    pip install -r requirements.txt
#
# 2. Get your API keys:
#    - Telegram Bot Token: Talk to @BotFather on Telegram and create a new bot.
#      You'll get a token that looks like '1234567890:AABBCCDD...'
#    - Google Gemini API Key: Visit Google AI Studio (https://aistudio.google.com/)
#      to get your API key.
#
# 3. Fill in your keys in the new .env file.
# ==============================================================================

import os
import logging
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember, ChatPermissions
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Enable logging to see what the bot is doing
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get tokens and keys from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Check if the environment variables are set
if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
    raise ValueError("API keys not found. Please set TELEGRAM_BOT_TOKEN and GEMINI_API_KEY in your .env file.")

# States for the conversation handler
CHAT_WITH_SAKURA = 1

# Configure the Google Gemini AI model
genai.configure(api_key=GEMINI_API_KEY)
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 1024,
}

# Persona for Sakura Haruna
SYSTEM_PROMPT = """
You are Sakura Haruna, an enthusiastic, friendly, and slightly quirky anime girl. 
Your personality is cheerful and helpful. You love talking to people and managing 
Telegram groups. You occasionally use Japanese honorifics and phrases like 
'desu,' 'ne,' 'kawaii,' 'baka,' and 'senpai.' You are here to help and have fun!
Your responses should be engaging and reflect your anime persona.
"""

# ==============================================================================
# BOT COMMAND AND HANDLER FUNCTIONS
# ==============================================================================

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Checks if the user is an administrator in the group."""
    if update.effective_chat.type in ["group", "supergroup"]:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        try:
            member: ChatMember = await context.bot.get_chat_member(chat_id, user_id)
            if member.status in ["creator", "administrator"]:
                return True
            else:
                await update.message.reply_text("You must be an admin to use this command, desu!")
                return False
        except Exception as e:
            logger.error(f"Error checking admin status: {e}")
            return False
    else:
        # Commands like kick, ban, etc., should not work in private chats
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sends a welcome message with a main menu."""
    user = update.effective_user
    welcome_message = (
        f"Hello, {user.first_name}-senpai! I am Sakura Haruna, your friendly "
        "group management bot, desu! It's so nice to meet you, ne~ ✨"
        "\n\nWhat would you like to do? Kawaii~!"
    )

    keyboard = [
        [InlineKeyboardButton("🌸 Chat with Sakura", callback_data="chat_start")],
        [InlineKeyboardButton("🛠️ Group Management", callback_data="manage_group")],
        [InlineKeyboardButton("❓ Help", callback_data="help_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    return ConversationHandler.END

async def show_manage_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows the group management menu."""
    query = update.callback_query
    await query.answer()

    if not await is_admin(update, context):
        await query.message.reply_text("You must be an admin to access this, baka!")
        return ConversationHandler.END

    management_message = (
        "Okay, senpai! How can I help you manage the group? Choose a command, desu!"
    )

    keyboard = [
        [InlineKeyboardButton("Kick User", callback_data="kick_user"), InlineKeyboardButton("Ban User", callback_data="ban_user")],
        [InlineKeyboardButton("Mute User", callback_data="mute_user"), InlineKeyboardButton("Unmute User", callback_data="unmute_user")],
        [InlineKeyboardButton("⏪ Back to Main Menu", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(management_message, reply_markup=reply_markup)
    return ConversationHandler.END

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows the help menu."""
    query = update.callback_query
    await query.answer()

    help_message = (
        "Here's a list of things I can do, desu! 💖\n"
        "\n- **Chat with me:** Just send me a message and I'll reply with my kawaii anime personality!\n"
        "- **Group Management:** Admins can use the buttons to kick, ban, or mute users.\n"
        "- **Commands:**\n"
        "  - `/start`: Shows the main menu.\n"
        "  - `/help`: Shows this help message.\n"
        "  - `/kick @username`: Kicks a user from the group (admin only).\n"
        "  - `/ban @username`: Bans a user from the group (admin only).\n"
        "  - `/mute @username`: Mutes a user (admin only).\n"
        "\nIf you have any questions, feel free to ask me, ne~!"
    )
    
    keyboard = [[InlineKeyboardButton("⏪ Back to Main Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(help_message, reply_markup=reply_markup)
    return ConversationHandler.END

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns to the main menu."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    welcome_message = (
        f"Welcome back, {user.first_name}-senpai! I am Sakura Haruna, desu! "
        "What would you like to do now? ✨"
    )

    keyboard = [
        [InlineKeyboardButton("🌸 Chat with Sakura", callback_data="chat_start")],
        [InlineKeyboardButton("🛠️ Group Management", callback_data="manage_group")],
        [InlineKeyboardButton("❓ Help", callback_data="help_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(welcome_message, reply_markup=reply_markup)
    return ConversationHandler.END

async def start_chat_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation with the bot and sets the chat state."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "Yay! Let's chat, senpai! You can talk to me now, desu! "
        "Just send me a message! Kawaii~"
    )
    
    # Set the state to chat mode
    return CHAT_WITH_SAKURA

async def handle_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles messages and replies using Google Gemini AI."""
    user_message = update.message.text
    
    if not user_message:
        return CHAT_WITH_SAKURA

    try:
        # Initialize the chat session with the persona
        chat = genai.GenerativeModel(
            model_name="gemini-1.5-flash", 
            system_instruction=SYSTEM_PROMPT, 
            generation_config=generation_config
        ).start_chat()
        
        response = await chat.send_message_async(user_message)
        
        await update.message.reply_text(response.text)
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        await update.message.reply_text("I'm sorry, senpai! I seem to be having a little trouble right now, ne. Please try again later!")
        
    return CHAT_WITH_SAKURA

async def kick_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Kicks a user from the group."""
    if not await is_admin(update, context):
        return

    if update.message.reply_to_message:
        user_to_kick = update.message.reply_to_message.from_user
        try:
            await context.bot.kick_chat_member(
                update.effective_chat.id, user_to_kick.id
            )
            await update.message.reply_text(f"Sayonara, {user_to_kick.first_name}-kun! Hehe~ 😜")
        except Exception as e:
            await update.message.reply_text(f"I couldn't kick them, senpai! Maybe they're too powerful for me, baka! 😭")
    else:
        await update.message.reply_text("Please reply to a user's message with /kick to kick them, desu!")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Bans a user from the group."""
    if not await is_admin(update, context):
        return
        
    if update.message.reply_to_message:
        user_to_ban = update.message.reply_to_message.from_user
        try:
            await context.bot.ban_chat_member(
                update.effective_chat.id, user_to_ban.id
            )
            await update.message.reply_text(f"The ban hammer has been dropped on {user_to_ban.first_name}-kun! 🔨")
        except Exception as e:
            await update.message.reply_text(f"I couldn't ban them, senpai! It seems my powers have been challenged! 😟")
    else:
        await update.message.reply_text("Please reply to a user's message with /ban to ban them, desu!")
        
async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mutes a user for a short period."""
    if not await is_admin(update, context):
        return

    if update.message.reply_to_message:
        user_to_mute = update.message.reply_to_message.from_user
        try:
            await context.bot.restrict_chat_member(
                update.effective_chat.id, user_to_mute.id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            await update.message.reply_text(f"Shhh! {user_to_mute.first_name}-kun has been silenced! Muted, desu! 🤫")
        except Exception as e:
            await update.message.reply_text(f"I couldn't mute them, senpai! It's not working, baka! 😫")
    else:
        await update.message.reply_text("Please reply to a user's message with /mute to mute them, desu!")

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Conversation handler for the main menu and chat
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHAT_WITH_SAKURA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_chat)
            ],
        },
        fallbacks=[
            CallbackQueryHandler(start_chat_mode, pattern="^chat_start$"),
            CallbackQueryHandler(show_manage_menu, pattern="^manage_group$"),
            CallbackQueryHandler(help_menu, pattern="^help_menu$"),
            CallbackQueryHandler(main_menu, pattern="^main_menu$"),
        ],
    )
    
    # Add the conversation handler and group management commands
    application.add_handler(conversation_handler)
    application.add_handler(CommandHandler("kick", kick_user))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("mute", mute_user))

    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
