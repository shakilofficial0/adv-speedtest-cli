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
import asyncio
import websockets
import time
from typing import Optional, List
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
    def save_user_data(email: str, user_data: dict) -> None:
        """Save user profile data to cache
        
        Args:
            email: User email
            user_data: User profile data from window.OOKLA.globals
        """
        cookies_file = Config.get_cookies_file_path()
        
        try:
            if cookies_file.exists():
                with open(cookies_file, 'r') as f:
                    all_data = json.load(f)
            else:
                all_data = {}
            
            if email not in all_data:
                all_data[email] = {}
            
            user_entry = all_data[email]
            if isinstance(user_entry, dict):
                user_entry['user_data'] = user_data
                user_entry['user_data_saved_at'] = datetime.now().isoformat()
            
            with open(cookies_file, 'w') as f:
                json.dump(all_data, f, indent=2)
        
        except Exception as e:
            print(f"✗ Error saving user data: {str(e)}")
    
    @staticmethod
    def load_user_data(email: str) -> Optional[dict]:
        """Load user profile data from cache
        
        Args:
            email: User email
            
        Returns:
            User profile data dict or None if not found
        """
        cookies_file = Config.get_cookies_file_path()
        
        try:
            if not cookies_file.exists():
                return None
            
            with open(cookies_file, 'r') as f:
                all_data = json.load(f)
            
            user_entry = all_data.get(email)
            if user_entry and isinstance(user_entry, dict):
                return user_entry.get('user_data')
            
            return None
        
        except Exception as e:
            print(f"✗ Error loading user data: {str(e)}")
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
        """Verify if cached login is still valid and fetch user details"""
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
            if response.status_code in [200, 302]:
                # Fetch user details for cached login
                user_data = LoginManager.fetch_user_details(email)
                return user_data is not None
            
            return False
        
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
                
                # Fetch user details from speedtest homepage
                user_data = LoginManager.fetch_user_details(email)
                if user_data:
                    print(f"✓ User data cached: {user_data.get('userName', 'Unknown')}")
                
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
    def fetch_user_details(email: str) -> Optional[dict]:
        """Fetch user details from https://www.speedtest.net/
        
        Extracts window.OOKLA.globals data from the page HTML.
        Returns the user data if logged in, None otherwise.
        """
        try:
            cookies = CookieManager.load_cookies(email)
            
            if not cookies:
                print("✗ No cookies found for user")
                return None
            
            print("Fetching user details...")
            headers = {
                'User-Agent': LoginManager.USER_AGENT,
                'Referer': 'https://www.speedtest.net/'
            }
            
            response = requests.get(
                'https://www.speedtest.net/',
                headers=headers,
                cookies=cookies,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"✗ Failed to fetch user details (Status: {response.status_code})")
                return None
            
            # Extract window.OOKLA.globals from HTML
            html_content = response.text
            
            # Find the script tag containing window.OOKLA.globals
            import re
            pattern = r'window\.OOKLA\.globals\s*=\s*({.*?});\s*window\.OOKLA\.isBlocked'
            match = re.search(pattern, html_content, re.DOTALL)
            
            if not match:
                print("✗ Could not find user data in page")
                return None
            
            try:
                globals_json_str = match.group(1)
                user_data = json.loads(globals_json_str)
                
                # Check if user is logged in
                if user_data.get('userName'):
                    print(f"✓ User details fetched for {user_data.get('userName')}")
                    # Save user data to cache
                    CookieManager.save_user_data(email, user_data)
                    return user_data
                else:
                    print("✗ User not logged in")
                    return None
            
            except json.JSONDecodeError as e:
                print(f"✗ Failed to parse user data: {str(e)}")
                return None
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching user details: {str(e)}")
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


class ServerManager:
    """Handle speedtest server operations"""
    
    CONFIG_API = "https://www.speedtest.net/api/js/config-sdk?engine=js&limit=10&https_functional=true"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    
    @staticmethod
    def get_or_create_anonymous_user() -> str:
        """Get or create anonymous user for non-logged-in users"""
        anonymous_email = "anonymous_user"
        
        # Check if anonymous user already has cookies
        existing_cookies = CookieManager.load_cookies(anonymous_email)
        if existing_cookies:
            return anonymous_email
        
        # Create anonymous user with empty cookies
        CookieManager.save_cookies(anonymous_email, {})
        return anonymous_email
    
    @staticmethod
    def fetch_server_config(user_email: Optional[str] = None) -> Optional[dict]:
        """Fetch server configuration from speedtest API
        
        Args:
            user_email: User email to use cookies from. If None, uses anonymous user.
            
        Returns:
            dict with config data including servers, or None if failed
        """
        try:
            # Use anonymous user if no email provided
            if not user_email:
                user_email = ServerManager.get_or_create_anonymous_user()
            
            # Load cookies for user
            cookies = CookieManager.load_cookies(user_email)
            if not cookies:
                cookies = {}
            
            print("Fetching server configuration...")
            headers = {
                'User-Agent': ServerManager.USER_AGENT,
                'Referer': 'https://www.speedtest.net/'
            }
            
            response = requests.get(
                ServerManager.CONFIG_API,
                headers=headers,
                cookies=cookies,
                timeout=10
            )
            
            if response.status_code == 200:
                config_data = response.json()
                
                # Store token and guid in user data
                if 'clientAuth' in config_data and 'token' in config_data['clientAuth']:
                    ServerManager._save_client_auth(user_email, config_data['clientAuth'], config_data.get('guid'))
                
                print(f"✓ Server configuration fetched successfully!")
                return config_data
            else:
                print(f"✗ Failed to fetch config (Status: {response.status_code})")
                return None
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching server config: {str(e)}")
            return None
        except ValueError as e:
            print(f"✗ Invalid response format: {str(e)}")
            return None
        except KeyboardInterrupt:
            raise
    
    @staticmethod
    def _save_client_auth(user_email: str, client_auth: dict, guid: Optional[str]) -> None:
        """Save client auth token and guid to user data"""
        cookies_file = Config.get_cookies_file_path()
        
        try:
            if cookies_file.exists():
                with open(cookies_file, 'r') as f:
                    all_data = json.load(f)
            else:
                all_data = {}
            
            if user_email not in all_data:
                all_data[user_email] = {}
            
            user_data = all_data[user_email]
            if isinstance(user_data, dict):
                user_data['client_auth'] = client_auth
                if guid:
                    user_data['guid'] = guid
            
            with open(cookies_file, 'w') as f:
                json.dump(all_data, f, indent=2)
        
        except Exception as e:
            print(f"✗ Error saving client auth: {str(e)}")
    
    @staticmethod
    def pick_random_server(servers: list) -> Optional[dict]:
        """Pick a random server from the list
        
        Args:
            servers: List of server dictionaries
            
        Returns:
            Random server dict or None if list is empty
        """
        if not servers:
            return None
        
        import random
        return random.choice(servers)
    
    @staticmethod
    def fetch_search_results(search_query: str, user_email: Optional[str] = None) -> Optional[dict]:
        """Fetch servers matching search criteria
        
        Args:
            search_query: Search query (ISP, server name, or location)
            user_email: User email to use cookies from. If None, uses anonymous user.
            
        Returns:
            dict with config data including filtered servers, or None if failed
        """
        try:
            # Use anonymous user if no email provided
            if not user_email:
                user_email = ServerManager.get_or_create_anonymous_user()
            
            # Load cookies for user
            cookies = CookieManager.load_cookies(user_email)
            if not cookies:
                cookies = {}
            
            # URL encode the search query
            from urllib.parse import quote
            encoded_query = quote(search_query)
            
            search_api = f"https://www.speedtest.net/api/js/config-sdk?engine=js&limit=30&https_functional=true&search={encoded_query}"
            
            print(f"Searching for servers matching '{search_query}'...")
            headers = {
                'User-Agent': ServerManager.USER_AGENT,
                'Referer': 'https://www.speedtest.net/'
            }
            
            response = requests.get(
                search_api,
                headers=headers,
                cookies=cookies,
                timeout=10
            )
            
            if response.status_code == 200:
                config_data = response.json()
                
                # Store token and guid in user data
                if 'clientAuth' in config_data and 'token' in config_data['clientAuth']:
                    ServerManager._save_client_auth(user_email, config_data['clientAuth'], config_data.get('guid'))
                
                if 'servers' in config_data and config_data['servers']:
                    print(f"✓ Found {len(config_data['servers'])} server(s) matching your search!")
                else:
                    print("✗ No servers found matching your search criteria.")
                
                return config_data
            else:
                print(f"✗ Failed to search servers (Status: {response.status_code})")
                return None
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Error searching servers: {str(e)}")
            return None
        except ValueError as e:
            print(f"✗ Invalid response format: {str(e)}")
            return None
        except KeyboardInterrupt:
            raise
    
    @staticmethod
    def get_distance_color(distance: float) -> str:
        """Get color code based on distance
        
        Distance ranges:
        0-100km: Green
        100-500km: Cyan
        500-1000km: Yellow
        1000-2000km: Magenta
        2000+km: Red
        """
        if distance <= 100:
            return Fore.GREEN
        elif distance <= 500:
            return Fore.CYAN
        elif distance <= 1000:
            return Fore.YELLOW
        elif distance <= 2000:
            return Fore.MAGENTA
        else:
            return Fore.RED
    
    @staticmethod
    def get_server_display_name(server: dict) -> str:
        """Get formatted display name for a server with color-coded distance"""
        sponsor = server.get('sponsor', 'Unknown')
        name = server.get('name', 'Unknown')
        distance = server.get('distance', 0)
        country = server.get('country', 'Unknown')
        
        distance_color = ServerManager.get_distance_color(distance)
        distance_str = f"{distance_color}{distance}km{Style.RESET_ALL}"
        
        return f"{sponsor} - {name}, {country} ({distance_str})"


class State:
    """Application state management"""
    def __init__(self):
        self.is_logged_in = False
        self.current_user = None
        self.selected_server = None  # Store full server dict
        self.speedtest_mode = "multiple"  # 'multiple' or 'single'
    
    def login(self, username: str):
        """Set user as logged in"""
        self.is_logged_in = True
        self.current_user = username
    
    def logout(self):
        """Logout user"""
        self.is_logged_in = False
        self.current_user = None
    
    def set_server(self, server_dict: Optional[dict]):
        """Set selected server
        
        Args:
            server_dict: Server dictionary from API or None for auto-pick
        """
        self.selected_server = server_dict
    
    def get_server_display(self) -> str:
        """Get server display text"""
        if self.selected_server is None:
            return "Auto Pick"
        
        # If it's a dict, get the display name
        if isinstance(self.selected_server, dict):
            return ServerManager.get_server_display_name(self.selected_server)
        
        # Fallback for string (legacy)
        return str(self.selected_server)


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
        
        # Server selection with color coding
        server_display = state.get_server_display()
        if server_display == "Auto Pick":
            colored_server = f"{Fore.YELLOW}{server_display}{Style.RESET_ALL}"
        else:
            colored_server = f"{Fore.GREEN}{server_display}{Style.RESET_ALL}"
        
        menu_items.append((menu_number, f"Select Server ({colored_server})"))
        menu_number += 1
        
        # Speed test options
        menu_items.append((menu_number, "Run SpeedTest"))
        menu_number += 1
        
        menu_items.append((menu_number, "Run SpeedTest and Share"))
        menu_number += 1
        
        # Settings option
        menu_items.append((menu_number, "Settings"))
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
            
            # Get cached users (excluding anonymous_user)
            all_cached_users = CookieManager.get_cached_users()
            cached_users = [u for u in all_cached_users if u != "anonymous_user"]
            
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


class ServerSelectionUI:
    """Handle server selection UI - wrapper around ServerManager"""
    
    @staticmethod
    def search_server(current_user: Optional[str] = None) -> Optional[dict]:
        """Handle server search functionality
        
        Args:
            current_user: Currently logged-in user email
            
        Returns:
            Selected server dict or None if cancelled
        """
        try:
            Display.print_header()
            print("SEARCH SERVER")
            print("=" * 50)
            print("(Press Ctrl+C to go back to main menu)")
            print("=" * 50)
            print()
            
            search_query = input("Enter search criteria (ISP/Server/Location): ").strip()
            
            if not search_query:
                print("✗ Search query cannot be empty")
                input("Press Enter to continue...")
                return None
            
            print()
            # Fetch search results
            config = ServerManager.fetch_search_results(search_query, current_user)
            
            if not config or 'servers' not in config or not config['servers']:
                print("✗ No servers found")
                input("Press Enter to continue...")
                return None
            
            servers = config['servers']
            
            print()
            for idx, server in enumerate(servers, 1):
                display_name = ServerManager.get_server_display_name(server)
                print(f"{idx}. {display_name}")
            
            print("=" * 50)
            print()
            
            choice = int(input("Select server number: ").strip())
            
            if 1 <= choice <= len(servers):
                selected_server = servers[choice - 1]
                display_name = ServerManager.get_server_display_name(selected_server)
                print(f"✓ Server selected: {display_name}")
                input("Press Enter to continue...")
                return selected_server
            else:
                print("✗ Invalid selection")
                input("Press Enter to continue...")
                return None
        
        except ValueError:
            print("✗ Invalid input. Please enter a number.")
            input("Press Enter to continue...")
            return None
        except KeyboardInterrupt:
            raise
    
    @staticmethod
    def select_server(current_user: Optional[str] = None) -> Optional[dict]:
        """Handle server selection UI
        
        Args:
            current_user: Currently logged-in user email
            
        Returns:
            Selected server dict or None for auto-pick
        """
        try:
            Display.print_header()
            print("SELECT SERVER")
            print("=" * 50)
            print("(Press Ctrl+C to go back to main menu)")
            print("=" * 50)
            print()
            
            # Fetch server configuration
            config = ServerManager.fetch_server_config(current_user)
            
            if not config or 'servers' not in config:
                print("✗ Failed to load servers")
                input("Press Enter to continue...")
                return None
            
            servers = config['servers']
            
            print("\n0. Auto Pick (Nearest Server)")
            for idx, server in enumerate(servers, 1):
                display_name = ServerManager.get_server_display_name(server)
                print(f"{idx}. {display_name}")
            
            total_options = len(servers) + 1  # +1 for search option
            print(f"{total_options}. Search Server")
            print("=" * 50)
            print()
            
            choice = int(input("Select server number: ").strip())
            
            if choice == 0:
                # Auto pick - choose random server
                selected_server = ServerManager.pick_random_server(servers)
                if selected_server:
                    display_name = ServerManager.get_server_display_name(selected_server)
                    print(f"✓ Server set to: {display_name} (Auto Pick)")
                    input("Press Enter to continue...")
                    return selected_server
                else:
                    print("✗ No servers available")
                    input("Press Enter to continue...")
                    return None
            
            elif 1 <= choice <= len(servers):
                selected_server = servers[choice - 1]
                display_name = ServerManager.get_server_display_name(selected_server)
                print(f"✓ Server selected: {display_name}")
                input("Press Enter to continue...")
                return selected_server
            
            elif choice == total_options:
                # Call search server
                return ServerSelectionUI.search_server(current_user)
            
            else:
                print("✗ Invalid selection")
                input("Press Enter to continue...")
                return None
        
        except ValueError:
            print("✗ Invalid input. Please enter a number.")
            input("Press Enter to continue...")
            return None
        except KeyboardInterrupt:
            raise  # Re-raise to be caught by the menu handler


class PingTest:
    """Handle WebSocket ping test for latency measurement"""
    
    @staticmethod
    async def run_ping_test(server: dict, num_pings: int = 10) -> Optional[List[float]]:
        """Run ping test via WebSocket
        
        Args:
            server: Server dictionary with 'host' key
            num_pings: Number of ping packets to send
            
        Returns:
            List of ping times in milliseconds, or None if failed
        """
        try:
            host = server.get('host')
            if not host:
                print("✗ Server does not have a host URL")
                return None
            
            # Construct WebSocket URL
            ws_url = f"wss://{host}/ws?"
            
            ping_times = []
            pong_count = 0
            timeout_count = 0
            
            print(f"Connecting to {host}...")
            
            try:
                async with websockets.connect(ws_url, ping_interval=None) as websocket:
                    print(f"✓ Connected to {host}")
                    print(f"Sending {num_pings} ping packets...\n")
                    
                    for i in range(num_pings):
                        try:
                            # Send PING with timestamp
                            ping_timestamp = int(time.time() * 1000)
                            ping_message = f"PING {ping_timestamp}\t{i}\t"
                            
                            send_time = time.time()
                            await asyncio.wait_for(websocket.send(ping_message), timeout=5.0)
                            
                            # Wait for PONG response
                            pong_message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                            
                            receive_time = time.time()
                            
                            # Calculate latency in milliseconds
                            latency_ms = (receive_time - send_time) * 1000
                            ping_times.append(latency_ms)
                            pong_count += 1
                            
                            # Parse PONG response for display
                            print(f"PONG received: {latency_ms:.2f} ms")
                            
                            # Small delay between pings
                            await asyncio.sleep(0.1)
                        
                        except asyncio.TimeoutError:
                            print(f"✗ Timeout waiting for PONG #{i+1}")
                            timeout_count += 1
                        except Exception as e:
                            print(f"✗ Error on ping #{i+1}: {str(e)}")
                            timeout_count += 1
                    
                    print(f"\n✓ Ping test complete: {pong_count} successful, {timeout_count} timeouts")
                    
            except (websockets.exceptions.WebSocketException, OSError) as e:
                print(f"✗ WebSocket connection failed: {str(e)}")
                return None
            
            if not ping_times:
                print("✗ No successful pings received")
                return None
            
            return ping_times
        
        except Exception as e:
            print(f"✗ Ping test error: {str(e)}")
            return None
    
    @staticmethod
    def calculate_ping_stats(ping_times: List[float]) -> dict:
        """Calculate ping statistics
        
        Args:
            ping_times: List of ping times in milliseconds
            
        Returns:
            Dictionary with ping statistics
        """
        if not ping_times:
            return {}
        
        ping_times_sorted = sorted(ping_times)
        avg = sum(ping_times) / len(ping_times)
        
        return {
            'min': min(ping_times),
            'max': max(ping_times),
            'avg': avg,
            'median': ping_times_sorted[len(ping_times_sorted) // 2],
            'stddev': (sum((x - avg) ** 2 for x in ping_times) / len(ping_times)) ** 0.5,
            'count': len(ping_times)
        }


class SpeedTest:
    """Handle speed test operations"""
    
    @staticmethod
    def run_test(state: State = None) -> dict:
        """Run speed test with server and user details
        
        Args:
            state: Application state containing user and server information
        """
        try:
            Display.print_header()
            print("RUNNING SPEED TEST")
            print("=" * 50)
            print("(Press Ctrl+C to go back to main menu)")
            print("=" * 50)
            print()
            
            # Show User Information
            if state and state.current_user:
                print("USER INFORMATION")
                print("-" * 50)
                print(f"Username: {state.current_user}")
                
                # Try to load and display user data
                user_data = CookieManager.load_user_data(state.current_user)
                if user_data:
                    print(f"Email: {user_data.get('email', 'N/A')}")
                    print(f"ISP: {user_data.get('isp', 'N/A')}")
                    location = user_data.get('location', {})
                    if location:
                        print(f"Location: {location.get('countryName', 'N/A')}")
                        print(f"Coordinates: {location.get('latitude', 0)}, {location.get('longitude', 0)}")
                print()
            
            # Show Server Information
            # Auto-fetch and select server if not already selected
            server = state.selected_server if state else None
            
            if not server and state:
                print("Fetching server list...")
                config = ServerManager.fetch_server_config(state.current_user)
                
                # Check if server fetch failed
                if not config:
                    print()
                    print("=" * 50)
                    print(f"{Fore.RED}✗ ERROR{Style.RESET_ALL}")
                    print("=" * 50)
                    print("Failed to fetch server list.")
                    print("This usually means:")
                    print("  • No internet connection")
                    print("  • Speedtest server is unavailable")
                    print("  • Network is blocked")
                    print("=" * 50)
                    input("Press Enter to go back to main menu...")
                    return {
                        "ping": 0,
                        "download": 0,
                        "upload": 0,
                        "server": "N/A",
                        "error": "Server fetch failed"
                    }
                
                if 'servers' in config:
                    servers = config['servers']
                    if servers:
                        server = ServerManager.pick_random_server(servers)
                        state.set_server(server)
                        print("✓ Server auto-selected\n")
                    else:
                        print()
                        print("=" * 50)
                        print(f"{Fore.RED}✗ ERROR{Style.RESET_ALL}")
                        print("=" * 50)
                        print("No servers available in the response.")
                        print("=" * 50)
                        input("Press Enter to go back to main menu...")
                        return {
                            "ping": 0,
                            "download": 0,
                            "upload": 0,
                            "server": "N/A",
                            "error": "No servers available"
                        }
            
            if server:
                print("SERVER INFORMATION")
                print("-" * 50)
                print(f"Sponsor: {server.get('sponsor', 'N/A')}")
                print(f"Server: {server.get('name', 'N/A')}")
                print(f"Country: {server.get('country', 'N/A')}")
                distance_color = ServerManager.get_distance_color(server.get('distance', 0))
                print(f"Distance: {distance_color}{server.get('distance', 0)}km{Style.RESET_ALL}")
                print(f"Host: {server.get('host', 'N/A')}")
                print(f"ID: {server.get('id', 'N/A')}")
                print()
            
            # Show Speedtest Mode
            if state:
                print("TEST CONFIGURATION")
                print("-" * 50)
                mode_display = "Multiple Connection" if state.speedtest_mode == "multiple" else "Single Connection"
                mode_color = Fore.GREEN if state.speedtest_mode == "multiple" else Fore.CYAN
                print(f"Mode: {mode_color}{mode_display}{Style.RESET_ALL}")
                print()
            
            # Ping Test
            print("STEP 1: PING TEST")
            print("-" * 50)
            print("Measuring latency...\n")
            
            ping_stats = {}
            if server:
                try:
                    # Run actual WebSocket ping test
                    ping_times = asyncio.run(PingTest.run_ping_test(server, num_pings=10))
                    
                    if ping_times:
                        ping_stats = PingTest.calculate_ping_stats(ping_times)
                        print(f"\n✓ Ping Test Complete!")
                        print(f"  Min: {ping_stats['min']:.2f} ms")
                        print(f"  Max: {ping_stats['max']:.2f} ms")
                        print(f"  Avg: {ping_stats['avg']:.2f} ms")
                        print(f"  Median: {ping_stats['median']:.2f} ms")
                        print(f"  Samples: {ping_stats['count']}")
                    else:
                        print("✗ Ping test failed")
                        # Fallback to demo data
                        demo_ping_times = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        ping_stats = PingTest.calculate_ping_stats(demo_ping_times)
                except Exception as e:
                    print(f"✗ Error during ping test: {str(e)}")
                    # Fallback to demo data
                    demo_ping_times = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    ping_stats = PingTest.calculate_ping_stats(demo_ping_times)
            else:
                # No server available, use demo data
                demo_ping_times = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                ping_stats = PingTest.calculate_ping_stats(demo_ping_times)
            
            print()
            
            print("STEP 2: DOWNLOAD TEST - Demo")
            print("-" * 50)
            print("(To be implemented)")
            print()
            
            print("STEP 3: UPLOAD TEST - Demo")
            print("-" * 50)
            print("(To be implemented)")
            print()
            
            input("Press Enter to continue...")
            
            # Placeholder result
            return {
                "ping": ping_stats['avg'],
                "download": 95.2,
                "upload": 45.8,
                "server": "Test Server"
            }
        except KeyboardInterrupt:
            raise  # Re-raise to be caught by the menu handler
    
    @staticmethod
    def run_test_and_share(state: State = None) -> dict:
        """Run speed test and prepare for sharing
        
        Args:
            state: Application state containing user and server information
        """
        try:
            Display.print_header()
            print("RUNNING SPEED TEST AND SHARE")
            print("=" * 50)
            print("(Press Ctrl+C to go back to main menu)")
            print("=" * 50)
            print()
            
            # Call the standard run_test to get base results
            result = SpeedTest.run_test(state)
            
            # Check if there was an error in the test
            if "error" in result:
                # Error was already displayed by run_test, return as-is
                return {
                    "ping": result.get("ping", 0),
                    "download": result.get("download", 0),
                    "upload": result.get("upload", 0),
                    "server": result.get("server", "N/A"),
                    "share_link": "N/A",
                    "error": result.get("error", "Test failed")
                }
            
           
            
            # Generate a unique share link (placeholder implementation)
            import hashlib
            from datetime import datetime
            
            test_data = f"{result['ping']}{result['download']}{result['upload']}{datetime.now()}"
            share_id = hashlib.md5(test_data.encode()).hexdigest()[:8].upper()
            share_link = f"https://speedtest.example.com/results/{share_id}"
            
            
            # Add share_link to result and return
            result["share_link"] = share_link
            return result
        except KeyboardInterrupt:
            raise  # Re-raise to be caught by the menu handler


class SettingsManager:
    """Handle application settings"""
    
    @staticmethod
    def show_settings(state: State) -> None:
        """Display and handle settings menu"""
        while True:
            try:
                Display.print_header()
                print("SETTINGS")
                print("=" * 50)
                print("(Press Ctrl+C to go back to main menu)")
                print("=" * 50)
                print()
                
                # Display current speedtest mode
                mode_display = "Multiple Connection" if state.speedtest_mode == "multiple" else "Single Connection"
                colored_mode = f"{Fore.GREEN}{mode_display}{Style.RESET_ALL}" if state.speedtest_mode == "multiple" else mode_display
                
                print("1. Select Speedtest Mode (Current: {})".format(colored_mode))
                print("=" * 50)
                print()
                
                choice = input("Select option (1 to continue, 0 to go back): ").strip()
                
                if choice == "0":
                    return
                elif choice == "1":
                    SettingsManager.select_speedtest_mode(state)
                else:
                    print("✗ Invalid selection")
                    input("Press Enter to continue...")
            
            except KeyboardInterrupt:
                raise
    
    @staticmethod
    def select_speedtest_mode(state: State) -> None:
        """Select speedtest connection mode"""
        try:
            Display.print_header()
            print("SELECT SPEEDTEST MODE")
            print("=" * 50)
            print("(Press Ctrl+C to go back to settings)")
            print("=" * 50)
            print()
            
            # Display options with color coding
            multiple_color = f"{Fore.GREEN}(Default){Style.RESET_ALL}" if state.speedtest_mode == "multiple" else ""
            single_color = f"{Fore.GREEN}(Current){Style.RESET_ALL}" if state.speedtest_mode == "single" else ""
            
            print("1. Multiple Connection {}".format(multiple_color))
            print("2. Single Connection {}".format(single_color))
            print("=" * 50)
            print()
            
            choice = input("Select option: ").strip()
            
            if choice == "1":
                state.speedtest_mode = "multiple"
                print(f"\n✓ Speedtest mode set to: {Fore.GREEN}Multiple Connection{Style.RESET_ALL}")
                input("Press Enter to continue...")
            elif choice == "2":
                state.speedtest_mode = "single"
                print(f"\n✓ Speedtest mode set to: Single Connection")
                input("Press Enter to continue...")
            else:
                print("✗ Invalid selection")
                input("Press Enter to continue...")
        
        except KeyboardInterrupt:
            raise


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
                server = ServerSelectionUI.select_server(self.state.current_user)
                # server can be None (auto-pick) or a dict (selected server)
                self.state.set_server(server)
                return True
            
            elif "Run SpeedTest and Share" in action:
                result = SpeedTest.run_test_and_share(self.state)
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
                result = SpeedTest.run_test(self.state)
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
            
            elif "Settings" in action:
                SettingsManager.show_settings(self.state)
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
