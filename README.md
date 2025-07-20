# telegram-deepseekAPI-bot-for-groop-chat
A sophisticated Telegram bot optimized for group chat with dual personalities powered by DeepSeek AI API, featuring advanced memory management, whitelist security, and adaptive behavior modes.

## 🌟 Features

### Dual Mode System
- **Chat Mode**: Raiden Ei personality - goddess-like, witty, mysterious
- **Assistant Mode**: Helpful AI assistant - professional, detailed, supportive

### Advanced Capabilities
- **Smart Memory Management**: Persistent conversation history with mode-specific limits
- **Whitelist Security**: Personal/group access control
- **Spontaneous Interactions**: AI decides when to join conversations naturally
- **Adaptive Token Limits**: Different response lengths per mode

## 🚀 What This Bot Can Do

### Core Functionality
1. **Dual Personality System**
   - Switch between Raiden Ei (goddess) and helpful assistant personalities
   - Mode-specific memory limits and behavior patterns

2. **Intelligent Conversation Management**
   - Remembers up to 30 messages (Chat Mode) or 10 messages (Assistant Mode)
   - Tracks reply threads and conversation context
   - Understands who replied to whom

3. **Smart Response Triggers**
   - Responds when mentioned (`@raiden`, `raiden`, `ei`)
   - Replies to users who respond to the bot
   - 2% chance of spontaneous replies in Chat Mode (goddess behavior)

4. **Security & Access Control**
   - Whitelist mode for personal/private use
   - User ID and Chat ID filtering
   - Silent blocking of unauthorized users

## 🎭 Bot Personalities

### Chat Mode - Raiden Ei (The Electro Archon)
```
Personality: Powerful goddess, witty, mysterious, commanding presence
Response Style: 1-3 sentences, impactful, no emojis/asterisks
Memory: 30 messages
Spontaneous Replies: 2% chance
Max Tokens: 500
Behavior: Divine being who chooses when to engage mortals
```

### Assistant Mode - Helpful AI Assistant
```
Personality: Professional, friendly, informative
Response Style: Detailed, helpful, clear explanations
Memory: 10 messages  
Spontaneous Replies: None (direct engagement only)
Max Tokens: 1300
Behavior: Focused on solving problems and providing information
```

## 📋 Commands

| Command | Description | Usage |
|---------|-------------|--------|
| `/start` | Initialize bot and show current mode | `/start` |
| `/mode` | Show/change bot mode | `/mode` or `/mode chat` or `/mode assistant` |
| `/info` | Get user/chat IDs for whitelist setup | `/info` |

### Command Examples

**Check Current Mode:**
```
/mode
```
*Shows: Current mode and available options*

**Switch to Chat Mode:**
```
/mode chat
```
*Activates Raiden Ei personality*

**Switch to Assistant Mode:**
```
/mode assistant  
```
*Activates helpful assistant mode*

**Get Whitelist Information:**
```
/info
```
*Returns your user ID, chat ID, and whitelist status*

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8+
- Telegram Bot Token
- DeepSeek API Key

### Installation Steps

1. **Clone the repository:**
```bash
git clone https://github.com/xiaoint/telegram-deepseekAPI-bot-for-groop-chat.git
cd telegram-deepseekAPI-bot-for-groop-chat
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Setup environment variables:**
```bash
# Edit .env with your tokens and configuration
```

4. **Run the bot:**
```bash
python bot.py
```

## ⚙️ Configuration

### Environment Variables (.env file)

#### Required Variables
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

#### Whitelist Configuration
```env
# Enable/disable whitelist (true/false)
WHITELIST_ENABLED=true

# Whitelisted users (comma-separated)
# Supports: user IDs, usernames, @usernames
WHITELIST_USERS=123456789,@username,friend_id

# Whitelisted chats (comma-separated)
# Private chats: positive numbers, Groups: negative numbers
WHITELIST_CHATS=123456789,-1001234567890
```

### Configuration Examples

#### Personal Use Only
```env
WHITELIST_ENABLED=true
WHITELIST_USERS=123456789,@your_friend
WHITELIST_CHATS=123456789,-1001234567890
```

#### Public Bot
```env
WHITELIST_ENABLED=false
WHITELIST_USERS=
WHITELIST_CHATS=
```

## 🎨 Customizing System Prompts

The bot's personality is defined by system prompts in `bot.py`. Here's how to modify them:

### Chat Mode System Prompt
Located in `bot.py` as `CHAT_SYSTEM_PROMPT`:

```python
CHAT_SYSTEM_PROMPT = (
    "You are Raiden Ei — the Electro Archon, a powerful and intelligent goddess..."
    # Modify this section to change Chat Mode personality
)
```

### Assistant Mode System Prompt  
Located in `bot.py` as `ASSISTANT_SYSTEM_PROMPT`:

```python
ASSISTANT_SYSTEM_PROMPT = (
    "You are a helpful AI assistant named Raiden..."
    # Modify this section to change Assistant Mode personality
)
```

### Key Customization Areas

1. **Personality Description**: Opening lines defining character
2. **Tone & Style**: Response format and communication style  
3. **Memory Structure**: How the bot processes conversation history
4. **Behavior**: Response triggers and interaction patterns

### Example Custom Personality
```python
CUSTOM_SYSTEM_PROMPT = (
    "You are a friendly robot companion with a love for science and jokes. "
    "You speak enthusiastically about technology and always try to make people smile. "
    "Keep responses to 1-2 sentences and include science facts when relevant."
)
```

## 🔒 Whitelist System

### How It Works
1. **Disabled**: Bot responds to anyone (public mode)
2. **Enabled**: Bot checks both user AND chat whitelists
3. **Access Denied**: Bot silently ignores unauthorized messages

### Getting IDs for Whitelist
Use `/info` command to get required IDs:
- **User ID**: Your unique Telegram ID
- **Chat ID**: Unique ID for the current chat/group

### User ID Formats Supported
- User IDs: `123456789`
- Usernames: `username` or `@username`  
- Mixed: `123456789,@friend,another_id`

## 📁 File Structure

```
telegram-deepseekAPI-bot-for-groop-chat/
├── bot.py                 # Main bot logic and handlers
├── deepseek_client.py     # DeepSeek API integration
├── memory_manager.py      # Conversation memory management
├── utils.py              # Utility functions
├── requirements.txt      # Python dependencies
└── memory/              # Conversation history storage
    └── [group_id].json  # Per-group memory files
```

## 🧠 How Memory Works

### Memory Storage
- Each chat group has its own memory file (`memory/[group_id].json`)
- Messages stored with metadata: username, target, timestamp, message ID
- Reply tracking for conversation context

### Memory Limits by Mode
- **Chat Mode**: 30 messages maximum
- **Assistant Mode**: 10 messages maximum
- **Auto-cleanup**: Older messages automatically removed

### Memory Data Structure
```json
{
  "username": "john_doe",
  "target": "alice",
  "message": "Hello there!",
  "message_id": 12345,
  "timestamp": "2025-07-20T15:30:00+00:00",
  "reply_to_message_id": 12344
}
```

## 🔧 API Configuration

### DeepSeek API Settings

The bot uses different parameters for each mode:

#### Chat Mode (Raiden Ei)
```python
temperature = 1.3          # More creative/unpredictable
top_p = 0.95              # Higher randomness
frequency_penalty = 0.3    # Reduce repetition
presence_penalty = 0.3     # Encourage topic diversity
max_tokens = 500          # Shorter responses
```

#### Assistant Mode
```python
temperature = 0.7         # More controlled
top_p = 0.9              # Moderate randomness
frequency_penalty = 0.1   # Less repetition penalty
presence_penalty = 0.1    # Less topic forcing
max_tokens = 1300        # Longer responses
```

## 🚨 Error Handling

### Built-in Error Handling
- API timeout protection (30 seconds)
- File I/O error handling
- JSON parsing error recovery
- Network connection failures
- Memory corruption protection

### Logging
- API errors logged to console
- Memory operation errors tracked
- Whitelist violations silently handled

## 📈 Performance Features

### Async Operations
- Non-blocking file operations
- Concurrent memory management
- Async lock system for thread safety

### Resource Management
- Token limit optimization per mode
- Memory auto-cleanup
- File-based persistent storage

## 🔄 Mode Switching

### Automatic Behavior Changes
When switching modes:
1. **Memory cleared** (prevents personality conflicts)
2. **System prompt changed** (new personality)
3. **Token limits adjusted** (response length)
4. **Behavior patterns updated** (spontaneous replies)

### Use Cases
- **Chat Mode**: Casual conversations, entertainment, roleplay
- **Assistant Mode**: Questions, research, problem-solving, tasks

## 🛠️ Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check whitelist settings
   - Verify API keys
   - Check `/info` for access status

2. **Memory issues**
   - Memory files in `./memory/` directory
   - Check file permissions
   - Memory auto-clears on mode switch

3. **API errors**
   - Verify DeepSeek API key
   - Check network connection
   - Review API quotas

### Debug Commands
- `/info` - Check access and IDs
- `/mode` - Verify current mode
- Check console output for error logs

## 📋 Dependencies

```
python-telegram-bot==21.3   # Telegram API wrapper
python-dotenv==1.0.1        # Environment variable loading
requests==2.32.3            # HTTP requests for DeepSeek API
aiofiles==24.1.0           # Async file operations
```

## 🚀 Deployment Options

### Local Development
```bash
python bot.py
```

### Production Deployment
- Docker containerization
- Systemd service
- Cloud hosting (AWS, Google Cloud, etc.)
- Process managers (PM2, supervisord)

## 📄 License & Credits

- Built with python-telegram-bot
- Powered by DeepSeek AI
- personality 1 inspired by Raiden Ei from anime game

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add your improvements
4. Submit pull request

## 📞 Support

For issues and questions:
- Open GitHub issues
- Check troubleshooting section
- Review configuration examples

---

**Ready to deploy your Enhanced telegram Bot!** ⚡🤖
