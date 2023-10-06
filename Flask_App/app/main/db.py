import gspread
from oauth2client.service_account import ServiceAccountCredentials

import firebase_admin
from firebase_admin import credentials,db

class FireBase:
    _initialized = False

    def __init__(self):
        if not FireBase._initialized:
            cred = credentials.Certificate(r"C:\Users\Idan's PC\OneDrive\Desktop\Pandabuy\pandabuy-400210-firebase-adminsdk-5qwel-2c877b63e3.json")
            firebase_admin.initialize_app(cred, {'databaseURL': 'https://pandabuy-400210-default-rtdb.europe-west1.firebasedatabase.app/'})
            FireBase._initialized = True

        self.ref = db.reference('/Items')
        self.new_ref = db.reference('/New_Items')

    def get_item_name(self,item):
        item_to_search = item.lower()
        items_to_display = set()

        nodes = self.ref.get().keys()
        for node in nodes:
            if item_to_search in node.lower():
                items_to_display.add(node)

        if len(items_to_display) > 1:
            return self.get_data_by_nodes(items_to_display)
        
        return None
    
    def get_data_by_nodes(self,items_to_display):
        nodes = self.ref.get()
        set_of_items = []
        for item in items_to_display:
            if item in nodes:
                item_set = {item: nodes[item]}
                set_of_items.append(item_set)
                
        return set_of_items

