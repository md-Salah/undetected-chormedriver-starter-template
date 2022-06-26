import time
from helpers.scraper import Scraper
from selenium.common.exceptions import TimeoutException
import os
import random
import pandas as pd

from helpers.functions import read_txt, formatted_time, formatted_number_with_comma, countdown, execution_time, read_csv, write_to_csv
from helpers.user import generate_user_info
from helpers.gui import open_file

# Header of the program
start_time = time.time()

# Body
url = read_txt('websites.txt')[0]
scraper = Scraper(url)


# Footer
os.system('cls')
print('Execution Completed\n\nReport:\n================================')
execution_time(start_time)

os.system('pause')        
scraper.driver.close()

                

        

