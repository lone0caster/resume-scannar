import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent

class LinkedInBot:
    def __init__(self, driver_path=r"C:/Users/abhij/Mini Project/chromedriver.exe"):
        self.driver_path = driver_path
        self.user_agent = UserAgent().random
        self.driver = self.create_driver()

    def create_driver(self):
        option = webdriver.ChromeOptions()
        option.add_argument(f'user-agent={self.user_agent}')
        option.add_argument('--disable-blink-features=AutomationControlled')
        option.add_argument("--window-size=1920,1080")
        # driver = webdriver.Chrome(executable_path=self.driver_path, chrome_options=option)
        driver = webdriver.Chrome(options = option)
        driver.maximize_window()
        return driver

    def open_url(self, url):
        self.driver.get(url)

        try:
            # Dismiss any login pop-ups or banners if they exist
            self.driver.find_element(By.TAG_NAME, 'body').click()
        except:
            pass

        try:
            # Wait for 3 seconds
            time.sleep(3)

            # Click on the specified coordinates
            x = 191
            y = 363

            action = ActionChains(self.driver)
            action.move_by_offset(x, y).click().perform()
            print("Clicked at coordinates ({}, {}).".format(x, y))
        except Exception as e:
            print("Failed to click at coordinates ({}, {}):".format(x, y), e)

    def scrape_data(self):
        try:
            # Find the h2 element with the specified class
            title_element = self.driver.find_element(By.CLASS_NAME, 'top-card-layout__headline')
            # Get the text of the title
            title = title_element.text
            print("Title of the LinkedIn person:", title)
            return title
        except Exception as e:
            return None

    def scrape_experience(self):
        try:
            # Find the ul element with the specified class
            experience_list = self.driver.find_element(By.CLASS_NAME, 'experience__list')
            # Find all the li elements within the ul
            experiences = experience_list.find_elements(By.TAG_NAME, 'li')
            experiecnes_list = ""
            # Extract and print the text of each experience
            print("Experiences:")
            for experience in experiences:
                experiecnes_list += experience.text
                print(experience.text)
            return experiecnes_list
        except Exception as e:
            print("Experience not found.")

    def scrape_education(self):
        try:
            # Find the ul element with the specified class
            education_list = self.driver.find_element(By.CLASS_NAME, 'education__list')
            # Find all the li elements within the ul
            educations = education_list.find_elements(By.TAG_NAME, 'li')
            education_string = ""
            # Extract and print the text of each education
            print("Education:")
            for education in educations:
                education_list += education.text
                print(education.text)
            return education_string
        except Exception as e:
            print("Education not found.")

    def scrape_activities(self):
        try:
            # Find all the ul elements with the specified data-test-id
            activities_lists = self.driver.find_elements(By.CSS_SELECTOR, '[data-test-id="activities__list"]')

            # Initialize a set to store unique activities
            unique_activities = set()

            # Iterate through each activities list
            for activities_list in activities_lists:
                # Find all the li elements within the activities list
                activities = activities_list.find_elements(By.TAG_NAME, 'li')

                # Extract and add the text of each activity to the set
                for activity in activities:
                    unique_activities.add(activity.text)

            # Convert the set back to a list to remove duplicates
            unique_activities_list = list(unique_activities)

            # Clean the activities list
            cleaned_activities_list = self.clean_activities_list(unique_activities_list)

            # Print the cleaned activities list
            activity_string = ""
            print("Activities:")
            for activity in cleaned_activities_list:
                print(activity)
                activity_string += activity
                print('\n')
            return activity_string
        except Exception as e:
            print("Activities not found.")

    def clean_activities_list(self, activities_list):
        cleaned_activities = []
        unique_activities = set()  # Use a set to store unique activities
        for activity in activities_list:
            # Extract the relevant information and remove "Liked by" part
            activity_text = activity.split("Liked by")[0].strip()
            unique_activities.add(activity_text)  # Add the cleaned activity to the set

        # Convert the set to a list to maintain order
        unique_activities_list = list(unique_activities)

        # Divide each activity text into two parts and keep only the first 50% of each
        for activity in unique_activities_list:
            halfway_index = len(activity) // 2
            first_half_activity = activity[:halfway_index]
            cleaned_activities.append(first_half_activity)

        return cleaned_activities


    def scrape_certifications(self):
        try:
            # # Find the div element with the specified data-section
            # certifications_section = self.driver.find_element(By.CSS_SELECTOR, '[data-section="certifications__list"]')
            # # Find all the li elements within the div
            # certifications = certifications_section.find_elements(By.TAG_NAME, 'li')

            # Find the div element with the specified ID
            certifications_section = self.driver.find_element(By.ID, 'licenses_and_certifications')
            # Find all the li elements within the div
            certifications = certifications_section.find_elements(By.TAG_NAME, 'li')
            certification_string = ""
            # Extract and print the text of each certification
            print("Certifications:")
            for certification in certifications_section:
                # Check if the text contains "See credential"
                cert_text = certification.text.replace("See credential", "")
                certifications_string += cert_text
                print(cert_text)
            return certification_string
        except Exception as e:
            print("Certifications not found.")