from selenium import webdriver
from selenium.webdriver.common.by import By
from chromedriver_py import binary_path
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import json


### Este código não está funcionando!! Ainda em trabalho ###


service = webdriver.ChromeService(executable_path=binary_path)
options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options, service=service)
driver.get('https://www.catho.com.br/vagas/')

keyword_input = driver.find_element(By.ID, 'keyword')
keyword_input.clear()
keyword_input.send_keys('Ciência de Dados')

submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
submit_button.click()
jobs = {}
i = 1
def data():
    cards = driver.find_elements(By.CSS_SELECTOR, 'li[class="search-result-custom_jobItem__OGz3a"]')
    
    for card in cards:
        title = card.find_element(By.CSS_SELECTOR, 'a').text
        link = card.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
        company = card.find_element(By.CSS_SELECTOR, 'p[class="sc-sLsrZ iJixUK"]').text
        salary = card.find_element(By.CSS_SELECTOR, 'div[class="custom-styled_salaryText__oSvPo"]').text
        desc = card.find_element(By.CSS_SELECTOR, 'div[class="job-description"]').text

        job_data = {
            'Título': title,
            'Empresa': company,
            'Salário': salary,
            'Descricao': desc,
            'Link': link,
        }

        jobs.update({i: job_data})
        i += 1

print(jobs)
# with open('app\data\vagas.json', 'w') as file:
#     json.dump(jobs, file)
