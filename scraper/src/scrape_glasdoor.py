import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from datetime import datetime

keyword = "Data Scientist"
num_jobs = 10
verbose = True

def get_jobs(keyword, num_jobs, verbose):
    '''Gathers jobs as a dataframe, scraped from Glassdoor'''
    

    # Configure ChromeDriver and Chrome paths
    chrome_service = Service("/usr/bin/chromedriver") 
    options = Options()
    options.binary_location = "/usr/bin/google-chrome"  

    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # Initialize the WebDriver
    driver = webdriver.Chrome(service=chrome_service, options=options)
    driver.set_window_size(1120, 1000)
    
    char = str(len(keyword))
    url = f'https://www.glassdoor.com/Job/{keyword}-jobs-SRCH_KO0,{char}.htm'
    driver.get(url)
    jobs = []
    time.sleep(5)
    processed = set()
    
    while len(jobs) < num_jobs:
        try:
            job_cards = driver.find_elements(By.CLASS_NAME, 'JobCard_jobCardContainer__arQlW')
            if verbose:
                print(f"Found job cards: {len(job_cards)}")
        except:
            continue
        
        if verbose:
            print(f"Progress: {len(jobs)}/{num_jobs}")
        if len(jobs) >= num_jobs:
            break
        
        for job_card in job_cards:
            if len(jobs) >= num_jobs:
                break
            
            try:
                try:
                    driver.find_element(By.XPATH, "/html/body/div[11]/div[2]/div[2]/div[1]/div[1]/button").click()
                    if verbose:
                        print("Clicked the cross to close pop-up.")
                except NoSuchElementException:
                    pass
                
                job_url = job_card.find_element(By.CLASS_NAME, 'JobCard_jobTitle__GLyJ1').get_attribute('href')
                if job_url not in processed:
                    job_card.click()
                    time.sleep(2)
                    collected_successfully = False
                    while not collected_successfully:
                        try:
                            company_name = job_card.find_element(By.CLASS_NAME, 'EmployerProfile_compactEmployerName__9MGcV').text
                            location = job_card.find_element(By.CLASS_NAME, 'JobCard_location__Ds1fM').text
                            job_title = job_card.find_element(By.CLASS_NAME, 'JobCard_jobTitle__GLyJ1').text
                            job_description = job_card.find_element(By.CLASS_NAME, 'JobCard_jobDescriptionSnippet__l1tnl').text
                            collected_successfully = True
                            processed.add(job_url)
                        except NoSuchElementException:
                            time.sleep(5)
                    
                    try:
                        salary_estimate = job_card.find_element(By.CLASS_NAME, 'JobCard_salaryEstimate__QpbTW').text
                    except NoSuchElementException:
                        salary_estimate = -1
                    
                    try:
                        rating = job_card.find_element(By.CLASS_NAME, 'rating-single-star_RatingText__XENmU').text
                    except NoSuchElementException:
                        rating = -1
                    
                    if verbose:
                        print(f"Job Title: {job_title}")
                        print(f"Salary Estimate: {salary_estimate}")
                        print(f"Job Description: {job_description[:500]}")
                        print(f"Rating: {rating}")
                        print(f"Company Name: {company_name}")
                        print(f"Location: {location}")
                    
                    jobs.append({
                        "Job Title": job_title,
                        "Salary Estimate": salary_estimate,
                        "Job Description": job_description,
                        "Rating": rating,
                        "Company Name": company_name,
                        "Location": location,
                        "URL": job_url,
                    })
            except (ElementClickInterceptedException, ElementNotInteractableException):
                continue
        
            try:
                close_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'CloseButton'))
                )
                close_button.click()
                if verbose:
                    print("Clicked 'CloseButton'.")
                time.sleep(3)
            except Exception as e:
                if verbose:
                    print(f"Error clicking 'CloseButton': {e}")
    
    driver.quit()
    return pd.DataFrame(jobs)

def update_dataset():
    import re  
    
    df_new = get_jobs(keyword, num_jobs, verbose)
    
    data_dir = "/app/data/"
    existing_csv = os.path.join(data_dir, "ds_salaries.csv")
    
    if os.path.exists(existing_csv):
        csv_data = pd.read_csv(existing_csv)
    else:
        csv_data = pd.DataFrame()
    
    df_new.rename(columns={
        "Job Title": "job_title",
        "Salary Estimate": "salary",
        "Location": "company_location",
        "Company Name": "company_name"
    }, inplace=True)
    
    current_year = datetime.now().year
    df_new['work_year'] = current_year
    df_new['salary_currency'] = 'EUR'
    
    # Add missing columns with default values or NaN
    if not csv_data.empty:
        for col in csv_data.columns:
            if col not in df_new.columns:
                df_new[col] = None
    
        glassdoor_data = df_new[csv_data.columns]
        combined_data = pd.concat([csv_data, glassdoor_data], ignore_index=True)
    else:
        combined_data = df_new
    
    # Function to extract the first numeric value from the salary string
    def extract_first_number(salary_str):
        if isinstance(salary_str, str):
            cleaned_str = re.sub(r'[^\d\-]', '', salary_str)
            numbers = re.findall(r'\d+', cleaned_str)
            if numbers:
                return int(numbers[0])
        elif isinstance(salary_str, (int, float)):
            return salary_str
        return -1  
    
    combined_data['salary'] = combined_data['salary'].apply(extract_first_number)
    combined_data = combined_data[combined_data['salary'] != -1]
    combined_data['salary'] = combined_data['salary'].astype(int)
    
    combined_data.to_csv(existing_csv, index=False)
    if verbose:
        print(f"Combined and cleaned dataset saved to {existing_csv}")

if __name__ == "__main__":
    update_dataset()
