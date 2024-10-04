from ..utils.logs import log  # noqa
import re
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions

from ..models import Settings, Systems


def main(system: Systems):
    driver = webdriver.Chrome()

    driver.get("https://r3.minicrm.hu/")

    email = driver.find_element(By.ID, "Email")
    email.send_keys(system.email)

    text_field = driver.find_element(By.ID, "Password")
    text_field.send_keys(system.password)

    text_field.find_element(
        By.XPATH, '//*[@id="Content"]/div/div[1]/form/div[4]/input'
    ).click()
    system_id = re.search(r"https://r3\.minicrm\.hu/(\d+)/", driver.current_url).group(
        1
    )
    system.system_id = system_id
    system.save()

    time.sleep(5)

    ignored_exceptions = (
        NoSuchElementException,
        StaleElementReferenceException,
    )
    your_element = WebDriverWait(driver, 5, ignored_exceptions=ignored_exceptions)
    your_element.until(
        expected_conditions.presence_of_element_located((By.LINK_TEXT, "Felmérés"))
    ).click()
    time.sleep(5)
    Settings(
        label="Felmérés",
        value=re.search(r"#Project-(\d+)", driver.current_url).group(1),
        system=system,
        type="Category_Id",
    ).save()
    your_element.until(
        expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="Container"]/div/div/aside/div[2]')
        )
    ).click()
    time.sleep(5)
    Settings(
        label="Új érdeklődő",
        value=re.search(r"StatusId=(\d+)", driver.current_url).group(1),
        system=system,
        type="Status_Id",
    ).save()

    driver.quit()


if __name__ == "__main__":
    for i in Systems.objects.filter(
        system_id__isnull=True, email__isnull=False, password__isnull=False
    ):
        main(i)
