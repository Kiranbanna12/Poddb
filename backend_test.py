#!/usr/bin/env python3
"""
Backend API Testing Suite for Admin Panel APIs & Authentication
Tests Admin Authentication, Contribution Management, Sync Management, and User Management
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Backend URL from frontend .env
BASE_URL = "https://moderator-hub-4.preview.emergentagent.com/api"

class AdminPanelTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.regular_user_token = None
        self.admin_token = None
        self.test_user_id = None
        
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
        """Test Suite 1: Authentication Flow - User Registration"""
        try:
            url = f"{self.base_url}/auth/register"
            payload = {
                "username": "testuser2024",
                "email": "testuser2024@example.com",
                "password": "TestPass123!",
                "full_name": "Test User 2024"
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                if "token" in data and "user" in data:
                    user = data["user"]
                    token = data["token"]
                    
                    # Verify JWT token structure
                    try:
                        import jwt
                        decoded = jwt.decode(token, options={"verify_signature": False})
                        if "user_id" in decoded and "email" in decoded and "role" in decoded:
                            self.regular_user_token = token
                            self.test_user_id = user.get("id")
                            details = f"User created: {user.get('username')}, Role: {decoded.get('role')}"
                            self.log_test("User Registration", True, details)
                        else:
                            self.log_test("User Registration", False, 
                                        "JWT token missing required fields (user_id, email, role)", decoded)
                    except Exception as jwt_error:
                        self.log_test("User Registration", False, f"JWT decode error: {jwt_error}")
                else:
                    self.log_test("User Registration", False, 
                                "Missing 'token' or 'user' in response", data)
            elif response.status_code == 400:
                # User might already exist
                self.log_test("User Registration", True, "User already exists (acceptable)")
                # Try to login instead
                self.test_user_login()
            else:
                self.log_test("User Registration", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("User Registration", False, f"Exception: {str(e)}")

    def test_user_login(self):
        """Test Suite 1: Authentication Flow - User Login"""
        try:
            url = f"{self.base_url}/auth/login"
            payload = {
                "identifier": "testuser2024@example.com",
                "password": "TestPass123!"
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                if "success" in data and data["success"] and "token" in data and "user" in data:
                    user = data["user"]
                    token = data["token"]
                    
                    # Verify JWT token structure
                    try:
                        import jwt
                        decoded = jwt.decode(token, options={"verify_signature": False})
                        if "user_id" in decoded and "email" in decoded and "role" in decoded:
                            self.regular_user_token = token
                            self.test_user_id = user.get("id")
                            details = f"Login successful: {user.get('username')}, Role: {decoded.get('role')}"
                            self.log_test("User Login", True, details)
                        else:
                            self.log_test("User Login", False, 
                                        "JWT token missing required fields", decoded)
                    except Exception as jwt_error:
                        self.log_test("User Login", False, f"JWT decode error: {jwt_error}")
                else:
                    self.log_test("User Login", False, 
                                "Missing required fields in response", data)
            else:
                self.log_test("User Login", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("User Login", False, f"Exception: {str(e)}")

    def test_jwt_token_verification(self):
        """Test Suite 1: Authentication Flow - JWT Token Verification"""
        if not self.regular_user_token:
            self.log_test("JWT Token Verification", False, "No token available (registration/login failed)")
            return
            
        try:
            url = f"{self.base_url}/auth/me"
            headers = {"Authorization": f"Bearer {self.regular_user_token}"}
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check user data
                if "id" in data and "email" in data and "role" in data:
                    # Ensure password_hash is not exposed
                    if "password_hash" not in data:
                        details = f"Token valid, User: {data.get('username')}, Role: {data.get('role')}"
                        self.log_test("JWT Token Verification", True, details)
                    else:
                        self.log_test("JWT Token Verification", False, 
                                    "Security issue: password_hash exposed in response", data)
                else:
                    self.log_test("JWT Token Verification", False, 
                                "Missing required user fields", data)
            else:
                self.log_test("JWT Token Verification", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("JWT Token Verification", False, f"Exception: {str(e)}")

    def test_admin_login(self):
        """Test Suite 2: Admin Authentication - Admin Login"""
        try:
            url = f"{self.base_url}/auth/login"
            payload = {
                "identifier": "kiranbanna12@gmail.com",
                "password": "Admin1234!@#"
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                if "success" in data and data["success"] and "token" in data and "user" in data:
                    user = data["user"]
                    token = data["token"]
                    
                    # Verify JWT token has admin role
                    try:
                        import jwt
                        decoded = jwt.decode(token, options={"verify_signature": False})
                        if decoded.get("role") == "admin":
                            self.admin_token = token
                            details = f"Admin login successful: {user.get('email')}, Role: {decoded.get('role')}"
                            self.log_test("Admin Login", True, details)
                        else:
                            self.log_test("Admin Login", False, 
                                        f"Expected admin role, got: {decoded.get('role')}", decoded)
                    except Exception as jwt_error:
                        self.log_test("Admin Login", False, f"JWT decode error: {jwt_error}")
                else:
                    self.log_test("Admin Login", False, 
                                "Missing required fields in response", data)
            else:
                self.log_test("Admin Login", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Admin Login", False, f"Exception: {str(e)}")

    def test_admin_contribution_stats(self):
        """Test Suite 3: Admin Contribution APIs - Get Statistics"""
        if not self.admin_token:
            self.log_test("Admin Contribution Stats", False, "No admin token available")
            return
            
        try:
            url = f"{self.base_url}/admin/contributions/stats"
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "success" in data and data["success"] and "stats" in data:
                    stats = data["stats"]
                    # Check for expected stat fields
                    expected_fields = ["pending", "in_review", "approved_today", "rejected_today"]
                    present_fields = [field for field in expected_fields if field in stats]
                    
                    details = f"Stats retrieved: {len(present_fields)}/{len(expected_fields)} fields present"
                    self.log_test("Admin Contribution Stats", True, details)
                else:
                    self.log_test("Admin Contribution Stats", False, 
                                "Missing 'success' or 'stats' in response", data)
            else:
                self.log_test("Admin Contribution Stats", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Admin Contribution Stats", False, f"Exception: {str(e)}")

    def test_admin_contributions_list(self):
        """Test Suite 3: Admin Contribution APIs - Get Contributions List"""
        if not self.admin_token:
            self.log_test("Admin Contributions List", False, "No admin token available")
            return
            
        try:
            url = f"{self.base_url}/admin/contributions"
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            params = {"page": 1, "limit": 20}
            
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "success" in data and data["success"] and "contributions" in data:
                    contributions = data["contributions"]
                    details = f"Retrieved {len(contributions)} contributions"
                    self.log_test("Admin Contributions List", True, details)
                else:
                    self.log_test("Admin Contributions List", False, 
                                "Missing 'success' or 'contributions' in response", data)
            else:
                self.log_test("Admin Contributions List", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Admin Contributions List", False, f"Exception: {str(e)}")

    def test_admin_contributions_filter_status(self):
        """Test Suite 3: Admin Contribution APIs - Filter by Status"""
        if not self.admin_token:
            self.log_test("Admin Contributions Filter Status", False, "No admin token available")
            return
            
        try:
            url = f"{self.base_url}/admin/contributions"
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            params = {"status": "pending"}
            
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "success" in data and data["success"] and "contributions" in data:
                    contributions = data["contributions"]
                    details = f"Retrieved {len(contributions)} pending contributions"
                    self.log_test("Admin Contributions Filter Status", True, details)
                else:
                    self.log_test("Admin Contributions Filter Status", False, 
                                "Missing 'success' or 'contributions' in response", data)
            else:
                self.log_test("Admin Contributions Filter Status", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Admin Contributions Filter Status", False, f"Exception: {str(e)}")

    def test_admin_contributions_filter_type(self):
        """Test Suite 3: Admin Contribution APIs - Filter by Type"""
        if not self.admin_token:
            self.log_test("Admin Contributions Filter Type", False, "No admin token available")
            return
            
        try:
            url = f"{self.base_url}/admin/contributions"
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            params = {"contribution_type": "new_podcast"}
            
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "success" in data and data["success"] and "contributions" in data:
                    contributions = data["contributions"]
                    details = f"Retrieved {len(contributions)} new_podcast contributions"
                    self.log_test("Admin Contributions Filter Type", True, details)
                else:
                    self.log_test("Admin Contributions Filter Type", False, 
                                "Missing 'success' or 'contributions' in response", data)
            else:
                self.log_test("Admin Contributions Filter Type", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Admin Contributions Filter Type", False, f"Exception: {str(e)}")

    def test_admin_sync_stats(self):
        """Test Suite 4: Admin Sync APIs - Get Sync Statistics"""
        if not self.admin_token:
            self.log_test("Admin Sync Stats", False, "No admin token available")
            return
            
        try:
            url = f"{self.base_url}/admin/sync/stats"
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "success" in data and data["success"] and "stats" in data:
                    stats = data["stats"]
                    # Check for expected sync stat fields
                    expected_fields = ["total_playlists", "auto_sync_enabled", "syncs_today"]
                    present_fields = [field for field in expected_fields if field in stats]
                    
                    details = f"Sync stats retrieved: {len(present_fields)}/{len(expected_fields)} fields present"
                    self.log_test("Admin Sync Stats", True, details)
                else:
                    self.log_test("Admin Sync Stats", False, 
                                "Missing 'success' or 'stats' in response", data)
            else:
                self.log_test("Admin Sync Stats", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Admin Sync Stats", False, f"Exception: {str(e)}")

    def test_admin_sync_history(self):
        """Test Suite 4: Admin Sync APIs - Get Sync History"""
        if not self.admin_token:
            self.log_test("Admin Sync History", False, "No admin token available")
            return
            
        try:
            url = f"{self.base_url}/admin/sync/history"
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            params = {"page": 1, "limit": 10}
            
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "success" in data and data["success"] and "history" in data:
                    history = data["history"]
                    details = f"Retrieved {len(history)} sync history entries"
                    self.log_test("Admin Sync History", True, details)
                else:
                    self.log_test("Admin Sync History", False, 
                                "Missing 'success' or 'history' in response", data)
            else:
                self.log_test("Admin Sync History", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Admin Sync History", False, f"Exception: {str(e)}")

    def test_admin_users_list(self):
        """Test Suite 5: Admin User Management APIs - Get Users List"""
        if not self.admin_token:
            self.log_test("Admin Users List", False, "No admin token available")
            return
            
        try:
            url = f"{self.base_url}/admin/users"
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            params = {"page": 1, "limit": 20}
            
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "users" in data and "total" in data:
                    users = data["users"]
                    total = data["total"]
                    details = f"Retrieved {len(users)} users out of {total} total"
                    self.log_test("Admin Users List", True, details)
                else:
                    self.log_test("Admin Users List", False, 
                                "Missing 'users' or 'total' in response", data)
            else:
                self.log_test("Admin Users List", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Admin Users List", False, f"Exception: {str(e)}")

    def test_admin_user_details(self):
        """Test Suite 5: Admin User Management APIs - Get User Details"""
        if not self.admin_token or not self.test_user_id:
            self.log_test("Admin User Details", False, "No admin token or test user ID available")
            return
            
        try:
            url = f"{self.base_url}/admin/users/{self.test_user_id}"
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "id" in data and "username" in data and "email" in data and "role" in data:
                    details = f"Retrieved user details: {data.get('username')} ({data.get('email')})"
                    self.log_test("Admin User Details", True, details)
                else:
                    self.log_test("Admin User Details", False, 
                                "Missing required user fields", data)
            else:
                self.log_test("Admin User Details", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Admin User Details", False, f"Exception: {str(e)}")

    def test_admin_access_without_token(self):
        """Test Suite 6: Authorization Tests - Admin Access Without Token"""
        try:
            url = f"{self.base_url}/admin/contributions/stats"
            # No Authorization header
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 401:
                self.log_test("Admin Access Without Token", True, 
                            "Correctly returned 401 Unauthorized")
            else:
                self.log_test("Admin Access Without Token", False, 
                            f"Expected 401, got HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Admin Access Without Token", False, f"Exception: {str(e)}")

    def test_admin_access_with_regular_user_token(self):
        """Test Suite 6: Authorization Tests - Admin Access With Regular User Token"""
        if not self.regular_user_token:
            self.log_test("Admin Access With Regular User Token", False, "No regular user token available")
            return
            
        try:
            url = f"{self.base_url}/admin/contributions/stats"
            headers = {"Authorization": f"Bearer {self.regular_user_token}"}
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 403:
                self.log_test("Admin Access With Regular User Token", True, 
                            "Correctly returned 403 Forbidden")
            else:
                self.log_test("Admin Access With Regular User Token", False, 
                            f"Expected 403, got HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Admin Access With Regular User Token", False, f"Exception: {str(e)}")

    def test_admin_role_verification(self):
        """Test Suite 6: Authorization Tests - Admin Role Verification"""
        if not self.admin_token:
            self.log_test("Admin Role Verification", False, "No admin token available")
            return
            
        try:
            # Test multiple admin endpoints to verify role access
            endpoints = [
                "/admin/contributions/stats",
                "/admin/sync/stats", 
                "/admin/users"
            ]
            
            successful_endpoints = 0
            for endpoint in endpoints:
                url = f"{self.base_url}{endpoint}"
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                
                response = self.session.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    successful_endpoints += 1
            
            if successful_endpoints == len(endpoints):
                details = f"Admin role verified: {successful_endpoints}/{len(endpoints)} endpoints accessible"
                self.log_test("Admin Role Verification", True, details)
            else:
                details = f"Admin role issue: only {successful_endpoints}/{len(endpoints)} endpoints accessible"
                self.log_test("Admin Role Verification", False, details)
                
        except Exception as e:
            self.log_test("Admin Role Verification", False, f"Exception: {str(e)}")

    def test_user_registration_and_login(self):
        """Test Suite 5: Contribution Form Fixes - User Registration and Login"""
        try:
            # First register a test user
            register_url = f"{self.base_url}/auth/register"
            register_payload = {
                "username": "testcontributor",
                "email": "testcontributor@example.com",
                "password": "testpass123"
            }
            
            register_response = self.session.post(register_url, json=register_payload, timeout=10)
            
            if register_response.status_code == 200:
                register_data = register_response.json()
                
                if "token" in register_data and "user" in register_data:
                    # Store token for contribution test
                    self.auth_token = register_data["token"]
                    details = f"User registered: {register_data['user'].get('username', 'N/A')}"
                    self.log_test("User Registration", True, details)
                    
                    # Now test login
                    login_url = f"{self.base_url}/auth/login"
                    login_payload = {
                        "identifier": "testcontributor@example.com",
                        "password": "testpass123"
                    }
                    
                    login_response = self.session.post(login_url, json=login_payload, timeout=10)
                    
                    if login_response.status_code == 200:
                        login_data = login_response.json()
                        
                        if "token" in login_data and "success" in login_data and login_data["success"]:
                            # Update token from login
                            self.auth_token = login_data["token"]
                            details = f"Login successful for: {login_data.get('user', {}).get('username', 'N/A')}"
                            self.log_test("User Login", True, details)
                        else:
                            self.log_test("User Login", False, 
                                        "Missing token or success=false in login response", login_data)
                    else:
                        self.log_test("User Login", False, 
                                    f"Login HTTP {login_response.status_code}: {login_response.text}")
                else:
                    self.log_test("User Registration", False, 
                                "Missing token or user in registration response", register_data)
            elif register_response.status_code == 400:
                # User might already exist, try login directly
                self.log_test("User Registration", True, "User already exists (acceptable)")
                
                # Try login
                login_url = f"{self.base_url}/auth/login"
                login_payload = {
                    "identifier": "testcontributor@example.com",
                    "password": "testpass123"
                }
                
                login_response = self.session.post(login_url, json=login_payload, timeout=10)
                
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    if "token" in login_data:
                        self.auth_token = login_data["token"]
                        self.log_test("User Login", True, "Login successful with existing user")
                    else:
                        self.log_test("User Login", False, "Missing token in login response", login_data)
                else:
                    self.log_test("User Login", False, 
                                f"Login HTTP {login_response.status_code}: {login_response.text}")
            else:
                self.log_test("User Registration", False, 
                            f"Registration HTTP {register_response.status_code}: {register_response.text}")
                
        except Exception as e:
            self.log_test("User Registration and Login", False, f"Exception: {str(e)}")

    def test_contribution_submission_with_auth(self):
        """Test Suite 5: Contribution Form Fixes - Contribution Submission with Authentication"""
        if not hasattr(self, 'auth_token') or not self.auth_token:
            self.log_test("Contribution Submission with Auth", False, 
                        "No auth token available (registration/login failed)")
            return
            
        try:
            url = f"{self.base_url}/contributions"
            payload = {
                "title": "Test Podcast for Contribution",
                "description": "This is a test podcast submission",
                "youtube_playlist_id": "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
                "categories": ["Technology"],
                "languages": ["English"],
                "location": "Mumbai, Maharashtra, India",
                "website": "https://testpodcast.com",
                "team_members": []
            }
            
            # Add Authorization header manually
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "id" in data:
                    details = f"Contribution created with ID: {data['id']}"
                    self.log_test("Contribution Submission with Auth", True, details)
                else:
                    self.log_test("Contribution Submission with Auth", False, 
                                "Missing 'id' in response", data)
            else:
                self.log_test("Contribution Submission with Auth", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Contribution Submission with Auth", False, f"Exception: {str(e)}")

    def test_contribution_submission_without_auth(self):
        """Test Suite 5: Contribution Form Fixes - Contribution Submission without Authentication"""
        try:
            url = f"{self.base_url}/contributions"
            payload = {
                "title": "Test Podcast Unauthorized",
                "description": "This should fail without auth",
                "youtube_playlist_id": "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
                "categories": ["Technology"],
                "languages": ["English"]
            }
            
            # Don't include Authorization header
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 401:
                self.log_test("Contribution Submission without Auth", True, 
                            "Correctly returned 401 Unauthorized")
            else:
                self.log_test("Contribution Submission without Auth", False, 
                            f"Expected 401, got HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Contribution Submission without Auth", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all test suites"""
        print("=" * 80)
        print("BACKEND API TESTING SUITE - CONTRIBUTION FORM FIXES")
        print("=" * 80)
        print(f"Testing against: {self.base_url}")
        print()
        
        # Test Suite 5: Contribution Form Fixes (Priority)
        print("🔧 TEST SUITE 5: Contribution Form Fixes")
        print("-" * 50)
        self.test_add_new_location()
        self.test_add_new_location_minimal()
        self.test_search_locations()
        self.test_user_registration_and_login()
        self.test_contribution_submission_with_auth()
        self.test_contribution_submission_without_auth()
        
        # Test Suite 1: YouTube API Integration
        print("🎥 TEST SUITE 1: YouTube API Integration")
        print("-" * 50)
        self.test_youtube_fetch_playlist()
        self.test_youtube_fetch_video()
        
        # Test Suite 2: Smart Search Endpoints
        print("🔍 TEST SUITE 2: Smart Search Endpoints")
        print("-" * 50)
        self.test_search_categories()
        self.test_add_new_category()
        self.test_search_languages()
        self.test_add_new_language()
        self.test_search_people()
        
        # Test Suite 3: People/Team Management
        print("👥 TEST SUITE 3: People/Team Management")
        print("-" * 50)
        self.test_create_person()
        self.test_get_person_by_id()
        self.test_search_people_with_query()
        
        # Test Suite 4: Episode Management
        print("📺 TEST SUITE 4: Episode Management")
        print("-" * 50)
        self.test_get_podcast_episodes()
        self.test_episode_import_preview()
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        failed = len(self.test_results) - passed
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print()
        
        if failed > 0:
            print("FAILED TESTS:")
            print("-" * 40)
            for result in self.test_results:
                if not result["success"]:
                    print(f"❌ {result['test']}: {result['details']}")
            print()
        
        print("PASSED TESTS:")
        print("-" * 40)
        for result in self.test_results:
            if result["success"]:
                print(f"✅ {result['test']}")
        
        return passed, failed

if __name__ == "__main__":
    tester = BackendTester()
    tester.run_all_tests()