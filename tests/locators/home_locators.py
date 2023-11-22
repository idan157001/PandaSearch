from selenium.webdriver.common.by import By
class Home_Page_Locators:
    SEARCH_BAR = (By.ID,'search') # search bar 
    SEARCH_BUTTON = (By.ID,'submit_search') # submit bar 
    ###
    SEARCH_RESULT = (By.ID,'product_containers') # success result 
    ERROR_SEARCH_RESULT = (By.ID,'error_message') # error result message 
