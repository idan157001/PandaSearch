import requests
import json
random_user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
headers = {"User-Agent": random_user_agent}
r = requests.get('https://thor.weidian.com/detail/getItemSkuInfo/1.0?param=%7B%22itemId%22%3A%224439379179%22%7D',headers=headers)
req = json.loads(r.text)
print(req['result']['itemTitle'])