from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class DarazScraperStrict:

    def __init__(self, driver):
        self.driver = driver
        self.base_url = "https://www.daraz.com.np/catalog/?&q={}&page={}"

    def smooth_scroll(self, step=400):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            for i in range(0, last_height, step):
                self.driver.execute_script(f"window.scrollTo(0, {i});")
                time.sleep(0.3)

            time.sleep(1)
            new_height = self.driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                break

            last_height = new_height

    def open_page(self, keyword, page_no):
        url = self.base_url.format(keyword, page_no)
        self.driver.get(url)

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ICdUp"))
        )

    def get_all_item_links(self):
        """Extract ALL product links from .ICdUp using elements (not element)."""

        container = self.driver.find_elements(By.CSS_SELECTOR, ".ICdUp")

        links = []
        for items_div in container:
            a = items_div.find_element(By.TAG_NAME, "a")
            link = a.get_attribute("href")
            if link and "daraz.com.np/products" in link:
                links.append(link)

        return list(set(links))  # unique

    def scrape_item(self, url):
        """Scrape one product page using your EXACT logic."""
        self.driver.get(url)
        self.smooth_scroll()

        title = self.driver.find_element(By.CSS_SELECTOR, ".pdp-mod-product-badge-title").text

        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".score"))
        )
        score = self.driver.find_element(By.CSS_SELECTOR, ".score").text
        count = self.driver.find_element(By.CSS_SELECTOR, ".count").text
        price = self.driver.find_element(By.CSS_SELECTOR, ".pdp-product-price").text

        # print(price)
        rating = score.split("/")[0]
        total_ratings = count.split(" ")[0]

        if "%" in price:
            percent_discount = int(price.split("-")[1].replace("%", ""))
            price_before_discount = int(price.split("\n")[1].split("Rs. ")[1]
                                          .split("-")[0].replace(",", ""))
            
        else :
            percent_discount = 0
            price_before_discount= int(price.split("Rs. ")[1].replace(",",""))

        price_after_discount = int(price_before_discount - price_before_discount * percent_discount / 100)
        description = self.driver.find_element(
            By.CSS_SELECTOR, ".html-content.pdp-product-highlights"
        ).text

        return {
            "title": title,
            "score": score,
            "count": count,
            "rating": rating,
            "total_ratings": total_ratings,
            "price_before_discount": price_before_discount,
            "price_after_discount": price_after_discount,
            "percent_discount": percent_discount,
            "description": description,
            "url": url
        }

    def scrape(self, keyword, pages=1):
        """Scrape N pages exactly using your original code behavior."""
        all_items = []

        for p in range(1, pages + 1):
            print(f"\n🔵 Page {p}")

            self.open_page(keyword, p)
            self.smooth_scroll()
            item_links = self.get_all_item_links()

            print(f"  Found {len(item_links)} items.")

            for link in item_links:
                try:
                    print(f"   Scraping: {link}")
                    info = self.scrape_item(link)
                    # print(self.scrape_item(link))
                    all_items.append(info)
                except Exception as e:
                    print(f"   ❌ Failed to scrape: {link}")
                    print(f"   Error type: {type(e).__name__}")
                    print(f"   Error message: {str(e)}")

        # return all_items
        import pandas as pd
        return pd.DataFrame(all_items)
