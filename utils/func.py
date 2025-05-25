# utils/func.py

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from tabulate import tabulate
from termcolor import cprint
from time import sleep
from utils.dict_maker import IPODict


class MeroShareBot:
    def __init__(self, headless=True):
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920x1080')
        options.add_argument("--start-maximized")
        options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
        )

        if headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-software-rasterizer')

        self.driver = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 30)

    def login(self, dp, username, password):
        self.driver.get("https://meroshare.cdsc.com.np/#/login")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "app-login")))

        self.wait.until(EC.presence_of_element_located((By.NAME, "selectBranch")))
        self.driver.find_element(By.NAME, "selectBranch").click()

        dp_entry = self.driver.find_element(By.CLASS_NAME, "select2-search__field")
        dp_entry.click()
        dp_entry.send_keys(dp)
        dp_entry.send_keys(Keys.ENTER)

        self.driver.find_element(By.NAME, "username").send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)

        sleep(1)
        self.driver.find_element(By.CLASS_NAME, "sign-in").click()

    def goto_asba(self):
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "app-dashboard")))
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='sideBar']/nav/ul/li[8]/a/span")))
        self.driver.find_element(By.XPATH, "//*[@id='sideBar']/nav/ul/li[8]/a/span").click()
        self.wait.until(EC.url_to_be("https://meroshare.cdsc.com.np/#/asba"))

    def open_ipo_lister(self):
        self.driver.find_element(By.XPATH, '//*[@id="main"]/div/app-asba/div/div[1]/div/div/ul/li[1]').click()
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "app-applicable-issue")))
        self.driver.implicitly_wait(10)

        ipo_list = self.driver.find_elements(By.CLASS_NAME, "company-name")
        cprint(f"Total number of open IPO shares: {len(ipo_list)}", "green")

        data = IPODict(ipo_list)
        col_names = ["Option", "Name of Company", "Type of Issue"]
        cprint("IPO List Fetched Successfully! Showing all results!", "green")
        cprint(tabulate(data, headers=col_names, tablefmt="grid"), "green")

    def ipo_selector(self, ind=""):
        if ind == "":
            ind = int(input("Enter the code of the respective IPO you want to apply for: "))
        if ind == 0:
            iposelector_index = ""
        else:
            iposelector_index = f"[{ind}]"

        apply_btn = self.driver.find_element(
            By.XPATH,
            f'//*[@id="main"]/div/app-asba/div/div[2]/app-applicable-issue/div/div/div/div/div{iposelector_index}/div/div[2]/div/div[4]/button'
        )
        apply_btn.click()
        cprint("IPO Selected Successfully", "green")

    def apply_ipo(self, kitta, crn, txn_pin):
        self.wait.until_not(EC.url_to_be("https://meroshare.cdsc.com.np/#/asba"))

        bank_dropdown = Select(self.driver.find_element(By.NAME, "selectBank"))
        bank_list = bank_dropdown.options

        if len(bank_list) > 2:
            cprint("\nMultiple bank accounts detected. Please select one to continue...", "red")
            banks = [[i, b.text] for i, b in enumerate(bank_list[1:], start=1)]
            cprint(tabulate(banks, headers=["Option", "Bank Name"], tablefmt="grid"), "green")
            selected = int(input("Select the respective option to continue:"))
            self.driver.find_element(By.XPATH, f"//*[@id='selectBank']/option[{selected}]").click()
        else:
            self.driver.find_element(By.XPATH, "//*[@id='selectBank']/option[2]").click()
        sleep(1)
        self.wait.until(EC.presence_of_element_located((By.NAME, "accountNumber")))
        account_dropdown = Select(self.driver.find_element(By.NAME, "accountNumber"))
        if len(account_dropdown.options) > 1:
            account_dropdown.select_by_index(1)  # Selects second option (index 1)
        else:
         raise Exception("Account number dropdown has no selectable options.")
        self.driver.find_element(By.NAME, "appliedKitta").send_keys(kitta)
        self.driver.find_element(By.NAME, "crnNumber").send_keys(crn)
        self.driver.find_element(By.NAME, "disclaimer").click()

        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Proceed')]"))).click()
        self.wait.until(EC.presence_of_element_located((By.NAME, "transactionPIN"))).send_keys(txn_pin)
        sleep(1)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Apply')]"))).click()

        msg = self.driver.find_element(By.CLASS_NAME, "toast-message").text
        cprint(msg, "green" if "successfully" in msg.lower() else "red")

    def quit_browser(self):
        self.driver.quit()
