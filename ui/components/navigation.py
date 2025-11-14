"""
Navigation Header Component
Reusable top navigation bar with glassmorphism design
"""

import streamlit as st


def render_navigation():
    """
    Render the sticky navigation header with page navigation buttons
    Matches the design from UI_MOCKUP_PROFESSIONAL.html
    """
    
    # Get current page from query params or default to Home
    current_page = st.session_state.get('current_page', 'Home')
    
    # Navigation CSS and HTML
    nav_html = """
    <style>
        /* Navigation Bar */
        .nav-header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 9999;
            padding: 20px 40px;
            background: rgba(15, 15, 30, 0.8);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        }
        
        .nav-content {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .nav-logo {
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.02em;
        }
        
        .nav-buttons {
            display: flex;
            gap: 8px;
        }
        
        .nav-btn {
            background: none;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            font-size: 15px;
            border-radius: 8px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            color: #a1a1aa;
            font-weight: 500;
            text-decoration: none;
            border: 1px solid transparent;
        }
        
        .nav-btn:hover {
            background: rgba(255, 255, 255, 0.05);
            color: #e4e4e7;
        }
        
        .nav-btn.active {
            background: rgba(59, 130, 246, 0.15);
            color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.3);
        }
        
        /* Spacer to prevent content from hiding under fixed nav */
        .nav-spacer {
            height: 80px;
        }
        
        /* Mobile responsiveness */
        @media (max-width: 768px) {
            .nav-header {
                padding: 15px 20px;
            }
            
            .nav-content {
                flex-direction: column;
                gap: 12px;
            }
            
            .nav-logo {
                font-size: 20px;
            }
            
            .nav-buttons {
                width: 100%;
                justify-content: center;
                flex-wrap: wrap;
            }
            
            .nav-btn {
                padding: 8px 16px;
                font-size: 14px;
            }
        }
    </style>
    
    <div class="nav-header">
        <div class="nav-content">
            <div class="nav-logo">GIS Portfolio Analyzer</div>
            <div class="nav-buttons" id="nav-buttons">
                <!-- Navigation buttons will be rendered by Streamlit -->
            </div>
        </div>
    </div>
    <div class="nav-spacer"></div>
    """
    
    # Render the nav HTML
    st.markdown(nav_html, unsafe_allow_html=True)
    
    # Unique container for navigation buttons
    st.markdown('<div class="nav-button-container">', unsafe_allow_html=True)
    
    # Additional CSS to position button container at the nav level
    st.markdown("""
    <style>
        /* Position ONLY the nav button container to overlay on the nav */
        .nav-button-container + div[data-testid="stHorizontalBlock"] {
            position: fixed !important;
            top: 20px !important;
            right: 40px !important;
            z-index: 10000 !important;
            background: transparent !important;
            width: auto !important;
        }
        
        /* Style ONLY nav buttons to match nav design */
        .nav-button-container + div[data-testid="stHorizontalBlock"] button {
            background: none !important;
            border: 1px solid transparent !important;
            padding: 10px 20px !important;
            font-size: 15px !important;
            border-radius: 8px !important;
            color: #a1a1aa !important;
            font-weight: 500 !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        .nav-button-container + div[data-testid="stHorizontalBlock"] button:hover {
            background: rgba(255, 255, 255, 0.05) !important;
            color: #e4e4e7 !important;
            border: 1px solid transparent !important;
        }
        
        /* Primary (active) button styling */
        .nav-button-container + div[data-testid="stHorizontalBlock"] button[kind="primary"] {
            background: rgba(59, 130, 246, 0.15) !important;
            color: #60a5fa !important;
            border: 1px solid rgba(59, 130, 246, 0.3) !important;
        }
        
        .nav-button-container + div[data-testid="stHorizontalBlock"] button[kind="primary"]:hover {
            background: rgba(59, 130, 246, 0.2) !important;
            border: 1px solid rgba(59, 130, 246, 0.4) !important;
        }
        
        /* Hide button container column gaps */
        .nav-button-container + div[data-testid="stHorizontalBlock"] [data-testid="column"] {
            padding: 0 4px !important;
        }
        
        /* Hide the marker div */
        .nav-button-container {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Create navigation buttons using Streamlit columns
    col_home, col_map, col_upload, col_settings = st.columns(4)
    
    with col_home:
        if st.button("Home", key="nav_home", use_container_width=True, 
                    type="primary" if current_page == "Home" else "secondary"):
            st.switch_page("pages/1_Home.py")
    
    with col_map:
        if st.button("Map Viewer", key="nav_map", use_container_width=True,
                    type="primary" if current_page == "Map Viewer" else "secondary"):
            st.switch_page("pages/2_Map_Viewer.py")
    
    with col_upload:
        if st.button("Upload Data", key="nav_upload", use_container_width=True,
                    type="primary" if current_page == "Upload Data" else "secondary"):
            st.switch_page("pages/3_Upload_Data.py")
    
    with col_settings:
        if st.button("Settings", key="nav_settings", use_container_width=True,
                    type="primary" if current_page == "Settings" else "secondary"):
            st.switch_page("pages/4_Settings.py")

