from sys import exit
import os
import random
import time
from selenium.webdriver.common.keys import Keys

from modules.scraper import Scraper
from modules.utility import formatted_time, data_countdown, countdown, execution_time
from modules.files import read_csv, read_txt, write_to_csv, write_to_txt, read_txt_in_dict, pd_read_csv
from modules.numbers import formatted_number_with_comma, numbers_within_str, str_to_int

def main():
    d.go_to_page(url)
    pass
    
    
if __name__ == "__main__":
    START_TIME = time.time()


    # Global variables
    url = 'https://google.com/'
    d = Scraper()
    # d.print_executable_path()
    

    main()
    
    
    # Footer for reporting
    execution_time(START_TIME)

    # Finally Close the browser
    input('Press any key to exit the browser...')
    d.close()
