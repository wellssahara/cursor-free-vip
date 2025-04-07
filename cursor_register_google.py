from oauth_auth import main as oauth_main

def main(translator=None):
    """Handle Google OAuth registration"""
    oauth_main('google', translator) 