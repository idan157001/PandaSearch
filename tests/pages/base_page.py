from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver

class Base_Page:
    def __init__(self,driver):
        self.driver = driver
    
    def wait_for_element(self,locator,timeout=10):
        return WebDriverWait(self.driver,timeout).until(
            EC.presence_of_element_located(locator)
        )
    def get_url(self):
        return self.driver.current_url