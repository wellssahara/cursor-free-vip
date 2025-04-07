from oauth_auth import main as oauth_main

def main(translator=None):
    """Handle GitHub OAuth registration"""
    oauth_main('github', translator) 