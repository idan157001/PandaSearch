import gspread
from oauth2client.service_account import ServiceAccountCredentials

import firebase_admin
from firebase_admin import credentials,db
from link_maker import make_link,make_img,save_imgs
import re
import random
import string
import os 
import time

class FireBase:
    _initialized = False

    def __init__(self):
        if not FireBase._initialized:
            cred = credentials.Certificate(r"C:\Users\Idan's PC\OneDrive\Desktop\Pandabuy\pandabuy-400210-firebase-adminsdk-5qwel-2c877b63e3.json")
            firebase_admin.initialize_app(cred, {'databaseURL': 'https://pandabuy-400210-default-rtdb.europe-west1.firebasedatabase.app/'})
            FireBase._initialized = True

        self.ref = db.reference('/Items')
        self.new_ref = db.reference('/New_Items')

    def write_data(self, node: str, data_dict: dict):

        # Write data to the Firebase Database under the specified node

        try:
            self.new_ref.child(node).set(data_dict)
        except ValueError as e:
            raise e
    def upload_imgs_to_new_items(self):
        # Need to use 
        # Uploading Links of img for each item in /New_Items
        nodes_to_update = []
        urls = []
        data = self.new_ref.get()
        for (node,values) in data.items():
            if 'img' not in values:
                urls.append(values['link'])
                nodes_to_update.append(node)
        
        results = make_img(urls)
        
        for node,img_link in zip(nodes_to_update,results):
                self.new_ref.child(node).update({'img':img_link})
        print(f'Uploaded {len(results)}\nNot Uploaded {len(nodes_to_update)}')
        return(len(nodes_to_update))
    def check_links_from_db(self):
         
        #Read Lines From Firebase check if link is good 

        counter = 0 
        rows = self.new_ref.get()
        for x,y in rows.items():
            link = str(y['link'])
            if link.startswith('https://www.pandabuy.com/product') and  link.endswith('&inviteCode=ZGTWERRP3'):
                counter+=1
        print(f'bad rows: {len(rows)-counter}')

    def changing_new_items_links(self):

        #Changing the InviteCode affilate link and upload it to FireBase /New_Items
        #This Function take some time 

        links = []
        nodes_name_to_update = []
        node = self.new_ref.get()

        for node_name,values in node.items():
            link = values['link']  
            if not link.endswith('&inviteCode=ZGTWERRP3'):
                nodes_name_to_update.append(node_name)
                links.append(link)
                 
        print(f'Working On New Links {len(links)} ')
        new_links = make_link(links)

        node = self.new_ref.get()
        for new_link,node_name in zip(new_links,nodes_name_to_update):
            if new_link is None or  not new_link.startswith('https://www.pandabuy.com/product'):
                self.new_ref.child(node_name).delete()
                continue

            
            self.new_ref.child(node_name).update({'link':new_link})
            print(new_link)
        print('New Linked Uploaded')
        database.check_links_from_db()

    def upload_newItems_to_items(self):
        
        #Upload items from /New Items to Items + Check if len == 3 (check if link,dollar,cny is there)

        print('Moving /New_Items >>> /Items')
        new_items_data = self.new_ref.get()
        
        for name,item_data in new_items_data.items():
             if len(item_data) == 4:
                  self.ref.child(name).set(item_data)
                  
        print('All Items has been moved')
    def remove_bad_files(self):
        #check if img in firebase if not remove it from folder
        #fixing bug if happend
        removed_count = 0
        folder_path = fr"C:\Users\Idan's PC\OneDrive\Desktop\Pandabuy\pandabuy\Items"
        items_data = self.ref.get()
        s = set()
        s1 = set()
        for node,item_data in items_data.items():
            s.add(item_data['file_name'])
        

        for item in os.listdir(folder_path):
            if item not in s:
                os.remove(f'{folder_path}\{item}')
                removed_count+=1

        print(removed_count)

    def save_img_into_file(self):
            #Saving Images to folder 
            print('Saving Images to folder')
            chars = string.ascii_letters + string.digits
            urls = []
            files_name = []
            items_data = self.ref.get()
            folder_path = fr"C:\Users\Idan's PC\OneDrive\Desktop\Pandabuy\pandabuy\Items"

            for node,item_data in items_data.items():
                file_id = ''.join(random.choice(chars) for _ in range(32))

                while os.path.exists(os.path.join(folder_path, file_id)):
                    file_id = ''.join(random.choice(chars) for _ in range(32))

                if 'file_name' not in item_data:
                    if '.png' in item_data['img']:
                        self.ref.child(node).update({'file_name':f'{file_id}.png'})
                    else:
                        self.ref.child(node).update({'file_name':f'{file_id}.jpg'})

                    items_data = self.ref.get()
                    for node,item_data in items_data.items():
                        urls.append(item_data['img'])
                        files_name.append(item_data['file_name'])

            save_imgs(urls,files_name)
            print('Images Saved')


    def clear_new_items(self):

        #Remove /New_Items from db 

        new_items_data = self.new_ref.get()
        for name in new_items_data:
            self.new_ref.child(name).delete()
         
                 
class Spread_sheet(FireBase):
    def __init__(self):
        self.credentials_file = r"C:\Users\Idan's PC\OneDrive\Desktop\Pandabuy\pandabuy-400210-e9f9703a03af.json"
        self.config()
        self.new_ref = self.ref = db.reference('/New_Items') 
        super().__init__()

    def config(self):
        #Configuration for the google authentication
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, scope)
        self.gc = gspread.authorize(credentials)
    
    def clean_name_chars(self,name) -> str :

        #Making sure data is valid

        illegal_character_pattern = re.compile(r'[^a-zA-Z0-9]')
        
        if '\n' in name:
            name = str(name).replace('\n',' ')
        if '\r' in name:
            name = str(name).replace('\r',' ')
    
        # Replace each illegal character with a space
        name = re.sub(illegal_character_pattern, ' ', name)
        return name
    
    def check_if_item_already_exits(self,name,dollar):
        data = self.new_ref.get()
        try:
            if data:
                if name in data.keys():
                    if data[name]['dollar'] != dollar:
                        new_name = f'{name} VVV{random.randint(100,999)}'
                        while new_name in data.keys():
                            new_name = f'{name} VVV{random.randint(100,999)}'
                        return new_name
                return name
        except Exception as e:
             raise e
         

    def write_spreadsheet_to_firebase(self, spreadsheet_url: str,start_cell:int,end_cell:int):
        print('Uploading Links to Firebase')

        spreadsheet = self.gc.open_by_url(spreadsheet_url)
        worksheet = spreadsheet.get_worksheet(0)
        data = worksheet.get_all_values()

        for row in data[start_cell:end_cell]:
            if len(row) < 4:
                continue  

            name, link, cny, dollar = None, None, None, None

            for cell_value in row:
                name = row[0]
                if '$' in cell_value:
                    dollar = cell_value
                elif '¥' in cell_value:
                    cny = cell_value
                elif 'pandabuy' in cell_value and 'https://' in cell_value:
                    link = cell_value
 
            if any(item is None for item in (name, link, cny, dollar)):
                continue
            else:
                    name_valid = self.clean_name_chars(name)
                    if name_valid and len(link) > 20:
                        new_ref_data = self.new_ref.get()
                        if new_ref_data is not None:
                            if name_valid not in new_ref_data.keys():
                                self.write_data(name_valid, {'link': link, 'cny': cny, 'dollar': dollar})
                        else:
                            self.write_data(name_valid, {'link': link, 'cny': cny, 'dollar': dollar})

        print('Links Uploaded')
    

# SpreadSheet_url to upload
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1ffvM_fax9iuLEvqgIwprl7SMf2n0B8YaSLKXb843Wo4/htmlview?pru=AAABgurjdTc*cg2AYCugO3MpTM4qGBA62A#gid=0'
database = FireBase()
item = Spread_sheet()


def new_items_db():
    item.write_spreadsheet_to_firebase(spreadsheet_url,8,450)
    #database.changing_new_items_links()
    
    """not_uploaded = database.upload_imgs_to_new_items()# run solo
    while not_uploaded > 0:
        time.sleep(10)
        not_uploaded = database.upload_imgs_to_new_items()
    print('Finish')
    """
def items_db():
    database.upload_newItems_to_items()
    item.save_img_into_file()

def main():
    new_items_db()
    #items_db()

main()

#database.remove_bad_files()

