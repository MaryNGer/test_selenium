import os
import re

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

load_dotenv()


def is_valid(text: str) -> bool:
    """
    Функция проверяет, является ли строка IP-адресом или датой и временем.

    :param text: Строка для проверки.
    :return: True, если строка соответствует IP-адресу или дате и времени, иначе False.
    """

    combined_pattern = (
        r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$|"
        r"^\d{2}\.\d{2}\.\d{4}, \d{2}:\d{2}$"
    )
    return re.match(combined_pattern, text) is not None


def login(driver: webdriver.Chrome, _login: str, _password: str) -> bool:
    """
    Функция выполняет вход в систему.

    :param driver: Экземпляр веб-драйвера.
    :param _login: Логин для входа.
    :param _password: Пароль для входа.
    :raises WebDriverException: Если возникает ошибка при взаимодействии с веб-драйвером.
    :raises TimeoutException: Если превышено время ожидания изменения URL после входа.
    :return: True, если вход выполнен успешно, иначе False.
    """

    try:
        driver.find_element(By.LINK_TEXT, "Вход").click()
        driver.find_element(By.NAME, "email").send_keys(_login)
        driver.find_element(By.NAME, "password").send_keys(_password + Keys.ENTER)

        WebDriverWait(driver, 5).until(
            EC.url_changes(driver.current_url)
        )
        return True

    except TimeoutException:
        print(f"Ошибка авторизации '{login.__name__}': Неверный логин или пароль")
        return False

    except WebDriverException as ex:
        print(f"Ошибка в функции '{login.__name__}': {ex}")
        return False


def get_proxies(driver: webdriver.Chrome) -> None:
    """
    Функция переходит на страницу с прокси и вызывает функцию обработки таблицы.

    :param driver: Экземпляр веб-драйвера.
    :raises WebDriverException: Если переход на страницу 'Мои прокси'
    и вкладку IPv4 Shared Прокси не произошел за 10 секунд.
    :raises WebDriverException: Если возникает ошибка при взаимодействии с веб-драйвером.
    """

    try:

        driver.get("https://belurk.online/my-proxies/ipv4-shared")

        WebDriverWait(driver, 10).until(
            EC.url_to_be("https://belurk.online/my-proxies/ipv4-shared")
        )

        process_table(driver)

    except TimeoutException:
        print(f"Ошибка в функции '{get_proxies.__name__}':"
              f"Переход на страницу https://belurk.online/my-proxies/ipv4-shared не произошел за 10 секунд")

    except WebDriverException as ex:
        print(f"Ошибка в функции '{login.__name__}': {ex}")


def process_table(driver: webdriver.Chrome) -> None:
    """
    Функция обработчик таблицы с прокси.

    :param driver: Экземпляр веб-драйвера.
    :raises TimeoutException: Если таблица не найдена или не загружена в течение 10 секунд.
    :raises WebDriverException: Если возникает ошибка при взаимодействии с веб-драйвером.
    """

    try:
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//table//tbody"))
        )

        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            cells = row.find_elements(By.XPATH, ".//td")
            result = [cell.text for cell in cells if is_valid(cell.text)]
            print(" - ".join(result))

    except TimeoutException:
        print(f"Ошибка в функции '{process_table.__name__}':"
              f"Таблица не найдена или не загружена в течение 10 секунд")

    except WebDriverException as ex:
        print(f"Ошибка в функции '{login.__name__}': {ex}")


def setup_driver() -> webdriver.Chrome:
    """
    Настраивает и возвращает экземпляр веб-драйвера.

    :return: Экземпляр веб-драйвера.
    :raises WebDriverException: Если возникает ошибка при настройке веб-драйвера.
    """

    try:
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        # options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=options)

        driver.implicitly_wait(10)

        driver.get("https://belurk.online/")
        return driver

    except WebDriverException as ex:
        print(f"Ошибка в функции '{setup_driver.__name__}': {ex}")


def main() -> None:
    """
    Основная функция, выполняющая логику программы.

    :raises WebDriverException: Если возникает ошибка при выполнении основных операций.
    """

    _login = os.getenv("LOGIN")
    _password = os.getenv("PASSWORD")

    driver = setup_driver()

    try:
        if login(driver, _login, _password):

            get_proxies(driver)
        else:
            print("Авторизация не удалась. Проверьте логин и пароль.")

    except WebDriverException as ex:
        print(f"Ошибка в функции '{main.__name__}': {ex}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
