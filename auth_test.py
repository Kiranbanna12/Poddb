#!/usr/bin/env python3
"""
Authentication Testing Suite - Sign In/Login Fix
Tests the authentication functionality that was just fixed based on review request
"""

import requests
import json
import sys
from typing import Dict, Any, Optional
import jwt

# Backend URL from frontend .env
BASE_URL = "https://auth-doctor.preview.emergentagent.com/api"

class AuthTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.test_user_token = None
        self.test_user_data = None
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def test_username_availability_check_available(self):
        """Test 1: Username Availability Check - Available"""
        try:
            url = f"{self.base_url}/auth/check-username/{self.test_user_data['username']}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "available" in data and data["available"] == True:
                    self.log_test("Username Availability Check (Available)", True, 
                                f"Username '{self.test_user_data['username']}' is available")
                else:
                    self.log_test("Username Availability Check (Available)", False, 
                                "Expected available: true", data)
            elif response.status_code == 404:
                self.log_test("Username Availability Check (Available)", False, 
                            "Endpoint not implemented - GET /api/auth/check-username/{username}")
            else:
                self.log_test("Username Availability Check (Available)", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Username Availability Check (Available)", False, f"Exception: {str(e)}")

    def test_email_availability_check_available(self):
        """Test 2: Email Availability Check - Available"""
        try:
            url = f"{self.base_url}/auth/check-email/{self.test_user_data['email']}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "available" in data and data["available"] == True:
                    self.log_test("Email Availability Check (Available)", True, 
                                f"Email '{self.test_user_data['email']}' is available")
                else:
                    self.log_test("Email Availability Check (Available)", False, 
                                "Expected available: true", data)
            elif response.status_code == 404:
                self.log_test("Email Availability Check (Available)", False, 
                            "Endpoint not implemented - GET /api/auth/check-email/{email}")
            else:
                self.log_test("Email Availability Check (Available)", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Email Availability Check (Available)", False, f"Exception: {str(e)}")

    def test_user_registration(self):
        """Test 3: User Registration"""
        try:
            url = f"{self.base_url}/auth/register"
            response = self.session.post(url, json=self.test_user_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for expected fields in response
                if "success" in data and data["success"]:
                    if "user_id" in data:
                        self.log_test("User Registration", True, 
                                    f"User registered successfully with ID: {data['user_id']}")
                    else:
                        self.log_test("User Registration", True, 
                                    "User registered successfully (no user_id in response)")
                elif "user" in data and "token" in data:
                    # Alternative response format
                    self.log_test("User Registration", True, 
                                f"User registered successfully: {data['user'].get('username', 'N/A')}")
                else:
                    self.log_test("User Registration", False, 
                                "Missing success indicator or user data", data)
            else:
                self.log_test("User Registration", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("User Registration", False, f"Exception: {str(e)}")

    def test_username_availability_check_taken(self):
        """Test 4: Username Availability Check - Taken (after registration)"""
        try:
            url = f"{self.base_url}/auth/check-username/{self.test_user_data['username']}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "available" in data and data["available"] == False:
                    self.log_test("Username Availability Check (Taken)", True, 
                                f"Username '{self.test_user_data['username']}' is now taken")
                else:
                    self.log_test("Username Availability Check (Taken)", False, 
                                "Expected available: false after registration", data)
            elif response.status_code == 404:
                self.log_test("Username Availability Check (Taken)", False, 
                            "Endpoint not implemented - GET /api/auth/check-username/{username}")
            else:
                self.log_test("Username Availability Check (Taken)", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Username Availability Check (Taken)", False, f"Exception: {str(e)}")

    def test_login_with_credentials(self):
        """Test 5: Login with Credentials"""
        try:
            url = f"{self.base_url}/auth/login"
            login_data = {
                "identifier": self.test_user_data["username"],  # or email
                "password": self.test_user_data["password"],
                "remember_me": False
            }
            
            # Try with identifier field first
            response = self.session.post(url, json=login_data, timeout=10)
            
            if response.status_code != 200:
                # Try with email field (alternative format)
                login_data_alt = {
                    "email": self.test_user_data["email"],
                    "password": self.test_user_data["password"]
                }
                response = self.session.post(url, json=login_data_alt, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for session token or JWT token
                if "session_token" in data:
                    self.session_token = data["session_token"]
                    # Set cookie for subsequent requests
                    self.session.cookies.set("session_token", self.session_token)
                    self.log_test("Login with Credentials", True, 
                                f"Login successful, session token received")
                elif "token" in data:
                    self.session_token = data["token"]
                    # Set Authorization header for subsequent requests
                    self.session.headers.update({"Authorization": f"Bearer {self.session_token}"})
                    self.log_test("Login with Credentials", True, 
                                f"Login successful, JWT token received")
                else:
                    self.log_test("Login with Credentials", False, 
                                "No session_token or token in response", data)
            else:
                self.log_test("Login with Credentials", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Login with Credentials", False, f"Exception: {str(e)}")

    def test_get_current_user(self):
        """Test 6: Get Current User"""
        if not self.session_token:
            self.log_test("Get Current User", False, "No session token available (login failed)")
            return
            
        try:
            url = f"{self.base_url}/auth/me"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "username" in data and data["username"] == self.test_user_data["username"]:
                    self.log_test("Get Current User", True, 
                                f"Current user retrieved: {data['username']}")
                else:
                    self.log_test("Get Current User", False, 
                                "Username mismatch or missing", data)
            elif response.status_code == 401:
                self.log_test("Get Current User", False, 
                            "Authentication failed - check session token format")
            else:
                self.log_test("Get Current User", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Get Current User", False, f"Exception: {str(e)}")

    def test_get_user_profile(self):
        """Test 7: Get User Profile"""
        if not self.session_token:
            self.log_test("Get User Profile", False, "No session token available (login failed)")
            return
            
        try:
            url = f"{self.base_url}/profile"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get User Profile", True, 
                            f"Profile retrieved for user: {data.get('username', 'N/A')}")
            elif response.status_code == 404:
                self.log_test("Get User Profile", False, 
                            "Endpoint not implemented - GET /api/profile")
            elif response.status_code == 401:
                self.log_test("Get User Profile", False, 
                            "Authentication failed - check session token")
            else:
                self.log_test("Get User Profile", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Get User Profile", False, f"Exception: {str(e)}")

    def test_update_profile(self):
        """Test 8: Update Profile"""
        if not self.session_token:
            self.log_test("Update Profile", False, "No session token available (login failed)")
            return
            
        try:
            url = f"{self.base_url}/profile"
            update_data = {
                "full_name": "Test User Updated",
                "bio": "This is my test bio"
            }
            response = self.session.put(url, json=update_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data and data["success"]:
                    self.log_test("Update Profile", True, "Profile updated successfully")
                else:
                    self.log_test("Update Profile", True, "Profile update response received")
            elif response.status_code == 404:
                self.log_test("Update Profile", False, 
                            "Endpoint not implemented - PUT /api/profile")
            elif response.status_code == 401:
                self.log_test("Update Profile", False, 
                            "Authentication failed - check session token")
            else:
                self.log_test("Update Profile", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Update Profile", False, f"Exception: {str(e)}")

    def test_change_password(self):
        """Test 9: Change Password"""
        if not self.session_token:
            self.log_test("Change Password", False, "No session token available (login failed)")
            return
            
        try:
            url = f"{self.base_url}/profile/change-password"
            password_data = {
                "current_password": self.test_user_data["password"],
                "new_password": self.new_password,
                "confirm_password": self.new_password
            }
            response = self.session.put(url, json=password_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data and data["success"]:
                    self.log_test("Change Password", True, "Password changed successfully")
                    # Update our test password for subsequent tests
                    self.test_user_data["password"] = self.new_password
                else:
                    self.log_test("Change Password", True, "Password change response received")
                    self.test_user_data["password"] = self.new_password
            elif response.status_code == 404:
                self.log_test("Change Password", False, 
                            "Endpoint not implemented - PUT /api/profile/change-password")
            elif response.status_code == 401:
                self.log_test("Change Password", False, 
                            "Authentication failed - check session token")
            else:
                self.log_test("Change Password", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Change Password", False, f"Exception: {str(e)}")

    def test_login_with_new_password(self):
        """Test 10: Login with New Password"""
        try:
            url = f"{self.base_url}/auth/login"
            login_data = {
                "identifier": self.test_user_data["username"],
                "password": self.new_password,
                "remember_me": False
            }
            
            # Try with identifier field first
            response = self.session.post(url, json=login_data, timeout=10)
            
            if response.status_code != 200:
                # Try with email field (alternative format)
                login_data_alt = {
                    "email": self.test_user_data["email"],
                    "password": self.new_password
                }
                response = self.session.post(url, json=login_data_alt, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Login with New Password", True, 
                            "Login successful with new password")
            else:
                self.log_test("Login with New Password", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Login with New Password", False, f"Exception: {str(e)}")

    def test_get_active_sessions(self):
        """Test 11: Get Active Sessions"""
        if not self.session_token:
            self.log_test("Get Active Sessions", False, "No session token available (login failed)")
            return
            
        try:
            url = f"{self.base_url}/profile/sessions"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get Active Sessions", True, 
                                f"Retrieved {len(data)} active sessions")
                else:
                    self.log_test("Get Active Sessions", True, 
                                "Active sessions response received")
            elif response.status_code == 404:
                self.log_test("Get Active Sessions", False, 
                            "Endpoint not implemented - GET /api/profile/sessions")
            elif response.status_code == 401:
                self.log_test("Get Active Sessions", False, 
                            "Authentication failed - check session token")
            else:
                self.log_test("Get Active Sessions", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Get Active Sessions", False, f"Exception: {str(e)}")

    def test_password_reset_flow(self):
        """Test 12: Password Reset Flow"""
        try:
            url = f"{self.base_url}/auth/forgot-password"
            reset_data = {
                "email": self.test_user_data["email"]
            }
            response = self.session.post(url, json=reset_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data and data["success"]:
                    self.log_test("Password Reset Flow", True, 
                                "Password reset request successful")
                else:
                    self.log_test("Password Reset Flow", True, 
                                "Password reset response received")
            elif response.status_code == 404:
                self.log_test("Password Reset Flow", False, 
                            "Endpoint not implemented - POST /api/auth/forgot-password")
            else:
                self.log_test("Password Reset Flow", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Password Reset Flow", False, f"Exception: {str(e)}")

    def test_logout(self):
        """Test 13: Logout"""
        if not self.session_token:
            self.log_test("Logout", False, "No session token available (login failed)")
            return
            
        try:
            url = f"{self.base_url}/auth/logout"
            response = self.session.post(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data and data["success"]:
                    self.log_test("Logout", True, "Logout successful")
                else:
                    self.log_test("Logout", True, "Logout response received")
                # Clear session token
                self.session_token = None
                self.session.cookies.clear()
                self.session.headers.pop("Authorization", None)
            elif response.status_code == 404:
                self.log_test("Logout", False, 
                            "Endpoint not implemented - POST /api/auth/logout")
            elif response.status_code == 401:
                self.log_test("Logout", False, 
                            "Authentication failed - check session token")
            else:
                self.log_test("Logout", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Logout", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all authentication tests"""
        print("=" * 80)
        print("AUTHENTICATION SYSTEM BACKEND API TESTING SUITE")
        print("=" * 80)
        print(f"Testing against: {self.base_url}")
        print(f"Test user: {self.test_user_data['username']} ({self.test_user_data['email']})")
        print()
        
        # Pre-registration tests
        print("🔍 PRE-REGISTRATION AVAILABILITY CHECKS")
        print("-" * 50)
        self.test_username_availability_check_available()
        self.test_email_availability_check_available()
        
        # Registration and post-registration checks
        print("📝 USER REGISTRATION")
        print("-" * 50)
        self.test_user_registration()
        self.test_username_availability_check_taken()
        
        # Authentication tests
        print("🔐 AUTHENTICATION FLOW")
        print("-" * 50)
        self.test_login_with_credentials()
        self.test_get_current_user()
        
        # Profile management tests
        print("👤 PROFILE MANAGEMENT")
        print("-" * 50)
        self.test_get_user_profile()
        self.test_update_profile()
        self.test_change_password()
        self.test_login_with_new_password()
        
        # Session management tests
        print("🔄 SESSION MANAGEMENT")
        print("-" * 50)
        self.test_get_active_sessions()
        self.test_password_reset_flow()
        self.test_logout()
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("AUTHENTICATION TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        failed = len(self.test_results) - passed
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print()
        
        if failed > 0:
            print("❌ FAILED TESTS:")
            print("-" * 40)
            for result in self.test_results:
                if not result["success"]:
                    print(f"• {result['test']}: {result['details']}")
            print()
        
        print("✅ PASSED TESTS:")
        print("-" * 40)
        for result in self.test_results:
            if result["success"]:
                print(f"• {result['test']}")
        
        return passed, failed

if __name__ == "__main__":
    tester = AuthTester()
    tester.run_all_tests()