from bs4 import BeautifulSoup
import requests
import os
import shutil
import time 

start = time.time() # start counting processing time


DIR = os.getcwd()
url = input('URL: ')


# creating output folder
domain = url.split('/')[2].split('.')[0]
OUTPUT_PATH = os.path.join(DIR, domain)

# Check if folder exist
if os.path.exists(OUTPUT_PATH):
    shutil.rmtree(OUTPUT_PATH)

# creating output dir
os.mkdir(OUTPUT_PATH)


response = requests.get(url)
soup = BeautifulSoup(response.text, features='html.parser')

# creating index.html
with open(os.path.join(OUTPUT_PATH, 'index.html'), 'w', encoding='utf-8') as file:
    # replacing pathes which starting from / ( root folder )
    for link in soup.find_all('link', href=True):
        if link['href'][0] == '/':
            link['href'] = link['href'][1::]


    for link in soup.find_all('script', src=True):
        if link['src'][0] == '/':
            link['src'] = link['src'][1::]
    
    
    # removing srcsets
    for img in soup.find_all('img', srcset=True):
        del img['srcset']

    # prettifying file
    file.write(soup.prettify())


to_export = ['link', 'script', 'img']

for src_type in to_export:
    if src_type == 'link':
        matches = soup.find_all(src_type, href=True)
    else:
        matches = soup.find_all(src_type, src=True)
    for i in matches:
        try:
            href = i['href']
        except:
            href = i['src']
        if href.startswith('http') or href.startswith('data:'):
            continue
        file_path = href.split('/')

        # creating folder for file
        file_folder = '/'.join(file_path[:-1])
        new_path = os.path.join(OUTPUT_PATH, file_folder)
        os.makedirs(new_path, exist_ok=True)

        # insert file into folder
        if '?' in file_path[-1]:
            file_name = file_path[-1].split('?')[0]
        else:
            file_name = file_path[-1]
        file_content = requests.get(url + href, stream=True)
        file_dir = os.path.join(new_path, file_name)
        if file_content.status_code == 200:
            with open(file_dir, 'wb') as f:
                file_content.raw.decode_content = True
                shutil.copyfileobj(file_content.raw, f)  


end = time.time() - start ## final process time


print(f'Scrapping complete in {round(end, 3)} seconds!')
print(f'localhost url: http://127.0.0.1:5500/{domain}/')