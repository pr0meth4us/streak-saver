from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import logging


class LoginService:
    """Secure login automation service."""

    @staticmethod
    def get_webdriver():
        """Create a secure, managed WebDriver instance."""
        try:
            service = Service(ChromeDriverManager().install())
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            return webdriver.Chrome(service=service, options=options)
        except Exception as e:
            logging.error(f"WebDriver initialization failed: {e}")
            raise

    @classmethod
    def login_to_tiktok(cls, username, password):
        """Automated login to TikTok with robust error handling."""
        driver = None
        try:
            driver = cls.get_webdriver()
            driver.get("https://www.tiktok.com/login")
            driver.implicitly_wait(10)  # More robust waiting

            # Flexible login method detection
            login_methods = {
                'email': "//button[contains(text(), 'Email')]",
                'phone': "//button[contains(text(), 'Phone')]"
            }

            # Dynamic login method selection
            login_type = 'email' if '@' in username else 'phone'
            tab = driver.find_element(By.XPATH, login_methods.get(login_type))
            tab.click()

            # Input credentials
            input_locator = By.NAME
            input_field = driver.find_element(input_locator, login_type)
            input_field.send_keys(username)

            password_field = driver.find_element(By.NAME, "password")
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)

            # Wait and verify login
            driver.implicitly_wait(15)
            return driver.current_url != "https://www.tiktok.com/login"

        except Exception as e:
            logging.error(f"TikTok login failed: {e}")
            return False
        finally:
            if driver:
                driver.quit()
