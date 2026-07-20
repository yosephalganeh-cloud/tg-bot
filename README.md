# tg-bot 🚀

A high-speed, multi-threaded Telegram message sender CLI tool built for fast broadcasting using multiple Telegram Bot Tokens.

Developed by **[yoseph alganeh](https://github.com/yosephalganeh-cloud)**

---

## 🌟 Features

- **⚡ Multi-Threaded Execution:** Sends large numbers of messages in parallel at maximum speed.
- **🔄 Automatic Token Rotation:** Cycles through registered Telegram bot tokens seamlessly.
- **💾 Persistent Token Storage:** Automatically saves added bot tokens to `bot.txt` so you never lose them.
- **🎨 Stylish CLI Interface:** Clean, colorful, and intuitive terminal UI with smooth execution logging.
- **🛡️ Error Handling:** Graceful handling of user interrupts (`Ctrl+C`) and network timeouts without traceback errors.

---

## 📦 Requirements

- **Python 3.x**
- **Zero Third-Party Dependencies:** Built purely with Python standard libraries (`urllib`, `concurrent.futures`, `json`, `os`, `sys`).

---

## 🚀 Installation & Usage

### 1. Clone the Repository
```bash
git clone https://github.com/yosephalganeh-cloud/tg-bot.git
cd tg-bot
```

### 2. Run the Tool
```bash
python tg-bot.py
```

---

## 🛠️ How to Use

1. **Option 1: Add Bot**
   - Select how many Telegram bots you wish to add.
   - Paste your Bot Token(s) obtained from [@BotFather](https://t.me/BotFather).
   - Tokens will automatically be saved into `bot.txt`.

2. **Option 2: Start Bot**
   - Enter the target **Chat ID** or **Username** (e.g., `@username` or `123456789`).
   - Enter your text message.
   - Specify how many times you want to send it.
   - Sit back and watch the multi-threaded fast dispatch!

---

## 📁 File Structure

```text
tg-bot/
├── tg-bot.py     # Main Python CLI script
├── bot.txt       # Auto-saved list of Telegram Bot Tokens
├── LICENSE       # Project License
└── README.md     # Documentation
```

---

## ⚠️ Disclaimer

This tool is created strictly for educational, testing, and authorized message broadcasting purposes. Please use it responsibly and adhere to Telegram's Terms of Service.

---

### 👨‍💻 Developer
Created with ❤️ by **yoseph alganeh**
