import requests
import random
import requests
import asyncio
from bs4 import BeautifulSoup as bs
import urllib.parse
import json
import re
import os
from PIL import Image
import io
import cv2
import numpy as np
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode
from dotenv import load_dotenv
load_dotenv()


My_Urls = []
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/89.0.774.68 Safari/537.36 Edg/89.0.774.68",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36 Edg/89.0.774.68",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
]

async def fetch_reviews(url) -> int:
    try:
        if url == 'bad_link':
            return 0
        
        random_user_agent = random.choice(user_agents)
        headers = {"User-Agent": random_user_agent}

        response = await asyncio.to_thread(requests.get, url, headers=headers,timeout=10)
        if response.status_code == 200:
            text = json.loads(response.text)
            reviews_count = (text['data']['count'])
            if reviews_count > 10:
                return reviews_count
            return 0
    except Exception as e:
        return 0
async def grab_link(url):
    #Change Affilate code to mine 

    try:
        random_user_agent = random.choice(user_agents)
        headers = {"User-Agent": random_user_agent}

        response = await asyncio.to_thread(requests.get, url, headers=headers,timeout=10)
        if response.status_code == 200:
            url = response.url
            
            if 'https://www.pandabuy.com/product' not in url:
                return None
            if 'weidian.com' in url:
                my_url =  url.split("inviteCode=")[0] + '&inviteCode=ZGTWERRP3'
                parsed_url = urlparse(my_url)
                query_params = parse_qs(parsed_url.query)
                desired_params = {
                'url': query_params.get('url', [''])[0],
                'inviteCode': query_params.get('inviteCode', [''])[0]}
                new_query = urlencode(desired_params, doseq=True)
                my_url = f"https://www.pandabuy.com/product?{new_query}"
                print(my_url)
                    
                return my_url
        

    except Exception as e:
        raise e

# Create and run the asyncio event loop
async def grab_links_runner(urls):
    
    # activating grab_link() 
    if len(urls) <= 100:
        print(f'Uploading {len(urls)} links')
        results = await asyncio.gather(*(grab_link(url) for url in urls))
        return results
    else:
        results = []
        url_len = len(urls)
        chunks = url_len//100
        s,e = 0,100
        for i in range(chunks+1):
            if i == chunks:
                results += await asyncio.gather(*(grab_link(url) for url in urls[chunks*100:url_len]))
                
            results += await asyncio.gather(*(grab_link(url) for url in urls[s:e]))
            s+=100
            e+=100
            print(f'chunk ({i+1}/{chunks+1})')
    
        return results
    
async def save_img_runner(urls,files_name):
    tasks = [save_img(url,file_name) for url,file_name in zip(urls,files_name)]
    results = await asyncio.gather(*tasks)
    return results

async def save_img(url,file_name):
    file_path = fr"C:\Users\Idan's PC\OneDrive\Desktop\Pandabuy\pandabuy\Items\{file_name}"
    random_user_agent = random.choice(user_agents)
    headers = {"User-Agent": random_user_agent}
    try:
        response = await asyncio.to_thread(requests.get, url, headers=headers,timeout=3)
        if response.status_code == 200:
            
                print(file_path)
                new_width = 400
                new_height = 400
                img_array = np.frombuffer(response.content, np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                resized_img = cv2.resize(img, (new_width, new_height))
                cv2.imwrite(file_path, resized_img)
    except:
        return file_path
        


def set_brand_tag(name,arg):
    tags = []
    clothing_vocabulary = {"jacket", "shirt", "t-shirt", "blouse", "sweater", "cardigan", "hoodie", "coat", "vest", "suit", "tie", "bow tie", "trousers", "jeans", "shorts", "skirt", "dress", "overalls", "jumpsuit", "blazer", "raincoat", "windbreaker", "trench coat", "poncho", "kimono", "onesie", "romper", "pajamas", "socks", "stockings", "tights", "leggings", "underwear", "bra", "panties", "boxers", "briefs", "swimsuit", "bikini", "flip-flops", "sneakers", "high heels", "sandals", "boots", "loafers", "oxfords", "espadrilles", "slippers", "scarf", "hat", "cap", "beanie", "gloves", "mittens", "sunglasses", "belt", "suspenders", "watch", "necklace", "earrings", "bracelet", "ring", "brooch", "cufflinks", "pocket square", "handbag", "backpack", "tote bag", "clutch", "wallet", "umbrella", "shawl", "tie pin", "cane", "hairband", "hairpin", "clogs", "moccasins"}
    sneaker_brands = set({'dunks','travis','dunk','vt','nike','adidas', 'air','jordan', 'air force', 'yeezy', 'bapesta', 'balenciaga', 'converse', 'off white', 'mcqueen', 'new balance', 'sacai', 'acg mountain', 'air max', 'louis vuitton', 'amiri',"gucci", "louis vuitton", "chanel", "prada", "versace", "dior", "balenciaga", "fendi", "burberry", "givenchy", "valentino", "dolce & gabbana", "alexander mcqueen", "calvin klein", "ralph lauren", "tommy hilfiger", "michael kors", "coach", "marc jacobs", "kate spade", "yves saint laurent (ysl)", "hermes", "balmain", "celine", "off-white", "bottega veneta", "zara", "h&m", "mango", "topshop", "gap", "levi's", "diesel", "armani", "hugo boss", "lacoste", "puma", "nike", "adidas", "reebok", "converse", "new balance", "vans", "timberland", "dr. martens", "ugg", "north face", "patagonia", "columbia", "under armour", "champion", "supreme", "off-white", "bape", "vetements", "officine generale", "acne studios", "alexachung", "amiri", "nina ricci", "vivienne westwood", "isabel marant", "comme des garcons", "gareth pugh", "rick owens", "marni", "stella mccartney", "bally", "lanvin", "comme des garcons play", "comme des garcons shirt", "kenzo", "celine", "givenchy", "rick owens drkshdw", "maison margiela", "amiri", "palm angels", "fear of god", "rothco", "stone island", "neil barrett", "r13", "undercover", "junya watanabe", "kolor", "maison margiela", "issey miyake", "jil sander", "comme des garcons homme", "comme des garcons homme plus", "number (n)ine", "huf", "palace", "billionaire boys club", "a bathing ape", "supreme", "off-white"})
    
    if arg == 'clothing':
        tag_set  = clothing_vocabulary
    elif arg == 'brand':
        tag_set = sneaker_brands

    for word in name.lower().split():
        if word in tag_set:
            tags.append(word)
    return tags

        
def get_name(name):
    bad_chars = "!@#$%^&*}{/>,()"
    bad_chars_pattern = re.escape(bad_chars)


    try:
        name = ' '.join(name.split(' '))
        name = re.sub(r'[\u4e00-\u9fff]+', '', name)
        
        if 'n1ke' in name.lower():
            name =  re.sub(r'\bN1KE\b', 'Nike', name, flags=re.IGNORECASE)
         
        if 'return' in name:
            name = ''.join(name.split('return')[:-1]) 
        name = re.sub(f"[{bad_chars_pattern}].*", "", name) # remove not chars
        name = re.sub(r'nk', 'Nike', name,flags=re.IGNORECASE)
        name = re.sub(r'j0rdan', 'Jordan', name,flags=re.IGNORECASE)

        name = re.sub(r'[^a-zA-Z0-9 ]', '', name) 
        name = (' '.join(name.split(' ')[:-1])).strip()
        
        return name
    except Exception as e:
        raise e
def get_today_date():
    today = datetime.now()
    date = today.strftime("%m/%d/%y")
    return date

async def fetch_data(url):
    
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    item_id = query_params.get('url')[0].split('=')[1]
    item_id = item_id.split('&')[0]
    new_url = f"https://thor.weidian.com/detail/getItemSkuInfo/1.0?param=%7B%22itemId%22%3A%22{item_id}%22%7D"
    try:
        random_user_agent = random.choice(user_agents)
        headers = {"User-Agent": random_user_agent}

        response = await asyncio.to_thread(requests.get, new_url, headers=headers,timeout=10)
        if response.status_code == 200:
            url = await shorter_link(url)
            upload_date = get_today_date()
            req = json.loads(response.text)
           
            results = req['result']
            price = str(results['itemDiscountHighPrice'])
            price = re.sub(r'00$', '', price)
            cny_price = int(price)
            img = results['itemMainPic']
            
            name = get_name(results['itemTitle'])
            brand = set_brand_tag(name,'brand')
            clothing_type = set_brand_tag(name,'clothing')
            
            return {'name':name,'img':img,'cny_price':cny_price,'link':url,'brand':brand,'clothing_type':clothing_type,'upload_date':upload_date}
        else:
            print(response.url)
    except Exception as e:
        raise e
async def shorter_link(url) -> str:
    try:
        api_url ="https://www.pandabuy.com/gateway/user/proxyList/getInviteUrl"
        data = {"link":url}
        random_user_agent = random.choice(user_agents)
        headers = {"User-Agent": random_user_agent,"Authorization": os.getenv("getInviteUrl_authorization")}

        response = await asyncio.to_thread(requests.post, api_url, headers=headers,timeout=10,data=data)
        if response.status_code == 200:
            response = response.json()
            return (response['data'])
            

    except Exception:
        raise Exception
    
async def get_data_runner(urls):
    tasks = [fetch_data(url) for url in urls if url is not None]
    results = await asyncio.gather(*tasks)
    return results

async def get_reviews_runner(urls):
    tasks = [fetch_reviews(url) for url in urls if url is not None]
    results = await asyncio.gather(*tasks)
    return results


####################
def make_link(urls):
    return asyncio.run(grab_links_runner(urls))

def save_imgs(urls,files_name):
    return asyncio.run(save_img_runner(urls,files_name))

def get_data(urls):
    return asyncio.run(get_data_runner(urls))

def get_reviews(urls):
    return asyncio.run(get_reviews_runner(urls))

print(os.getenv("getInviteUrl_authorization"))