from dotenv import load_dotenv
from openai import OpenAI
import subprocess
import traceback
import requests
import json
import os


MY_UNIVERSITY = "Stanford"                     # University to check alumni status
SUBJECT_LINE = "Stanford student reaching out" # Default subject line for emails
MULTIPLE_PROMPTS = True                        # Flag to determine prompt selection method
PROMPT_FILE = 'vc.txt'                         # Prompt file if MULTIPLE_PROMPTS is False
SMALLER_MODEL = 'gpt-3.5-turbo'                # Model for simple tasks (can be any gpt model)
MEDIUM_MODEL = 'gpt-4o'                        # Model for general tasks, ideally can look things up on the internet
LARGER_MODEL = 'o1-mini'                       # Model for writing an email (can be any gpt model)


class Person:
    """
    A class to store and process information about a person, as extracted from a LinkedIn profile.
    Contains methods to generate email addresses and create a text summary.
    """
    def __init__(self):
        # Basic personal information
        self.first = ""
        self.last = ""
        self.headline = ""
        self.location = ""
        self.about = ""
        # Containers for additional data
        self.domains = []
        self.education = []
        self.current_job = []
        self.past_experience = []
        self.emails = []
        # Boolean flags
        self.female = False
        self.alumni = False

    class Experience:
        """
        A nested class to represent work experience.
        """
        def __init__(self):
            self.company = ""
            self.title = ""
            self.industry = ""
            self.description = ""
            self.mission = ""

    class Education:
        """
        A nested class to represent education details.
        """
        def __init__(self):
            self.school = ""
            self.degree = ""
            self.field = ""

    def possible_emails(self, domain, first, last):
        """
        Generate a list of potential email addresses based on the provided domain and person's first/last name.
        """
        try:
            return [
                f"{first}.{last}@{domain}",
                f"{first[0]}{last}@{domain}",
                f"{first}{last[0]}@{domain}",
                f"{first}@{domain}",
                f"{last}@{domain}",
                f"{first}{last}@{domain}",
                f"{first}_{last}@{domain}",
                f"{first}-{last}@{domain}"
            ]
        except Exception as e:
            print(f"Error generating possible emails: {e}")
            return []

    def upadate_emails(self):
        """
        Update the person's email list using the domains available.
        Also adds alumni emails if applicable.
        """
        try:
            first, last = self.first.lower(), self.last.lower()
            for domain in self.domains:
                self.emails.extend(self.possible_emails(domain, first, last))
            if self.alumni:
                self.emails.extend(self.possible_emails('alumni.stanford.edu', first, last))
        except Exception as e:
            print(f"Error updating emails: {e}")

    def summary(self):
        """
        Generate a text summary of the person's profile to be used as input for the LLM.
        """
        try:
            output = []
            # Add basic info if available
            if self.first:
                output.append(f"First Name: {self.first}")
            if self.last:
                output.append(f"Last Name: {self.last}")
            if self.headline:
                output.append(f"Headline: {self.headline}")
            if self.location:
                output.append(f"Location: {self.location}")
            # Gender information based on the flag
            gender = 'Female' if self.female else 'Male/Unsure'
            output.append(f"Gender: {gender}")
            # About section
            if self.about:
                output.append(f"About: {self.about}")
            alumni_status = 'Yes' if self.alumni else 'No'
            output.append(f"Alumni: {alumni_status}")
            # Education information
            if self.education:
                output.append("Education:")
                for edu in self.education:
                    education_info = []
                    if edu.school:
                        education_info.append(f"School: {edu.school}")
                    if edu.degree:
                        education_info.append(f"Degree: {edu.degree}")
                    if edu.field:
                        education_info.append(f"Field: {edu.field}")
                    if education_info:
                        output.append(f"  - {', '.join(education_info)}")
            # Current job information
            if self.current_job:
                output.append("Current Experience:")
                for exp in self.current_job:
                    current_info = []
                    if exp.company:
                        current_info.append(f"Company: {exp.company}")
                    if exp.title:
                        current_info.append(f"Title: {exp.title}")
                    if exp.industry:
                        current_info.append(f"Industry: {exp.industry}")
                    if current_info:
                        output.append(f"  - {', '.join(current_info)}")
                    if exp.mission:
                        output.append(f"  - Mission: {exp.mission}")
            # Past experience information
            if self.past_experience:
                output.append("Past Experience:")
                for exp in self.past_experience:
                    past_info = []
                    if exp.company:
                        past_info.append(f"Company: {exp.company}")
                    if exp.title:
                        past_info.append(f"Title: {exp.title}")
                    if exp.industry:
                        past_info.append(f"Industry: {exp.industry}")
                    if past_info:
                        output.append(f"  - {', '.join(past_info)}")
            return "\n".join(output)
        except Exception as e:
            print(f"Error generating summary: {e}")
            return ""

    def experience_summary(self):
        """
        Generate a summary specifically for work experience.
        """
        try:
            summary = []
            summary.append(f"Headline: {self.headline if self.headline else 'None'}")
            if self.current_job:
                summary.append("Current Experience:")
                # Iterate over current jobs to list details
                for exp in self.current_job:
                    summary.append(f"  - {exp.title} at {exp.company}, in {exp.industry}.")
            else:
                summary.append("Current Experience: None")
            return "\n".join(summary)
        except Exception as e:
            print(f"Error generating experience summary: {e}")
            return ""

# Email Automation Functions

def send_bcc_emails(possible_emails_text, subject, body):
    """
    Send an email to a list of potential emails using an AppleScript.
    """
    try:
        # Locate the BCC AppleScript file relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, 'guess_send_email.scpt')
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"BCC email script not found: {script_path}")
        # Execute the AppleScript via subprocess
        subprocess.check_call(['osascript', script_path, possible_emails_text, subject, body])
    except subprocess.CalledProcessError as e:
        print(f"Error sending BCC emails: {e}")
    except Exception as e:
        print(f"Unexpected error in send_bcc_emails: {e}")

# LLM Functions

def compose_message(person_summary, prompt_file):
    """
    Compose a message by reading a prompt file, appending the person's summary, and sending it to the LLM.
    """
    try:
        # Ensure the API key is available
        api_key = os.getenv('OPENAI')
        if not api_key:
            raise EnvironmentError("OPENAI API key not found in environment variables.")
        llm_client = OpenAI(api_key=api_key)
        print("Person summary for LLM:\n", person_summary)
        # Check if the prompt file exists
        if not os.path.exists(prompt_file):
            raise FileNotFoundError(f"Prompt file '{prompt_file}' does not exist.")
        # Read the content of the prompt file
        with open(prompt_file, 'r') as file:
            prompt_content = file.read()
        # Combine prompt content with the person's summary
        prompt = prompt_content + "\n\n" + person_summary
        model = LARGER_MODEL  # The model being used for LLM
        response = llm_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        response_message = response.choices[0].message.content
        return response_message
    except Exception as e:
        print("Error composing message:")
        traceback.print_exc()
        return ""

def is_female_name(first_name):
    """
    Determine if the given first name is typically female by querying the LLM.
    """
    try:
        api_key = os.getenv('OPENAI')
        if not api_key:
            raise EnvironmentError("OPENAI API key not found in environment variables.")
        client = OpenAI(api_key=api_key)
        # System prompt asking if the name is typically female
        sys_prompt = (
            f"Is the name '{first_name}' typically female? "
            "Respond with 'True' if it is female, and 'False' if it is male or if the gender of the name is ambiguous."
        )
        model = SMALLER_MODEL
        system_prompt = {"role": "system", "content": sys_prompt}
        response = client.chat.completions.create(model=model, messages=[system_prompt])
        answer = response.choices[0].message.content.strip().lower()
        if answer == 'true':
            return True
        elif answer == 'false':
            return False
        else:
            print('Invalid response for gender:', answer)
            return False
    except Exception as e:
        print("Error determining gender:")
        traceback.print_exc()
        return False

def get_mission(company):
    """
    Retrieve the mission of the specified company using the LLM.
    """
    try:
        api_key = os.getenv('OPENAI')
        if not api_key:
            raise EnvironmentError("OPENAI API key not found in environment variables.")
        client = OpenAI(api_key=api_key)
        # System prompt asking for the company's mission in a specific format
        sys_prompt = (
            f"Respond with the mission of the tech company {company}. "
            "Respond with ONLY the mission of this company in the format 'to __'. Be specific. "
            "If you are unsure, respond only with 'False'"
        )
        model = MEDIUM_MODEL
        system_prompt = {"role": "system", "content": sys_prompt}
        response = client.chat.completions.create(model=model, messages=[system_prompt])
        answer = response.choices[0].message.content.strip().lower()
        if answer != 'false':
            return answer
        return ''
    except Exception as e:
        print(f"Error getting mission for {company}: {e}")
        traceback.print_exc()
        return ''

def get_prompt(person_summary):
    """
    Select a prompt file based on the person's summary using the LLM to choose from available options.
    """
    try:
        api_key = os.getenv('OPENAI')
        if not api_key:
            raise EnvironmentError("OPENAI API key not found in environment variables.")
        client = OpenAI(api_key=api_key)
        # Locate the prompt selection file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_selection_file = os.path.join(script_dir, "prompts", 'prompt-selection.txt')
        if not os.path.exists(prompt_selection_file):
            raise FileNotFoundError(f"Prompt selection file '{prompt_selection_file}' does not exist.")
        # Read the content of the prompt selection file
        with open(prompt_selection_file, 'r') as file:
            sys_prompt_content = file.read()
        model = MEDIUM_MODEL
        system_prompt = {"role": "system", "content": sys_prompt_content}
        user_prompt = {"role": "user", "content": person_summary}
        response = client.chat.completions.create(model=model, messages=[system_prompt, user_prompt])
        # The answer should be the name of the prompt file (in lowercase)
        answer = response.choices[0].message.content.strip().lower()
        prompt_file = os.path.join(script_dir, "prompts", answer)
        if not os.path.exists(prompt_file):
            raise FileNotFoundError(f"The prompt file '{prompt_file}' does not exist.")
        return prompt_file
    except Exception as e:
        print("Error selecting prompt:")
        traceback.print_exc()
        raise e

# LinkedIn Scraper Functions

def get_person(data):
    """
    Parse the JSON data from the LinkedIn scraper and populate a Person object.
    """
    try:
        data = data['person']
        person = Person()
        # Extract basic profile details
        person.first = data.get('firstName', '')
        person.last = data.get('lastName', '')
        person.headline = data.get('headline', '')
        person.location = data.get('location', '')
        person.about = data.get('summary', '')
        person.female = is_female_name(person.first)
        # Limit experience processing to a maximum of 3 entries
        num_exp = data['positions'].get('positionsCount', 0)
        num_exp = num_exp if num_exp < 3 else 3

        # Process work experience entries
        for i in range(num_exp):
            experience = person.Experience()
            exp = data['positions']['positionHistory'][i]
            experience.company = exp.get('companyName', '')
            experience.title = exp.get('title', '')
            experience.description = exp.get('description', '')

            # If the experience is current (i.e., no end date provided)
            if not exp.get('startEndDate', {}).get('end'):
                company_data = webscrape(exp.get('linkedInUrl', ''), 'company')
                if company_data and 'company' in company_data:
                    company_data = company_data['company']
                    website = company_data.get('websiteUrl', '')
                    if website:
                        person.domains.append(get_domain_from_url(website))
                    experience.industry = company_data.get('industry', '')
                    person.current_job.append(experience)
            else:
                person.past_experience.append(experience)

        # Retrieve mission for the first current job if available
        if person.current_job:
            person.current_job[0].mission = get_mission(person.current_job[0].company)
        # Limit education processing to a maximum of 3 entries
        num_ed = data['schools'].get('educationsCount', 0)
        num_ed = num_ed if num_ed < 3 else 3

        # Process education entries
        for i in range(num_ed):
            education = person.Education()
            edu = data['schools']['educationHistory'][i]
            education.school = edu.get('schoolName', '')
            education.degree = edu.get('degreeName', '')
            field = edu.get('fieldOfStudy', '')
            education.field = field if field != education.degree else ""
            # Check if the school matches the target university for alumni status
            if MY_UNIVERSITY.lower() in education.school.lower():
                person.alumni = True
            person.education.append(education)

        return person
    except Exception as e:
        print("Error parsing person data:")
        traceback.print_exc()
        raise e

def webscrape(linkedin_url, type):
    """
    Query the Scrapin API to retrieve data for a given LinkedIn URL.
    The 'type' parameter determines if the query is for 'profile' or 'company' data.
    """
    try:
        if type not in ['profile', 'company']:
            raise ValueError("Invalid type for webscrape. Must be 'profile' or 'company'.")
        url = f"https://api.scrapin.io/enrichment/{type}"
        api_key = os.getenv('SCRAPIN')
        if not api_key:
            raise EnvironmentError("SCRAPIN API key not found in environment variables.")
        params = {"linkedInUrl": linkedin_url, "apikey": api_key}
        response = requests.get(url, params=params)
        # Check for successful HTTP response
        if response.status_code == 200:
            # Clean up the response string and decode JSON
            response_string = response.text.strip("()").strip("'")
            try:
                data = json.loads(response_string)
                return data
            except json.JSONDecodeError as json_err:
                print("Error decoding JSON response from scrapin API:", json_err)
                return {}
        elif response.status_code == 400 and type == 'company':
            print("Company data not found (400).")
            return {}
        else:
            print(f"Request failed with status code: {response.status_code}")
            return {}
    except requests.RequestException as req_err:
        print("Request error during webscrape:", req_err)
        return {}
    except Exception as e:
        print("Unexpected error in webscrape:")
        traceback.print_exc()
        return {}

def get_domain_from_url(url):
    """
    Extract the domain from a given URL.
    """
    try:
        if not url:
            return ""
        # Remove the scheme (http, https, etc.)
        if "://" in url:
            url = url.split("://")[1]
        # Get the domain (portion before the first '/')
        domain = url.split('/')[0]
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except Exception as e:
        print("Error extracting domain from URL:", e)
        return ""

# Main Loop

def main():
    """
    Main function for running the cold emailing automation tool.
    Handles user input, processes LinkedIn data, composes an email, and sends it.
    """
    try:
        print("\nWelcome to The Cold Emailing Automation Tool! Enter a LinkedIn URL to get started.")
        while True:
            # Prompt user for a LinkedIn URL
            linkedin_url = input("Enter LinkedIn URL: ").strip()
            if not linkedin_url:
                print("Empty input, please enter a valid LinkedIn URL.")
                continue
            # Validate the LinkedIn URL format
            if "https://www.linkedin.com/in/" not in linkedin_url:
                print("Invalid LinkedIn URL. Please enter a valid LinkedIn URL. Example: https://linkedin.com/in/janedoe")
                continue
            # Scrape the profile data from LinkedIn using Scrapin
            profile_data = webscrape(linkedin_url, 'profile')
            if not profile_data:
                print("Failed to retrieve profile data. Please check the URL or try again later.")
                continue
            # Parse the profile data into a Person object
            person = get_person(profile_data)
            person_summary = person.summary()
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Determine which prompt file to use (multiple prompts vs. a default prompt)
            if MULTIPLE_PROMPTS:
                prompt_file = get_prompt(person_summary)
            else:
                prompt_file = os.path.join(script_dir, "prompts", PROMPT_FILE)
            subject = SUBJECT_LINE
            # Compose the email message using the LLM
            body = compose_message(person_summary, prompt_file)
            if not body:
                print("Failed to compose email message. Aborting email sending.")
                continue
            # Update email list based on potential domains
            person.upadate_emails()
            if not person.emails:
                print("No possible emails generated. Aborting.")
                continue
            possible_emails_text = ",".join(person.emails)
            # Send the email using the BCC email script
            send_bcc_emails(possible_emails_text, subject, body)
            print("Email composed successfully")
    except Exception as e:
        print("An error occurred in the main loop:")
        traceback.print_exc()

# Entry Point

if __name__ == '__main__':
    try:
        # Load environment variables from a .env file if present
        load_dotenv()
    except Exception as e:
        print("Error loading environment variables:", e)
    main()