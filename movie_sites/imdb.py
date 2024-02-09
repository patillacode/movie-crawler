import traceback

from pathlib import Path

from retrying import retry
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.driver import get_driver


def write_to_file(
    original_title, title, year, director, writer, cast, genres, sinopsis, folder
):
    print("creando fichero ...")
    Path(f"{folder}").mkdir(parents=True, exist_ok=True)

    with open(f"{folder}/{title}.txt", "w") as file:
        file.write(f"{title.upper()}\n")
        file.write(f"{original_title}\n")
        file.write(".\n")
        file.write(f"{year}\n")
        file.write(".\n")
        file.write("Dirección\n")
        file.write(f"{director}\n")
        file.write(".\n")
        file.write("Guión\n")
        file.write(f"{writer}\n")
        file.write(".\n")
        file.write("Reparto\n")
        for member in cast:
            file.write(f"{member}, ")
        file.write("\n")
        file.write(".\n")
        file.write("Género\n")
        for genre in genres:
            file.write(f"{genre}, ")
        file.write("\n")
        file.write(".\n")
        file.write("Sinopsis\n")
        file.write(f"{sinopsis}\n")

    print(f"fichero creado en: {Path(f'{folder}').resolve()}/{title}.txt")


def decline_cookies(driver):
    try:
        cookies_prompt = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[2]/div/div/div[2]/div/button[1]")
            )
        )
        cookies_prompt.click()
    except NoSuchElementException:
        print("The cookies prompt was not found.")


@retry(
    retry_on_exception=lambda err: isinstance(
        err, (NoSuchElementException, WebDriverException)
    ),
    stop_max_attempt_number=3,
    wait_fixed=2000,
)
def imdb(headless, url, folder):
    try:
        with get_driver(headless) as driver:
            print("getting page at url: ", url)
            driver.get(url)
            decline_cookies(driver)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )

            title = driver.find_element(By.CLASS_NAME, "hero__primary-text").text
            print(f"título: {title}")

            try:
                original_title = driver.find_element(
                    By.XPATH,
                    "/html/body/div[2]/main/div/section[1]/section/div[3]/section/"
                    "section/div[2]/div[1]/div",
                ).text
                print(f"título original: {original_title}")

            except NoSuchElementException:
                print("The original title was not found.")
                original_title = ""

            year = driver.find_element(
                By.XPATH,
                (
                    '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/'
                    "section/div[2]/div[1]/ul/li[1]/a"
                ),
            ).text
            print(f"año: {year}")

            director = driver.find_element(
                By.XPATH,
                (
                    '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/'
                    "section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[1]/div/ul/li/a"
                ),
            ).text
            print(f"director: {director}")

            writer = driver.find_element(
                By.XPATH,
                (
                    '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/'
                    "section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[2]/div/ul/li/a"
                ),
            ).text
            print(f"guión: {writer}")

            castbox = driver.find_element(
                By.XPATH,
                '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section'
                "/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[3]/div/ul",
            )
            print("reparto:")
            cast = []
            # get the children of the castbox which is a ul
            # get the li within the ul
            for li in castbox.find_elements(By.TAG_NAME, "li"):
                cast.append(li.text)
                print(li.text)

            chips = driver.find_element(
                By.XPATH,
                (
                    '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/'
                    "section/div[3]/div[2]/div[1]/section/div[1]/div[2]"
                ),
            )
            print("género:")
            genres = []
            for chip in chips.find_elements(By.TAG_NAME, "a"):
                genres.append(chip.text)
                print(chip.text)

            print("sinopsis:")
            sinopsis = driver.find_element(
                By.XPATH,
                (
                    '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/'
                    "section/div[3]/div[2]/div[1]/section/p"
                ),
            ).text
            print(sinopsis)
            write_to_file(
                original_title,
                title,
                year,
                director,
                writer,
                cast,
                genres,
                sinopsis,
                folder,
            )

    except NoSuchElementException as err:
        error_message = (
            f"{traceback.format_exc()}\nURL: {url}. An element was not found on the page."
        )
        print(error_message)
        raise err
    except TimeoutException as err:
        error_message = f"{traceback.format_exc()}\nURL: {url}. The operation timed out."
        print(error_message)
        raise err
    except WebDriverException as err:
        error_message = (
            f"{traceback.format_exc()}\nURL: {url}. "
            "A WebDriver exception occurred: {err}."
        )
        print(error_message)
        raise err
