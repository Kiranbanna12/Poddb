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

    def test_youtube_fetch_playlist(self):
        """Test Suite 1: YouTube API Integration - Fetch Playlist"""
        try:
            url = f"{self.base_url}/youtube/fetch-playlist"
            payload = {
                "playlist_url": "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
            }
            
            response = self.session.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if "playlist" in data and "episodes" in data:
                    playlist = data["playlist"]
                    episodes = data["episodes"]
                    
                    # Check playlist details
                    required_playlist_fields = ["title", "description", "channel_name"]
                    missing_fields = [field for field in required_playlist_fields if field not in playlist]
                    
                    if missing_fields:
                        self.log_test("YouTube Fetch Playlist", False, 
                                    f"Missing playlist fields: {missing_fields}", data)
                        return
                    
                    # Check if episodes array exists and has content
                    if not isinstance(episodes, list):
                        self.log_test("YouTube Fetch Playlist", False, 
                                    "Episodes should be an array", data)
                        return
                    
                    # Check for Cloudinary URLs if episodes exist
                    cloudinary_check = True
                    if episodes:
                        for episode in episodes[:3]:  # Check first 3 episodes
                            if "thumbnail_cloudinary" not in episode:
                                cloudinary_check = False
                                break
                    
                    details = f"Playlist: {playlist.get('title', 'N/A')}, Episodes: {len(episodes)}"
                    if cloudinary_check and episodes:
                        details += ", Cloudinary URLs present"
                    elif not episodes:
                        details += ", No episodes found (may be empty playlist)"
                    else:
                        details += ", Cloudinary URLs missing"
                    
                    self.log_test("YouTube Fetch Playlist", True, details)
                else:
                    self.log_test("YouTube Fetch Playlist", False, 
                                "Missing 'playlist' or 'episodes' in response", data)
            else:
                self.log_test("YouTube Fetch Playlist", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("YouTube Fetch Playlist", False, f"Exception: {str(e)}")

    def test_youtube_fetch_video(self):
        """Test Suite 1: YouTube API Integration - Fetch Single Video"""
        try:
            url = f"{self.base_url}/youtube/fetch-video"
            payload = {
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            }
            
            response = self.session.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ["title", "description", "duration", "thumbnail"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("YouTube Fetch Video", False, 
                                f"Missing fields: {missing_fields}", data)
                    return
                
                # Check for Cloudinary URL
                cloudinary_present = "thumbnail_cloudinary" in data
                details = f"Title: {data.get('title', 'N/A')[:50]}..."
                if cloudinary_present:
                    details += ", Cloudinary URL present"
                else:
                    details += ", Cloudinary URL missing"
                
                self.log_test("YouTube Fetch Video", True, details)
            else:
                self.log_test("YouTube Fetch Video", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("YouTube Fetch Video", False, f"Exception: {str(e)}")

    def test_search_categories(self):
        """Test Suite 2: Smart Search - Categories"""
        try:
            url = f"{self.base_url}/search/categories"
            params = {"q": "tech", "limit": 5}
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    details = f"Found {len(data)} categories matching 'tech'"
                    self.log_test("Search Categories", True, details)
                else:
                    self.log_test("Search Categories", False, 
                                "Response should be an array", data)
            else:
                self.log_test("Search Categories", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Search Categories", False, f"Exception: {str(e)}")

    def test_add_new_category(self):
        """Test Suite 2: Smart Search - Add New Category"""
        try:
            url = f"{self.base_url}/search/categories/add"
            params = {
                "name": "TestCategory",
                "description": "Test Description",
                "icon": "TestIcon"
            }
            
            response = self.session.post(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "id" in data and "slug" in data:
                    details = f"Created category with ID: {data['id']}, Slug: {data.get('slug', 'N/A')}"
                    self.log_test("Add New Category", True, details)
                else:
                    self.log_test("Add New Category", False, 
                                "Missing 'id' or 'slug' in response", data)
            else:
                self.log_test("Add New Category", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Add New Category", False, f"Exception: {str(e)}")

    def test_search_languages(self):
        """Test Suite 2: Smart Search - Languages"""
        try:
            url = f"{self.base_url}/search/languages"
            params = {"q": "hindi", "limit": 5}
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    details = f"Found {len(data)} languages matching 'hindi'"
                    self.log_test("Search Languages", True, details)
                else:
                    self.log_test("Search Languages", False, 
                                "Response should be an array", data)
            else:
                self.log_test("Search Languages", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Search Languages", False, f"Exception: {str(e)}")

    def test_add_new_language(self):
        """Test Suite 2: Smart Search - Add New Language"""
        try:
            url = f"{self.base_url}/search/languages/add"
            params = {
                "code": "test",
                "name": "TestLang",
                "native_name": "Test"
            }
            
            response = self.session.post(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "code" in data and "name" in data:
                    details = f"Created language: {data['name']} ({data['code']})"
                    self.log_test("Add New Language", True, details)
                else:
                    self.log_test("Add New Language", False, 
                                "Missing 'code' or 'name' in response", data)
            else:
                self.log_test("Add New Language", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Add New Language", False, f"Exception: {str(e)}")

    def test_search_locations(self):
        """Test Suite 2: Smart Search - Locations"""
        try:
            url = f"{self.base_url}/search/locations"
            params = {"q": "mumbai", "limit": 5}
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    details = f"Found {len(data)} locations matching 'mumbai'"
                    self.log_test("Search Locations", True, details)
                else:
                    self.log_test("Search Locations", False, 
                                "Response should be an array", data)
            else:
                self.log_test("Search Locations", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Search Locations", False, f"Exception: {str(e)}")

    def test_search_people(self):
        """Test Suite 2: Smart Search - People"""
        try:
            url = f"{self.base_url}/search/people"
            params = {"q": "", "limit": 5}
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    details = f"Found {len(data)} people (may be empty initially)"
                    self.log_test("Search People", True, details)
                else:
                    self.log_test("Search People", False, 
                                "Response should be an array", data)
            else:
                self.log_test("Search People", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Search People", False, f"Exception: {str(e)}")

    def test_create_person(self):
        """Test Suite 3: People/Team Management - Create Person"""
        try:
            url = f"{self.base_url}/people"
            payload = {
                "full_name": "Test Host",
                "role": "Host",
                "bio": "Test bio for podcast host",
                "location": "Mumbai",
                "instagram_url": "https://instagram.com/testhost"
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "id" in data and "slug" in data:
                    self.created_person_id = data["id"]  # Store for later tests
                    details = f"Created person: {data.get('full_name', 'N/A')} (ID: {data['id']})"
                    self.log_test("Create Person", True, details)
                else:
                    self.log_test("Create Person", False, 
                                "Missing 'id' or 'slug' in response", data)
            else:
                self.log_test("Create Person", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Create Person", False, f"Exception: {str(e)}")

    def test_get_person_by_id(self):
        """Test Suite 3: People/Team Management - Get Person by ID"""
        if not self.created_person_id:
            self.log_test("Get Person by ID", False, "No person ID available (create person test failed)")
            return
            
        try:
            url = f"{self.base_url}/people/{self.created_person_id}"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "id" in data and "full_name" in data:
                    details = f"Retrieved person: {data.get('full_name', 'N/A')}"
                    self.log_test("Get Person by ID", True, details)
                else:
                    self.log_test("Get Person by ID", False, 
                                "Missing required fields in response", data)
            else:
                self.log_test("Get Person by ID", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Get Person by ID", False, f"Exception: {str(e)}")

    def test_search_people_with_query(self):
        """Test Suite 3: People/Team Management - Search People with Query"""
        try:
            url = f"{self.base_url}/search/people"
            params = {"q": "Test", "limit": 5}
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    # Check if our created person is in the results
                    found_test_host = any(person.get('full_name') == 'Test Host' for person in data)
                    details = f"Found {len(data)} people matching 'Test'"
                    if found_test_host:
                        details += " (includes 'Test Host')"
                    self.log_test("Search People with Query", True, details)
                else:
                    self.log_test("Search People with Query", False, 
                                "Response should be an array", data)
            else:
                self.log_test("Search People with Query", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Search People with Query", False, f"Exception: {str(e)}")

    def test_get_podcast_episodes(self):
        """Test Suite 4: Episode Management - Get Podcast Episodes"""
        try:
            # Test with podcast ID 1 (if exists)
            url = f"{self.base_url}/podcasts/1/episodes"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    details = f"Found {len(data)} episodes for podcast 1"
                    self.log_test("Get Podcast Episodes", True, details)
                else:
                    self.log_test("Get Podcast Episodes", False, 
                                "Response should be an array", data)
            elif response.status_code == 404:
                # Podcast doesn't exist, which is acceptable
                self.log_test("Get Podcast Episodes", True, "Podcast 1 not found (acceptable)")
            else:
                self.log_test("Get Podcast Episodes", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Get Podcast Episodes", False, f"Exception: {str(e)}")

    def test_episode_import_preview(self):
        """Test Suite 4: Episode Management - Episode Import Preview"""
        try:
            url = f"{self.base_url}/episodes/import"
            payload = {
                "source_type": "video",
                "source_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "season_number": 1
                # No podcast_id for preview mode
            }
            
            response = self.session.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if "episodes" in data and "success" in data:
                    episodes = data["episodes"]
                    if isinstance(episodes, list) and len(episodes) > 0:
                        episode = episodes[0]
                        # Check if it has video data
                        if "title" in episode and "youtube_video_id" in episode:
                            details = f"Preview mode: {len(episodes)} episode(s), Title: {episode['title'][:50]}..."
                            self.log_test("Episode Import Preview", True, details)
                        else:
                            self.log_test("Episode Import Preview", False, 
                                        "Missing video data in episode", data)
                    else:
                        self.log_test("Episode Import Preview", False, 
                                    "No episodes in response", data)
                else:
                    self.log_test("Episode Import Preview", False, 
                                "Missing 'episodes' or 'success' in response", data)
            else:
                self.log_test("Episode Import Preview", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Episode Import Preview", False, f"Exception: {str(e)}")

    def test_add_new_location(self):
        """Test Suite 5: Contribution Form Fixes - Add New Location"""
        try:
            url = f"{self.base_url}/search/locations/add"
            params = {
                "location": "Mumbai",
                "state": "Maharashtra", 
                "country": "India"
            }
            
            response = self.session.post(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields in response
                required_fields = ["location", "name"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Add New Location", False, 
                                f"Missing fields: {missing_fields}", data)
                    return
                
                # Verify formatted name
                expected_name = "Mumbai, Maharashtra, India"
                if data.get("name") == expected_name:
                    details = f"Location created: {data['name']}"
                    self.log_test("Add New Location", True, details)
                else:
                    details = f"Name format incorrect. Expected: {expected_name}, Got: {data.get('name')}"
                    self.log_test("Add New Location", False, details, data)
            else:
                self.log_test("Add New Location", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Add New Location", False, f"Exception: {str(e)}")

    def test_add_new_location_minimal(self):
        """Test Suite 5: Contribution Form Fixes - Add New Location (Minimal Data)"""
        try:
            url = f"{self.base_url}/search/locations/add"
            params = {
                "location": "Delhi"
                # No state or country
            }
            
            response = self.session.post(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "location" in data and "name" in data:
                    # Should just be "Delhi" without commas
                    expected_name = "Delhi"
                    if data.get("name") == expected_name:
                        details = f"Minimal location created: {data['name']}"
                        self.log_test("Add New Location (Minimal)", True, details)
                    else:
                        details = f"Name format incorrect. Expected: {expected_name}, Got: {data.get('name')}"
                        self.log_test("Add New Location (Minimal)", False, details, data)
                else:
                    self.log_test("Add New Location (Minimal)", False, 
                                "Missing required fields", data)
            else:
                self.log_test("Add New Location (Minimal)", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Add New Location (Minimal)", False, f"Exception: {str(e)}")

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