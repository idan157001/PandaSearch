import gspread
from oauth2client.service_account import ServiceAccountCredentials

import firebase_admin
from firebase_admin import credentials,db
import os

class Search:
    _initialized = False

    def __init__(self):
        if not Search._initialized:
            cred = credentials.Certificate(r"C:\Users\Idan's PC\OneDrive\Desktop\Pandabuy\firebase_auth.json")
            firebase_admin.initialize_app(cred, {'databaseURL': os.getenv('databaseURL')})
            Search._initialized = True

        self.ref = db.reference('/Items')
        self.new_ref = db.reference('/New_Items')
        self.display_items = list()
        self.sneaker_brands = {'dunks','dunk','vt','nike','adidas', 'air','jordan', 'air force', 'yeezy', 'bapesta', 'balenciaga', 'converse', 'off white', 'mcqueen', 'new balance', 'sacai', 'acg mountain', 'air max', 'louis vuitton', 'amiri'}


    
    def user_search_can_split(self,search_text:str) -> bool:
        """
        checks if user_search query has more than 1 word
        """
        search_text = search_text.split()
        if len(search_text) > 1:
            return True

        
    def in_sneaker_brands(self,search_list,item_data) -> set:#
        """
        Checks if item_data[brand] inside search_list (search query from user) 
        """
        item_brand = item_data.get('brand',None)
        if item_brand is not None:
            for word in search_list:
                    if word in item_brand:
                        return True
                    

    def split_search_query(self,search_text:str) -> str:
        return search_text.split() 
      

    def word_in_node_name(self,word,new_items_to_display):
        if new_items_to_display:
            return True
        

    def sort_by_name(self,search_list,items_to_display:list):#
        new_items_to_display = items_to_display.copy()
        db_items = self.ref.get()
        items_to_sort = []
        for word in search_list:
            
            if new_items_to_display:
                for item in new_items_to_display:
                    if word in item.get('name').lower() and word not in self.sneaker_brands:                        
                        items_to_sort.append(item)
            else:
                for node,items_data in db_items.items():
                    if word in items_data.get('name').lower() and word not in self.sneaker_brands:
                        items_to_sort.append(items_data)

    
        for item in items_to_sort:
            if item in new_items_to_display:
                new_items_to_display.remove(item)
            new_items_to_display.insert(0,item)
        return new_items_to_display
    

    def sort_by_reviews(self,items_to_display:list):
        """
        Sort items_to_display by reviews
        """
        print(items_to_display)
        return sorted(items_to_display,key=lambda item:item['reviews'],reverse=True)
    

    def sort_search(self,search_text:str):
        search_text = search_text.lower()
        db_items = self.ref.get()
        items_to_display = list()

        search_list = self.split_search_query(search_text)
        for node,item_data in db_items.items():
           if self.in_sneaker_brands(search_list,item_data):
               items_to_display.append(item_data)

        items_to_display = self.sort_by_reviews(items_to_display)       
        items_to_display = self.sort_by_name(search_list,items_to_display)
        if items_to_display:
            return items_to_display
        return None
                
###############
    
    
        
     


    def search_runner(self,search_text:str):
        if len(search_text) > 30 or len(search_text) < 3:
            return None
        return self.sort_search(search_text)