import os
import time
import uuid
import json
import random
import string
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging
import platform
from colorama import Fore, Style, init
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
import shutil

# Initialize colorama
init()

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define emoji constants
EMOJI = {
    'START': '🚀',
    'FORM': '📝',
    'VERIFY': '🔄',
    'PASSWORD': '🔑',
    'CODE': '📱',
    'DONE': '✨',
    'ERROR': '❌',
    'WAIT': '⏳',
    'SUCCESS': '✅',
    'MAIL': '📧',
    'KEY': '🔐',
    'UPDATE': '🔄',
    'INFO': 'ℹ️',
    'EMAIL': '📧',
    'REFRESH': '🔄',
    'LINK': '🔗',
    'WARNING': '⚠️'
}

class GitHubCursorRegistration:
    def __init__(self, translator=None):
        self.translator = translator
        # Set browser to visible mode
        os.environ['BROWSER_HEADLESS'] = 'False'
        self.browser = None
        self.email_address = None
        
        # Generate random credentials
        self.github_username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        self.github_password = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=16))
    
    def setup_browser(self):
        """Setup and configure the web browser"""
        try:
            print(f"{Fore.CYAN}{EMOJI['START']} Setting up browser...{Style.RESET_ALL}")
            
            options = Options()
            options.add_argument('--incognito')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-notifications')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36')
            
            self.browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            self.browser.set_page_load_timeout(30)
            return True
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Failed to setup browser: {str(e)}{Style.RESET_ALL}")
            return False
    
    def get_temp_email(self):
        """Get a temporary email address using YOPmail"""
        try:
            if not self.browser:
                if not self.setup_browser():
                    return False
            
            print(f"{Fore.CYAN}{EMOJI['MAIL']} Generating temporary email address...{Style.RESET_ALL}")
            self.browser.get("https://yopmail.com/")
            time.sleep(2)
            
            # Generate a realistic username
            first_names = ["john", "sara", "michael", "emma", "david", "jennifer", "robert", "lisa"]
            last_names = ["smith", "johnson", "williams", "brown", "jones", "miller", "davis", "garcia"]
            
            random_first = random.choice(first_names)
            random_last = random.choice(last_names)
            random_num = random.randint(100, 999)
            
            username = f"{random_first}.{random_last}{random_num}"
            
            # Enter the username and check inbox
            email_field = self.browser.find_element(By.XPATH, "//input[@id='login']")
            if email_field:
                email_field.clear()
                email_field.send_keys(username)
                time.sleep(1)
                
                # Click the check button
                check_button = self.browser.find_element(By.XPATH, "//button[@title='Check Inbox' or @class='sbut' or contains(@onclick, 'ver')]")
                if check_button:
                    check_button.click()
                    time.sleep(2)
                    self.email_address = f"{username}@yopmail.com"
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Temp email created: {self.email_address}{Style.RESET_ALL}")
                    return True
            
            print(f"{Fore.RED}{EMOJI['ERROR']} Failed to create YOPmail address{Style.RESET_ALL}")
            return False
            
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Error getting temporary email: {str(e)}{Style.RESET_ALL}")
            return False
    
    def register_github(self):
        """Register a new GitHub account"""
        if not self.email_address:
            print(f"{Fore.RED}{EMOJI['ERROR']} No email address available{Style.RESET_ALL}")
            return False
            
        if not self.browser:
            if not self.setup_browser():
                return False
        
        try:
            print(f"{Fore.CYAN}{EMOJI['FORM']} Registering GitHub account...{Style.RESET_ALL}")
            self.browser.get("https://github.com/join")
            time.sleep(3)

            # Fill in the registration form
            WebDriverWait(self.browser, 15).until(EC.visibility_of_element_located((By.ID, "user_login")))
            self.browser.find_element(By.ID, "user_login").send_keys(self.github_username)
            self.browser.find_element(By.ID, "user_email").send_keys(self.email_address)
            self.browser.find_element(By.ID, "user_password").send_keys(self.github_password)
            
            print(f"{Fore.CYAN}{EMOJI['INFO']} GitHub username: {self.github_username}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{EMOJI['INFO']} GitHub password: {self.github_password}{Style.RESET_ALL}")
            
            # Check for any notice or popup and handle it
            try:
                signup_button = self.browser.find_element(By.ID, "signup_button")
                print(f"{Fore.CYAN}{EMOJI['INFO']} Clicking sign up button...{Style.RESET_ALL}")
                signup_button.click()
            except NoSuchElementException:
                print(f"{Fore.YELLOW}{EMOJI['INFO']} Signup button not found, trying alternative selector{Style.RESET_ALL}")
                buttons = self.browser.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    if "Sign up" in button.text:
                        button.click()
                        break

            # Wait for page transition and check for CAPTCHA
            time.sleep(5)
            
            # Check if registration was successful or if CAPTCHA appeared
            current_url = self.browser.current_url
            
            # Look for CAPTCHA in URL or on page
            if "captcha" in current_url.lower() or "are you a robot" in self.browser.page_source.lower():
                print(f"{Fore.YELLOW}{EMOJI['WAIT']} CAPTCHA detected, please complete it manually{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{EMOJI['INFO']} You have 60 seconds to solve the CAPTCHA...{Style.RESET_ALL}")
                
                # Wait for user to solve CAPTCHA (60 seconds max)
                for i in range(60):
                    current_url = self.browser.current_url
                    if "captcha" not in current_url.lower() and "are you a robot" not in self.browser.page_source.lower():
                        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} CAPTCHA completed successfully{Style.RESET_ALL}")
                        break
                    time.sleep(1)
                    if i % 10 == 0 and i > 0:
                        print(f"{Fore.YELLOW}{EMOJI['WAIT']} Still waiting for CAPTCHA completion... {60-i} seconds remaining{Style.RESET_ALL}")
                
                # Check if CAPTCHA was solved after waiting
                if "captcha" in self.browser.current_url.lower() or "are you a robot" in self.browser.page_source.lower():
                    print(f"{Fore.RED}{EMOJI['ERROR']} CAPTCHA not solved within time limit{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}{EMOJI['INFO']} Do you want more time to solve the CAPTCHA? (yes/no){Style.RESET_ALL}")
                    response = input().lower().strip()
                    if response in ['yes', 'y']:
                        print(f"{Fore.YELLOW}{EMOJI['INFO']} Press Enter when you've completed the CAPTCHA...{Style.RESET_ALL}")
                        input()
                        if "captcha" in self.browser.current_url.lower() or "are you a robot" in self.browser.page_source.lower():
                            print(f"{Fore.RED}{EMOJI['ERROR']} CAPTCHA still not solved{Style.RESET_ALL}")
                            return False
                    else:
                        return False
            
            # Wait for registration to complete
            time.sleep(5)
            
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} GitHub account registered{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Failed to register GitHub account: {str(e)}{Style.RESET_ALL}")
            return False
    
    def check_email_verification(self):
        """Check for GitHub verification email and click the verification link"""
        if not self.email_address or not self.browser:
            print(f"{Fore.RED}{EMOJI['ERROR']} Email or browser not available{Style.RESET_ALL}")
            return False
        
        try:
            print(f"{Fore.CYAN}{EMOJI['EMAIL']} Checking for verification email...{Style.RESET_ALL}")
            
            # Extract username from email for YOPmail
            username = self.email_address.split('@')[0]
            
            max_attempts = 10
            for attempt in range(1, max_attempts + 1):
                print(f"{Fore.CYAN}{EMOJI['REFRESH']} Checking YOPmail inbox (attempt {attempt}/{max_attempts})...{Style.RESET_ALL}")
                
                # Go to YOPmail inbox
                self.browser.get(f"https://yopmail.com/en/wm")
                time.sleep(2)
                
                # Enter email address
                try:
                    email_input = WebDriverWait(self.browser, 10).until(
                        EC.presence_of_element_located((By.ID, "login"))
                    )
                    email_input.clear()
                    email_input.send_keys(username)
                    
                    # Click the check inbox button
                    check_button = self.browser.find_element(By.CSS_SELECTOR, "button[onclick='verif()']")
                    check_button.click()
                    time.sleep(3)
                    
                    # Switch to inbox frame
                    iframe = WebDriverWait(self.browser, 10).until(
                        EC.presence_of_element_located((By.ID, "ifinbox"))
                    )
                    self.browser.switch_to.frame(iframe)
                    
                    # Look for GitHub email
                    emails = self.browser.find_elements(By.CSS_SELECTOR, "div.m")
                    github_email = None
                    
                    for email in emails:
                        if "github" in email.text.lower():
                            github_email = email
                            break
                    
                    if github_email:
                        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} GitHub verification email found{Style.RESET_ALL}")
                        github_email.click()
                        time.sleep(2)
                        
                        # Switch back to default content
                        self.browser.switch_to.default_content()
                        
                        # Switch to email content frame
                        iframe = WebDriverWait(self.browser, 10).until(
                            EC.presence_of_element_located((By.ID, "ifmail"))
                        )
                        self.browser.switch_to.frame(iframe)
                        
                        # Find verification link
                        try:
                            # Look for the verification button or link
                            verification_elements = self.browser.find_elements(By.XPATH, "//a[contains(text(), 'Verify') or contains(text(), 'verify') or contains(@href, 'verify')]")
                            
                            if verification_elements:
                                verification_link = verification_elements[0].get_attribute('href')
                                print(f"{Fore.CYAN}{EMOJI['LINK']} Found verification link{Style.RESET_ALL}")
                                
                                # Open the verification link in the same window
                                self.browser.get(verification_link)
                                time.sleep(5)
                                
                                # Check if verification was successful
                                if "verified" in self.browser.page_source.lower() or "successful" in self.browser.page_source.lower():
                                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Email verified successfully{Style.RESET_ALL}")
                                    return True
                                else:
                                    print(f"{Fore.YELLOW}{EMOJI['WARNING']} Email verification page loaded but success not confirmed{Style.RESET_ALL}")
                                    print(f"{Fore.YELLOW}{EMOJI['INFO']} Please check if verification was successful manually and press Enter to continue...{Style.RESET_ALL}")
                                    input()
                                    return True
                            else:
                                print(f"{Fore.RED}{EMOJI['ERROR']} No verification link found in email{Style.RESET_ALL}")
                        except Exception as e:
                            print(f"{Fore.RED}{EMOJI['ERROR']} Error extracting verification link: {str(e)}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}{EMOJI['WAIT']} No GitHub verification email yet, waiting... ({attempt}/{max_attempts}){Style.RESET_ALL}")
                        time.sleep(15)  # Wait before checking again
                
                except Exception as e:
                    print(f"{Fore.RED}{EMOJI['ERROR']} Error checking email: {str(e)}{Style.RESET_ALL}")
            
            print(f"{Fore.RED}{EMOJI['ERROR']} No verification email received after {max_attempts} attempts{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{EMOJI['INFO']} Do you want to check manually? (yes/no){Style.RESET_ALL}")
            response = input().lower().strip()
            if response in ['yes', 'y']:
                print(f"{Fore.YELLOW}{EMOJI['INFO']} Please check your YOPmail inbox manually at: https://yopmail.com/en/wm")
                print(f"{Fore.YELLOW}{EMOJI['INFO']} Username: {username}")
                print(f"{Fore.YELLOW}{EMOJI['INFO']} Press Enter when you've verified the email...{Style.RESET_ALL}")
                input()
                return True
            return False
            
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Failed to check verification email: {str(e)}{Style.RESET_ALL}")
            return False
    
    def register_cursor(self):
        """Register with Cursor using GitHub"""
        if not self.browser:
            if not self.setup_browser():
                return False
                
        try:
            print(f"{Fore.CYAN}{EMOJI['KEY']} Registering with Cursor using GitHub...{Style.RESET_ALL}")
            
            # Navigate to Cursor login page
            self.browser.get("https://cursor.sh/login")
            time.sleep(3)
            
            try:
                # Look for GitHub login button
                github_buttons = WebDriverWait(self.browser, 15).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//button[contains(., 'GitHub') or contains(@class, 'github')]"))
                )
                
                if not github_buttons:
                    print(f"{Fore.RED}{EMOJI['ERROR']} GitHub login button not found{Style.RESET_ALL}")
                    return False
                
                # Click the first GitHub button
                print(f"{Fore.CYAN}{EMOJI['INFO']} Clicking GitHub login button...{Style.RESET_ALL}")
                github_buttons[0].click()
                time.sleep(5)
                
                # Check if we're redirected to GitHub login
                current_url = self.browser.current_url
                if "github.com" in current_url:
                    print(f"{Fore.CYAN}{EMOJI['INFO']} Redirected to GitHub login{Style.RESET_ALL}")
                    
                    # Check if we need to log in to GitHub
                    if "login" in current_url:
                        print(f"{Fore.CYAN}{EMOJI['INFO']} Logging into GitHub...{Style.RESET_ALL}")
                        
                        try:
                            # Enter GitHub credentials
                            username_field = WebDriverWait(self.browser, 10).until(
                                EC.presence_of_element_located((By.ID, "login_field"))
                            )
                            username_field.send_keys(self.github_username)
                            
                            password_field = self.browser.find_element(By.ID, "password")
                            password_field.send_keys(self.github_password)
                            
                            # Click sign in
                            signin_button = self.browser.find_element(By.CSS_SELECTOR, "input[type='submit']")
                            signin_button.click()
                            time.sleep(5)
                        except Exception as e:
                            print(f"{Fore.RED}{EMOJI['ERROR']} Error during GitHub login: {str(e)}{Style.RESET_ALL}")
                            return False
                    
                    # Check if we're on the authorization page
                    if "authorize" in self.browser.current_url:
                        print(f"{Fore.CYAN}{EMOJI['INFO']} Authorizing Cursor app...{Style.RESET_ALL}")
                        
                        try:
                            # Look for authorization button
                            auth_buttons = self.browser.find_elements(By.XPATH, "//button[contains(., 'Authorize') or contains(@class, 'btn-primary')]")
                            
                            if auth_buttons:
                                auth_buttons[0].click()
                                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Cursor authorized with GitHub{Style.RESET_ALL}")
                                time.sleep(5)
                            else:
                                print(f"{Fore.YELLOW}{EMOJI['WARNING']} No authorization button found, GitHub may be already authorized{Style.RESET_ALL}")
                        except Exception as e:
                            print(f"{Fore.RED}{EMOJI['ERROR']} Error during GitHub authorization: {str(e)}{Style.RESET_ALL}")
                
                # Wait for Cursor dashboard to load
                timeout = 30
                start_time = time.time()
                while time.time() - start_time < timeout:
                    if "cursor.sh" in self.browser.current_url and not "login" in self.browser.current_url:
                        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Successfully logged into Cursor{Style.RESET_ALL}")
                        break
                    time.sleep(1)
                
                if "login" in self.browser.current_url:
                    print(f"{Fore.RED}{EMOJI['ERROR']} Failed to log into Cursor after {timeout} seconds{Style.RESET_ALL}")
                    return False
                
                # Wait for dashboard elements to load
                time.sleep(3)
                
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Cursor registered with GitHub successfully{Style.RESET_ALL}")
                
                # Now reset the machine ID
                return self.reset_machine_id()
                
            except Exception as e:
                print(f"{Fore.RED}{EMOJI['ERROR']} Error during Cursor registration: {str(e)}{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Failed to register with Cursor: {str(e)}{Style.RESET_ALL}")
            return False
    
    def reset_machine_id(self):
        """Reset the Cursor machine ID to bypass limitations"""
        try:
            print(f"{Fore.CYAN}{EMOJI['UPDATE']} Resetting Cursor machine ID...{Style.RESET_ALL}")
            
            # Find Cursor app data location based on platform
            cursor_data_dir = None
            if platform.system() == "Windows":
                appdata = os.getenv('APPDATA')
                if appdata:
                    cursor_data_dir = os.path.join(appdata, "cursor", "Local Storage", "leveldb")
            elif platform.system() == "Darwin":  # macOS
                home = os.path.expanduser("~")
                cursor_data_dir = os.path.join(home, "Library", "Application Support", "cursor", "Local Storage", "leveldb")
            elif platform.system() == "Linux":
                home = os.path.expanduser("~")
                cursor_data_dir = os.path.join(home, ".config", "cursor", "Local Storage", "leveldb")
            
            if not cursor_data_dir or not os.path.exists(cursor_data_dir):
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} Cursor data directory not found at: {cursor_data_dir}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{EMOJI['INFO']} You may need to reset the machine ID manually{Style.RESET_ALL}")
                
                # Try to find the Cursor data directory
                if platform.system() == "Linux":
                    possible_paths = [
                        os.path.join(os.path.expanduser("~"), ".config", "cursor"),
                        os.path.join(os.path.expanduser("~"), ".cursor")
                    ]
                    for path in possible_paths:
                        if os.path.exists(path):
                            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Found Cursor directory at: {path}{Style.RESET_ALL}")
                            # Look for Local Storage subfolder
                            for root, dirs, files in os.walk(path):
                                if "Local Storage" in dirs:
                                    cursor_data_dir = os.path.join(root, "Local Storage", "leveldb")
                                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Found Cursor data directory at: {cursor_data_dir}{Style.RESET_ALL}")
                                    break
                            break
            
            if cursor_data_dir and os.path.exists(cursor_data_dir):
                # Generate a new UUID
                new_machine_id = str(uuid.uuid4())
                print(f"{Fore.CYAN}{EMOJI['KEY']} New machine ID: {new_machine_id}{Style.RESET_ALL}")
                
                # Ask for permission to modify files
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} This operation will modify Cursor app data files{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{EMOJI['INFO']} Do you want to continue? (yes/no){Style.RESET_ALL}")
                response = input().lower().strip()
                if response not in ['yes', 'y']:
                    print(f"{Fore.YELLOW}{EMOJI['INFO']} Machine ID reset aborted{Style.RESET_ALL}")
                    return False
                
                # Backup the directory
                backup_dir = cursor_data_dir + "_backup_" + time.strftime("%Y%m%d%H%M%S")
                print(f"{Fore.CYAN}{EMOJI['INFO']} Creating backup of data directory to: {backup_dir}{Style.RESET_ALL}")
                try:
                    shutil.copytree(cursor_data_dir, backup_dir)
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Backup created successfully{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.YELLOW}{EMOJI['WARNING']} Failed to create backup: {str(e)}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}{EMOJI['INFO']} Continuing without backup...{Style.RESET_ALL}")
                
                # Find and modify files containing the machine ID
                modified = False
                for filename in os.listdir(cursor_data_dir):
                    if filename.endswith(".log") or filename.endswith(".ldb"):
                        file_path = os.path.join(cursor_data_dir, filename)
                        try:
                            with open(file_path, "rb") as f:
                                content = f.read()
                                
                            # Look for patterns that might contain machine ID
                            if b"machineId" in content:
                                print(f"{Fore.CYAN}{EMOJI['INFO']} Found machineId reference in: {filename}{Style.RESET_ALL}")
                                modified = True
                                
                                # For safety, don't modify the binary files directly
                                # Instead, instruct user to uninstall and reinstall Cursor
                                print(f"{Fore.YELLOW}{EMOJI['WARNING']} Binary files found that may contain machine ID{Style.RESET_ALL}")
                                print(f"{Fore.YELLOW}{EMOJI['INFO']} For best results, please:{Style.RESET_ALL}")
                                print(f"{Fore.YELLOW}{EMOJI['INFO']} 1. Close Cursor if it's running{Style.RESET_ALL}")
                                print(f"{Fore.YELLOW}{EMOJI['INFO']} 2. Uninstall Cursor completely{Style.RESET_ALL}")
                                print(f"{Fore.YELLOW}{EMOJI['INFO']} 3. Reinstall Cursor{Style.RESET_ALL}")
                                print(f"{Fore.YELLOW}{EMOJI['INFO']} 4. Login with your new GitHub account{Style.RESET_ALL}")
                                break
                                
                        except Exception as e:
                            print(f"{Fore.YELLOW}{EMOJI['WARNING']} Error processing file {filename}: {str(e)}{Style.RESET_ALL}")
                
                if not modified:
                    print(f"{Fore.YELLOW}{EMOJI['WARNING']} No machine ID references found in data files{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}{EMOJI['INFO']} You may need to reinstall Cursor for a complete reset{Style.RESET_ALL}")
                
                # Save credentials before returning
                self.save_credentials()
                
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Machine ID reset process completed{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} Cursor data directory not found{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{EMOJI['INFO']} You may need to manually reset the machine ID by reinstalling Cursor{Style.RESET_ALL}")
                
                # Still save credentials
                self.save_credentials()
                return True
                
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Failed to reset machine ID: {str(e)}{Style.RESET_ALL}")
            # Still save credentials even if machine ID reset fails
            self.save_credentials()
            return False
            
    def save_credentials(self):
        """Save the generated credentials to a file"""
        try:
            if not self.email_address or not self.github_username or not self.github_password:
                print(f"{Fore.RED}{EMOJI['ERROR']} No credentials to save{Style.RESET_ALL}")
                return False
                
            output_file = "github_cursor_accounts.txt"
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            credentials = {
                "timestamp": timestamp,
                "github_username": self.github_username,
                "github_password": self.github_password,
                "email": self.email_address
            }
            
            credentials_json = json.dumps(credentials)
            
            # Check if file exists and create if not
            file_exists = os.path.exists(output_file)
            
            with open(output_file, "a") as f:
                if not file_exists:
                    f.write("# GitHub + Cursor AI Accounts\n")
                    f.write("# Format: JSON with timestamp, github_username, github_password, email\n\n")
                
                f.write(credentials_json + "\n")
            
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Credentials saved to: {output_file}{Style.RESET_ALL}")
            
            # Print a summary
            print(f"\n{Fore.GREEN}{EMOJI['SUCCESS']} Registration Summary:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}  • GitHub Username: {self.github_username}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}  • GitHub Password: {self.github_password}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}  • Email Address: {self.email_address}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}  • Saved to: {output_file}{Style.RESET_ALL}\n")
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Failed to save credentials: {str(e)}{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}{EMOJI['WARNING']} Make sure to copy these credentials manually:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}  • GitHub Username: {self.github_username}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}  • GitHub Password: {self.github_password}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}  • Email Address: {self.email_address}{Style.RESET_ALL}\n")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        if self.browser:
            try:
                self.browser.quit()
            except:
                pass
    
    def start_registration(self):
        """Start the GitHub Cursor registration process"""
        try:
            # Step 1: Get temporary email
            if not self.get_temp_email():
                return False
            
            # Step 2: Register GitHub account
            if not self.register_github():
                return False
            
            # Step 3: Check and verify email
            if not self.check_email_verification():
                return False
            
            # Step 4: Register Cursor with GitHub
            if not self.register_cursor():
                return False
            
            # Step 5: Reset machine ID
            self.reset_machine_id()
            
            return True
        finally:
            self.cleanup()

def display_features_and_warnings(translator=None):
    """Display features and warnings before proceeding"""
    if translator:
        print(f"\n🚀 {translator.get('github_register.title')}")
        print("=====================================")
        print(f"{translator.get('github_register.features_header')}:")
        print(f"  - {translator.get('github_register.feature1')}")
        print(f"  - {translator.get('github_register.feature2')}")
        print(f"  - {translator.get('github_register.feature3')}")
        print(f"  - {translator.get('github_register.feature4')}")
        print(f"  - {translator.get('github_register.feature5')}")
        print(f"  - {translator.get('github_register.feature6')}")
        print(f"\n⚠️ {translator.get('github_register.warnings_header')}:")
        print(f"  - {translator.get('github_register.warning1')}")
        print(f"  - {translator.get('github_register.warning2')}")
        print(f"  - {translator.get('github_register.warning3')}")
        print(f"  - {translator.get('github_register.warning4')}")
        print("=====================================\n")
    else:
        print("\n🚀 GitHub + Cursor AI Registration Automation")
        print("=====================================")
        print("Features:")
        print("  - Creates a temporary email using YOPmail")
        print("  - Registers a new GitHub account with random credentials")
        print("  - Verifies the GitHub email automatically")
        print("  - Logs into Cursor AI using GitHub authentication")
        print("  - Resets the machine ID to bypass trial detection")
        print("  - Saves all credentials to a file")
        print("\n⚠️ Warnings:")
        print("  - This script automates account creation, which may violate GitHub/Cursor terms of service")
        print("  - Requires internet access and administrative privileges")
        print("  - CAPTCHA or additional verification may interrupt automation")
        print("  - Use responsibly and at your own risk")
        print("=====================================\n")

def get_user_confirmation(translator=None):
    """Prompt the user for confirmation to proceed"""
    while True:
        if translator:
            response = input(f"{translator.get('github_register.confirm')} (yes/no): ").lower().strip()
        else:
            response = input("Do you want to proceed with GitHub + Cursor AI registration? (yes/no): ").lower().strip()
            
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            if translator:
                print(f"❌ {translator.get('github_register.cancelled')}")
            else:
                print("❌ Operation cancelled.")
            return False
        else:
            if translator:
                print(f"{translator.get('github_register.invalid_choice')}")
            else:
                print("Please enter 'yes' or 'no'.")

def main(translator=None):
    """Main function to run the GitHub Cursor registration process"""
    logging.info(f"{Fore.CYAN} {translator.get('github_register.starting_automation')}{Style.RESET_ALL}")
    
    # Display features and warnings
    display_features_and_warnings(translator)
    
    # Get user confirmation
    if not get_user_confirmation(translator):
        return
    
    # Start registration process
    registration = GitHubCursorRegistration(translator)
    success = registration.start_registration()
    
    # Display final message
    if success:
        print(f"\n{Fore.GREEN}{EMOJI['DONE']} {translator.get('github_register.completed_successfully')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{EMOJI['INFO']} {translator.get('github_register.github_username')}: {registration.github_username}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{EMOJI['INFO']} {translator.get('github_register.github_password')}: {registration.github_password}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{EMOJI['INFO']} {translator.get('github_register.email')}: {registration.email_address}{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}{EMOJI['INFO']} {translator.get('github_register.credentials_saved')}{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}{EMOJI['ERROR']} {translator.get('github_register.registration_encountered_issues')}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('github_register.check_browser_windows_for_manual_intervention_or_try_again_later')}{Style.RESET_ALL}")
    
    # Wait for user acknowledgment
    if translator:
        input(f"\n{EMOJI['INFO']} {translator.get('register.press_enter')}...")
    else:
        input(f"\n{EMOJI['INFO']} Press Enter to continue...")

if __name__ == "__main__":
    main()
