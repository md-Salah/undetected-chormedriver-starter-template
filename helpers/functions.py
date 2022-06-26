import datetime
import re
from helpers.user import generate_user_info
import random
import os
from os import listdir
from os.path import isfile, join
import time
import pandas as pd


def read_txt(file_name):
    file_dir = os.getcwd() + "\\inputs\\" + file_name
    try:
        with open(file_dir, "r") as file:
            data = file.read()
            list = data.split("\n")
            data = []
            for site in list:
                data.append(site.strip())
    except:
        print(f'{file_name} file not found in {file_dir}')
        exit()
    return data

def get_acc_info():
    users = read_txt('names.txt')
    data = []
    for user in users:
        user = generate_user_info(user)
        images = [f for f in listdir('images') if isfile(join('images', f))]
        index = random.randint(0,len(images)-1)
        image = os.path.abspath(os.getcwd()) + '\images\\' + images[index]
        user['img'] = image
        data.append(user)
    return data
    
def formatted_time(t, hours = False):
    m, s = divmod(t, 60)
    h, m = divmod(m, 60)
    if hours:
        return '{:d}:{:02d}:{:02d}'.format(h, m, s)
    else: 
        return '{:02d}:{:02d}'.format(m, s)

def formatted_number_with_comma(number):
    return ("{:,}".format(number))

def countdown(t):
    while t:
        mins, secs = divmod(t, 60) 
        hours, mins = divmod(mins, 60)
        timer = '{:02d}:{:02d}:{:02d}'.format(hours, mins, secs) 
        print(timer, end="\r") 
        time.sleep(1) 
        t -= 1
    print('Waiting is over')

def execution_time(start_time):
    print('Execution time: ', datetime.timedelta(seconds= int(time.time() - start_time)))

def read_csv(file_name):
    try:
        df = pd.read_csv(file_name)
        data = df.values.tolist()
    except:
        data = []
    # Returning data as a list
    return data

def write_to_csv(data, labels, filename = 'output.csv'):
    pd.DataFrame(data, columns=labels).to_csv(filename, index=False)