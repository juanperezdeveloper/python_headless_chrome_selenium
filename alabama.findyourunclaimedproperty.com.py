import pandas
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

search_keyword = "David"

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/80.0.3987.132 Safari/537.36'

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--ignore-certificate-errors')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(f'user-agent={user_agent}')
options.headless = True

with webdriver.Chrome(options=options) as driver:
    driver.get("https://alabama.findyourunclaimedproperty.com/app/claim-search")
    wait = WebDriverWait(driver, 20)

    wait.until(EC.element_to_be_clickable((By.ID, "lastName"))).send_keys(search_keyword, Keys.ENTER)
    items_per_page = wait.until(EC.element_to_be_clickable((By.ID, 'itemsPerPage')))
    Select(items_per_page).select_by_value("80")

    columns = ["Property ID", "Owner Name", "Address", "City", "State", "ZIP Code",
               "Reporting Business Name", "Amount"]
    result = pandas.DataFrame(columns=columns)
    while True:
        rows = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR,
                                                                 "table.table tr[scope=row]:not([hidden])")))

        data = driver.execute_script("return [...document.querySelectorAll('[scope=row]:not([hidden])')].map(tr=>"
                                     "[...tr.querySelectorAll('.text-uppercase')].map(td=> td.textContent))")

        result = result.append(pandas.DataFrame(data, columns=columns)).reset_index(drop=True)

        next_page = driver.find_element_by_xpath(
            "//*[@id='topPropertySearchResultsPager']//li[./a[@aria-label='Next']]")
        if "disabled" in next_page.get_attribute("class"):
            break

        next_page.click()

result.to_csv(f"{search_keyword}_data.csv", index=False)
result.to_excel(f"{search_keyword}_data.xlsx", index=False)
