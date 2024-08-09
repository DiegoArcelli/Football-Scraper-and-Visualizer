from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Replace 'path/to/chromium' with your Chromium path
url = "https://www.whoscored.com/Matches/1809759/Live/Europe-Champions-League-Manchester-City-Real-Madrid"
options = Options()
options.binary_location = '/usr/bin/chromium-browser'
options.add_argument('--remote-debugging-pipe')
driver = webdriver.Chrome(options=options)

# Retrieve the capabilities
driver.get(url)

# Close the driver