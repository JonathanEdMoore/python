from selenium import webdriver
from selenium.webdriver.safari.service import Service
from selenium.webdriver.safari.options import Options

# Set up Selenium WebDriver for Safari
service = Service()  # No need to specify path for SafariDriver
options = Options()  # Safari options are limited, not usually needed

driver = webdriver.Safari(service=service, options=options)

# URL of the webpage
url = 'https://www.census.gov/popclock/data_tables.php?component=pyramid'
driver.get(url)

# Extract data from the webpage (adjust as needed)
script = driver.find_element(By.TAG_NAME, 'script').get_attribute('innerHTML')
print(script)

# Close the browser
driver.quit()
