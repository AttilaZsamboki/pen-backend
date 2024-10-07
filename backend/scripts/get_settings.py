from ..utils.logs import log  # noqa
import re
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions

from ..models import SystemSettings, Systems


class SaveSetting:
    def __init__(self, driver, label: str, system: Systems, type: str):
        self.driver = driver
        self.label = label
        self.system = system
        self.type = type

    def main(self):
        return SystemSettings(
            label=self.label,
            value=self.get_value(),
            system=self.system,
            type=self.type,
        ).save()

    def get_value(self):
        match self.type:
            case "CategoryId":
                return self.get_category_id()
            case "StatusId":
                return self.get_status_id()

    def get_status_id(self):
        return re.search(r"StatusId=(\d+)", self.driver.current_url).group(1)

    def get_category_id(self):
        return re.search(r"#Project-(\d+)", self.driver.current_url).group(1)


def get_your_element(driver, x, retries=3):
    ignored_exceptions = (
        NoSuchElementException,
        StaleElementReferenceException,
    )
    for attempt in range(retries):
        try:
            your_element = WebDriverWait(
                driver, 10, ignored_exceptions=ignored_exceptions
            )
            return your_element.until(
                expected_conditions.presence_of_element_located(x)
            )
        except TimeoutException:
            if attempt < retries - 1:
                time.sleep(2)  # Wait before retrying
                continue
            else:
                raise


def get_status_ids(driver, system: Systems):
    def save(label: str):
        SaveSetting(driver, label, system, "StatusId").main()

    visited = set()
    visited.add("Lomtár")
    while True:
        elements = driver.find_elements(
            By.CLASS_NAME, "SidebarFilter_xH3uKe6RhokUwHLg1mxF"
        )
        if len(elements) == len(visited):
            break
        element = [element for element in elements if element.text not in visited][0]

        inner_text = element.text
        element.click()
        time.sleep(5)
        save(inner_text)
        visited.add(inner_text)


def get_category_ids(driver, system: Systems):
    modules = ["Felmérés", "Ajánlat", "Megrendelés"]
    for module in modules:
        driver.find_element(By.PARTIAL_LINK_TEXT, module).click()
        SystemSettings(
            label="Felmérés",
            value=re.search(r"#Project-(\d+)", driver.current_url).group(1),
            system=system,
            type="CategoryId",
        ).save()
        time.sleep(5)
        get_status_ids(driver, system)


def login(system: Systems):
    driver = webdriver.Chrome()

    driver.get("https://r3.minicrm.hu/")

    email = driver.find_element(By.ID, "Email")
    email.send_keys(system.email)

    text_field = driver.find_element(By.ID, "Password")
    text_field.send_keys(system.password)

    text_field.find_element(
        By.XPATH, '//*[@id="Content"]/div/div[1]/form/div[4]/input'
    ).click()
    time.sleep(5)
    return driver


def main(system: Systems):
    driver = login(system)
    system_id = re.search(r"https://r3\.minicrm\.hu/(\d+)/", driver.current_url).group(
        1
    )
    Systems.objects.filter(id=system.id).update(system_id=system_id)

    system.system_id = system_id
    get_category_ids(driver, system)
    driver.quit()


if __name__ == "__main__":
    for i in Systems.objects.filter(email__isnull=False, password__isnull=False):
        main(i)
        break
