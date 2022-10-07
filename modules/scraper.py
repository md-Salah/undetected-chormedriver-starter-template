from modules.files import read_executable_path_info
from modules.proxy_plugin import proxy_plugin

import json
import zipfile
import os
from sys import exit
import pickle
import time
import getpass
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from multiprocessing import freeze_support
freeze_support()
import undetected_chromedriver as uc


class Scraper:

    wait_element_time = 3                           # The time we are waiting for element to get loaded in the html in each loop count
    cookies_folder = 'cookies' + os.path.sep        # In this folder we will save cookies from logged in users


    def __init__(self, url='', headless='', proxy='', reaction='exit', profile=''):
        settings = read_executable_path_info('inputs/settings.txt', '=')
        
        self.url = url
        self.browser_executable_path = settings['browser'] or None
        self.driver_executable_path = os.path.join(os.getcwd(), settings['driver']) if settings['driver'] else None
        self.headless = headless or (True if settings['headless'].lower() == 'true' else False)
        self.reaction = settings['reaction'] or reaction
        self.chrome_version = settings['chrome_version'] or None
        self.proxy = proxy or settings['proxy']
        
        self.setup_driver_options(self.headless, self.proxy, profile)
        self.setup_driver()

    # Automatically close driver on destruction of the object
    def __del__(self):
        pass

    # Add these options in order to make chrome driver appear as a human instead of detecting it as a bot
    def setup_driver_options(self, headless, proxy, profile):
        self.driver_options = uc.ChromeOptions()

        arguments = [
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
            '--start-maximized',
            # '--disable-blink-features=AutomationControlled',              # This will solve the driver.get(url) error & also selenium detection, chrome shows warning
            # '--disable-dev-shm-usage',                                    # May be required for headless chrome
            # '--no-sandbox',                                               # with sandbox, one tab cannot watch another tab
            '--disable-popup-blocking',                                     # Otherwise new tab will not be opened
            '--no-first-run --no-service-autorun --password-store=basic',   # just some options passing in to skip annoying popups
        ]
        
        if profile:
            arguments.append(f'--user-data-dir=c:\\temp\\{profile}')     # Saving user profile, It causes the error sometimes like 127.0.0 chrome not found

        # experimental_options = {
        #     'excludeSwitches': ['enable-automation', 'enable-logging'],
        #     'prefs': {
        #         'profile.default_content_setting_values.notifications': 2,

        #         
        #         'credentials_enable_service': False,          # Disable the save password popups
        #         'profile.password_manager_enabled': False
        #     }
        # }

        # for key, value in experimental_options.items():
        # 	self.driver_options.add_experimental_option(key, value)

        for argument in arguments:
            self.driver_options.add_argument(argument)

        if headless:
            self.driver_options.add_argument('--headless')

        if proxy:
            if len(proxy.split(':')) < 2:
                self.driver_options.add_argument(f'--proxy-server={proxy}')   # proxy=106.122.8.54:3128
            else:
                # Proxy with authentication
                pluginfolder = proxy_plugin(proxy)
                pluginfolder = os.path.join(os.getcwd(), pluginfolder)
                self.driver_options.add_argument(f'--load-extension={pluginfolder}')

    # Setup chrome driver with predefined options
    def setup_driver(self):

        self.driver = uc.Chrome(
            options=self.driver_options,
            driver_executable_path=self.driver_executable_path,
            browser_executable_path=self.browser_executable_path,
            version_main=self.chrome_version,
            use_subprocess = True
        )

    def print_executable_path(self):
        print('chrome browser path:', self.browser_executable_path)
        print('chromedriver path:', self.driver_executable_path)
        print('headless:', self.headless)
        print('Exit:', self.reaction)
        print('chrome version:', self.chrome_version)
        print('proxy:', self.proxy)
        
    # Add login functionality and load cookies if there are any with 'cookies_file_name'
    def add_login_functionality(self, is_logged_in_selector, loop_count=10, login_function=None, exit_on_login_failure=True, cookies_file_name='cookies'):
        # Three step Login. 1:Using cookies, 2:By Selenium UI automation, 3:Manual login Then press any key
        self.is_logged_in_selector = is_logged_in_selector
        self.cookies_file_name = cookies_file_name + '.pkl'
        self.cookies_file_path = self.cookies_folder + self.cookies_file_name
        self.login_status = self.is_logged_in(loop_count)

        # Step 1: Check if there is a cookie file saved
        if self.login_status == False:
            if self.is_cookie_file():
                self.load_cookies()		# Load cookies
                # Check if user is logged in after adding the cookies
                self.login_status = self.is_logged_in(loop_count)

        # Step 2: Call the login method for Selenium UI interaction login
        if self.login_status == False:
            if login_function:
                login_function()
                self.login_status = self.is_logged_in(loop_count)  # Check if user is logged in

        # Step 3: Manual Login
        if self.login_status == False:
            input('Login manually, Then press ENTER...')
            self.sleep(1.0, 3.0)
            self.login_status = self.is_logged_in(loop_count)  # Check if user is logged in

        if self.login_status == True:
            self.save_cookies()		# User is logged in. So, save the cookies
        elif exit_on_login_failure == True:
            self.handle_exception(reason='Sorry, We are failed to be logged In.', reaction='exit')

        return self.login_status

    # Check if cookie file exists
    def is_cookie_file(self):
        return os.path.exists(self.cookies_file_path)

    # Load cookies from file
    def load_cookies(self):
        # Load cookies from the file
        cookies_file = open(self.cookies_file_path, 'rb')
        cookies = pickle.load(cookies_file)

        for cookie in cookies:
            self.driver.add_cookie(cookie)

        cookies_file.close()

        self.go_to_page(self.url)

        time.sleep(5)

    # Save cookies to file
    def save_cookies(self):
        # Do not save cookies if there is no cookies_file name
        if not hasattr(self, 'cookies_file_path'):
            return

        # Create folder for cookies if there is no folder in the project
        if not os.path.exists(self.cookies_folder):
            os.mkdir(self.cookies_folder)

        # Open or create cookies file
        cookies_file = open(self.cookies_file_path, 'wb')

        # Get current cookies from the driver
        cookies = self.driver.get_cookies()

        # Save cookies in the cookie file as a byte stream
        pickle.dump(cookies, cookies_file)

        cookies_file.close()

    # Check if user is logged in based on a html element that is visible only for logged in users
    def is_logged_in(self, loop_count=3):
        element = self.find_element(
            self.is_logged_in_selector, loop_count=loop_count, reaction='pause', wait_element_time=3)
        return True if element else False

    # Wait random amount of seconds before taking some action so the server won't be able to tell if you are a bot
    def sleep(self, a=0.5, b=None, implicit=False):
        if b == None:
            random_sleep_seconds = a
        else:
            random_sleep_seconds = round(random.uniform(a, b), 2)

        if implicit:
            self.driver.implicitly_wait(random_sleep_seconds)
        else:
            time.sleep(random_sleep_seconds)

    # Goes to a given page and waits random time before that to prevent detection as a bot
    def go_to_page(self, url):
        self.sleep()
        self.driver.get(url)

    def handle_exception(self, reason, reaction=None):  # Utility function handles exit on missing element behavior
        reaction = reaction or self.reaction    #Default action (exit)
        
        if reaction == 'exit':
            raise Exception(reason)
        elif reaction == 'warning':
            print(reason) # Warning and Ignore the error
        elif reaction == 'pause':
            input(reason) # Pause the execution
        elif reaction == 'ignore':
            pass
        else:
            raise Exception('Reaction type is not correct')

    def find_element(self, css_selector='', xpath='', ref_element=None, loop_count=1, reaction='exit', wait_element_time=None):

        element, error = None, ''
        wait_element_time = wait_element_time or self.wait_element_time
        driver = ref_element or self.driver

        # Intialize the condition to wait
        if css_selector:
            wait_until = EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector))
        elif xpath:
            wait_until = EC.visibility_of_element_located((By.XPATH, xpath))
        else:
            self.handle_exception(reason='ERROR: CSS_SELECTOR | XPATH is required to find element', reaction='exit')

        i = 1
        while True:
            try:
                element = WebDriverWait(driver, wait_element_time).until(wait_until)
            except TimeoutException:
                pass
            except Exception as e:
                error = e
            
            if i == loop_count or element:
                break
            else:
                i += 1
                time.sleep(1)

        if element:
            return element
        else:
            self.handle_exception(reason=f'ERROR: Timed out waiting for the element with selector "{css_selector or xpath}" to load\n{error}', reaction=reaction)

        return None

    def find_elements(self, css_selector='', xpath='', ref_element=None, loop_count=1, reaction='exit'):

        elements, error = [], ''
        driver = ref_element or self.driver

        i = 1
        while True:
            try:
                if css_selector:
                    elements = driver.find_elements(By.CSS_SELECTOR, css_selector)
                elif xpath:
                    elements = driver.find_elements(By.XPATH, xpath)
                else:
                    self.handle_exception(reason='ERROR: CSS_SELECTOR | XPATH is required to find elements', reaction='exit')
            except Exception as e:
                error = e
            
            if i == loop_count or elements:
                break
            else:
                i += 1
                time.sleep(1)
        
        if elements:
            return elements    
        else:
            self.handle_exception(reason=f'ERROR: Timed out waiting for the element with selector "{css_selector or xpath}" to load\n{error}', reaction=reaction)

        return []

    def click_checkbox(self, css_selector='input[type="checkbox"]', index=0, loop_count=1):
        elements = self.find_elements(css_selector=css_selector, loop_count=loop_count)
        return self.element_click(element=elements[index])

    def click_radio(self, css_selector='input[type="radio"]', index=0, loop_count=1):
        elements = self.find_elements(css_selector=css_selector, loop_count=loop_count)
        return self.element_click(element=elements[index])

    def select_dropdown(self, css_selector, val='', text=''):
        element = self.find_element(css_selector)
        select = Select(element)
        if text:
            select.select_by_visible_text(text)
        else:
            val = str(val)
            select.select_by_value(val)

    def add_emoji(self, selector, text):
        JS_ADD_TEXT_TO_INPUT = """
		var elm = arguments[0], txt = arguments[1];
		elm.value += txt;
		elm.dispatchEvent(new Event('change'));
		"""
        element = self.driver.find_element(By.CSS_SELECTOR, selector)
        self.driver.execute_script(JS_ADD_TEXT_TO_INPUT, element, text)
        element.send_keys('.')
        element.send_keys(Keys.BACKSPACE)
        element.send_keys(Keys.TAB)

    def scroll_wait(self, selector, sleep_duration=2):
        element = self.driver.find_element(By.CSS_SELECTOR, selector)
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto',block: 'center',inline: 'center'});", element)
        time.sleep(sleep_duration)

    # Wait random time before cliking on the element
    def element_click(self, css_selector='', xpath='', element=None, ref_element=None, loop_count=1, wait_element_time=None, reaction='exit', delay=0.5):
        success, error = False, ''
        if (css_selector or xpath) and element is None:
            element = self.find_element(css_selector=css_selector, xpath=xpath, ref_element=ref_element, loop_count=loop_count, reaction=reaction, wait_element_time=wait_element_time)

        if element:
            if delay:
                self.sleep(delay)
                
            try:
                element.click()
                success = True
            except ElementClickInterceptedException:
                self.element_click_by_javaScript(element=element)
                success = True
            except Exception as e:
                error = e
        
        if not success:
            self.handle_exception(f'Cannot click element {element} with selector {css_selector or xpath}\n{error}', reaction=reaction)
        
        return success, element

    # Wait random time before sending the keys to the element
    def element_send_keys(self, text, css_selector='', xpath='', element=None, ref_element=None,  clear_input=True, loop_count=1, wait_element_time=None, reaction='exit', delay=0.5):

        success, error = False, ''
        if (css_selector or xpath) and element is None:
            element = self.find_element(css_selector=css_selector, xpath=xpath, ref_element=ref_element, loop_count=loop_count, wait_element_time=wait_element_time, reaction=reaction)

        if element:
            if delay:
                self.sleep(delay)

            self.element_click(element=element, delay=False, reaction=reaction)
            if clear_input:
                self.element_clear(element=element, delay=False, reaction=reaction)
            
            try:
                element.send_keys(text)
                success = True
            except Exception as e:
                error = e
            
        if not success:
            self.handle_exception(f'Cannot send keys with selector {css_selector or xpath}\n{error}', reaction=reaction)
            
        return success, element

    # scraper.input_file_add_files('input[accept="image/jpeg,image/png,image/webp"]', images_path)
    def input_file_add_files(self, css_selector, files, loop_count=1, reaction='exit'):
        input_file = self.find_element(
            css_selector=css_selector, loop_count=loop_count, reaction=reaction)

        self.sleep()

        try:
            input_file.send_keys(files)
        except InvalidArgumentException:
            self.handle_exception(reason=f'ERROR: Exiting input_file_add_files! Please check if these file paths are correct:\n {files}', reaction='exit')

    # Wait random time before clearing the element (popup)
    def element_clear(self, css_selector='', xpath='', element=None, ref_element=None, loop_count=1, reaction='exit', delay=False):

        success, error = False, ''
        if (css_selector or xpath) and element is None:
            element = self.find_element(css_selector=css_selector, xpath=xpath, ref_element=ref_element, loop_count=loop_count, reaction=reaction)

        if element:
            self.element_click(element=element, delay=False)
            if delay:
                self.sleep(delay)
              
            try:  
                element.clear()

                if element.get_attribute('value') != '':
                    element.send_keys(Keys.CONTROL + "a")
                    element.send_keys(Keys.DELETE)
                success = True
            except Exception as e:
                error = e
                
        if not success:
            self.handle_exception(f'Cannot clear element {element} with selector {css_selector or xpath}\n{error}', reaction=reaction)
            
        return success, element

    def element_wait_to_be_invisible(self, selector):
        wait_until = EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, selector))

        try:
            WebDriverWait(self.driver, self.wait_element_time).until(
                wait_until)
        except:
            self.handle_exception(
                reason=f'Error: waiting the element with selector {selector} to be invisible')

    def open_new_tab(self, url):
        self.driver.execute_script("window.open(arguments[0])", url)
        self.driver.switch_to.window(self.driver.window_handles[1])

    def close_tab_and_back_homepage(self):
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def switch_to_tab(self, tab_index):
        tab_index = int(tab_index)
        self.driver.switch_to.window(self.driver.window_handles[tab_index])

    def element_click_by_javaScript(self, element):
        # If the element is not clickable in normal way because element is covered by another element
        self.driver.execute_script('arguments[0].click()', element)
        return element

    def element_set_attribute(self, element, key='value', value=''):
        self.driver.execute_script("arguments[0].setAttribute(arguments[1], arguments[2])", element, key, value)

    def get_network_log(self):
        logs = self.driver.execute_script('''
                                    var performance = window.performance || 
                                    window.mozPerformance || 
                                    window.msPerformance || 
                                    window.webkitPerformance || {}; 
                                    var network = performance.getEntries() || {}; 
                                    return network; 
                                    ''')
        return logs

    def move_to_element(self, element):
        action = ActionChains(self.driver)
        action.move_to_element(element)
        action.perform()

    def close(self, quit=False):
        try:
            if quit:
                self.driver.quit()
            else:
                self.driver.close()
            return True
        except:
            return False

    def what_is_my_ip(self, log=True):
        self.go_to_page('https://api.ipify.org/?format=json')
        my_ip = self.find_element('body').text
        if my_ip:
            my_ip = json.loads(my_ip)
        if log:
            print(my_ip['ip'])
            
        return my_ip['ip']