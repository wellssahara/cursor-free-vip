import psutil
import time
from colorama import Fore, Style, init
import sys
import os

# Initialize colorama
init()

# Define emoji constants
EMOJI = {
    "PROCESS": "⚙️",
    "SUCCESS": "✅",
    "ERROR": "❌",
    "INFO": "ℹ️",
    "WAIT": "⏳"
}

class CursorQuitter:
    def __init__(self, timeout=5, translator=None):
        self.timeout = timeout
        self.translator = translator  # Use the passed translator
        
    def quit_cursor(self):
        """Gently close Cursor processes"""
        try:
            print(f"{Fore.CYAN}{EMOJI['PROCESS']} {self.translator.get('quit_cursor.start')}...{Style.RESET_ALL}")
            cursor_processes = []
            
            # Collect all Cursor processes
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() in ['cursor.exe', 'cursor']:
                        cursor_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if not cursor_processes:
                print(f"{Fore.GREEN}{EMOJI['INFO']} {self.translator.get('quit_cursor.no_process')}{Style.RESET_ALL}")
                return True

            # Gently request processes to terminate
            for proc in cursor_processes:
                try:
                    if proc.is_running():
                        print(f"{Fore.YELLOW}{EMOJI['PROCESS']} {self.translator.get('quit_cursor.terminating', pid=proc.pid)}...{Style.RESET_ALL}")
                        proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Wait for processes to terminate naturally
            print(f"{Fore.CYAN}{EMOJI['WAIT']} {self.translator.get('quit_cursor.waiting')}...{Style.RESET_ALL}")
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                still_running = []
                for proc in cursor_processes:
                    try:
                        if proc.is_running():
                            still_running.append(proc)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if not still_running:
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('quit_cursor.success')}{Style.RESET_ALL}")
                    return True
                    
                time.sleep(0.5)
                
            # If processes are still running after timeout
            if still_running:
                process_list = ", ".join([str(p.pid) for p in still_running])
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('quit_cursor.timeout', pids=process_list)}{Style.RESET_ALL}")
                return False
                
            return True

        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('quit_cursor.error', error=str(e))}{Style.RESET_ALL}")
            return False

def quit_cursor(translator=None, timeout=5):
    """Convenient function for directly calling the quit function"""
    quitter = CursorQuitter(timeout, translator)
    return quitter.quit_cursor()

if __name__ == "__main__":
    # If run directly, use the default translator
    from main import translator as main_translator
    quit_cursor(main_translator)