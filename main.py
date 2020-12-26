# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 13:15:32 2020

@author: Pavel
"""
import requests
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = 'https://tululu.org/txt.php?id=32168'

response = requests.get(url, verify=False)
response.raise_for_status()

with open('book.txt', 'w') as file:
    file.write(response.text)
