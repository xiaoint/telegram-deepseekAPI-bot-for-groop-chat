import re
import random
from datetime import datetime
from typing import Dict, Any, Optional, List

def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """Format timestamp to ISO format with timezone."""
    if timestamp is None:
        timestamp = datetime.utcnow()
    return timestamp.strftime("%Y-%m-%dT%H:%M:%S+00:00")

def extract_username(user) -> str:
    """Extract username from Telegram user object."""
    if user.username:
        return user.username
    elif user.first_name:
        return user.first_name
    else:
        return f"user_{user.id}"

def is_bot_mentioned(text: str) -> bool:
    """Check if bot is mentioned in the message."""
    if not text:
        return False
    
    text_lower = text.lower()
    triggers = ['raiden', 'ei', '@raiden', '@ei']
    
    for trigger in triggers:
        if trigger in text_lower:
            return True
    
    return False

def extract_target_from_reply(message) -> Optional[str]:
    """Extract target username from reply."""
    if message.reply_to_message and message.reply_to_message.from_user:
        return extract_username(message.reply_to_message.from_user)
    return None

def should_spontaneous_reply() -> bool:
    """2% chance for spontaneous reply."""
    return random.random() < 0.02

def find_message_by_id(messages: List[Dict[str, Any]], message_id: int) -> Optional[Dict[str, Any]]:
    """Find a message in the history by its ID."""
    for msg in messages:
        if msg.get('message_id') == message_id:
            return msg
    return None

def format_reply_context(original_message: Dict[str, Any]) -> str:
    """Format the original message for context."""
    if original_message:
        return (f"[User is replying to a message from {original_message['username']} "
                f"that said: \"{original_message['message']}\"]")
    return ""

def clean_message_for_api(messages: list) -> str:
    """Convert message history to a readable format for the API."""
    context_lines = []
    for msg in messages:
        line = f"[{msg['timestamp']}] {msg['username']}"
        if msg['target']:
            line += f" → {msg['target']}"
        line += f": {msg['message']}"
        context_lines.append(line)
    
    return "\n".join(context_lines)

def validate_mode(mode: str) -> bool:
    """Validate if the provided mode is supported."""
    return mode.lower() in ["chat", "assistant"]

def get_mode_description(mode: str) -> str:
    """Get a description of what a mode does."""
    descriptions = {
        "chat": (
            "**Chat Mode**: Raiden Ei personality\n"
            "• 30 message memory\n"
            "• Spontaneous replies (2% chance)\n"
            "• Goddess-like personality\n"
            "• Short, impactful responses (1-3 sentences)"
        ),
        "assistant": (
            "**Assistant Mode**: Helpful AI assistant\n"
            "• 10 message memory\n"
            "• Direct responses only\n"
            "• Professional, helpful tone\n"
            "• Detailed responses (up to 1300 tokens)"
        )
    }
    return descriptions.get(mode.lower(), "Unknown mode")

def format_mode_switch_message(old_mode: str, new_mode: str) -> str:
    """Format a message for mode switching."""
    if new_mode == "chat":
        return (
            f"Switched from {old_mode.title()} Mode to **Chat Mode**.\n\n"
            "I'm back to being Raiden Ei. The conversation just got more interesting."
        )
    else:
        return (
            f"Switched from {old_mode.title()} Mode to **Assistant Mode**.\n\n"
            "I'm now your helpful assistant. How can I help you today?"
        )

def should_respond_in_mode(mode: str, is_mentioned: bool, is_reply: bool, spontaneous_chance: bool = False) -> bool:
    """Determine if bot should respond based on mode and triggers."""
    if mode == "chat":
        # Chat mode: respond to mentions, replies, and sometimes spontaneously
        return is_mentioned or is_reply or (spontaneous_chance and should_spontaneous_reply())
    else:  # assistant mode
        # Assistant mode: only respond to direct engagement
        return is_mentioned or is_reply