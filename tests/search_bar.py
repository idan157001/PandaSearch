import unittest
from selenium import webdriver
from pages.home_page import HomePage

class Test_Search_bar(unittest.TestCase):

    def setUp(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-logging")
        self.driver = webdriver.Chrome(options=chrome_options)
        
        self.base_url = "https://pandasearch.onrender.com/"
        self.driver.get(self.base_url)

    def test_search_bar_query_success(self):
        success_words = ['nike','aIr','BlacK','Yeezy']
        home_page = HomePage(self.driver)

        for word in success_words:
            with self.subTest(word):
                home_page.search_for_product(word)
                
                self.assertTrue(home_page.success_result().is_displayed(),'No Results')
                self.assertEqual(home_page.get_url(),f"https://pandasearch.onrender.com/?q={word}")

                home_page.clear_search_bar()

            self.driver.get(self.base_url)

    def test_search_bar_query_fail(self):
        fail_words = ['fafeag','FmioFEA5','Kopw','ALWRlf']
        home_page = HomePage(self.driver)

        for word in fail_words:
            with self.subTest(word):
                home_page.search_for_product(word)
                
                self.assertTrue(home_page.fail_result().is_displayed(),'Error Message Not Found')
                self.assertEqual(home_page.get_url(),f"https://pandasearch.onrender.com/?q={word}")
                
                home_page.clear_search_bar()

            self.driver.get(self.base_url)

    def tearDown(self):
        self.driver.close()