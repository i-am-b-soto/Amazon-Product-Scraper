from selenium.webdriver.chrome.options import Options


def custom_options():
    options = Options()
    options.add_argument("--disable-gpu")  # Safe in most headless environments
    options.add_argument("--window-size=1880,800")  # Explicit viewport size
    options.add_argument("--no-sandbox")  # Required by some container environments
    options.add_argument("--disable-dev-shm-usage")  # Prevents crashes in containers
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36")
    return options