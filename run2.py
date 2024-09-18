import requests
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from fake_useragent import UserAgent
from fake_headers import Headers
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Initialize UserAgent and Headers
ua = UserAgent()
headers_generator = Headers()

# Function to load proxies from file
def load_proxies(filename):
    with open(filename, 'r') as f:
        proxies = f.readlines()
    return [proxy.strip() for proxy in proxies if proxy.strip()]

# Function to load URL from file
def load_url(filename):
    with open(filename, 'r') as f:
        return f.readline().strip()

# Function to generate fake headers
def generate_fake_headers():
    headers = headers_generator.generate()
    headers['User-Agent'] = ua.random
    return headers

# Function to visit site using requests
def visit_site_with_proxy(proxy, url):
    session = requests.Session()
    proxy_dict = {
        "http": proxy,
        "https": proxy
    }
    headers = generate_fake_headers()
    
    try:
        time.sleep(random.uniform(2, 5))  # Random delay
        response = session.get(url, proxies=proxy_dict, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Visited {url} using proxy: {proxy}")
        print(f"Status code: {response.status_code}")
        print(f"Title: {soup.title.string if soup.title else 'No title found'}")
        
        return f"Request successful with proxy {proxy}."
    
    except requests.RequestException as e:
        return f"Failed to connect using proxy {proxy}: {e}"

# Function to visit site using Selenium
def visit_site_with_selenium(proxy, url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Run headless
    chrome_options.add_argument(f"user-agent={ua.random}")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Set proxy for Chrome
    chrome_options.add_argument(f'--proxy-server={proxy}')
    
    # Set Chrome binary location (update this path as needed)
    chrome_options.binary_location = "/workspaces/breakfold/chrome-linux64/chrome"  # Chrome이 설치된 경로로 변경

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        print(f"Visited {url} using Selenium and proxy: {proxy}")
        print(f"Page title: {driver.title}")
        driver.quit()
        return f"Selenium request successful with proxy {proxy}."
    
    except Exception as e:
        return f"Selenium request failed with proxy {proxy}: {e}"
def kill_chrome_drivers():
    for proc in psutil.process_iter(['pid', 'name']):
        if 'chromedriver' in proc.info['name']:
            proc.terminate()
            proc.wait()

# Signal handler to catch Ctrl + C
def signal_handler(sig, frame):
    print('Signal received, killing all ChromeDriver processes...')
    kill_chrome_drivers()
    exit(0)
# Function to run requests in parallel
def run_parallel_requests(url, proxies, max_threads=5, use_selenium=False):
    results = []
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_proxy = {}
        
        for proxy in proxies:
            if use_selenium:
                future_to_proxy[executor.submit(visit_site_with_selenium, proxy, url)] = proxy
            else:
                future_to_proxy[executor.submit(visit_site_with_proxy, proxy, url)] = proxy
        
        for future in as_completed(future_to_proxy):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append(f"Error: {e}")
    
    return results

# Main script
if __name__ == "__main__":
    # Load proxies and URL
    proxies = load_proxies("NewGoodProxy.txt")
    url = load_url("site.txt")
    
    # Use ThreadPoolExecutor to visit the site with proxies
    use_selenium = True  # Set to True to use Selenium instead of requests
    results = run_parallel_requests(url, proxies, max_threads=5, use_selenium=use_selenium)
    
    # Print results
    for result in results:
        print(result)
