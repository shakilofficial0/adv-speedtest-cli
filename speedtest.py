#!/usr/bin/env python3
"""
Advanced Speedtest CLI - A cross-platform speedtest utility
Version: 1.0.0
Author: Shakil Ahmed
Email: shakilofficial0@gmail.com
"""

import os
import sys
import json
import requests
from typing import Optional
from pathlib import Path
from datetime import datetime, timedelta
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class Config:
    """Configuration constants"""
    VERSION = "1.0.0"
    AUTHOR = "Shakil Ahmed"
    GITHUB_REPO_LINK = "https://github.com/shakilofficial0/adv-speedtest-cli"
    EMAIL = "shakilofficial0@gmail.com"
    BANNER =  """
░█▀▀░█▀█░█▀▀░█▀▀░█▀▄░▀█▀░█▀▀░█▀▀░▀█▀░░░░░█▀▀░█░░░▀█▀
░▀▀█░█▀▀░█▀▀░█▀▀░█░█░░█░░█▀▀░▀▀█░░█░░▄▄▄░█░░░█░░░░█░
░▀▀▀░▀░░░▀▀▀░▀▀▀░▀▀░░░▀░░▀▀▀░▀▀▀░░▀░░░░░░▀▀▀░▀▀▀░▀▀▀
"""
    # API endpoints
    SPEEDTEST_LOGIN_API = "https://api.speedtest.net/user-login.php"
    
    @staticmethod
    def get_cookies_file_path() -> Path:
        """Get cross-platform cookies storage path"""
        if os.name == 'nt':  # Windows
            app_data = os.getenv('APPDATA') or os.path.expanduser('~')
            cookies_dir = Path(app_data) / 'advanced-speedtest-cli'
        else:  # macOS and Linux
            cookies_dir = Path.home() / '.advanced-speedtest-cli'
        
        cookies_dir.mkdir(parents=True, exist_ok=True)
        return cookies_dir / 'cookies.json'


class CookieManager:
    """Manage authentication cookies for speedtest.net"""
    
    @staticmethod
    def save_cookies(email: str, cookies: dict, expiration: Optional[str] = None) -> None:
        """Save cookies to file for a specific email
        
        Args:
            email: User email
            cookies: Dictionary of cookies to store
            expiration: Expiration timestamp (from response headers), if available
        """
        cookies_file = Config.get_cookies_file_path()
        
        try:
            # Load existing cookies
            if cookies_file.exists():
                with open(cookies_file, 'r') as f:
                    all_cookies = json.load(f)
            else:
                all_cookies = {}
            
            # Calculate expiration time if not provided
            if not expiration and cookies:
                # Look for expiration in cookies
                for key, value in cookies.items():
                    if isinstance(value, dict) and 'expires' in value:
                        expiration = value['expires']
                        break
            
            # Store cookies with metadata
            all_cookies[email] = {
                'cookies': cookies,
                'saved_at': datetime.now().isoformat(),
                'expires_at': expiration or None
            }
            
            # Save to file
            with open(cookies_file, 'w') as f:
                json.dump(all_cookies, f, indent=2)
            
        except Exception as e:
            print(f"✗ Error saving cookies: {str(e)}")
    
    @staticmethod
    def load_cookies(email: str) -> Optional[dict]:
        """Load cookies for a specific email"""
        cookies_file = Config.get_cookies_file_path()
        
        try:
            if not cookies_file.exists():
                return None
            
            with open(cookies_file, 'r') as f:
                all_cookies = json.load(f)
            
            user_data = all_cookies.get(email)
            if user_data and isinstance(user_data, dict):
                # Handle both old format (direct cookies) and new format (with metadata)
                if 'cookies' in user_data:
                    return user_data['cookies']
                else:
                    return user_data
            
            return None
        
        except Exception as e:
            print(f"✗ Error loading cookies: {str(e)}")
            return None
    
    @staticmethod
    def is_cookie_expired(email: str) -> bool:
        """Check if stored cookies have expired"""
        cookies_file = Config.get_cookies_file_path()
        
        try:
            if not cookies_file.exists():
                return True
            
            with open(cookies_file, 'r') as f:
                all_cookies = json.load(f)
            
            user_data = all_cookies.get(email)
            if not user_data:
                return True
            
            # If new format with metadata
            if isinstance(user_data, dict) and 'expires_at' in user_data:
                expires_at = user_data.get('expires_at')
                if expires_at:
                    try:
                        expiry_datetime = datetime.fromisoformat(expires_at)
                        return datetime.now() > expiry_datetime
                    except ValueError:
                        # If we can't parse the date, assume not expired
                        return False
                return False
            
            # If old format (direct cookies), assume not expired
            return False
        
        except Exception as e:
            print(f"✗ Error checking cookie expiration: {str(e)}")
            return True
    
    @staticmethod
    def get_cookie_expiration(email: str) -> Optional[str]:
        """Get expiration date string for a user's cookies"""
        cookies_file = Config.get_cookies_file_path()
        
        try:
            if not cookies_file.exists():
                return None
            
            with open(cookies_file, 'r') as f:
                all_cookies = json.load(f)
            
            user_data = all_cookies.get(email)
            if isinstance(user_data, dict) and 'expires_at' in user_data:
                return user_data.get('expires_at')
            
            return None
        
        except Exception as e:
            print(f"✗ Error getting cookie expiration: {str(e)}")
            return None
    
    @staticmethod
    def delete_cookies(email: str) -> None:
        """Delete cookies for a specific email"""
        cookies_file = Config.get_cookies_file_path()
        
        try:
            if not cookies_file.exists():
                return
            
            with open(cookies_file, 'r') as f:
                all_cookies = json.load(f)
            
            if email in all_cookies:
                del all_cookies[email]
                
                with open(cookies_file, 'w') as f:
                    json.dump(all_cookies, f, indent=2)
        
        except Exception as e:
            print(f"✗ Error deleting cookies: {str(e)}")
    
    @staticmethod
    def get_cached_users() -> list:
        """Get list of all cached/previously logged-in users"""
        cookies_file = Config.get_cookies_file_path()
        
        try:
            if not cookies_file.exists():
                return []
            
            with open(cookies_file, 'r') as f:
                all_cookies = json.load(f)
            
            return list(all_cookies.keys())
        
        except Exception as e:
            print(f"✗ Error reading cached users: {str(e)}")
            return []


class LoginManager:
    """Handle speedtest.net authentication and login"""
    
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    @staticmethod
    def fetch_session_cookie() -> Optional[dict]:
        """Fetch initial session cookie from speedtest.net"""
        try:
            headers = {
                'User-Agent': LoginManager.USER_AGENT,
                'Referer': 'https://api.speedtest.net/user-login.php'
            }
            
            response = requests.get(
                Config.SPEEDTEST_LOGIN_API,
                headers=headers,
                timeout=10,
                allow_redirects=False
            )
            
            # Extract cookies from response
            if response.cookies:
                return dict(response.cookies)
            
            return None
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching session: {str(e)}")
            return None
    
    @staticmethod
    def verify_cached_login(email: str) -> bool:
        """Verify if cached login is still valid"""
        cookies = CookieManager.load_cookies(email)
        
        if not cookies:
            return False
        
        try:
            headers = {
                'User-Agent': LoginManager.USER_AGENT,
                'Referer': 'https://api.speedtest.net/user-login.php'
            }
            
            # Verify cached cookies by making a GET request
            response = requests.get(
                Config.SPEEDTEST_LOGIN_API,
                headers=headers,
                cookies=cookies,
                timeout=10,
                allow_redirects=False
            )
            
            # If cookies are valid and user is authenticated, we should get a redirect or success
            return response.status_code in [200, 302]
        
        except requests.exceptions.RequestException:
            return False
    
    @staticmethod
    def login_with_credentials(email: str, password: str) -> Optional[str]:
        """Login with email and password
        
        Returns email if successful (status 302), None if failed (status 200)
        """
        try:
            # Step 1: Fetch initial session cookie
            print("Fetching session...")
            session_cookies = LoginManager.fetch_session_cookie()
            
            if not session_cookies:
                print("✗ Failed to fetch session")
                return None
            
            # Step 2: Login with credentials
            print("Authenticating...")
            headers = {
                'User-Agent': LoginManager.USER_AGENT,
                'Origin': 'https://api.speedtest.net',
                'Referer': 'https://api.speedtest.net/user-login.php',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            login_data = {
                'action': 'login',
                'email': email,
                'password': password,
                'remember-me': 'on'
            }
            
            response = requests.post(
                Config.SPEEDTEST_LOGIN_API,
                data=login_data,
                headers=headers,
                cookies=session_cookies,
                timeout=10,
                allow_redirects=False
            )
            
            # Status 302 means redirect (successful login)
            if response.status_code == 302:
                # Merge new cookies with session cookies
                all_cookies = {**session_cookies}
                if response.cookies:
                    all_cookies.update(dict(response.cookies))
                
                # Extract expiration time from Set-Cookie headers
                expiration = None
                if 'set-cookie' in response.headers:
                    # Parse Set-Cookie header for Max-Age or expires
                    cookie_header = response.headers['set-cookie']
                    if 'Max-Age=' in cookie_header:
                        try:
                            max_age_str = cookie_header.split('Max-Age=')[1].split(';')[0]
                            max_age = int(max_age_str)
                            expiration_datetime = datetime.now()
                            from datetime import timedelta
                            expiration_datetime += timedelta(seconds=max_age)
                            expiration = expiration_datetime.isoformat()
                        except (ValueError, IndexError):
                            pass
                
                CookieManager.save_cookies(email, all_cookies, expiration)
                print(f"✓ Login successful!")
                return email
            # Status 200 means failed login
            elif response.status_code == 200:
                print("✗ Invalid credentials")
                return None
            else:
                print(f"✗ Unexpected response status: {response.status_code}")
                return None
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Login failed: {str(e)}")
            return None
        except KeyboardInterrupt:
            raise
    
    @staticmethod
    def logout_with_cookies(email: str) -> bool:
        """Logout using stored cookies
        
        Sends GET request to logout endpoint. Returns True regardless of status code.
        """
        try:
            cookies = CookieManager.load_cookies(email)
            
            if not cookies:
                print("✗ No cached cookies found")
                return False
            
            print("Logging out...")
            headers = {
                'User-Agent': LoginManager.USER_AGENT,
                'Referer': 'https://api.speedtest.net/user-logout.php'
            }
            
            response = requests.get(
                'https://api.speedtest.net/user-logout.php',
                headers=headers,
                cookies=cookies,
                timeout=10,
                allow_redirects=False
            )
            
            # Status 302 or 200 both mean logout successful
            if response.status_code in [200, 302]:
                print("✓ Logout successful!")
                return True
            else:
                print(f"✗ Logout failed with status {response.status_code}")
                return False
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Logout error: {str(e)}")
            return False
        except KeyboardInterrupt:
            raise


class State:
    """Application state management"""
    def __init__(self):
        self.is_logged_in = False
        self.current_user = None
        self.selected_server = None
    
    def login(self, username: str):
        """Set user as logged in"""
        self.is_logged_in = True
        self.current_user = username
    
    def logout(self):
        """Logout user"""
        self.is_logged_in = False
        self.current_user = None
    
    def set_server(self, server_name: str):
        """Set selected server"""
        self.selected_server = server_name
    
    def get_server_display(self) -> str:
        """Get server display text"""
        if self.selected_server is None:
            return "Auto Pick"
        return self.selected_server


class Display:
    """Handle all display and UI related functions"""
    
    @staticmethod
    def clear_screen():
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_banner(banner_text: str):
        """Print ASCII art banner"""
        print(banner_text)
    
    @staticmethod
    def print_header() -> None:
        """Print header with banner and author details"""
        Display.clear_screen()
        Display.print_banner(Config.BANNER)
        print("=" * 50)
        print(f"Version: {Config.VERSION}")
        print(f"GitHub: {Config.GITHUB_REPO_LINK}")
        print(f"Author: {Config.AUTHOR}")
        print(f"Email: {Config.EMAIL}")
        print("=" * 50)
        print()
    
    @staticmethod
    def print_menu(state: State) -> None:
        """Display main menu"""
        Display.print_header()
        
        # Build menu
        menu_items = []
        menu_number = 1
        
        # Login/Logout option
        if not state.is_logged_in:
            menu_items.append((menu_number, "Login"))
            menu_number += 1
        
        # Server selection
        server_display = state.get_server_display()
        menu_items.append((menu_number, f"Select Server ({server_display})"))
        menu_number += 1
        
        # Speed test options
        menu_items.append((menu_number, "Run SpeedTest"))
        menu_number += 1
        
        menu_items.append((menu_number, "Run SpeedTest and Share"))
        menu_number += 1
        
        # Logout option (only if logged in)
        if state.is_logged_in:
            menu_items.append((menu_number, f"Logout ({state.current_user})"))
            menu_number += 1
        
        # Display menu items
        print("MENU")
        print("=" * 50)
        for num, item in menu_items:
            print(f"{num}. {item}")
        print("0. Exit")
        print("=" * 50)
        print()
        
        return menu_items
    
    @staticmethod
    def print_footer() -> None:
        """Print author credits and version"""
        print()
        print("=" * 50)
        print(f"Version: {Config.VERSION}")
        print(f"GitHub: {Config.GITHUB_REPO_LINK}")
        print(f"Author: {Config.AUTHOR}")
        print(f"Email: {Config.EMAIL}")
        print("=" * 50)


class AuthManager:
    """Handle authentication operations - UI layer"""
    
    @staticmethod
    def login() -> Optional[str]:
        """Handle user login with UI"""
        try:
            Display.print_header()
            print("LOGIN")
            print("=" * 50)
            print("(Press Ctrl+C to go back to main menu)")
            print("=" * 50)
            print()
            
            # Get cached users
            cached_users = CookieManager.get_cached_users()
            
            if cached_users:
                print("Previously logged-in users:")
                print("-" * 50)
                for idx, user_email in enumerate(cached_users, 1):
                    # Check if cookie is expired
                    is_expired = CookieManager.is_cookie_expired(user_email)
                    expiration_str = CookieManager.get_cookie_expiration(user_email)
                    
                    if is_expired:
                        print(f"{idx}. {user_email} {Fore.RED}[EXPIRED]{Style.RESET_ALL}")
                    elif expiration_str:
                        print(f"{idx}. {user_email} (Expires: {expiration_str})")
                    else:
                        print(f"{idx}. {user_email}")
                
                print(f"{len(cached_users) + 1}. New Login")
                print("-" * 50)
                print()
                
                try:
                    choice = input("Select user or enter new login (number): ").strip()
                    choice_num = int(choice)
                    
                    # Check if user selected a cached user
                    if 1 <= choice_num <= len(cached_users):
                        selected_email = cached_users[choice_num - 1]
                        
                        # Check if cookies are expired
                        if CookieManager.is_cookie_expired(selected_email):
                            print("\n✗ Cached login expired. Please enter password.")
                            password = input("Enter password: ").strip()
                            result = LoginManager.login_with_credentials(selected_email, password)
                            if result:
                                print(f"✓ Login successful! Welcome {selected_email}")
                                input("Press Enter to continue...")
                                return result
                            else:
                                input("Press Enter to continue...")
                                return None
                        
                        # Verify cached login
                        print("\nVerifying cached login...")
                        if LoginManager.verify_cached_login(selected_email):
                            print(f"✓ Login successful! Welcome {selected_email}")
                            input("Press Enter to continue...")
                            return selected_email
                        else:
                            print("✗ Cached login verification failed. Please enter password.")
                            password = input("Enter password: ").strip()
                            result = LoginManager.login_with_credentials(selected_email, password)
                            if result:
                                print(f"✓ Login successful! Welcome {selected_email}")
                                input("Press Enter to continue...")
                                return result
                            else:
                                input("Press Enter to continue...")
                                return None
                    # User chose "New Login"
                    elif choice_num == len(cached_users) + 1:
                        email = input("Enter email: ").strip()
                        password = input("Enter password: ").strip()
                        
                        result = LoginManager.login_with_credentials(email, password)
                        
                        if result:
                            print(f"✓ Login successful! Welcome {email}")
                            input("Press Enter to continue...")
                            return result
                        else:
                            input("Press Enter to continue...")
                            return None
                    else:
                        print("✗ Invalid selection")
                        input("Press Enter to continue...")
                        return None
                
                except ValueError:
                    print("✗ Invalid input. Please enter a number.")
                    input("Press Enter to continue...")
                    return None
            
            else:
                # No cached users, proceed with new login
                email = input("Enter email: ").strip()
                password = input("Enter password: ").strip()
                
                result = LoginManager.login_with_credentials(email, password)
                
                if result:
                    print(f"✓ Login successful! Welcome {email}")
                    input("Press Enter to continue...")
                    return result
                else:
                    input("Press Enter to continue...")
                    return None
        
        except KeyboardInterrupt:
            raise  # Re-raise to be caught by the menu handler
    
    @staticmethod
    def logout(email: str) -> None:
        """Handle user logout with UI"""
        try:
            Display.print_header()
            print("LOGOUT")
            print("=" * 50)
            print("(Press Ctrl+C to go back to main menu)")
            print("=" * 50)
            print()
            
            confirm = input(f"Logout from {email}? (y/n): ").strip().lower()
            if confirm == 'y':
                # Send logout request to API
                logout_success = LoginManager.logout_with_cookies(email)
                
                # Remove cached cookies regardless of logout response
                CookieManager.delete_cookies(email)
                
                if logout_success:
                    print(f"✓ Logged out successfully")
                else:
                    print(f"✓ Cookies cleared locally")
            else:
                print("✗ Logout cancelled")
            
            input("Press Enter to continue...")
        
        except KeyboardInterrupt:
            raise  # Re-raise to be caught by the menu handler


class ServerManager:
    """Handle server selection"""
    
    # Placeholder servers - can be expanded
    AVAILABLE_SERVERS = [
        "Server 1 - New York",
        "Server 2 - Los Angeles",
        "Server 3 - London",
        "Server 4 - Tokyo",
        "Server 5 - Sydney",
    ]
    
    @staticmethod
    def select_server() -> Optional[str]:
        """Handle server selection"""
        try:
            Display.print_header()
            print("SELECT SERVER")
            print("=" * 50)
            print("(Press Ctrl+C to go back to main menu)")
            print("=" * 50)
            print()
            print("0. Auto Pick (Nearest Server)")
            
            for idx, server in enumerate(ServerManager.AVAILABLE_SERVERS, 1):
                print(f"{idx}. {server}")
            
            print("=" * 50)
            
            choice = int(input("Select server number: ").strip())
            
            if choice == 0:
                print("✓ Server set to: Auto Pick")
                input("Press Enter to continue...")
                return None
            elif 1 <= choice <= len(ServerManager.AVAILABLE_SERVERS):
                selected = ServerManager.AVAILABLE_SERVERS[choice - 1]
                print(f"✓ Server selected: {selected}")
                input("Press Enter to continue...")
                return selected
            else:
                print("✗ Invalid selection")
                input("Press Enter to continue...")
                return None
        except ValueError:
            print("✗ Invalid input")
            input("Press Enter to continue...")
            return None
        except KeyboardInterrupt:
            raise  # Re-raise to be caught by the menu handler


class SpeedTest:
    """Handle speed test operations"""
    
    @staticmethod
    def run_test() -> dict:
        """Run speed test"""
        try:
            Display.print_header()
            print("RUNNING SPEED TEST")
            print("=" * 50)
            print("(Press Ctrl+C to go back to main menu)")
            print("=" * 50)
            print()
            # TODO: Implement actual speed test logic
            print("Testing... (TODO: Implement speed test logic)")
            input("Press Enter to continue...")
            
            # Placeholder result
            return {
                "ping": 25.5,
                "download": 95.2,
                "upload": 45.8,
                "server": "Test Server"
            }
        except KeyboardInterrupt:
            raise  # Re-raise to be caught by the menu handler
    
    @staticmethod
    def run_test_and_share() -> dict:
        """Run speed test and prepare for sharing"""
        try:
            Display.print_header()
            print("RUNNING SPEED TEST AND SHARE")
            print("=" * 50)
            print("(Press Ctrl+C to go back to main menu)")
            print("=" * 50)
            print()
            # TODO: Implement actual speed test and share logic
            print("Testing and preparing share link... (TODO: Implement logic)")
            input("Press Enter to continue...")
            
            # Placeholder result
            return {
                "ping": 25.5,
                "download": 95.2,
                "upload": 45.8,
                "server": "Test Server",
                "share_link": "https://speedtest.example.com/results/abc123"
            }
        except KeyboardInterrupt:
            raise  # Re-raise to be caught by the menu handler


class MenuHandler:
    """Handle menu navigation and selection"""
    
    def __init__(self, state: State):
        self.state = state
    
    def handle_menu_choice(self, menu_items: list, choice: str) -> bool:
        """
        Handle user menu choice
        Returns: False if user wants to exit, True to continue
        """
        try:
            choice_num = int(choice.strip())
            
            # Exit option
            if choice_num == 0:
                return False
            
            # Find the corresponding menu item
            for menu_num, menu_text in menu_items:
                if menu_num == choice_num:
                    return self._execute_menu_action(menu_text)
            
            print("✗ Invalid selection. Please try again.")
            input("Press Enter to continue...")
            return True
            
        except ValueError:
            print("✗ Invalid input. Please enter a number.")
            input("Press Enter to continue...")
            return True
    
    def _execute_menu_action(self, action: str) -> bool:
        """Execute menu action based on selection"""
        
        try:
            if "Login" in action:
                username = AuthManager.login()
                if username:
                    self.state.login(username)
                return True
            
            elif "Select Server" in action:
                server = ServerManager.select_server()
                if server is not None or server == "Auto Pick":
                    self.state.set_server(server)
                return True
            
            elif "Run SpeedTest and Share" in action:
                result = SpeedTest.run_test_and_share()
                Display.print_header()
                print("SPEED TEST RESULTS")
                print("=" * 50)
                print(f"✓ Test Complete!")
                print(f"  Ping: {result['ping']} ms")
                print(f"  Download: {result['download']} Mbps")
                print(f"  Upload: {result['upload']} Mbps")
                print(f"  Share Link: {result.get('share_link', 'N/A')}")
                print("=" * 50)
                input("Press Enter to continue...")
                return True
            
            elif "Run SpeedTest" in action:
                result = SpeedTest.run_test()
                Display.print_header()
                print("SPEED TEST RESULTS")
                print("=" * 50)
                print(f"✓ Test Complete!")
                print(f"  Ping: {result['ping']} ms")
                print(f"  Download: {result['download']} Mbps")
                print(f"  Upload: {result['upload']} Mbps")
                print("=" * 50)
                input("Press Enter to continue...")
                return True
            
            elif "Logout" in action:
                AuthManager.logout(self.state.current_user)
                self.state.logout()
                return True
            
            return True
        
        except KeyboardInterrupt:
            # User pressed Ctrl+C during an action, return to main menu
            return True


class Application:
    """Main application class"""
    
    def __init__(self):
        self.state = State()
        self.menu_handler = MenuHandler(self.state)
    
    def run(self):
        """Main application loop"""
        while True:
            try:
                menu_items = Display.print_menu(self.state)
                choice = input("Select option: ")
                should_continue = self.menu_handler.handle_menu_choice(menu_items, choice)
                
                if not should_continue:
                    raise KeyboardInterrupt  # Trigger exit
            except KeyboardInterrupt:
                raise  # Re-raise to main to exit application


def main():
    """Entry point of the application"""
    app = Application()
    try:
        app.run()
    except KeyboardInterrupt:
        # Only close if user presses Ctrl+C from main menu
        print("\n\n" + "=" * 50)
        print("Thank you for using Advanced Speedtest CLI!")
        print("=" * 50)
        print(f"Version: {Config.VERSION}")
        print(f"GitHub: {Config.GITHUB_REPO_LINK}")
        print(f"Author: {Config.AUTHOR}")
        print(f"Email: {Config.EMAIL}")
        print("=" * 50)
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ An error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
