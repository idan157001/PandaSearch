import requests
import random
import requests
import asyncio
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


async def make_affiliate_link(url):
    #Making The Link and return it to Main
    try:
     
        random_user_agent = random.choice(user_agents)
        headers = {"User-Agent": random_user_agent}

        response = await asyncio.to_thread(requests.get, url, headers=headers,timeout=3)
        if response.status_code == 200:
            url = response.url
           
            my_url = url.split("inviteCode=")[0] + 'inviteCode=ZGTWERRP3'
            if my_url.startswith('https://www.pandabuy.com/product') and not my_url.endswith('&inviteCode=ZGTWERRP3'): # fix url where & is missing
                my_url =  my_url.split("inviteCode=")[0] + '&inviteCode=ZGTWERRP3'
                
            return my_url
        
        
        
    except Exception as e:
        raise e

# Create and run the asyncio event loop
async def main(urls):
    if len(urls) <= 100:
        print(f'Uploading {len(urls)} links')
        results = await asyncio.gather(*(make_affiliate_link(url) for url in urls))
        return results
    else:
        results = []
        url_len = len(urls)
        chunks = url_len//100
        s,e = 0,100
        for i in range(chunks+1):
            if i == chunks:
                results += await asyncio.gather(*(make_affiliate_link(url) for url in urls[chunks*100:url_len]))
                
            results += await asyncio.gather(*(make_affiliate_link(url) for url in urls[s:e]))
            s+=100
            e+=100
            print(f'chunk ({i+1}/{chunks+1})')
    
        return results


def runner(urls):
    return asyncio.run(main(urls))


