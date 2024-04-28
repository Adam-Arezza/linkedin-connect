import time
from configparser import ConfigParser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


config = ConfigParser()
config.read("settings.ini")
USERNAME = config["Login"]["user"]
PASSWORD = config["Login"]["password"]


def log_in(u,p,driver):
    print("Logging in...")
    try:
        url = "https://www.linkedin.com/login"
        driver.get(url)
        user = driver.find_element(By.ID, "username")
        password = driver.find_element(By.ID, "password")
        user.send_keys(u)
        password.send_keys(p)
        password.send_keys(Keys.RETURN)
        time.sleep(4)
        return True
    except Exception as e:
        print(f"There was an error: {e}")
        driver.quit()
        return False


def make_connection_requests(connect_list, wait): 
    print(f"Found: {len(connect_list)} possible connections")
    for item in connect_list:
        try:
            div = item.find_element(By.CLASS_NAME, 'entity-result__actions')
            if div.text == "Connect":
                button = div.find_element(By.TAG_NAME, 'button')
                button.click()
                time.sleep(2)
                send_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Send now']")))
                send_btn.click()
                global total_connections
                total_connections -= 1
                if total_connections == 0:
                    return
        except:
            print("couldn't find results")


#searches for the specific people with filters
def search_people(query, driver):
    wait = WebDriverWait(driver, 20)
    search_box = driver.find_element(By.XPATH,"//input[contains(@aria-label, 'Search')]")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    people_filter = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='People']")))
    people_filter.click()
    time.sleep(3)

    location_filter = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="searchFilter_geoUrn"]')))
    location_filter.click()
    time.sleep(3)

    #TODO use country from settings file to find country in the list instead of xpath
    country_filter = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div[3]/div[2]/section/div/nav/div/ul/li[5]/div/div/div/div[1]/div/form/fieldset/div[1]/ul/li[1]/label/p/span[1]')))
    country_filter.click()
    time.sleep(3)

    show_results = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div[3]/div[2]/section/div/nav/div/ul/li[5]/div/div/div/div[1]/div/form/fieldset/div[2]/button[last()]')))
    show_results.click()
    time.sleep(3)
    page_number = 1
    while total_connections > 0:
        connect_list = driver.find_elements(By.CLASS_NAME, 'reusable-search__result-container')
        make_connection_requests(connect_list, wait)
        print(f"Connections remaining: {total_connections}")
        if total_connections == 0:
            return
        print(f"Going to next page, page: {page_number+1}")
        driver.get(f'https://www.linkedin.com/search/results/people/?geoUrn=%5B%22101174742%22%5D&keywords=technical%20recruiter&page={page_number+1}')
        page_number += 1


def main():
    print("Enter the search terms for the people you want to connect with")
    print("Just type the terms with spaces in between")
    print("When done press the ENTER key")
    search_terms = input("Search terms: ")
    print(f"The search terms are: {search_terms}")
    print("How many connections should be made?")
    num_connections = input("Number of connections: ")
    try:
        global total_connections
        total_connections = int(num_connections)
        print(f"Will try to connect with: {total_connections}")
    except:
        print("Expected a number input, shutting down...")
        return

    captcha = False
    driver = webdriver.Firefox()  
    if not log_in(USERNAME, PASSWORD, driver):
        return
    if "https://www.linkedin.com/checkpoint/challenge/" in driver.current_url:
        print("Captcha detected, follow instructions")
        while not captcha:
           enter_pressed = input("Please solve the captcha on the screen to continue. Press ENTER key when done.")
           if enter_pressed == "":
               captcha = True
               break
    time.sleep(3)
    print("Entering search terms...")
    search_people(search_terms, driver)
    driver.quit()


if __name__ == "__main__":
    main()
    exit()
