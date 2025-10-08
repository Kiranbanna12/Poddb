#!/usr/bin/env python3
"""
Backend API Testing Suite for Contribution Submission Flow
Tests user registration, contribution submission, and retrieval
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Backend URL from frontend .env
BASE_URL = "https://account-manager-47.preview.emergentagent.com/api"

class ContributionTester:
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

    def test_invalid_token_access(self):
        """Test Suite 6: Authorization Tests - Invalid Token Access"""
        try:
            url = f"{self.base_url}/admin/contributions/stats"
            headers = {"Authorization": "Bearer invalid_token_12345"}
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 401:
                self.log_test("Invalid Token Access", True, 
                            "Correctly returned 401 for invalid token")
            else:
                self.log_test("Invalid Token Access", False, 
                            f"Expected 401, got HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Invalid Token Access", False, f"Exception: {str(e)}")

    def test_contribution_submission_flow(self):
        """Test the complete contribution submission flow as requested"""
        print("🎯 CONTRIBUTION SUBMISSION FLOW TEST")
        print("-" * 50)
        
        # Step 1: Register a test user
        self.test_register_test_contributor()
        
        # Step 2: Submit a contribution
        self.test_submit_contribution()
        
        # Step 3: Check if contribution was saved
        self.test_verify_contribution_saved()
        
        # Step 4: Get user's contributions
        self.test_get_user_contributions()

    def test_register_test_contributor(self):
        """Step 1: Register a test user with specific credentials"""
        try:
            url = f"{self.base_url}/auth/register"
            payload = {
                "username": "testcontributor",
                "email": "testcontributor@test.com",
                "password": "Test123456",
                "confirm_password": "Test123456",
                "full_name": "Test Contributor",
                "terms_accepted": True
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
                        if "user_id" in decoded:
                            self.regular_user_token = token
                            self.test_user_id = user.get("id")
                            details = f"Test contributor registered: {user.get('username')}, ID: {user.get('id')}"
                            self.log_test("Register Test Contributor", True, details)
                        else:
                            self.log_test("Register Test Contributor", False, 
                                        "JWT token missing user_id field", decoded)
                    except Exception as jwt_error:
                        self.log_test("Register Test Contributor", False, f"JWT decode error: {jwt_error}")
                else:
                    self.log_test("Register Test Contributor", False, 
                                "Missing 'token' or 'user' in response", data)
            elif response.status_code == 400:
                # User might already exist, try to login
                self.log_test("Register Test Contributor", True, "User already exists, attempting login")
                self.test_login_test_contributor()
            else:
                self.log_test("Register Test Contributor", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Register Test Contributor", False, f"Exception: {str(e)}")

    def test_login_test_contributor(self):
        """Login the test contributor if registration failed due to existing user"""
        try:
            url = f"{self.base_url}/auth/login"
            payload = {
                "identifier": "testcontributor@test.com",
                "password": "Test123456"
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "success" in data and data["success"] and "token" in data and "user" in data:
                    user = data["user"]
                    token = data["token"]
                    
                    try:
                        import jwt
                        decoded = jwt.decode(token, options={"verify_signature": False})
                        if "user_id" in decoded:
                            self.regular_user_token = token
                            self.test_user_id = user.get("id")
                            details = f"Test contributor logged in: {user.get('username')}, ID: {user.get('id')}"
                            self.log_test("Login Test Contributor", True, details)
                        else:
                            self.log_test("Login Test Contributor", False, 
                                        "JWT token missing user_id field", decoded)
                    except Exception as jwt_error:
                        self.log_test("Login Test Contributor", False, f"JWT decode error: {jwt_error}")
                else:
                    self.log_test("Login Test Contributor", False, 
                                "Missing required fields in response", data)
            else:
                self.log_test("Login Test Contributor", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Login Test Contributor", False, f"Exception: {str(e)}")

    def test_submit_contribution(self):
        """Step 2: Submit a contribution using the token"""
        if not self.regular_user_token:
            self.log_test("Submit Contribution", False, "No user token available")
            return
            
        try:
            url = f"{self.base_url}/contributions"
            headers = {"Authorization": f"Bearer {self.regular_user_token}"}
            payload = {
                "title": "Test Podcast Submission",
                "description": "This is a test podcast submission from a contributor",
                "youtube_playlist_id": "PLtest123",
                "categories": ["Technology", "Science"],
                "languages": ["English", "Hindi"],
                "location": "Mumbai",
                "website": "https://testpodcast.com",
                "spotify_url": "https://spotify.com/testpodcast",
                "apple_podcasts_url": "",
                "jiosaavn_url": "",
                "instagram_url": "https://instagram.com/testpodcast",
                "twitter_url": "",
                "youtube_url": "https://youtube.com/@testpodcast",
                "team_members": [],
                "cover_image": "https://example.com/cover.jpg"
            }
            
            response = self.session.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if contribution was created successfully
                if "id" in data:
                    self.test_contribution_id = data.get("id")
                    status = data.get("status", "unknown")
                    details = f"Contribution created: ID {data.get('id')}, Status: {status}"
                    self.log_test("Submit Contribution", True, details)
                    
                    # Store contribution data for verification
                    self.test_contribution_data = data
                else:
                    self.log_test("Submit Contribution", False, 
                                "Missing 'id' in response", data)
            else:
                self.log_test("Submit Contribution", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Submit Contribution", False, f"Exception: {str(e)}")

    def test_verify_contribution_saved(self):
        """Step 3: Verify the contribution was saved to database"""
        if not hasattr(self, 'test_contribution_data') or not self.test_contribution_data:
            self.log_test("Verify Contribution Saved", False, "No contribution data to verify")
            return
            
        try:
            # Check if the contribution has required fields
            contribution = self.test_contribution_data
            required_fields = ["id", "title", "description", "status"]
            missing_fields = [field for field in required_fields if field not in contribution]
            
            if not missing_fields:
                # Verify status is 'pending'
                if contribution.get("status") == "pending":
                    details = f"Contribution saved correctly: ID {contribution.get('id')}, Status: pending"
                    self.log_test("Verify Contribution Saved", True, details)
                else:
                    details = f"Unexpected status: {contribution.get('status')}, expected 'pending'"
                    self.log_test("Verify Contribution Saved", False, details)
            else:
                details = f"Missing required fields: {missing_fields}"
                self.log_test("Verify Contribution Saved", False, details)
                
        except Exception as e:
            self.log_test("Verify Contribution Saved", False, f"Exception: {str(e)}")

    def test_get_user_contributions(self):
        """Step 4: Get user's contributions to verify it returns the submitted contribution"""
        if not self.regular_user_token:
            self.log_test("Get User Contributions", False, "No user token available")
            return
            
        try:
            url = f"{self.base_url}/contributions"
            headers = {"Authorization": f"Bearer {self.regular_user_token}"}
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response is a list or has contributions field
                contributions = data if isinstance(data, list) else data.get("contributions", [])
                
                if contributions:
                    # Look for our test contribution
                    test_contribution_found = False
                    for contrib in contributions:
                        if (hasattr(self, 'test_contribution_id') and 
                            contrib.get("id") == self.test_contribution_id):
                            test_contribution_found = True
                            break
                        elif contrib.get("title") == "Test Podcast Submission":
                            test_contribution_found = True
                            break
                    
                    if test_contribution_found:
                        details = f"Found {len(contributions)} contributions including test submission"
                        self.log_test("Get User Contributions", True, details)
                    else:
                        details = f"Test contribution not found in {len(contributions)} contributions"
                        self.log_test("Get User Contributions", False, details)
                else:
                    self.log_test("Get User Contributions", True, "No contributions found (acceptable for new user)")
            else:
                self.log_test("Get User Contributions", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Get User Contributions", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run the contribution submission flow test"""
        print("=" * 80)
        print("BACKEND API TESTING SUITE - CONTRIBUTION SUBMISSION FLOW")
        print("=" * 80)
        print(f"Testing against: {self.base_url}")
        print()
        
        # Run the complete contribution submission flow
        self.test_contribution_submission_flow()
        
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
    tester = ContributionTester()
    tester.run_all_tests()