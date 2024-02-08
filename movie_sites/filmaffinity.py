import re
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

    # title is in the following format "xxxxx (zzzzzzzz)""
    # I need to separate xxxxx from (zzzzzzzz) with regex
    xxx = r"(.*) \((.*)\)"
    match = re.search(xxx, title)
    new_title = match.group(1)
    title_type = title.replace(f"{new_title} ", "")

    with open(f"{folder}/{new_title}.txt", "w") as file:
        file.write(f"{new_title.upper()} {title_type}\n")
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
            file.write(f"{genre} ")
        file.write("\n")
        file.write(".\n")
        file.write("Sinopsis\n")
        file.write(f"{sinopsis}\n")

    print(f"fichero creado en: {Path(f'{folder}').resolve()}/{new_title}.txt")


def decline_cookies(driver):
    try:
        cookies_prompt = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="qc-cmp2-ui"]/div[2]/div/button[3]/span')
            )
        )
        cookies_prompt.click()
    except NoSuchElementException:
        print("The cookies prompt was not found.")


def extract_movie_id(url):
    # The regex pattern to match the movie_id in the URL.
    pattern = r"film(\d+)\.html"
    match = re.search(pattern, url)
    if match:
        # The movie_id is the first group in the match.
        return match.group(1)
    else:
        return None


def get_cast(driver, url):
    movie_id = extract_movie_id(url)
    print("movie_id: ", movie_id)
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(f"https://www.filmaffinity.com/es/fullcredits.php?movie_id={movie_id}")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="mt-content-cell"]/div[4]/div[1]')
        )
    )
    castbox = driver.find_element(By.XPATH, '//*[@id="mt-content-cell"]/div[4]/div[1]')
    cast = []
    for div in castbox.find_elements(By.CLASS_NAME, "credit-li"):
        actor = (
            div.find_element(By.CLASS_NAME, "credit-info")
            .find_element(By.CLASS_NAME, "name")
            .text
        )
        cast.append(actor)
        print(actor)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return cast


@retry(
    retry_on_exception=lambda err: isinstance(
        err, (NoSuchElementException, WebDriverException)
    ),
    stop_max_attempt_number=3,
    wait_fixed=2000,
)
def filmaffinity(headless, url, folder):
    try:
        with get_driver(headless) as driver:
            print("getting page at url: ", url)
            driver.get(url)
            decline_cookies(driver)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )

            title = driver.find_element(By.XPATH, '//*[@id="main-title"]/span').text
            print(f"título: {title}")

            original_title = driver.find_element(
                By.XPATH,
                '//*[@id="left-column"]/dl[1]/dd[1]',
            ).text
            print(f"título original: {original_title}")

            year = driver.find_element(
                By.XPATH,
                ('//*[@id="left-column"]/dl[1]/dd[2]'),
            ).text
            print(f"año: {year}")

            director = driver.find_element(
                By.XPATH,
                ('//*[@id="left-column"]/dl[1]/dd[5]/div'),
            ).text
            print(f"director: {director}")

            writer = driver.find_element(
                By.XPATH,
                ('//*[@id="left-column"]/dl[1]/dd[6]/div'),
            ).text
            print(f"guión: {writer}")

            print("reparto:")
            cast = get_cast(driver, url)

            chips = driver.find_element(
                By.CLASS_NAME,
                ("card-genres"),
            )
            print("género:")
            genres = []
            for chip in chips.find_elements(By.TAG_NAME, "span"):
                genres.append(chip.text)
                print(chip.text)

            try:
                print("sinopsis:")
                sinopsis = driver.find_element(
                    By.XPATH,
                    ('//*[@id="left-column"]/dl[1]/dd[13]'),
                ).text.replace("(FILMAFFINITY)", "")
                print(sinopsis)
            except NoSuchElementException:
                print("The sinopsis was not found.")
                sinopsis = ""

            write_to_file(
                original_title,
                title,
                year,
                director,
                writer,
                cast,
                genres,
                sinopsis,
                f"{folder}/filmaffinity",
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
