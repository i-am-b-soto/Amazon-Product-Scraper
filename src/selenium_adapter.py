#import undetected_chromedriver as uc --> This is not thread safe as it modifies a binary file in a specific directory
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver


import random

# Optional: List of real-world user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
]


def get_random_user_agent():
    return random.choice(USER_AGENTS)


def custom_options():
    """
    
    """
    options = Options()
    user_agent = get_random_user_agent()
    options.add_argument('--headless=new')
    options.add_argument("--disable-gpu")  # Safe in most headless environments
    options.add_argument("--window-size=1880,800")  # Explicit viewport size
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")  # Required by some container environments
    options.add_argument("--disable-dev-shm-usage")  # Prevents crashes in containers
    #options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36")
    options.add_argument("--user-agent={}".format(user_agent))
    # TODO: Add option for proxy server
    return options


def get_driver():
    """
        Return a selenium web driver
    """
    #service = Service("/usr/bin/google-chrome")
    options = custom_options()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver