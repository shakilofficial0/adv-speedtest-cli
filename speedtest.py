#!/usr/bin/env python3
"""
Advanced Speedtest CLI - A cross-platform speedtest utility
Version: 1.0.0
Author: Shakil Ahmed
Email: shakilofficial0@gmail.com
"""

import os
import sys
from typing import Optional


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
    """Handle authentication operations"""
    
    @staticmethod
    def login() -> Optional[str]:
        """Handle user login"""
        try:
            Display.print_header()
            print("LOGIN")
            print("=" * 50)
            print("(Press Ctrl+C to go back to main menu)")
            print("=" * 50)
            print()
            username = input("Enter username or email: ").strip()
            password = input("Enter password: ").strip()
            
            # TODO: Implement actual authentication with database
            if username and password:
                print(f"✓ Login successful! Welcome {username}")
                input("Press Enter to continue...")
                return username
            else:
                print("✗ Invalid credentials")
                input("Press Enter to continue...")
                return None
        except KeyboardInterrupt:
            raise  # Re-raise to be caught by the menu handler
    
    @staticmethod
    def logout() -> None:
        """Handle user logout"""
        try:
            Display.print_header()
            print("LOGOUT")
            print("=" * 50)
            print("(Press Ctrl+C to go back to main menu)")
            print("=" * 50)
            print()
            print("✓ Logged out successfully")
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
                AuthManager.logout()
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
