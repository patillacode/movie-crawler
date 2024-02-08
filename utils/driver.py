from selenium import webdriver


def get_driver(headless):
    """
    Get a webdriver. Use Firefox if headless mode is enabled, otherwise use Chrome.

    Parameters:
    headless (bool): Whether to run the browser in headless mode.

    Returns:
    webdriver: The webdriver.
    """
    if headless:
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference("intl.accept_languages", "es")

        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")

        options.set_capability("pageLoadStrategy", "eager")
        options.profile = firefox_profile

        return webdriver.Firefox(options=options)

    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {"intl.accept_languages": "es_ES"})
    options.set_capability("pageLoadStrategy", "eager")
    return webdriver.Chrome(options=options)
