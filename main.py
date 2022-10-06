from sys import exit
import os
import random
import time
from selenium.webdriver.common.keys import Keys

from helpers.scraper import Scraper
from helpers.utility import formatted_time, data_countdown, countdown, execution_time
from helpers.files import read_csv, read_txt, write_to_csv, write_to_txt, read_txt_in_dict, pd_read_csv
from helpers.numbers import formatted_number_with_comma, numbers_within_str, str_to_int

def main():
    pass

if __name__ == "__main__":
    START_TIME = time.time()


    # Global variables
    url = 'https://www.google.com/search?q=what+is+my+ip'
    d = Scraper()
    d.print_executable_path()
    
    d.go_to_page(url)
    
    main()
    
    # Footer for reporting
    execution_time(START_TIME)

    # Finally Close the browser
    input('Press any key to exit the browser...')
    d.close()
