from oauth_auth import OAuthHandler
import time
from colorama import Fore, Style, init
import sys

# Initialize colorama
init()

# Define emoji constants
EMOJI = {
    'START': '🚀',
    'DELETE': '🗑️',
    'SUCCESS': '✅',
    'ERROR': '❌',
    'WAIT': '⏳',
    'INFO': 'ℹ️',
    'WARNING': '⚠️'
}

class CursorGoogleAccountDeleter(OAuthHandler):
    def __init__(self, translator=None):
        super().__init__(translator, auth_type='google')
        
    def delete_google_account(self):
        """Delete Cursor account using Google OAuth"""
        try:
            # Setup browser and select profile
            if not self.setup_browser():
                return False
                
            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('account_delete.starting_process') if self.translator else 'Starting account deletion process...'}{Style.RESET_ALL}")
            
            # Navigate to Cursor auth page - using the same URL as in registration
            self.browser.get("https://authenticator.cursor.sh/sign-up")
            time.sleep(2)
            
            # Click Google auth button using same selectors as in registration
            selectors = [
                "//a[contains(@href,'GoogleOAuth')]",
                "//a[contains(@class,'auth-method-button') and contains(@href,'GoogleOAuth')]",
                "(//a[contains(@class,'auth-method-button')])[1]"  # First auth button as fallback
            ]
            
            auth_btn = None
            for selector in selectors:
                try:
                    auth_btn = self.browser.ele(f"xpath:{selector}", timeout=2)
                    if auth_btn:
                        break
                except:
                    continue
            
            if not auth_btn:
                raise Exception(self.translator.get('account_delete.google_button_not_found') if self.translator else "Google login button not found")
                
            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('account_delete.logging_in') if self.translator else 'Logging in with Google...'}{Style.RESET_ALL}")
            auth_btn.click()
            
            # Wait for authentication to complete using a more robust method
            print(f"{Fore.CYAN}{EMOJI['WAIT']} {self.translator.get('account_delete.waiting_for_auth', fallback='Waiting for Google authentication...')}{Style.RESET_ALL}")
            
            # Dynamic wait for authentication
            max_wait_time = 120  # Increase maximum wait time to 120 seconds
            start_time = time.time()
            check_interval = 3  # Check every 3 seconds
            google_account_alert_shown = False  # Track if we've shown the alert already
            
            while time.time() - start_time < max_wait_time:
                current_url = self.browser.url
                
                # If we're already on the settings or dashboard page, we're successful
                if "/dashboard" in current_url or "/settings" in current_url or "cursor.com" in current_url:
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('account_delete.login_successful') if self.translator else 'Login successful'}{Style.RESET_ALL}")
                    break
                    
                # If we're on Google accounts page or accounts.google.com, wait for user selection
                if "accounts.google.com" in current_url:
                    # Only show the alert once to avoid spamming
                    if not google_account_alert_shown:
                        print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('account_delete.select_google_account', fallback='Please select your Google account...')}{Style.RESET_ALL}")
                        # Alert to indicate user action needed
                        try:
                            self.browser.run_js("""
                            alert('Please select your Google account to continue with Cursor authentication');
                            """)
                            google_account_alert_shown = True  # Mark that we've shown the alert
                        except:
                            pass  # Alert is optional
                
                # Sleep before checking again
                time.sleep(check_interval)
            else:
                # If the loop completed without breaking, it means we hit the timeout
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} {self.translator.get('account_delete.auth_timeout', fallback='Authentication timeout, continuing anyway...')}{Style.RESET_ALL}")
            
            # Check current URL to determine next steps
            current_url = self.browser.url
            
            # If we're already on the settings page, no need to navigate
            if "/settings" in current_url and "cursor.com" in current_url:
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('account_delete.already_on_settings', fallback='Already on settings page')}{Style.RESET_ALL}")
            # If we're on the dashboard or any Cursor page but not settings, navigate to settings
            elif "cursor.com" in current_url or "authenticator.cursor.sh" in current_url:
                print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('account_delete.navigating_to_settings', fallback='Navigating to settings page...')}{Style.RESET_ALL}")
                self.browser.get("https://www.cursor.com/settings")
            # If we're still on Google auth or somewhere else, try directly going to settings
            else:
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} {self.translator.get('account_delete.login_redirect_failed', fallback='Login redirection failed, trying direct navigation...')}{Style.RESET_ALL}")
                self.browser.get("https://www.cursor.com/settings")
                
            # Wait for the settings page to load
            time.sleep(3)  # Reduced from 5 seconds
            
            # First look for the email element to confirm we're logged in
            try:
                email_element = self.browser.ele("css:div[class='flex w-full flex-col gap-2'] div:nth-child(2) p:nth-child(2)")
                if email_element:
                    email = email_element.text
                    print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('account_delete.found_email', email=email, fallback=f'Found email: {email}')}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} {self.translator.get('account_delete.email_not_found', error=str(e), fallback=f'Email not found: {str(e)}')}{Style.RESET_ALL}")
            
            # Click on "Advanced" tab or dropdown - keep only the successful approach
            advanced_found = False
            
            # Direct JavaScript querySelector approach that worked according to logs
            try:
                advanced_element_js = self.browser.run_js("""
                    // Try to find the Advanced dropdown using querySelector with the exact classes
                    let advancedElement = document.querySelector('div.mb-0.flex.cursor-pointer.items-center.text-xs:not([style*="display: none"])');
                    
                    // If not found, try a more general approach
                    if (!advancedElement) {
                        const allDivs = document.querySelectorAll('div');
                        for (const div of allDivs) {
                            if (div.textContent.includes('Advanced') && 
                                div.className.includes('mb-0') && 
                                div.className.includes('flex') &&
                                div.className.includes('cursor-pointer')) {
                                advancedElement = div;
                                break;
                            }
                        }
                    }
                    
                    // Click the element if found
                    if (advancedElement) {
                        advancedElement.click();
                        return true;
                    }
                    
                    return false;
                """)
                
                if advanced_element_js:
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('account_delete.advanced_tab_clicked', fallback='Found and clicked Advanced using direct JavaScript selector')}{Style.RESET_ALL}")
                    advanced_found = True
                    time.sleep(1)  # Reduced from 2 seconds
            except Exception as e:
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} {self.translator.get('account_delete.advanced_tab_error', error=str(e), fallback='JavaScript querySelector approach failed: {str(e)}')}{Style.RESET_ALL}")
            
            if not advanced_found:
                # Fallback to direct URL navigation which is faster and more reliable
                try:
                    self.browser.get("https://www.cursor.com/settings?tab=advanced")
                    print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('account_delete.direct_advanced_navigation', fallback='Trying direct navigation to advanced tab')}{Style.RESET_ALL}")
                    advanced_found = True
                except:
                    raise Exception(self.translator.get('account_delete.advanced_tab_not_found') if self.translator else "Advanced option not found after multiple attempts")
            
            # Wait for dropdown/tab content to load
            time.sleep(2)  # Reduced from 4 seconds
            
            # Find and click the "Delete Account" button 
            delete_button_found = False
            
            # Simplified approach for delete button based on what worked
            delete_button_selectors = [
                'xpath://button[contains(., "Delete Account")]',
                'xpath://button[text()="Delete Account"]',
                'xpath://div[contains(text(), "Delete Account")]',
                'xpath://button[contains(text(), "Delete") and contains(text(), "Account")]'
            ]
                
            for selector in delete_button_selectors:
                try:
                    delete_button = self.browser.ele(selector, timeout=2)
                    if delete_button:
                        delete_button.click()
                        print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('account_delete.delete_button_clicked') if self.translator else 'Clicked on Delete Account button'}{Style.RESET_ALL}")
                        delete_button_found = True
                        break
                except:
                    continue
            
            if not delete_button_found:
                raise Exception(self.translator.get('account_delete.delete_button_not_found') if self.translator else "Delete Account button not found")
            
            # Wait for confirmation dialog to appear
            time.sleep(2)
            
            # Check if we need to input "Delete" at all - some modals might not require it
            input_required = True
            try:
                # Try detecting if the DELETE button is already enabled
                delete_button_enabled = self.browser.run_js("""
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const deleteButtons = buttons.filter(btn => 
                        btn.textContent.trim() === 'DELETE' || 
                        btn.textContent.trim() === 'Delete'
                    );
                    
                    if (deleteButtons.length > 0) {
                        return !deleteButtons.some(btn => btn.disabled);
                    }
                    return false;
                """)
                
                if delete_button_enabled:
                    print(f"{Fore.CYAN}{EMOJI['INFO']} DELETE button appears to be enabled already. Input may not be required.{Style.RESET_ALL}")
                    input_required = False
            except:
                pass
            
            # Type "Delete" in the confirmation input - only if required
            delete_input_found = False
            
            if input_required:
                # Try common selectors for the input field
                delete_input_selectors = [
                    'xpath://input[@placeholder="Delete"]',
                    'xpath://div[contains(@class, "modal")]//input',
                    'xpath://input',
                    'css:input'
                ]
                
                for selector in delete_input_selectors:
                    try:
                        delete_input = self.browser.ele(selector, timeout=3)
                        if delete_input:
                            delete_input.clear()
                            delete_input.input("Delete")
                            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('account_delete.typed_delete', fallback='Typed \"Delete\" in confirmation box')}{Style.RESET_ALL}")
                            delete_input_found = True
                            time.sleep(2)
                            break
                    except:
                        # Try direct JavaScript input as fallback
                        try:
                            self.browser.run_js(f"""
                                arguments[0].value = "Delete";
                                const event = new Event('input', {{ bubbles: true }});
                                arguments[0].dispatchEvent(event);
                                const changeEvent = new Event('change', {{ bubbles: true }});
                                arguments[0].dispatchEvent(changeEvent);
                            """, delete_input)
                            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('account_delete.typed_delete_js', fallback='Typed \"Delete\" using JavaScript')}{Style.RESET_ALL}")
                            delete_input_found = True
                            time.sleep(2)
                            break
                        except:
                            continue
                
                if not delete_input_found:
                    print(f"{Fore.YELLOW}{EMOJI['WARNING']} {self.translator.get('account_delete.delete_input_not_found', fallback='Delete confirmation input not found, continuing anyway')}{Style.RESET_ALL}")
                    time.sleep(2)
            
            # Wait before clicking the final DELETE button
            time.sleep(2)
            
            # Click on the final DELETE button
            confirm_button_found = False
            
            # Use JavaScript approach for the DELETE button
            try:
                delete_button_js = self.browser.run_js("""
                    // Try to find the DELETE button by exact text content
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const deleteButton = buttons.find(btn => 
                        btn.textContent.trim() === 'DELETE' || 
                        btn.textContent.trim() === 'Delete'
                    );
                    
                    if (deleteButton) {
                        console.log("Found DELETE button with JavaScript");
                        deleteButton.click();
                        return true;
                    }
                    
                    // If not found by text, try to find right-most button in the modal
                    const modalButtons = Array.from(document.querySelectorAll('.relative button, [role="dialog"] button, .modal button, [aria-modal="true"] button'));
                    
                    if (modalButtons.length > 1) {
                        modalButtons.sort((a, b) => {
                            const rectA = a.getBoundingClientRect();
                            const rectB = b.getBoundingClientRect();
                            return rectB.right - rectA.right;
                        });
                        
                        console.log("Clicking right-most button in modal");
                        modalButtons[0].click();
                        return true;
                    } else if (modalButtons.length === 1) {
                        console.log("Clicking single button found in modal");
                        modalButtons[0].click();
                        return true;
                    }
                    
                    return false;
                """)
                
                if delete_button_js:
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('account_delete.delete_button_clicked', fallback='Clicked DELETE button')}{Style.RESET_ALL}")
                    confirm_button_found = True
            except:
                pass
            
            if not confirm_button_found:
                # Fallback to simple selectors
                delete_button_selectors = [
                    'xpath://button[text()="DELETE"]',
                    'xpath://div[contains(@class, "modal")]//button[last()]'
                ]
                
                for selector in delete_button_selectors:
                    try:
                        delete_button = self.browser.ele(selector, timeout=2)
                        if delete_button:
                            delete_button.click()
                            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('account_delete.delete_button_clicked', fallback='Account deleted successfully!')}{Style.RESET_ALL}")
                            confirm_button_found = True
                            break
                    except:
                        continue
            
            if not confirm_button_found:
                raise Exception(self.translator.get('account_delete.confirm_button_not_found') if self.translator else "Confirm button not found")
            
            # Wait a moment to see the confirmation
            time.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('account_delete.error', error=str(e)) if self.translator else f'Error during account deletion: {str(e)}'}{Style.RESET_ALL}")
            return False
        finally:
            # Clean up browser
            if self.browser:
                try:
                    self.browser.quit()
                except:
                    pass
            
def main(translator=None):
    """Main function to handle Google account deletion"""
    print(f"\n{Fore.CYAN}{EMOJI['START']} {translator.get('account_delete.title') if translator else 'Cursor Google Account Deletion Tool'}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'─' * 50}{Style.RESET_ALL}")
    
    deleter = CursorGoogleAccountDeleter(translator)
    
    try:
        # Ask for confirmation
        print(f"{Fore.RED}{EMOJI['WARNING']} {translator.get('account_delete.warning') if translator else 'WARNING: This will permanently delete your Cursor account. This action cannot be undone.'}{Style.RESET_ALL}")
        confirm = input(f"{Fore.RED} {translator.get('account_delete.confirm_prompt') if translator else 'Are you sure you want to proceed? (y/N): '}{Style.RESET_ALL}").lower()
        
        if confirm != 'y':
            print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('account_delete.cancelled') if translator else 'Account deletion cancelled.'}{Style.RESET_ALL}")
            return
            
        success = deleter.delete_google_account()
        
        if success:
            print(f"\n{Fore.GREEN}{EMOJI['SUCCESS']} {translator.get('account_delete.success') if translator else 'Your Cursor account has been successfully deleted!'}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}{EMOJI['ERROR']} {translator.get('account_delete.failed') if translator else 'Account deletion process failed or was cancelled.'}{Style.RESET_ALL}")
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}{EMOJI['INFO']} {translator.get('account_delete.interrupted') if translator else 'Account deletion process interrupted by user.'}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('account_delete.unexpected_error', error=str(e)) if translator else f'Unexpected error: {str(e)}'}{Style.RESET_ALL}")
    finally:
        print(f"{Fore.YELLOW}{'─' * 50}{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 