import os
import sys
import time
import json
import signal
import urllib.request
import urllib.error
import urllib.parse
import concurrent.futures
import threading

# Tool Information
TOOL_NAME = "tg-bot"
DEVELOPER = "yoseph alganeh"
BOT_FILE = "bot.txt"
HISTORY_FILE = "sent_history.txt"

# Storage & Global Flags
registered_bots = []
stop_requested = False
file_lock = threading.Lock()

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

def handle_exit_signal(sig, frame):
    """Instant Ctrl+C Signal Handler."""
    global stop_requested
    stop_requested = True
    print(f"\n{Colors.WARNING}[!] Ctrl+C detected! Stopping immediately...{Colors.ENDC}")

# Register Signal Handler
signal.signal(signal.SIGINT, handle_exit_signal)

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

def log_sent_message(token, chat_id, message_id):
    """Save sent message details for future deletion."""
    with file_lock:
        with open(HISTORY_FILE, 'a') as f:
            f.write(f"{token},{chat_id},{message_id}\n")

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
    """Send message via Telegram Bot API with Rate Limit handling."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = urllib.parse.urlencode({'chat_id': chat_id, 'text': text}).encode('utf-8')
    req = urllib.request.Request(url, data=payload)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode('utf-8'))
            message_id = result.get('result', {}).get('message_id')
            return "SUCCESS", message_id
    except urllib.error.HTTPError as e:
        if e.code == 429:
            try:
                error_data = json.loads(e.read().decode('utf-8'))
                retry_after = error_data.get('parameters', {}).get('retry_after', 3)
                return "RATE_LIMIT", retry_after
            except:
                return "RATE_LIMIT", 3
        return "FAILED", None
    except Exception:
        return "FAILED", None

def worker_send_task(msg_index, total_messages, chat_id, message):
    """Worker function for sending messages."""
    global stop_requested
    if stop_requested:
        return 0

    bot_index = (msg_index - 1) % len(registered_bots)
    current_token = registered_bots[bot_index]
    
    while not stop_requested:
        status, result_data = send_telegram_message(current_token, chat_id, message)
        
        if status == "SUCCESS":
            log_sent_message(current_token, chat_id, result_data)
            print(f"{Colors.GREEN}[✓] Message {msg_index}/{total_messages} sent successfully via Bot #{bot_index + 1}{Colors.ENDC}")
            return 1
        elif status == "RATE_LIMIT":
            sleep_time = result_data
            print(f"{Colors.WARNING}[!] API Limit on Bot #{bot_index + 1}. Resting for {sleep_time}s...{Colors.ENDC}")
            time.sleep(sleep_time)
            continue
        else:
            print(f"{Colors.FAIL}[X] Message {msg_index}/{total_messages} failed via Bot #{bot_index + 1}.{Colors.ENDC}")
            return 0
            
    return 0

def start_bot():
    """Option 2: Start Fast Bot & Message Dispatcher."""
    global stop_requested
    stop_requested = False
    
    clear_screen()
    display_banner()
    print(f"{Colors.BOLD}[+] FAST MESSAGE DISPATCHER{Colors.ENDC}\n")

    if not registered_bots:
        print(f"{Colors.FAIL}[!] No bots found! Please add a bot first (Option 1).{Colors.ENDC}")
        time.sleep(2)
        return

    print(f"{Colors.GREEN}[+] Loaded Bots: {len(registered_bots)}{Colors.ENDC}\n")
    
    chat_id = input(f"{Colors.BLUE}Enter Username or Chat ID (e.g., @username or 123456789): {Colors.ENDC}").strip()
    if not chat_id:
        return

    message = input(f"{Colors.BLUE}Enter the Message: {Colors.ENDC}").strip()
    if not message:
        return
    
    try:
        num_messages = int(input(f"{Colors.BLUE}Enter the Number of Messages: {Colors.ENDC}").strip())
        if num_messages <= 0: num_messages = 1
    except ValueError:
        num_messages = 1

    print(f"\n{Colors.CYAN}[*] Starting ultra-fast broadcast... Press Ctrl+C to stop instantly.{Colors.ENDC}\n")
    
    successful_sends = 0
    max_threads = min(25, num_messages)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(worker_send_task, i, num_messages, chat_id, message) for i in range(1, num_messages + 1)]
        
        for future in concurrent.futures.as_completed(futures):
            if stop_requested:
                executor.shutdown(wait=False, cancel_futures=True)
                break
            try:
                successful_sends += future.result()
            except Exception:
                pass

    print(f"\n{Colors.BOLD}{Colors.GREEN}[✓] Broadcast Stopped/Finished! Sent {successful_sends}/{num_messages} messages.{Colors.ENDC}")
    input(f"\n{Colors.CYAN}Press Enter to return to Main Menu...{Colors.ENDC}")

def worker_delete_task(token, chat_id, msg_id):
    """Worker function for fast deletion."""
    global stop_requested
    if stop_requested:
        return False, msg_id

    url = f"https://api.telegram.org/bot{token}/deleteMessage"
    payload = urllib.parse.urlencode({'chat_id': chat_id, 'message_id': msg_id}).encode('utf-8')
    req = urllib.request.Request(url, data=payload)
    
    try:
        with urllib.request.urlopen(req, timeout=5):
            print(f"{Colors.GREEN}[✓] Successfully deleted message ID: {msg_id}{Colors.ENDC}")
            return True, msg_id
    except Exception:
        print(f"{Colors.FAIL}[X] Failed to delete message ID: {msg_id}{Colors.ENDC}")
        return False, msg_id

def delete_messages():
    """Option 3: Fast Multi-Threaded Delete Sent Messages."""
    global stop_requested
    stop_requested = False
    
    clear_screen()
    display_banner()
    print(f"{Colors.BOLD}[+] FAST DELETE SENT MESSAGES{Colors.ENDC}\n")

    if not os.path.exists(HISTORY_FILE):
        print(f"{Colors.WARNING}[!] No message history found.{Colors.ENDC}")
        time.sleep(2)
        return

    chat_id = input(f"{Colors.BLUE}Enter Chat ID to delete messages for: {Colors.ENDC}").strip()
    if not chat_id:
        return

    print(f"\n{Colors.CYAN}[*] Starting ultra-fast deletion... Press Ctrl+C to stop instantly.{Colors.ENDC}\n")
    
    with open(HISTORY_FILE, 'r') as f:
        lines = f.readlines()

    target_tasks = []
    remaining_lines = []

    for line in lines:
        line_data = line.strip().split(',')
        if len(line_data) == 3:
            token, saved_chat_id, msg_id = line_data
            if saved_chat_id == chat_id:
                target_tasks.append((token, chat_id, msg_id))
            else:
                remaining_lines.append(line)
        else:
            remaining_lines.append(line)

    deleted_count = 0
    if target_tasks:
        max_threads = min(25, len(target_tasks))
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [executor.submit(worker_delete_task, t, c, m) for t, c, m in target_tasks]
            
            for future in concurrent.futures.as_completed(futures):
                if stop_requested:
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                try:
                    success, msg_id = future.result()
                    if success:
                        deleted_count += 1
                except Exception:
                    pass

    # Update history file
    with open(HISTORY_FILE, 'w') as f:
        f.writelines(remaining_lines)

    print(f"\n{Colors.BOLD}{Colors.GREEN}[✓] Deletion Finished! Deleted {deleted_count} messages for {chat_id}.{Colors.ENDC}")
    input(f"\n{Colors.CYAN}Press Enter to return to Main Menu...{Colors.ENDC}")

def main():
    """Main Menu Loop."""
    global registered_bots, stop_requested
    registered_bots = load_bots()
    
    while True:
        stop_requested = False
        try:
            clear_screen()
            display_banner()
            print(f"{Colors.BOLD}=== MAIN MENU ==={Colors.ENDC}")
            print(f"{Colors.CYAN}[1]{Colors.ENDC} Add Bot")
            print(f"{Colors.CYAN}[2]{Colors.ENDC} Start Bot")
            print(f"{Colors.CYAN}[3]{Colors.ENDC} Delete Messages")
            print(f"{Colors.CYAN}[4]{Colors.ENDC} Exit")
            
            choice = input(f"\n{Colors.BLUE}Select an option (1-4): {Colors.ENDC}").strip()
            
            if choice == "1":
                add_bot()
            elif choice == "2":
                start_bot()
            elif choice == "3":
                delete_messages()
            elif choice == "4":
                print(f"\n{Colors.GREEN}Thank you for using {TOOL_NAME} by {DEVELOPER}! Goodbye.{Colors.ENDC}")
                sys.exit(0)
            else:
                print(f"{Colors.FAIL}[!] Invalid selection.{Colors.ENDC}")
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            print(f"\n{Colors.WARNING}Process terminated. Returning to Main Menu...{Colors.ENDC}")
            time.sleep(1)

if __name__ == "__main__":
    main()
