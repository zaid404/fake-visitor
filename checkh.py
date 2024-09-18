
import os
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor, wait
from glob import glob
from time import sleep

import requests
from fake_headers import Headers

os.system("")


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


print(bcolors.OKGREEN + """
  ____                                    
 |  _ \ _ __ _____  ___   _               
 | |_) | '__/ _ \ \/ / | | |              
 |  __/| | | (_) >  <| |_| |              
 |_|   |_|_ \___/_/\_\\__, |_             
      / ___| |__   ___|___/| | _____ _ __ 
     | |   | '_ \ / _ \/ __| |/ / _ \ '__|
     | |___| | | |  __/ (__|   <  __/ |   
      \____|_| |_|\___|\___|_|\_\___|_|   
                                          
""" + bcolors.ENDC)

print(bcolors.OKCYAN + """
[ GitHub : https://github.com/MShawon/YouTube-Viewer ]
""" + bcolors.ENDC)


checked = {}
cancel_all = False


def backup():
    try:
        # Open the existing backup file in append mode and the GoodProxy.txt file in read mode
        with open('NewGoodProxy.txt', 'r', encoding='utf-8') as good_proxy_file, \
             open('ProxyBackup.txt', 'a', encoding='utf-8') as backup_file:
            
            # Read the contents of GoodProxy.txt and write them to ProxyBackup.txt
            contents = good_proxy_file.read()
            backup_file.write(contents)
        
        print(bcolors.WARNING + 'Contents of GoodProxy.txt appended to ProxyBackup.txt' + bcolors.ENDC)
    except Exception as e:
        print(bcolors.FAIL + f'An error occurred while backing up proxies: {e}' + bcolors.ENDC)

    # Clear the contents of GoodProxy.txt
    open('NewGoodProxy.txt', 'w').close()




def clean_exe_temp(folder):
    try:
        temp_name = sys._MEIPASS.split('\\')[-1]
    except Exception:
        temp_name = None

    for f in glob(os.path.join('temp', folder, '*')):
        if temp_name not in f:
            shutil.rmtree(f, ignore_errors=True)

def update_proxy_list():
    proxy_url = 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt'
    response = requests.get(proxy_url)
    if response.status_code == 200:
        with open('http.txt', 'w') as file:
            file.write(response.text)
        print(bcolors.OKGREEN + 'Proxy list updated successfully. from git' + bcolors.ENDC)
    else:
        print(bcolors.FAIL + 'Failed to update proxy list.' + bcolors.ENDC)
        
def load_proxy():
    update_proxy_list()
    proxies = []

    filename = 'http.txt'

    if not os.path.isfile(filename) and filename[-4:] != '.txt':
        filename = f'{filename}.txt'

    try:
        with open(filename, encoding="utf-8") as fh:
            loaded = [x.strip() for x in fh if x.strip() != '']
    except Exception as e:
        print(bcolors.FAIL + str(e) + bcolors.ENDC)
        input('')
        sys.exit()

    for lines in loaded:
        if lines.count(':') == 3:
            split = lines.split(':')
            lines = f'{split[2]}:{split[-1]}@{split[0]}:{split[1]}'
        proxies.append(lines)

    return proxies


def main_checker(proxy_type, proxy, position):
    if cancel_all:
        raise KeyboardInterrupt

    checked[position] = None

    try:
        proxy_dict = {
            "http": f"{proxy_type}://{proxy}",
            "https": f"{proxy_type}://{proxy}",
        }

        header = Headers(
            headers=False
        ).generate()
        agent = header['User-Agent']

        headers = {
            'User-Agent': f'{agent}',
        }

        response = requests.get(
            'https://www.youtube.com/', headers=headers, proxies=proxy_dict, timeout=30)
        status = response.status_code

        if status != 200:
            raise Exception(status)

        print(bcolors.OKBLUE + f"Worker {position+1} | " + bcolors.OKGREEN +
              f'{proxy} | GOOD | Type : {proxy_type} | Response : {status}' + bcolors.ENDC)

        print(f'{proxy}', file=open('NewGoodProxy.txt', 'a'))

    except Exception as e:
        try:
            e = int(e.args[0])
        except Exception:
            e = ''
        print(bcolors.OKBLUE + f"Worker {position+1} | " + bcolors.FAIL +
              f'{proxy} | {proxy_type} | BAD | {e}' + bcolors.ENDC)
        checked[position] = proxy_type


def proxy_check(position):
    sleep(2)
    proxy = proxy_list[position]

    if '|' in proxy:
        splitted = proxy.split('|')
        main_checker(splitted[-1], splitted[0], position)
    else:
        main_checker('http', proxy, position)
        if checked[position] == 'http':
            main_checker('socks4', proxy, position)
        if checked[position] == 'socks4':
            main_checker('socks5', proxy, position)


def main():
    global cancel_all

    cancel_all = False
    pool_number = [i for i in range(total_proxies)]

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(proxy_check, position)
                   for position in pool_number]
        done, not_done = wait(futures, timeout=0)
        try:
            while not_done:
                freshly_done, not_done = wait(not_done, timeout=5)
                done |= freshly_done
        except KeyboardInterrupt:
            print(bcolors.WARNING +
                  'Hold on!!! Allow me a moment to finish the running threads' + bcolors.ENDC)
            cancel_all = True
            for future in not_done:
                _ = future.cancel()
            _ = wait(not_done, timeout=None)
            raise KeyboardInterrupt
        except IndexError:
            print(bcolors.WARNING + 'Number of proxies are less than threads. Provide more proxies or less threads. ' + bcolors.ENDC)


if __name__ == '__main__':

    clean_exe_temp(folder='proxy_check')
    backup()

    try:
        threads = 100
    except Exception:
        threads = 100

    proxy_list = load_proxy()
    # removing empty & duplicate proxies
    proxy_list = list(set(filter(None, proxy_list)))

    total_proxies = len(proxy_list)
    print(bcolors.OKCYAN +
          f'Total unique proxies : {total_proxies}' + bcolors.ENDC)

    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
