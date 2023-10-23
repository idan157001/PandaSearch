import gspread
from oauth2client.service_account import ServiceAccountCredentials
import firebase_admin
from firebase_admin import credentials,db
import os
from dotenv import load_dotenv
load_dotenv()

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
        self.sneaker_brands = set({'dunks','travis','dunk','vt','nike','adidas', 'air','jordan', 'air force', 'yeezy', 'bapesta', 'balenciaga', 'converse', 'off white', 'mcqueen', 'new balance', 'sacai', 'acg mountain', 'air max', 'louis vuitton', 'amiri',"gucci", "louis vuitton", "chanel", "prada", "versace", "dior", "balenciaga", "fendi", "burberry", "givenchy", "valentino", "dolce & gabbana", "alexander mcqueen", "calvin klein", "ralph lauren", "tommy hilfiger", "michael kors", "coach", "marc jacobs", "kate spade", "yves saint laurent (ysl)", "hermes", "balmain", "celine", "off-white", "bottega veneta", "zara", "h&m", "mango", "topshop", "gap", "levi's", "diesel", "armani", "hugo boss", "lacoste", "puma", "nike", "adidas", "reebok", "converse", "new balance", "vans", "timberland", "dr. martens", "ugg", "north face", "patagonia", "columbia", "under armour", "champion", "supreme", "off-white", "bape", "vetements", "officine generale", "acne studios", "alexachung", "amiri", "nina ricci", "vivienne westwood", "isabel marant", "comme des garcons", "gareth pugh", "rick owens", "marni", "stella mccartney", "bally", "lanvin", "comme des garcons play", "comme des garcons shirt", "kenzo", "celine", "givenchy", "rick owens drkshdw", "maison margiela", "amiri", "palm angels", "fear of god", "rothco", "stone island", "neil barrett", "r13", "undercover", "junya watanabe", "kolor", "maison margiela", "issey miyake", "jil sander", "comme des garcons homme", "comme des garcons homme plus", "number (n)ine", "huf", "palace", "billionaire boys club", "a bathing ape", "supreme", "off-white"})


    
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
        return sorted(items_to_display,key=lambda item:item['reviews'], reverse=True)
    
    def get_all_items(self,search_text):
        if search_text == 'All':
            db_items = self.ref.get() 
            items_list = list(db_items.values())
            sorted_items = self.sort_by_reviews(items_list)
            return sorted_items
        return None


    def sort_search(self,search_text:str):
        search_all = self.get_all_items(search_text)
        if search_all:
            return search_all
        
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
    
    def home_page_top_items(self):
        data = self.ref.get()
        sorted = self.sort_by_reviews((list(data.values())))
        return sorted[:4]


    def brand_quick_search(self):
        """
        make list of dicts sorted by top brand in count in db e.g jordan:32 nike:21 yeezy:11...
        """
        data = self.ref.get()
        brands_dict = {brand:0 for brand in self.sneaker_brands}
        for values in data.values():
            item_brands = values.get('brand',None)
            if item_brands:
                for brand in item_brands:  
                    if brand in brands_dict:
                        brands_dict[brand]+=1

        sorted_brands_dict = [brand for brand, value in sorted(brands_dict.items(), key=lambda item: item[1],reverse=True) if value > 0]
    
        return sorted_brands_dict[:5]



    def search_runner(self,search_text:str):
        if len(search_text) > 30 or len(search_text) < 1:
            return None
        return self.sort_search(search_text)
    

