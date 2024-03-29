#!/usr/bin/env python3

from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import pandas
import os.path
import time


##############
# Khai báo cấu hình
##############
SCOPES = ["https://www.googleapis.com/auth/indexing"]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
action_type = "URL_DELETED"
# Đường dẫn tới file api google
JSON_KEY_FILE = "google-key-file.json" 
# Đường dẫn tới file csv chứa thông tin các url cần xoá
filename = "abc_com.csv"

##############
# Kết Nối
##############

if os.path.isfile(JSON_KEY_FILE) == False:
    raise Exception(f"JSON KEY {JSON_KEY_FILE} not found")

print("Testing Authentication")

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    JSON_KEY_FILE, scopes=SCOPES)
http = credentials.authorize(httplib2.Http())

##############
# Đọc file csv
##############
print(f"Filename to read and save results is: {filename}")

if os.path.isfile(filename) == False:
    raise Exception(f"File {filename} not found")

urls = pandas.read_csv(filename)

if 'url' not in urls.columns:
    raise Exception(f"file {filename} does not contain a column called 'url'")

if os.access(filename, os.W_OK) == False:
    raise Exception(f"File {filename} is not writable")

print(f"Adding column to file to track status")
if 'action_status' not in urls.columns:
    urls['action_status'] = 'Unactioned'

urls.to_csv(filename, index=False)

##############
# Run Query loop
##############

urls_actionable_index = urls.query('action_status=="Unactioned"').index
urls_retry_index = urls.query('action_status =="429"').index
urls_total = len(urls)

print("#####################################")
print(f"Google API Action Type: {action_type}")
print(f"Actionable URL's: {len(urls_actionable_index)} out of {urls_total}")
print(f"Retry URL's     : {len(urls_retry_index)} out of {urls_total}")
if (len(urls_actionable_index)+len(urls_retry_index)) > 200:
    print("Warning, total urls is larger than 200, rate limiting is likely")
print("#####################################")

if str(input("Is this correct?' (y/n): ")).lower().strip() != 'y':
    print("Input not confirmed, quitting")
    exit()

def query_google(index):
    ratelimited=0
    for i in index:
        if ratelimited == 0:
            content = {'url': urls.url[i], 'type': action_type}
            response, content = http.request(
                ENDPOINT, method="POST", body=str(content))
            # enable debug 
           # with open(f'response_{i+1}.json', 'w') as f:
            #    f.write(content.decode('utf-8'))
            # end enable debug
            if response.status == 429:
                print("HTTP 429 recieved, exceeded Indexing API quota")
                ratelimited == 1
            if response.status != 200:
                raise Exception(f"Error: Non HTTP 200 response recieved. HTTP Status {response.status}")
            print(f"Result for item {i+1} of {len(index)} is {response.status}")
            urls.iloc[i]['action_status'] = response.status
        else:
            print(f"Too many rate limits recieved, aborting")

query_google(urls_actionable_index)
query_google(urls_retry_index)
print("All items processed")
##############
#Lưu kết quả
##############

urls.to_csv(filename, index=False)
