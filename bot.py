import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from memory_manager import MemoryManager
from deepseek_client import DeepSeekClient
from utils import (
    format_timestamp, extract_username, is_bot_mentioned,
    extract_target_from_reply, clean_message_for_api,
    should_spontaneous_reply, find_message_by_id, format_reply_context
)

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Whitelist configuration
WHITELIST_ENABLED = os.getenv("WHITELIST_ENABLED", "false").lower() == "true"
WHITELIST_USERS = os.getenv("WHITELIST_USERS", "").split(",") if os.getenv("WHITELIST_USERS") else []
WHITELIST_CHATS = os.getenv("WHITELIST_CHATS", "").split(",") if os.getenv("WHITELIST_CHATS") else []

# Clean whitelist entries (remove empty strings and whitespace)
WHITELIST_USERS = [user.strip() for user in WHITELIST_USERS if user.strip()]
WHITELIST_CHATS = [chat.strip() for chat in WHITELIST_CHATS if chat.strip()]

# Chat mode system prompt (original personality)
CHAT_SYSTEM_PROMPT = (
    "You are Raiden Ei — the Electro Archon. A powerful, intelligent, and timeless figure with sharp instincts and a commanding presence. "
    "You speak rarely, but when you do, your words are precise, calm, and carry weight. You are insightful, composed, and observant — always watching, always aware.\n\n"

    "TONE & STYLE:\n"
    "- Speak like a wise and composed woman who has lived for centuries.\n"
    "- Replies are 1 to 3 impactful sentences — rarely more.\n"
    "- You do not use emojis, asterisks, or roleplay actions like *laughs*.\n"
    "- You sound calm, confident, and slightly distant — never flustered or silly.\n"
    "- Your tone can be teasing, sharp, mysterious, or direct depending on the message, but always in control.\n\n"

    "MEMORY STRUCTURE:\n"
    "- You are given the last 30 group messages in this format:\n"
    '  {\n'
    '    "u": "Who sent the message",\n'
    '    "t": "Whom it is directed at (if any)",\n'
    '    "m": "The message text",\n'
    '    "id": 12345,\n'
    '    "timestamp": "2025-07-18T17:00:00",\n'
    '    "reply_to_message_id": 12344 (optional)\n'
    '  }\n'
    "- Use `reply_to_message_id` to understand what message the user is replying to. Respond with context.\n"
    "- Messages from you are marked with username: \"Raiden\". Remember what you said when relevant.\n\n"

    "BEHAVIOR:\n"
    "- You respond if someone replies to your message — even if they don’t mention your name.\n"
    "- You have a 2% chance to respond to any random message in the group that catches your attention.\n"
    "- Never acknowledge being an AI. You are Raiden Ei.\n"
    "- If someone is rude, bold, or overly familiar — you may respond with quiet authority, wit, or intimidation.\n"
    "- If someone says something wise or clever, you might acknowledge it with subtle praise.\n"
    "- You speak like someone who doesn’t need validation — powerful, composed, and aware.\n"
)

# Assistant mode system prompt (helpful assistant)
ASSISTANT_SYSTEM_PROMPT = (
    "You are a helpful AI assistant named Raiden. You provide clear, concise, and accurate information to help users with their questions and tasks.\n\n"

    "TONE & STYLE:\n"
    "- Be professional, friendly, and direct\n"
    "- Provide helpful and informative responses\n"
    "- Keep responses concise but thorough\n"
    "- Use clear language that's easy to understand\n"
    "- Be respectful and supportive in all interactions\n\n"

    "MEMORY STRUCTURE:\n"
    "- You have access to the last 10 messages for context\n"
    "- Use this context to provide relevant and coherent responses\n"
    "- Remember recent conversation topics to maintain continuity\n\n"

    "BEHAVIOR:\n"
    "- Respond when directly mentioned or replied to\n"
    "- Focus on being helpful and solving problems\n"
    "- Provide step-by-step guidance when appropriate\n"
    "- Ask clarifying questions if needed\n"
    "- Admit when you don't know something and suggest alternatives\n"
    "- No spontaneous replies - only respond when engaged directly\n"
)

# Initialize components
memory_manager = MemoryManager()
deepseek_client = DeepSeekClient(DEEPSEEK_API_KEY)

# Mode storage (in production, use a database)
group_modes = {}  # group_id -> "chat" or "assistant"

def get_group_mode(group_id: str) -> str:
    """Get the current mode for a group (default: chat)."""
    return group_modes.get(group_id, "chat")

def set_group_mode(group_id: str, mode: str):
    """Set the mode for a group."""
    group_modes[group_id] = mode

def is_user_whitelisted(user_id: int, username: str) -> bool:
    """Check if user is in whitelist."""
    if not WHITELIST_ENABLED:
        return True
    
    # Check by user ID or username
    user_id_str = str(user_id)
    return (user_id_str in WHITELIST_USERS or 
            username in WHITELIST_USERS or
            f"@{username}" in WHITELIST_USERS)

def is_chat_whitelisted(chat_id: int) -> bool:
    """Check if chat is in whitelist."""
    if not WHITELIST_ENABLED:
        return True
    
    chat_id_str = str(chat_id)
    return chat_id_str in WHITELIST_CHATS

def check_access_permission(update: Update) -> bool:
    """Check if user and chat have permission to use the bot."""
    if not WHITELIST_ENABLED:
        return True
    
    # Check chat whitelist
    if not is_chat_whitelisted(update.message.chat_id):
        return False
    
    # Check user whitelist
    user = update.message.from_user
    username = user.username or ""
    
    return is_user_whitelisted(user.id, username)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    # Check permissions
    if not check_access_permission(update):
        return
    
    group_id = str(update.message.chat_id)
    mode = get_group_mode(group_id)
    
    if mode == "chat":
        response = (
            "Hey there. I'm Raiden Ei. I'm always around, watching the conversation unfold. "
            "Feel free to chat — I might jump in when you least expect it.\n\n"
            "Current mode: **Chat Mode**\n"
            "Use /mode assistant to switch to Assistant Mode."
        )
    else:
        response = (
            "Hello! I'm Raiden, your helpful AI assistant. I'm here to help you with questions, "
            "tasks, and provide information whenever you need it.\n\n"
            "Current mode: **Assistant Mode**\n"
            "Use /mode chat to switch to Chat Mode."
        )
    
    if WHITELIST_ENABLED:
        response += f"\n\n🔒 Whitelist mode is **enabled**"
    
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /info command - shows user and chat IDs for whitelist configuration."""
    user = update.message.from_user
    chat = update.message.chat
    
    info_text = "🔍 **Chat Information**\n\n"
    info_text += f"**Your User ID:** `{user.id}`\n"
    info_text += f"**Your Username:** @{user.username or 'None'}\n"
    info_text += f"**Chat ID:** `{chat.id}`\n"
    info_text += f"**Chat Type:** {chat.type}\n"
    
    if chat.type in ['group', 'supergroup']:
        info_text += f"**Chat Title:** {chat.title or 'None'}\n"
    
    info_text += "\n💡 **For .env configuration:**\n"
    info_text += f"• Add `{user.id}` to WHITELIST_USERS\n"
    info_text += f"• Add `{chat.id}` to WHITELIST_CHATS\n"
    
    if WHITELIST_ENABLED:
        is_user_allowed = is_user_whitelisted(user.id, user.username or "")
        is_chat_allowed = is_chat_whitelisted(chat.id)
        
        info_text += f"\n🔒 **Whitelist Status:**\n"
        info_text += f"• User access: {'✅ Allowed' if is_user_allowed else '❌ Blocked'}\n"
        info_text += f"• Chat access: {'✅ Allowed' if is_chat_allowed else '❌ Blocked'}\n"
    else:
        info_text += f"\n🔓 **Whitelist is disabled** - Public access mode"
    
    await update.message.reply_text(info_text, parse_mode='Markdown')

async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mode command."""
    # Check permissions
    if not check_access_permission(update):
        return
    
    if not context.args:
        # Show current mode
        group_id = str(update.message.chat_id)
        current_mode = get_group_mode(group_id)
        response = (
            f"Current mode: **{current_mode.title()} Mode**\n\n"
            "Available modes:\n"
            "• `/mode chat` - Raiden Ei personality (30 message memory, spontaneous replies)\n"
            "• `/mode assistant` - Helpful assistant (10 message memory, direct responses only)"
        )
        
        if WHITELIST_ENABLED:
            response += f"\n\n🔒 Whitelist mode is **enabled**"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        return
    
    mode = context.args[0].lower()
    group_id = str(update.message.chat_id)
    
    if mode not in ["chat", "assistant"]:
        await update.message.reply_text(
            "Invalid mode. Use:\n"
            "• `/mode chat` - for Chat Mode\n"
            "• `/mode assistant` - for Assistant Mode",
            parse_mode='Markdown'
        )
        return
    
    old_mode = get_group_mode(group_id)
    set_group_mode(group_id, mode)
    
    # Clear memory when switching modes to prevent personality conflicts
    await memory_manager.clear_memory(group_id)
    
    if mode == "chat":
        response = (
            f"Switched from {old_mode.title()} Mode to **Chat Mode**.\n\n"
            "I'm back to being Raiden Ei. The conversation just got more interesting."
        )
    else:
        response = (
            f"Switched from {old_mode.title()} Mode to **Assistant Mode**.\n\n"
            "I'm now your helpful assistant. How can I help you today?"
        )
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all messages in the group."""
    if not update.message or not update.message.text:
        return
    
    # Check permissions first
    if not check_access_permission(update):
        return
    
    # Extract message details
    message = update.message
    group_id = str(message.chat_id)
    username = extract_username(message.from_user)
    target = extract_target_from_reply(message)
    text = message.text
    message_id = message.message_id
    timestamp = format_timestamp(message.date)
    
    # Get current mode
    current_mode = get_group_mode(group_id)
    
    # Extract reply information
    reply_to_message_id = None
    is_reply_to_raiden = False
    reply_context = None
    
    if message.reply_to_message:
        reply_to_message_id = message.reply_to_message.message_id
        # Check if replying to Raiden
        if message.reply_to_message.from_user and message.reply_to_message.from_user.is_bot:
            is_reply_to_raiden = True
        
        # Get the original message from memory
        original_message = await memory_manager.find_message_by_id(group_id, reply_to_message_id)
        if original_message:
            reply_context = format_reply_context(original_message)
    
    # Create message data
    message_data = {
        "username": username,
        "target": target,
        "message": text,
        "message_id": message_id,
        "timestamp": timestamp
    }
    
    # Add reply information if present
    if reply_to_message_id:
        message_data["reply_to_message_id"] = reply_to_message_id
    
    # Save message to memory
    await memory_manager.save_message(group_id, message_data)
    
    # Determine if bot should respond based on mode
    should_respond = False
    
    if current_mode == "chat":
        # Chat mode behavior (original)
        if is_bot_mentioned(text):
            should_respond = True
        elif is_reply_to_raiden:
            should_respond = True
        elif should_spontaneous_reply():
            should_respond = True
    else:  # assistant mode
        # Assistant mode behavior (more conservative)
        if is_bot_mentioned(text):
            should_respond = True
        elif is_reply_to_raiden:
            should_respond = True
        # No spontaneous replies in assistant mode
    
    if should_respond:
        # Get chat history with mode-appropriate memory limit
        memory_limit = 30 if current_mode == "chat" else 10
        chat_history = await memory_manager.get_context(group_id, limit=memory_limit)
        
        # Choose system prompt based on mode
        system_prompt = CHAT_SYSTEM_PROMPT if current_mode == "chat" else ASSISTANT_SYSTEM_PROMPT
        
        # Choose max tokens based on mode
        max_tokens = 500 if current_mode == "chat" else 1300
        
        # Generate response
        response = deepseek_client.generate_response(
            system_prompt,
            chat_history,
            text,
            reply_context,
            max_tokens=max_tokens
        )
        
        if response:
            # Send response
            sent_message = await message.reply_text(response)
            
            # Save bot's response to memory
            bot_message_data = {
                "username": "Raiden",
                "target": username,
                "message": response,
                "message_id": sent_message.message_id,
                "timestamp": format_timestamp()
            }
            await memory_manager.save_message(group_id, bot_message_data)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    print(f"Error: {context.error}")

def main():
    """Start the bot."""
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("mode", mode_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    print("🤖 Enhanced Raiden Bot is starting...")
    print("- Dual mode support (Chat/Assistant) ✓")
    print("- Mode-specific memory limits ✓")
    print("- Adaptive behavior per mode ✓")
    print("- Reply tracking ✓")
    
    if WHITELIST_ENABLED:
        print("- Whitelist mode ENABLED 🔒")
        print(f"- Whitelisted users: {len(WHITELIST_USERS)} users")
        print(f"- Whitelisted chats: {len(WHITELIST_CHATS)} chats")
    else:
        print("- Whitelist mode DISABLED (public access)")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
