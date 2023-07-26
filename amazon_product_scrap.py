from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.by import By
import time
from tqdm import tqdm
import time



def initialze_driver():
    driver=webdriver.Chrome()
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    return driver



def extract_data(driver):

    url='https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1'
    driver.get(url)

    url = []
    name = []
    price= []
    rating = []
    number_of_reviews = []
    product_description = []
    asin = []
    manufacturer = []
    description = []

    for page in tqdm(range(19), desc="Pages", unit="page"):
        time.sleep(2)
        for product in range(len(driver.find_elements(By.XPATH,'//div[@data-component-type="s-search-result"]'))):
            url.append(driver.find_elements(By.XPATH,'//div[@data-component-type="s-search-result"]')[product].find_element(By.XPATH,'.//h2/a').get_attribute('href'))
            name.append(driver.find_elements(By.XPATH,'//div[@data-component-type="s-search-result"]')[product].find_element(By.XPATH,'.//h2/a').text)
            try:
                rating.append(driver.find_elements(By.XPATH,'//div[@data-component-type="s-search-result"]')[product].find_elements(By.XPATH,'.//div[@class="a-row a-size-small"]/span')[0].get_attribute('aria-label').split()[0])
            except:
                rating.append('No rating')
            try:
                number_of_reviews.append(driver.find_elements(By.XPATH,'//div[@data-component-type="s-search-result"]')[product].find_elements(By.XPATH,'.//div[@class="a-row a-size-small"]/span')[1].get_attribute('aria-label'))
            except:
                number_of_reviews.append('No reviews')
            try:
                price.append(driver.find_elements(By.XPATH,'//div[@data-component-type="s-search-result"]')[product].find_element(By.XPATH,'.//div[@class="a-row a-size-base a-color-base"]').text.split()[0])
            except:
                price.append('No price')

        driver.find_element(By.XPATH,'//a[@class="s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"]').click()

 
    df = pd.DataFrame({'url':url,'name':name,'price':price,'rating':rating,'number_of_reviews':number_of_reviews})

    for i in tqdm(range(len(df['url'])), desc="Processing URLs", unit="URL"):
        driver.get(df['url'][i])
        time.sleep(2)

        try:
            l = driver.find_element(By.XPATH,'//ul[@class="a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list"]').text.split('\n')

            #ASIN
            temp_asin = 'No ASIN'
            for i in l:
                if i.startswith('ASIN'):
                    temp_asin = i.split(':')[-1]
                    break
            asin.append(temp_asin)

            #Manufacturer
            temp_manf = 'No manufacturer'
            for i in l:
                if i.startswith('Manufacturer'):
                    temp_manf = i.split(':')[-1]
                    break
            manufacturer.append(temp_manf)
        except:
            asin.append('No ASIN')
            manufacturer.append('No manufacturer')

        #Product description
        try:
            temp = driver.find_element(By.XPATH,'.//div[@id="productDescription"]').text
            if temp == '':
                product_description.append('No product description')
            else:
                product_description.append(temp)
        except:
            product_description.append('No product description')

        #description
        try:
            description.append(driver.find_element(By.XPATH,'.//div[@id="featurebullets_feature_div"]').text)
        except:
            description.append('No description')

    df1 = pd.DataFrame({'asin':asin,'manufacturer':manufacturer,'product_description':product_description,'description':description})
  
    df2 = pd.concat([df,df1],axis=1)

    return df2

if __name__ == '__main__':
    driver = initialze_driver()
    df = extract_data(driver)
    df.to_csv('amazon.csv',index=False)
    driver.quit()
    