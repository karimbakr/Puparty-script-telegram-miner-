import httpx
import json
import time
import random
from rich import print
from colorama import Fore, init,Style
import subprocess
import sys
import importlib.util
import os
import pyfiglet
from rich.console import Console
from rich.progress import Spinner
init(autoreset=True)
console = Console()



def create_gradient_banner(text):
    banner = pyfiglet.figlet_format(text,font='slant').splitlines()
    colors = [Fore.GREEN + Style.BRIGHT, Fore.YELLOW + Style.BRIGHT, Fore.RED + Style.BRIGHT]
    total_lines = len(banner)
    section_size = total_lines // len(colors)
    for i, line in enumerate(banner):
        if i < section_size:
            print(colors[0] + line)  # Green
        elif i < section_size * 2:
            print(colors[1] + line)  # Yellow
        else:
            print(colors[2] + line)  # Red

def print_info_box(social_media_usernames):
    colors = [Fore.CYAN, Fore.MAGENTA, Fore.LIGHTYELLOW_EX, Fore.BLUE, Fore.LIGHTWHITE_EX]
    
    box_width = max(len(social) + len(username) for social, username in social_media_usernames) + 4
    print(Fore.WHITE + Style.BRIGHT + '+' + '-' * (box_width - 2) + '+')
    
    for i, (social, username) in enumerate(social_media_usernames):
        color = colors[i % len(colors)]  # Cycle through colors
        print(color + f'| {social}: {username} |')
    
    print(Fore.WHITE + Style.BRIGHT + '+' + '-' * (box_width - 2) + '+')
    
def login_to_puparty():
    url = "https://tg-puparty-h5-api.puparty.com/api/v1/member/login"

    # قراءة محتوى ملف user.txt
    try:
        with open("user.txt", "r") as file:
            init_data = file.read().strip()  # قراءه النص من الملف
    except FileNotFoundError:
        print("[bold red]The file 'user.txt' was not found.[/bold red]")
        return None

    payload = {
        "initData": init_data,  # استخدام القيمة التي تم قراءتها من الملف
        "pid": None,
        "source": "ios",
        "tgVersion": "7.10"
    }

    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        'Content-Type': "application/json",
        'sec-ch-ua': "\"Not-A.Brand\";v=\"99\", \"Chromium\";v=\"124\"",
        'version': "1.1.0",
        'source': "ios",
        'sec-ch-ua-mobile': "?1",
        'token': "",
        'sec-ch-ua-platform': "\"Android\"",
        'origin': "https://h5.puparty.com",
        'sec-fetch-site': "same-site",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': "https://h5.puparty.com/",
        'accept-language': "en-US,en;q=0.9"
    }

    # إرسال الطلب باستخدام httpx
    with httpx.Client() as client:
        response = client.post(url, json=payload, headers=headers)

        # التأكد من نجاح الطلب
        if response.status_code == 200:
            try:
                # تحويل النص المستلم إلى JSON
                response_data = response.json()

                # استخراج الـ token من المفتاح "data"
                token = response_data.get("data", {}).get("token")
                if token:
                    print(token)
                    return token  # إرجاع التوكين
                else:
                    return None  # في حال لم يتم العثور على التوكين
            except json.JSONDecodeError:
                print("[bold red]Failed to decode JSON from the response.[/bold red]")
                return None
        else:
            print(f"[bold red]Request failed with status code {response.status_code}[/bold red]")
            return None

level = int(input(Fore.GREEN +" Your Pet Level : "))
def send_purchase_request_until_kanel_full(token):
    url = "https://tg-puparty-h5-api.puparty.com/api/v1/game/combine/purchase"

    payload = {
        "currency": 1,
        "level": level
    }

    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        'Content-Type': "application/json",
        'sec-ch-ua': "\"Not-A.Brand\";v=\"99\", \"Chromium\";v=\"124\"",
        'gameversion': "1.3.1",
        'sec-ch-ua-mobile': "?1",
        'access-control-allow-origin': "*",
        'company-code': "7",
        'token': token,  # التوكين يتم تمريره من المتغير
        'sec-ch-ua-platform': "\"Android\"",
        'origin': "https://h5.puparty.com",
        'sec-fetch-site': "same-site",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': "https://h5.puparty.com/",
        'accept-language': "en-US,en;q=0.9"
    }

    # إرسال الطلب باستخدام httpx
    with httpx.Client() as client:
        while True:
            response = client.post(url, json=payload, headers=headers)

            # استخراج البيانات من الاستجابة
            response_data = response.json()
            

            # التحقق من وجود رسالة الخطأ "max slot"
            if response_data.get('code') == 10002:
                print("[bold yellow]Max slot reached, retrying...[/bold yellow]")
                #print(response_data)
                
                send_combine_produce_request(token)
                break  # التوقف عن المحاولة إذا تم الوصول إلى الحد الأقصى

            # التحقق إذا كانت "kanel full" موجودة في الاستجابة
            if 'data' in response_data and 'kanel' in response_data['data'] and response_data['data']['kanel'] == 'full':
                print("[bold green]kanel full found![/bold green]")
                break  # الخروج من الحلقة بعد العثور على القيمة
            else:
                print("[bold red]Buy More pets...[/bold red]")
                send_combine_produce_request(token)

            time.sleep(5)  # إضافة تأخير 5 ثوانٍ قبل إرسال الطلب التالي


def send_combine_produce_request(token):
    url = "https://tg-puparty-h5-api.puparty.com/api/v1/game/combine/produce"

    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        'sec-ch-ua': "\"Not-A.Brand\";v=\"99\", \"Chromium\";v=\"124\"",
        'gameversion': "1.3.1",
        'sec-ch-ua-mobile': "?1",
        'content-type': "application/json",
        'access-control-allow-origin': "*",
        'company-code': "7",
        'token': token,  # التوكين هنا يتم تمريره من المتغير
        'sec-ch-ua-platform': "\"Android\"",
        'origin': "https://h5.puparty.com",
        'sec-fetch-site': "same-site",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': "https://h5.puparty.com/",
        'accept-language': "en-US,en;q=0.9"
    }

    # إرسال الطلب باستخدام httpx
    with httpx.Client() as client:
        response = client.post(url, headers=headers)

    try:
        response_data = response.json()

        # استخراج قيمة الذهب (gold) من داخل مفتاح 'data'
        if 'data' in response_data and 'gold' in response_data['data']:
            gold = response_data['data']['gold']
            print(f"[bold blue]Account Gold: {gold}[/bold blue]")
            return gold
        else:
            print("[bold red]Gold not found in the response.[/bold red]")

    except json.JSONDecodeError:
        print("[bold red]Error: The response is not in valid JSON format.[/bold red]")



def fetch_first_id(token):
    url = "https://tg-puparty-h5-api.puparty.com/api/v1/member/asset/collect/query"

    payload = {
        "pageNum": 1,
        "pageSize": 48
    }

    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        'Content-Type': "application/json",
        'sec-ch-ua': "\"Not-A.Brand\";v=\"99\", \"Chromium\";v=\"124\"",
        'version': "1.1.0",
        'source': "ios",
        'sec-ch-ua-mobile': "?1",
        'token': token,
        'sec-ch-ua-platform': "\"Android\"",
        'origin': "https://h5.puparty.com",
        'sec-fetch-site': "same-site",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': "https://h5.puparty.com/",
        'accept-language': "en-US,en;q=0.9"
    }

    try:
        # إرسال الطلب باستخدام httpx
        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()  # تحقق من وجود أخطاء HTTP

        # تحويل الرد إلى JSON
        data = response.json()
        #print(data)

        # استخراج أول id من قائمة list
        if 'data' in data and 'list' in data['data'] and len(data['data']['list']) > 0:
            first_id = data['data']['list'][0]['id']
            return first_id
        else:
            return "No IDs found in response"

    except httpx.RequestError as e:
        return f"An error occurred while making the request: {e}"
    except KeyError as e:
        return f"Key error: {e}"


def send_receive_request(token):
    url = "https://tg-puparty-h5-api.puparty.com/api/v1/member/asset/collect/receive"

    payload = {
        "id": fetch_first_id(token)
    }

    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        'Content-Type': "application/json",
        'sec-ch-ua': "\"Not-A.Brand\";v=\"99\", \"Chromium\";v=\"124\"",
        'version': "1.1.0",
        'source': "ios",
        'sec-ch-ua-mobile': "?1",
        'token': token,
        'sec-ch-ua-platform': "\"Android\"",
        'origin': "https://h5.puparty.com",
        'sec-fetch-site': "same-site",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': "https://h5.puparty.com/",
        'accept-language': "en-US,en;q=0.9"
    }

    try:
        # إرسال الطلب باستخدام httpx
        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()  # يتحقق من أخطاء HTTPs

        # تحويل الرد إلى JSON
        response_data = response.json()
        
        # طباعة الرد
        #print("Response:", json.dumps(response_data, indent=4))

        # التحقق من وجود الكود
        if response_data.get("code") == 0:
            print("Success: The ID has been processed successfully.")
        else:
            print(f"Error: {response_data.get('msg', 'Unknown error')}")

    except httpx.RequestError as e:
        print(f"Request error occurred: {e}")
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
    except json.JSONDecodeError:
        print("Error decoding JSON response.")

# استدعاء الدالة مع المعرف المطلوب

def send_combine_merge_request(token):
    url = "https://tg-puparty-h5-api.puparty.com/api/v1/game/combine/merge"

    while True:
        pos1 = random.randint(1, 9)
        pos2 = random.randint(1, 9)

        payload = {
            "pos1": pos1,
            "pos2": pos2
        }

        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
            'Content-Type': "application/json",
            'sec-ch-ua': "\"Not-A.Brand\";v=\"99\", \"Chromium\";v=\"124\"",
            'gameversion': "1.3.1",
            'sec-ch-ua-mobile': "?1",
            'access-control-allow-origin': "*",
            'company-code': "7",
            'token': token,  # التوكين يتم تمريره من المتغير
            'sec-ch-ua-platform': "\"Android\"",
            'origin': "https://h5.puparty.com",
            'sec-fetch-site': "same-site",
            'sec-fetch-mode': "cors",
            'sec-fetch-dest': "empty",
            'referer': "https://h5.puparty.com/",
            'accept-language': "en-US,en;q=0.9"
        }

        # إرسال الطلب باستخدام httpx
        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=headers)

        print(f"[bold cyan]Request with pos1={pos1} and pos2={pos2}:[/bold cyan]")

        # تحقق من وجود "success" في الاستجابة
        if "success" in response.text.lower():
            print("[bold green]Success: Up Level.[/bold green]")
            break

        print("[bold red]Not success yet, retrying in 5 seconds...[/bold red]")
        time.sleep(10)



# استدعاء الدالة وتخزين التوكين
token = login_to_puparty()

if token:
    banner_text = "Bot Puparty"
    os.system('cls' if os.name == 'nt' else 'clear')
    create_gradient_banner(banner_text)
    social_media_usernames = [
        ("Telegram Channel", "https://t.me/YOU742"),
        
        #("", "@"),
        ("Coder", "@Ke4oo"),
    ]
    
    print_info_box(social_media_usernames)
    
    while True:
    	send_purchase_request_until_kanel_full(token)
    	time.sleep(10)
    	send_combine_merge_request(token)
    	time.sleep(10)
    	send_receive_request(token)
    	time.sleep(10)
    
else:
    print("[bold red]Failed to login, cannot proceed with the requests.[/bold red]")