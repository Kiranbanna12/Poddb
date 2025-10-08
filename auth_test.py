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

    def test_user_registration(self):
        """Test 1: User Registration Flow"""
        try:
            url = f"{self.base_url}/auth/register"
            payload = {
                "username": "sarah_podcaster",
                "email": "sarah.podcaster@example.com",
                "password": "SecurePass123!"
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields in response
                required_fields = ["user", "token"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("User Registration", False, 
                                f"Missing fields in response: {missing_fields}", data)
                    return
                
                # Verify user object structure
                user = data["user"]
                user_required_fields = ["id", "username", "email"]
                user_missing_fields = [field for field in user_required_fields if field not in user]
                
                if user_missing_fields:
                    self.log_test("User Registration", False, 
                                f"Missing user fields: {user_missing_fields}", data)
                    return
                
                # Verify JWT token
                token = data["token"]
                try:
                    # Decode without verification to check structure
                    decoded = jwt.decode(token, options={"verify_signature": False})
                    if "user_id" not in decoded:
                        self.log_test("User Registration", False, 
                                    "JWT token missing user_id", data)
                        return
                except Exception as e:
                    self.log_test("User Registration", False, 
                                f"Invalid JWT token: {str(e)}", data)
                    return
                
                # Store for later tests
                self.test_user_token = token
                self.test_user_data = user
                
                details = f"User created: {user['username']} ({user['email']}) with valid JWT token"
                self.log_test("User Registration", True, details)
                
            elif response.status_code == 400:
                # User might already exist, try with different email
                payload["email"] = "sarah.podcaster2@example.com"
                payload["username"] = "sarah_podcaster2"
                
                response = self.session.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    self.test_user_token = data["token"]
                    self.test_user_data = data["user"]
                    details = f"User created with alternate email: {data['user']['username']}"
                    self.log_test("User Registration", True, details)
                else:
                    self.log_test("User Registration", False, 
                                f"HTTP {response.status_code}: {response.text}")
            else:
                self.log_test("User Registration", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("User Registration", False, f"Exception: {str(e)}")

    def test_login_with_email(self):
        """Test 2: Login with Email in identifier field"""
        try:
            url = f"{self.base_url}/auth/login"
            payload = {
                "identifier": "sarah.podcaster@example.com",  # Using email as identifier
                "password": "SecurePass123!"
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields in response
                required_fields = ["success", "user", "token", "message"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Login with Email", False, 
                                f"Missing fields in response: {missing_fields}", data)
                    return
                
                # Verify success field
                if data.get("success") != True:
                    self.log_test("Login with Email", False, 
                                "Success field is not true", data)
                    return
                
                # Verify JWT token
                token = data["token"]
                try:
                    decoded = jwt.decode(token, options={"verify_signature": False})
                    if "user_id" not in decoded:
                        self.log_test("Login with Email", False, 
                                    "JWT token missing user_id", data)
                        return
                except Exception as e:
                    self.log_test("Login with Email", False, 
                                f"Invalid JWT token: {str(e)}", data)
                    return
                
                user = data["user"]
                details = f"Login successful for {user.get('email', 'N/A')} with valid JWT token"
                self.log_test("Login with Email", True, details)
                
            elif response.status_code == 401:
                # Try with the alternate email if first one failed
                payload["identifier"] = "sarah.podcaster2@example.com"
                response = self.session.post(url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") == True and "token" in data:
                        details = f"Login successful with alternate email"
                        self.log_test("Login with Email", True, details)
                    else:
                        self.log_test("Login with Email", False, 
                                    "Missing success or token in response", data)
                else:
                    self.log_test("Login with Email", False, 
                                f"HTTP {response.status_code}: {response.text}")
            else:
                self.log_test("Login with Email", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Login with Email", False, f"Exception: {str(e)}")

    def test_login_with_username(self):
        """Test 3: Login with Username in identifier field"""
        try:
            url = f"{self.base_url}/auth/login"
            payload = {
                "identifier": "sarah_podcaster",  # Using username as identifier
                "password": "SecurePass123!"
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                if data.get("success") != True or "token" not in data:
                    self.log_test("Login with Username", False, 
                                "Missing success or token in response", data)
                    return
                
                # Verify JWT token
                token = data["token"]
                try:
                    decoded = jwt.decode(token, options={"verify_signature": False})
                    if "user_id" not in decoded:
                        self.log_test("Login with Username", False, 
                                    "JWT token missing user_id", data)
                        return
                except Exception as e:
                    self.log_test("Login with Username", False, 
                                f"Invalid JWT token: {str(e)}", data)
                    return
                
                user = data["user"]
                details = f"Login successful for username {user.get('username', 'N/A')} with valid JWT token"
                self.log_test("Login with Username", True, details)
                
            elif response.status_code == 401:
                # Try with alternate username
                payload["identifier"] = "sarah_podcaster2"
                response = self.session.post(url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") == True and "token" in data:
                        details = f"Login successful with alternate username"
                        self.log_test("Login with Username", True, details)
                    else:
                        self.log_test("Login with Username", False, 
                                    "Missing success or token in response", data)
                else:
                    self.log_test("Login with Username", False, 
                                f"HTTP {response.status_code}: {response.text}")
            else:
                self.log_test("Login with Username", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Login with Username", False, f"Exception: {str(e)}")

    def test_login_invalid_password(self):
        """Test 4: Login with Invalid Password"""
        try:
            url = f"{self.base_url}/auth/login"
            payload = {
                "identifier": "sarah.podcaster@example.com",
                "password": "WrongPassword123!"
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 401:
                data = response.json()
                if "detail" in data:
                    details = f"Correctly returned 401 with message: {data['detail']}"
                    self.log_test("Login Invalid Password", True, details)
                else:
                    self.log_test("Login Invalid Password", True, 
                                "Correctly returned 401 error")
            else:
                self.log_test("Login Invalid Password", False, 
                            f"Expected 401, got HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Login Invalid Password", False, f"Exception: {str(e)}")

    def test_login_nonexistent_user(self):
        """Test 5: Login with Non-existent User"""
        try:
            url = f"{self.base_url}/auth/login"
            payload = {
                "identifier": "nonexistent.user@example.com",
                "password": "SomePassword123!"
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 401:
                data = response.json()
                if "detail" in data:
                    details = f"Correctly returned 401 with message: {data['detail']}"
                    self.log_test("Login Nonexistent User", True, details)
                else:
                    self.log_test("Login Nonexistent User", True, 
                                "Correctly returned 401 error")
            else:
                self.log_test("Login Nonexistent User", False, 
                            f"Expected 401, got HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Login Nonexistent User", False, f"Exception: {str(e)}")

    def test_protected_endpoint_with_token(self):
        """Test 6: Protected Endpoint with Valid Token"""
        if not self.test_user_token:
            self.log_test("Protected Endpoint with Token", False, 
                        "No valid token available from previous tests")
            return
            
        try:
            url = f"{self.base_url}/auth/me"
            headers = {
                "Authorization": f"Bearer {self.test_user_token}"
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if user data is returned
                required_fields = ["id", "username", "email"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Protected Endpoint with Token", False, 
                                f"Missing user fields: {missing_fields}", data)
                    return
                
                # Verify no password_hash in response
                if "password_hash" in data:
                    self.log_test("Protected Endpoint with Token", False, 
                                "Response contains password_hash (security issue)", data)
                    return
                
                details = f"User data retrieved: {data.get('username', 'N/A')} ({data.get('email', 'N/A')})"
                self.log_test("Protected Endpoint with Token", True, details)
                
            else:
                self.log_test("Protected Endpoint with Token", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Protected Endpoint with Token", False, f"Exception: {str(e)}")

    def test_protected_endpoint_without_token(self):
        """Test 7: Protected Endpoint without Token"""
        try:
            url = f"{self.base_url}/auth/me"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 401:
                data = response.json()
                if "detail" in data:
                    details = f"Correctly returned 401 with message: {data['detail']}"
                    self.log_test("Protected Endpoint without Token", True, details)
                else:
                    self.log_test("Protected Endpoint without Token", True, 
                                "Correctly returned 401 error")
            else:
                self.log_test("Protected Endpoint without Token", False, 
                            f"Expected 401, got HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Protected Endpoint without Token", False, f"Exception: {str(e)}")

    def test_protected_endpoint_invalid_token(self):
        """Test 8: Protected Endpoint with Invalid Token"""
        try:
            url = f"{self.base_url}/auth/me"
            headers = {
                "Authorization": "Bearer invalid.jwt.token"
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 401:
                data = response.json()
                details = f"Correctly returned 401 for invalid token"
                self.log_test("Protected Endpoint Invalid Token", True, details)
            else:
                self.log_test("Protected Endpoint Invalid Token", False, 
                            f"Expected 401, got HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Protected Endpoint Invalid Token", False, f"Exception: {str(e)}")

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