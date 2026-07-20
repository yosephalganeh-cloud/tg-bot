import os
import sys
import time
import json
import urllib.request
import urllib.parse
import concurrent.futures

# Tool Information
TOOL_NAME = "tg-bot"
DEVELOPER = "yoseph alganeh"
BOT_FILE = "bot.txt"

# Storage for registered bot tokens
registered_bots = []

# ANSI Colors for Terminal Styling
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def clear_screen():
    """Clear terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def load_bots():
    """Load bots from bot.txt file into memory."""
    bots = []
    if os.path.exists(BOT_FILE):
        with open(BOT_FILE, 'r') as f:
            for line in f:
                token = line.strip()
                if token and token not in bots:
                    bots.append(token)
    return bots

def save_bot(token):
    """Save a new bot token to bot.txt file."""
    with open(BOT_FILE, 'a') as f:
        f.write(token + '\n')

def display_banner():
    """Display styled tool banner."""
    print(f"{Colors.CYAN}=" * 60)
    print(f"   {Colors.BOLD}TOOL NAME{Colors.ENDC} : {Colors.GREEN}{TOOL_NAME.upper()}{Colors.ENDC}")
    print(f"   {Colors.BOLD}DEVELOPER{Colors.ENDC} : {Colors.WARNING}{DEVELOPER}{Colors.ENDC}")
    print(f"{Colors.CYAN}=" * 60 + f"{Colors.ENDC}\n")

def add_bot():
    """Option 1: Add Bot Tokens and save to file."""
    clear_screen()
    display_banner()
    print(f"{Colors.BOLD}[+] ADD BOT CONFIGURATION{Colors.ENDC}\n")
    
    try:
        bot_count_str = input(f"{Colors.BLUE}Enter the number of bots to add: {Colors.ENDC}").strip()
        if not bot_count_str.isdigit() or int(bot_count_str) <= 0:
            print(f"{Colors.FAIL}[!] Please enter a valid number greater than 0.{Colors.ENDC}")
            time.sleep(1.5)
            return
        
        bot_count = int(bot_count_str)

        for i in range(1, bot_count + 1):
            token = input(f"{Colors.BLUE}Enter Bot Token #{i}: {Colors.ENDC}").strip()
            if token:
                if token not in registered_bots:
                    registered_bots.append(token)
                    save_bot(token)
                    print(f"{Colors.GREEN}[✓] Bot Token #{i} successfully saved to {BOT_FILE}!{Colors.ENDC}")
                else:
                    print(f"{Colors.WARNING}[!] Bot Token #{i} is already registered.{Colors.ENDC}")
            else:
                print(f"{Colors.WARNING}[!] Token cannot be empty. Skipped.{Colors.ENDC}")
        
        print(f"\n{Colors.GREEN}[✓] Total active bots ready to use: {len(registered_bots)}{Colors.ENDC}")
        
    except Exception as e:
        print(f"{Colors.FAIL}[!] An error occurred: {e}{Colors.ENDC}")
    
    input(f"\n{Colors.CYAN}Press Enter to return to Main Menu...{Colors.ENDC}")

def send_telegram_message(token, chat_id, text):
    """Send message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = urllib.parse.urlencode({
        'chat_id': chat_id,
        'text': text
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=payload)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('ok', False)
    except Exception:
        return False

def worker_task(msg_index, total_messages, chat_id, message):
    """Worker function for threading to send messages faster."""
    bot_index = (msg_index - 1) % len(registered_bots)
    current_token = registered_bots[bot_index]
    
    success = send_telegram_message(current_token, chat_id, message)
    
    if success:
        print(f"{Colors.GREEN}[✓] Message {msg_index}/{total_messages} sent successfully via Bot #{bot_index + 1}{Colors.ENDC}")
        return 1
    else:
        print(f"{Colors.FAIL}[X] Message {msg_index}/{total_messages} failed via Bot #{bot_index + 1}. Check API limits.{Colors.ENDC}")
        return 0

def start_bot():
    """Option 2: Start Fast Bot & Message Dispatcher."""
    clear_screen()
    display_banner()
    print(f"{Colors.BOLD}[+] FAST MESSAGE DISPATCHER{Colors.ENDC}\n")

    if not registered_bots:
        print(f"{Colors.FAIL}[!] No bots found! Please add a bot first (Option 1) or check {BOT_FILE}.{Colors.ENDC}")
        time.sleep(2)
        return

    print(f"{Colors.GREEN}[+] Loaded Bots: {len(registered_bots)}{Colors.ENDC}\n")
    
    chat_id = input(f"{Colors.BLUE}Enter Username or Chat ID (e.g., @username or 123456789): {Colors.ENDC}").strip()
    if not chat_id:
        print(f"{Colors.FAIL}[!] Chat ID cannot be empty.{Colors.ENDC}")
        time.sleep(1.5)
        return

    message = input(f"{Colors.BLUE}Enter the Message: {Colors.ENDC}").strip()
    if not message:
        print(f"{Colors.FAIL}[!] Message cannot be empty.{Colors.ENDC}")
        time.sleep(1.5)
        return
    
    try:
        num_messages_str = input(f"{Colors.BLUE}Enter the Number of Messages: {Colors.ENDC}").strip()
        num_messages = int(num_messages_str)
        if num_messages <= 0:
            num_messages = 1
    except ValueError:
        print(f"{Colors.WARNING}[!] Invalid number. Defaulting to 1 message.{Colors.ENDC}")
        num_messages = 1

    print(f"\n{Colors.CYAN}[*] Starting ultra-fast broadcast... Press Ctrl+C to stop.{Colors.ENDC}\n")
    
    successful_sends = 0
    
    try:
        # Using ThreadPoolExecutor for concurrent, fast sending
        max_threads = min(20, num_messages) # Max 20 simultaneous threads to avoid crashing
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [executor.submit(worker_task, i, num_messages, chat_id, message) for i in range(1, num_messages + 1)]
            
            for future in concurrent.futures.as_completed(futures):
                successful_sends += future.result()
                
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}[!] Process forcefully interrupted by user. Stopping safely...{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}[!] An unexpected error occurred: {e}{Colors.ENDC}")

    print(f"\n{Colors.BOLD}{Colors.GREEN}[✓] Broadcast Finished! Sent {successful_sends}/{num_messages} messages.{Colors.ENDC}")
    input(f"\n{Colors.CYAN}Press Enter to return to Main Menu...{Colors.ENDC}")

def main():
    """Main Menu Loop."""
    global registered_bots
    # Load bots from file at startup
    registered_bots = load_bots()
    
    while True:
        try:
            clear_screen()
            display_banner()
            print(f"{Colors.BOLD}=== MAIN MENU ==={Colors.ENDC}")
            print(f"{Colors.CYAN}[1]{Colors.ENDC} Add Bot")
            print(f"{Colors.CYAN}[2]{Colors.ENDC} Start Bot")
            print(f"{Colors.CYAN}[3]{Colors.ENDC} Exit")
            
            choice = input(f"\n{Colors.BLUE}Select an option (1-3): {Colors.ENDC}").strip()
            
            if choice == "1":
                add_bot()
            elif choice == "2":
                start_bot()
            elif choice == "3":
                print(f"\n{Colors.GREEN}Thank you for using {TOOL_NAME} by {DEVELOPER}! Goodbye.{Colors.ENDC}")
                sys.exit()
            else:
                print(f"{Colors.FAIL}[!] Invalid selection. Please choose 1, 2, or 3.{Colors.ENDC}")
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Exiting... Goodbye!{Colors.ENDC}")
            sys.exit()

if __name__ == "__main__":
    main()
