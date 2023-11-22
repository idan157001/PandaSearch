from .base_page import Base_Page
from locators.home_locators import Home_Page_Locators
from selenium.webdriver.common.by import By

class HomePage(Base_Page):
    locators = Home_Page_Locators
    
    def search_for_product(self,product_name):
        search_bar = self.wait_for_element(self.locators.SEARCH_BAR)
        search_bar.send_keys(product_name)
        
        search_button = self.wait_for_element(self.locators.SEARCH_BUTTON)
        search_button.click()

    def clear_search_bar(self):
        search_bar = self.wait_for_element(self.locators.SEARCH_BAR)
        search_bar.clear()
    
    def success_result(self):
        return self.wait_for_element(self.locators.SEARCH_RESULT)
    
    def fail_result(self):
        return self.wait_for_element(self.locators.ERROR_SEARCH_RESULT)
