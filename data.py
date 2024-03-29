import gspread
from oauth2client.service_account import ServiceAccountCredentials

import firebase_admin
from firebase_admin import credentials,db
from link_maker import make_link,save_imgs,get_data,get_reviews,shorter_link
import re
import random
import string
import os 
import time
from urllib.parse import urlparse, parse_qs
import requests
from dotenv import load_dotenv
from typing import Union
import asyncio
load_dotenv()


class Items:
    _initialized = False

    def __init__(self):
        if not Items._initialized:
            cred = credentials.Certificate(r"C:\Users\Idan's PC\OneDrive\Desktop\Pandabuy\firebase_auth.json")
            firebase_admin.initialize_app(cred, {'databaseURL': os.getenv('databaseURL')})
            Items._initialized = True

        self.ref = db.reference('/Items')
        self.new_ref = db.reference('/New_Items')
        self.folder_path = os.getenv('folder_path')

    def set_items_dict(self):
        self.items_dict = {}
        data = self.ref.get()
        for item_key, item_data in data.items():
            self.items_dict[item_key] = (item_data.get("link", ""), item_data.get("reviews", 0))

    def item_already_exits(self,item) -> bool:
        """
        Check if item already exits in db 
        """
        item_name,item_link,item_reviews = item['name'],item['link'],item['reviews']

        if item_name in self.items_dict: # if new_item_name already in db
            if item_reviews > self.items_dict[item_name][1]: # if same name and more reviews on new item
                self.ref.child(item_name).update({'link':item_link,'reviews':item_reviews})
                print(f'{item_name} Exits')
            return True
        return False
        
            
    def count_bad_rows(self):
        bad_row_count = 0
        rows = self.new_ref.get()

        for row_id, row_data in rows.items():
            link = row_data.get('link', '')
            if self.is_bad_link(link):
                bad_row_count += 1

        good_row_count = len(rows) - bad_row_count
        print(f'good rows: {good_row_count}, bad rows: {bad_row_count}')

    def is_bad_link(self,link):
        return link.startswith('https://www.pandabuy.comhttps://www.pandabuy.com/product') and link.endswith('&inviteCode=ZGTWERRP3')

    """def remove_if_filename_not_in_db(self,items):
        data = self.ref.get()
        for x,y in data.items():
            if y['file_name'] not in items:
                print(x)"""

    def upload_newItems_to_items(self):
        #Upload items from /New Items to Items 

        print('Moving /New_Items >>> /Items')
        item_len_min = 5
        new_items_data = self.new_ref.get()
        uploaded_items = 0
        for name,item_data in new_items_data.items():
             if len(item_data) > item_len_min:
                  if item_data.get('reviews',0) > 10:
                      uploaded_items+=1
                      self.ref.child(name).set(item_data)
                  
        print('All Items has been moved',uploaded_items)

    def remove_bad_files(self):
        #Delete file_name if file_name not in /Items 
        #fixing bug if happend
        removed_count = 0
        items_data = self.ref.get()
        files_counter = 0
        if items_data:
            db_file_names = set(file_name.get('file_name') for file_name in items_data.values() )
      
            for item in os.listdir(self.folder_path):
                
                if item not in db_file_names:
                    os.remove(f'{self.folder_path}\{item}')
                    removed_count+=1
                files_counter+=1


            print(f'{removed_count} bad files\nDB Items {len(db_file_names)}\nFolder Files {files_counter}')


    @staticmethod
    def get_dollar_price():
        api_key = os.getenv("dollar_api_key")
        endpoint = f"http://api.exchangeratesapi.io/v1/latest?access_key={api_key}"
        try:
            response = requests.get(endpoint)
            if response.status_code == 200:
                data = response.json()
                exchange_rates = data['rates']
                return exchange_rates['USD'] / exchange_rates['CNY']
            
            raise Exception('get_dollar_price()  status_code != 200')
    
        except Exception as e:
            raise e
    
    def update_short_link(self):
        data = self.ref.get()
        for x,y in data.items():
            link = y['link']
            if 'pandabuy.allapp.link' not in link:
                new_link = (asyncio.run(shorter_link(link)))
                print(x)
                self.ref.child(x).update({"link":new_link})
            




class New_Items(Items):
    def __init__(self):
        self.credentials_file = r"C:\Users\Idan's PC\OneDrive\Desktop\Pandabuy\google_auth.json"
        self.config_google_auth()
        super().__init__()
        self.set_items_dict()
        
    def config_google_auth(self):
        #Configuration for the google authentication
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, scope)
        self.gc = gspread.authorize(credentials)

    def upload_data(self,spreadsheet_url:str,start_cell,end_cell):
        links = list()
        spreadsheet = self.gc.open_by_url(spreadsheet_url)
        worksheet = spreadsheet.get_worksheet(0)
        data = worksheet.get_all_values()

        for row in data[start_cell:end_cell]:
            if len(row) < 4:
                continue  

            for cell_value in row:
                if 'pandabuy' in cell_value and 'https://' in cell_value:
                    link = cell_value
                    links.append(link)

        self.changing_new_items_links(links)


    def changing_new_items_links(self,links):
        #Changing the InviteCode affilate link and upload it to FireBase /New_Items
        
        print(f'Working On New Links {len(links)} ')
        
        new_links = make_link(links)
        reviews = get_reviews(self.make_reviews_links(new_links))
        items = get_data(new_links)
        cny_to_usd_rate = self.get_dollar_price()
        

        for index,item in enumerate(items):
            
            rev = reviews[index]
            cny_price = item['cny_price']
            amount_in_usd = cny_price * cny_to_usd_rate
            dollar_price = f'{amount_in_usd:.2f}'
            item['dollar_price'] = dollar_price
            item['reviews'] = rev
            node = item['name']
            exits = self.item_already_exits(item)
            if exits:
                continue
            if len(node) > 1 and rev > 10:
                self.new_ref.child(node).set(item)

        print('New Linked Uploaded')
    
    def make_reviews_links(self,links):
        reviews_links = []
        for link in links:
            if link:
                
                try:
                    if 'itemID=' in link:
                       item_id= link.split('itemID=')[1].split('&')[0]
                    else:
                        item_id = link.split("itemID%3D")[1].split("%26")[0]
                    link = f"https://www.pandabuy.com/gateway/comment/goods/review/count?goodsId={item_id}&goodsUrl=https:%2F%2Fweidian.com%2Fitem.html%3FitemID%3D{item_id}%26spider_token%3D4572&goodsPlatform=wd"
                    reviews_links.append(link)
                except:
                    reviews_links.append('bad_link')
        return reviews_links

    def save_img_into_file(self):
            #Saving Images to folder 
            print('Saving Images to folder')
            chars = string.ascii_letters + string.digits
            urls = []
            files_name = []
            items_data = self.new_ref.get()

            for node,item_data in items_data.items():
                file_id = ''.join(random.choice(chars) for _ in range(32))

                while os.path.exists(os.path.join(self.folder_path, file_id)):
                    file_id = ''.join(random.choice(chars) for _ in range(32))

                if 'file_name' not in item_data.keys():
                    
                    if '.png' in item_data['img']:
                        self.new_ref.child(node).update({'file_name':f'{file_id}.png'})
                    elif '.jpg' in item_data['img']:
                        self.new_ref.child(node).update({'file_name':f'{file_id}.jpg'})
                    else:
                        self.new_ref.child(node).delete()

            items_data = self.new_ref.get()
            for node,item_data in items_data.items():
                urls.append(item_data['img'])
                files_name.append(item_data['file_name'])

            bad_files = (save_imgs(urls,files_name))
            self.delete_item_bad_file_name(bad_files)
            
            print('Images Saved')

    def delete_item_bad_file_name(self,bad_files):
            items_data = self.new_ref.get()
            for bad_file in bad_files:
                if bad_file is not None:
                    for node,item_data in items_data:
                        if items_data['file_name'] == bad_file:
                            self.new_ref.child(node).delete()
                            print('deleted bad item')

                            
    def clear_new_items(self):
        #Remove /New_Items from db 
        new_items_data = self.new_ref.get()
        for name in new_items_data:
            self.new_ref.child(name).delete()

database = Items()
new_items = New_Items()

def runner():
    spreadsheet_url = ''
    database.remove_bad_files()
    new_items.upload_data(spreadsheet_url,50,150)
    #new_items.save_img_into_file()
    #database.upload_newItems_to_items()
    #database.clear_new_items()

#runner()


links = []
l = """"""
for i in l.split('\n'):
    if i:
        links.append(i.strip())
        
#database.remove_bad_files()
#new_items.changing_new_items_links(links)
#new_items.save_img_into_file()
#database.upload_newItems_to_items()
#new_items.clear_new_items()
#new_items.update_short_link()

