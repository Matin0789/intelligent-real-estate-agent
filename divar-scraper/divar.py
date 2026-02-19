from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

def scrape_and_save_data(driver):
    # 1. Locate elements using their class names
    # Note: For multiple classes, CSS Selector (dots) is more reliable than CLASS_NAME
    info_elements = driver.find_elements(By.CSS_SELECTOR, ".kt-group-row-item.kt-group-row-item__value.kt-group-row-item--info-row")
    unexpandable_elements = driver.find_elements(By.CLASS_NAME, "kt-unexpandable-row__value")

    # 2. Extract text and clean whitespace
    scraped_data = {
        "info_rows": [el.text.strip() for el in info_elements if el.text],
        "unexpandable_rows": [el.text.strip() for el in unexpandable_elements if el.text]
    }

    # 3. Save the data to a JSON file
    # 'ensure_ascii=False' allows Persian/UTF-8 characters to remain readable
    with open('page_data.json', 'a', encoding='utf-8') as json_file:
        json.dump(scraped_data, json_file, ensure_ascii=False, indent=4)

    print("Data successfully saved to page_data.json")

def professional_divar_crawler():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 10)

    try:
        # driver.get("https://divar.ir/s/tehran/real-estate")
        driver.get("https://divar.ir/s/tehran/real-estate/west-tehran-pars?districts=109%2C947&map_bbox=51.107464%2C35.536393%2C51.636307%2C35.896227&map_place_hash=1%7C%7Creal-estate")
        target_class = "content-dd848"
        
        # Initial wait to ensure the sidebar is loaded
        sidebar = wait.until(EC.presence_of_element_located((By.CLASS_NAME, target_class)))
        
        visited_links = set()
        retry_count = 0
        max_retries = 5 # As you requested

        while retry_count < max_retries:
            # 1. Get all links currently visible in the sidebar
            current_elements = sidebar.find_elements(By.CSS_SELECTOR, "a[href*='/v/']")
            current_links = [el.get_attribute("href") for el in current_elements]
            
            # 2. Filter only new links that we haven't entered yet
            new_links = [link for link in current_links if link not in visited_links]
            
            if new_links:
                # RESET retry count because we found data
                retry_count = 0 
                
                for url in new_links:
                    print(f"Processing Ad: {url}")
                    
                    # Enter the ad
                    driver.get(url)
                    time.sleep(2) # Wait to 'see' the ad

                    scrape_and_save_data(driver)
                    
                    # Exit (Go Back)
                    driver.back()
                    
                    # Add to visited list
                    visited_links.add(url)
                    
                    # Wait for sidebar to stabilize and re-locate it
                    time.sleep(2)
                    sidebar = wait.until(EC.presence_of_element_located((By.CLASS_NAME, target_class)))
            
            else:
                # NO NEW LINKS FOUND -> Start Scrolling and Counting Retries
                retry_count += 1
                print(f"No new links found. Scroll attempt {retry_count}/{max_retries}...")
                
                # Perform Scroll on the specific sidebar
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", sidebar)
                
                # Wait enough time for the page to load new data
                time.sleep(4) # Increased wait time for better stability
                
                # Re-locate sidebar to check again in the next loop
                sidebar = driver.find_element(By.CLASS_NAME, target_class)

        print(f"Finished. Could not find new links after {max_retries} consecutive scrolls.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    professional_divar_crawler()