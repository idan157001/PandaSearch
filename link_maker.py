import requests
import random
import requests
import asyncio
from bs4 import BeautifulSoup as bs
import urllib.parse

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
async def grab_image(url:str) -> str:

    # Send get request to url to get the image link

    url = urllib.parse.unquote(url)
    url = url.split('url=')[-1].split('&spider')[0]
    
    random_user_agent = random.choice(user_agents)
    headers = {"User-Agent": random_user_agent}
    try:
        response = await asyncio.to_thread(requests.get, url, headers=headers,timeout=10)
        if response.status_code == 200:
            contect = response.content 
            soup= bs(contect,'html.parser')
            link_element = soup.find('link', {'rel': 'preload', 'as': 'image'})

            if link_element:
                href = link_element.get('href')
                if href:
                    print(href)
                    img_link = href.split('?')[0]+ '?w=700&h=700&cp=1'
                    return img_link
    except:
        pass
async def grab_image_runner(urls) -> list:
    # Create a list of tasks for make_item_image
    tasks = [grab_image(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results
    
async def grab_link(url):

    #Change Affilate code to mine 

    try:
        random_user_agent = random.choice(user_agents)
        headers = {"User-Agent": random_user_agent}

        response = await asyncio.to_thread(requests.get, url, headers=headers,timeout=10)
        if response.status_code == 200:
            url = response.url
           
            my_url = url.split("inviteCode=")[0] + 'inviteCode=ZGTWERRP3'
            if my_url.startswith('https://www.pandabuy.com/product') and not my_url.endswith('&inviteCode=ZGTWERRP3'): # fix url where & is missing
                my_url =  my_url.split("inviteCode=")[0] + '&inviteCode=ZGTWERRP3'
                
            return my_url
        
        
        
    except Exception as e:
        pass

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

    response = await asyncio.to_thread(requests.get, url, headers=headers,timeout=10)
    if response.status_code == 200:
        with open(file_path,'wb') as file:
            file.write(response.content)

def make_link(urls):
    return asyncio.run(grab_links_runner(urls))

def make_img(urls,max_urls=30):
    urls = urls[:max_urls]
    return asyncio.run(grab_image_runner(urls))

def save_imgs(urls,files_name):
    return asyncio.run(save_img_runner(urls,files_name))



