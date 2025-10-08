#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: |
  Build an advanced contribution page with two entry options:
  1. YouTube Playlist Import - Fetch and populate podcast data automatically
  2. Manual Entry - Traditional form-based entry
  
  Features to implement:
  - YouTube API integration for playlist/video fetching
  - Smart search comboboxes with "Add New" functionality (categories, languages, locations, people)
  - Advanced episode management (add single/multiple, seasons, auto-sync)
  - Team management with episode assignment checkboxes
  - Cloudinary integration for image uploads
  - Daily auto-sync for playlists

backend:
  - task: "Database schema updates"
    implemented: true
    working: true
    file: "/app/backend/database/db.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Added episode_guests table for team member episode assignments, podcast_playlists table for auto-sync, added season fields to episodes table, enhanced people table with social media fields"

  - task: "YouTube API service integration"
    implemented: true
    working: "NA"
    file: "/app/backend/services/youtube_service.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Created YouTube service with playlist/video fetching, duration parsing, thumbnail extraction using google-api-python-client library"

  - task: "Cloudinary image upload service"
    implemented: true
    working: "NA"
    file: "/app/backend/services/cloudinary_service.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Created Cloudinary service for uploading images from URLs, files, and base64, integrated with YouTube thumbnail downloads"

  - task: "Database query functions for advanced features"
    implemented: true
    working: "NA"
    file: "/app/backend/database/queries.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added queries for people management, episode-guest assignments, episode bulk operations, smart search for categories/languages/locations/people, playlist sync management"

  - task: "API endpoints for YouTube integration"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added /api/youtube/fetch-playlist and /api/youtube/fetch-video endpoints with Cloudinary thumbnail uploads"

  - task: "API endpoints for smart search"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added search endpoints for categories, languages, locations, people with add-new functionality"

  - task: "API endpoints for people/team management"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added endpoints for creating people, assigning to episodes, searching people"

  - task: "API endpoints for episode management"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added endpoints for importing episodes (single/bulk), creating episodes, deleting episodes, getting podcast episodes"

frontend:
  - task: "Contribution page redesign - Entry options"
    implemented: false
    working: "NA"
    file: "/app/frontend/src/pages/ContributePage.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Not yet implemented - will create two-option landing page (YouTube Import vs Manual)"

  - task: "SmartSearchCombobox reusable component"
    implemented: false
    working: "NA"
    file: "To be created"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Not yet implemented - reusable component for search with add-new functionality"

  - task: "YouTube import workflow UI"
    implemented: false
    working: "NA"
    file: "To be created"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Not yet implemented - playlist URL input, fetch, auto-populate form"

  - task: "Episode management UI"
    implemented: false
    working: "NA"
    file: "To be created"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Not yet implemented - episode list, add modal, season modal"

  - task: "Team management UI with episode assignment"
    implemented: false
    working: "NA"
    file: "To be created"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Not yet implemented - search people, add new, episode checkboxes"

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 0
  run_ui: false

test_plan:
  current_focus:
    - "YouTube API service integration"
    - "Cloudinary image upload service"
    - "API endpoints for YouTube integration"
    - "API endpoints for smart search"
    - "API endpoints for people/team management"
    - "API endpoints for episode management"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: |
      Backend implementation complete for advanced contribution page features:
      
      Implemented:
      1. Database schema enhanced with episode_guests, podcast_playlists tables and season fields
      2. YouTube API service for fetching playlist/video data
      3. Cloudinary service for image uploads
      4. Comprehensive database queries for all new features
      5. Complete API endpoints for YouTube integration, smart search, people management, episode management
      
      Ready for testing:
      - YouTube playlist/video fetching endpoints
      - Cloudinary image upload integration
      - Smart search endpoints (categories, languages, locations, people)
      - People/team management endpoints
      - Episode import and management endpoints
      
      Next steps:
      - Test all backend endpoints
      - Implement frontend components
      - Integrate frontend with backend APIs