from multiprocessing.pool import ThreadPool
from bs4 import BeautifulSoup
import requests
import csv
import os


TIMEOUT = 7  # Proxy request timeout
file_path = 'working_proxies.csv'  # Write file
count_working_proxies = 0


def proxy_scrape():
    # Gets all proxies on the page and returns them in a set()
    url = r'https://free-proxy-list.net'

    r = requests.get(url, timeout=7)
    soup = BeautifulSoup(r.text, 'lxml')

    # Select the table excluding the first and the last row
    table = soup.select("#proxylisttable tr")
    table = table[1:-1]
    proxy_set = set()

    for row in table:
        # Go through each row, merge IP addresses with corresponding ports and add them to a set
        ip_addr = row.select_one('td').text
        port = row.select_one('td + td').text
        proxy = f'{ip_addr}:{port}'
        proxy_set.add(proxy)

    print(f'Total amount of proxies: {len(proxy_set)}')

    return proxy_set


def proxy_test(proxy):
    # Tests the scraped proxies and writes the working ones along with the time it took them to load the page to an .csv file

    # Using httpbin used to test the proxies
    url = 'http://httpbin.org/ip'
    proxies = {
        'http': f'http://{proxy}',
        'https': f'http://{proxy}',
    }
    try:
        r = requests.get(url, proxies=proxies, timeout=TIMEOUT)
        load_time = round(r.elapsed.total_seconds(), 3)  # Time it took the page to load
        if r.status_code == 200:
            # Check the status code, if 200 write it to the file
            global count_working_proxies
            count_working_proxies += 1
            csv_writer.writerow([proxy, load_time])
            print(f'Working proxy --> {proxy}')

    except requests.exceptions.Timeout:
        print(f'[TIMED OUT] Proxy took too long: {proxy} ')
    except Exception:
        print(f'[Error occurred] Proxy not working: {proxy}')
        pass


with open(file_path, 'w', newline='', errors='ignore') as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(['proxy', 'load time'])

    all_proxies = proxy_scrape()
    try:
        # Threading to speed up the proxy testing
        ThreadPool(processes=10).map(proxy_test, all_proxies)
    except Exception as e:
        print(f'[Thread error] {e}')

print(f'Total amount of working proxies {count_working_proxies}')
os.startfile(file_path)

