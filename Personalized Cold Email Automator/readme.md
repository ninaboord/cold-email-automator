# Cold Emailing Automation Tool

This tool automates the creation of hyper-personalized cold emails by scraping LinkedIn profiles and using an LLM (via OpenAI) to generate tailored email content. Simply provide a LinkedIn URL, and the script will open Apple Mail with a pre-composed email (body, subject, and BCC field). All you have to do is hit send!

> **Note:** This script is compatible **only with Apple Mail**.

---

## Features

- **LinkedIn Scraping:** Retrieves profile data and company details via the Scrapin API.
- **Email Personalization:** Uses LLM prompts to create personalized emails.
- **Multiple Email Guessing:** BCCs a list of possible email addresses based on the scraped profile.
- **Customizable Prompts:** Configure prompts in the `prompts` folder and select which one to use.

---

## Prerequisites

Ensure you have the following before starting:

- **Apple Mail** configured and open with your desired sending account.
- An [OpenAI](https://openai.com) account and API key (set as the `OPENAI` environment variable).
- A [Scrapin](https://scrapin.io) account and API key (set as the `SCRAPIN` environment variable).

Set these environment variables in a **.env** file (see instructions below).

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/cold-emailer.git
cd cold-emailer
```

### 2. (Optional) Create and Activate a Virtual Environment

#### macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Required Packages

```bash
pip install openai python-dotenv requests
```

**Packages Overview:**
- `openai`: To interact with the OpenAI API.
- `python-dotenv`: To load environment variables from a .env file.
- `requests`: For making HTTP requests to the Scrapin API.

### 4. Configuration

#### Environment Variables
Create a `.env` file in the project root and add your API keys:

```bash
OPENAI=sk-your-openai-api-key
SCRAPIN=sk-your-scrapin-api-key
```

> **Note:** Both services require paid accounts.

#### Global Variables
At the top of the script, you'll find key configuration variables:
- **`MY_UNIVERSITY`**: Sets the target university (e.g., `Stanford`) to determine alumni status.
- **`SUBJECT_LINE`**: Default subject line for emails (can be customized).
- **`MULTIPLE_PROMPTS`**: Boolean flag to select prompts dynamically or use a default prompt.
- **`PROMPT_FILE`**: Fallback prompt file if `MULTIPLE_PROMPTS` is set to `False`.
- **`SIMPLE_MODEL`** and **`LARGER_MODEL`**: Choose whichever openai models you would like to use. **`SMALLER_MODEL`** will handle simpler function tasks, while **`LARGER_MODEL`** will handle the email writing. Up to you which model to use, but make sure you use valid aliases specified on openai's API website if you decide to change them.

---

## Prompt Files

- **`prompts/prompt-selection.txt`**: Contains instructions for the LLM to analyze LinkedIn profiles and select a prompt file.
  - The response should be the filename of the selected prompt (e.g., `email_prompt.txt`).
- **`prompts/` folder**: Contains example prompts used by the LLM to generate emails. You can modify or add new ones.

### Tips for Writing Effective Prompts:
- Use clear and specific language.
- Include instructions on which LinkedIn details to reference.
- Test different prompts to optimize email output.

The script comes with examples in the prompts folder. You should modify them to suit your cold emailing needs. The reason why this tool uses templates is to ensure the email sounds like it was written like you -- not AI. You can use the following information in your prompt, as the AI is given the following information from the person's LinkedIn profile:

- First name
- Last name
- Headline
- Location
- About
- Education (school, degree, and field)
- Current company
- Current role/title
- Current company mission (note this is GPT generated based on the company, so it may be less accurate for startups)
- Current company description (from the company's page on LinkedIn)
- Past experience (companies and their roles)
- Gender (note that this is GPT generated based on their name, so if they have a nontraditional male/female name this could be incorrect)
- Whether or not they are an alumni (based off of the school you specifiy under **`MY_UNIVERSITY`**:)

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

---

## How It Works

1. **User Input**: Enter a LinkedIn URL in the terminal.
2. **Scraping**: The Scrapin API retrieves profile data (personal info, work experience, education, etc.).
3. **Email Generation**: The script summarizes the profile and sends it to OpenAI's API to generate a personalized email.
4. **Email Sending**: The email (with subject and BCC field filled) is opened in Apple Mail, ready for review and sending.

---

## Running the Script

Run the script directly from the terminal:

```bash
python entire/path/to/main.py
```

### Optional but Reccomended: Creating a Bash/Zsh Alias

To simplify execution, add an alias to your `.bashrc` or `.zshrc`:

```bash
alias email='/path/to/your/venv/bin/python -W "ignore:::urllib3" /path/to/your/project/main.py'
```

Example for a project located at `/Users/yourname/Code/ColdEmailer`:

```bash
alias email='/Users/yourname/Code/ColdEmailer/venv/bin/python -W "ignore:::urllib3" /Users/yourname/Code/ColdEmailer/main.py'
```

Reload your shell configuration:

```bash
source ~/.bashrc   # for bash
source ~/.zshrc    # for zsh
```

Now, simply type `email` in the terminal to run the tool.

---

## Final Notes

- **Email Sending**: Ensure you are logged into Apple Mail with your sending account before running the script.
- **No Code Changes Needed**: Modify only the configuration and prompt files; the script runs as-is.

Enjoy automating your cold emails!
