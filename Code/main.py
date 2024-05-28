from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


class MercadoLivreBot:
    def __init__(self, url, product_name):
        self.url = url
        self.product_name = product_name
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service)
        self.titles = []
        self.prices = []
        self.links = []

    def wait_for_object_to_appear(self, timeout, xpath):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return True
        except Exception as e:
            print(f"Error while waiting for object to appear: {e}")
            return False

    def website_access(self):
        self.driver.maximize_window()
        xpath_to_find = "//input[@class='nav-search-input']"
        self.driver.get(self.url)
        return self.wait_for_object_to_appear(20, xpath_to_find)

    def search_product(self):
        xpath_search = "//input[@class='nav-search-input']"
        try:
            if self.website_access():
                input_bar = self.driver.find_element(By.XPATH, xpath_search)
                input_bar.send_keys(self.product_name + Keys.ENTER)
                xpath_results = "//ol[@class='ui-search-layout ui-search-layout--grid']"
                if not self.wait_for_object_to_appear(20, xpath_results):
                    print(f"Could not find search results for {self.product_name}")
                    self.close_connection()
            else:
                print(f"Could not access the website")
                self.close_connection()
        except Exception as e:
            print(f"Error during product search: {e}")
            self.close_connection()

    def extract_data_from_website(self):
        xpath_to_find = "//ol[@class='ui-search-layout ui-search-layout--grid']"
        container_xpath_title = "//a[@class='ui-search-item__group__element ui-search-link__title-card ui-search-link']"
        container_xpath_price = ("//div[@class='ui-search-item__group ui-search-item__group--price ui-search-item__group--"
                                 "price-grid-container']//div[@class='ui-search-price__second-line']//span[@class='andes-money-"
                                 "amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript']")
        title_child = ".//h2"
        price_child = ".//span[@class='andes-money-amount__fraction']"
        try:
            if self.wait_for_object_to_appear(20, xpath_to_find):
                containers_title_and_link = self.driver.find_elements(By.XPATH, container_xpath_title)
                containers_price = self.driver.find_elements(By.XPATH, container_xpath_price)
                for title_and_link, price in zip(containers_title_and_link, containers_price):
                    title = title_and_link.find_element(By.XPATH, title_child).text
                    link = title_and_link.get_attribute("href")
                    price = price.find_element(By.XPATH, price_child).text
                    price = f"R${price}"

                    self.titles.append(title)
                    self.links.append(link)
                    self.prices.append(price)
        except Exception as e:
            print(f"Error during data extraction: {e}")
            self.close_connection()

    def create_csv_file(self):
        try:
            my_dict = {"Title": self.titles, "Price": self.prices, "Link": self.links}
            pd.DataFrame(my_dict).to_csv(r"C:\Users\Young1\Desktop\Selenium Course\mercado-livre-extraction\Data\DATA_EXTRACTED.csv", index=False)
        except Exception as e:
            print(f"Error while trying to create CSV file: {e}")
        finally:
            self.close_connection()

    def close_connection(self):
        self.driver.quit()

    def run(self):
        try:
            self.search_product()
            self.extract_data_from_website()
            self.create_csv_file()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.close_connection()

if __name__ == "__main__":
    url = "https://www.mercadolivre.com.br/"
    product_name = "Pc Gamer"
    robot = MercadoLivreBot(url=url, product_name=product_name)
    robot.run()
