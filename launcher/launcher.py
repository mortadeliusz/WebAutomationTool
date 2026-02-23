"""
Launcher - System browser authentication
"""
import logging
import subprocess
import sys
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from launcher.auth.callback_server import CallbackServer
from launcher.auth.backend_client import BackendClient, TokenInvalidError, BackendError
from config import BACKEND_URL

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def launch_main_app(user_data):
    """Launch main application with user data"""
    import json
    import base64
    
    # Encode user data (simple obfuscation)
    encoded = base64.b64encode(json.dumps(user_data).encode()).decode()
    
    main_app_path = Path(__file__).parent.parent / "main.py"
    
    # Suppress output in production, keep it in development
    if getattr(sys, 'frozen', False):
        # Running as packaged executable - suppress output for clean UX
        subprocess.Popen([
            sys.executable,
            str(main_app_path),
            '--session', encoded
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        # Running from source - keep output for debugging
        subprocess.Popen([
            sys.executable,
            str(main_app_path),
            '--session', encoded
        ])


def main():
    """Main launcher flow"""
    logger.info("Starting authentication flow")
    
    # 1. Start callback server (OS assigns available port)
    callback_server = CallbackServer()
    callback_server.start()
    logger.info(f"Callback server listening on port {callback_server.port}")
    
    # 2. Open browser with assigned port
    auth_url = f"{BACKEND_URL}/ui/auth/index.html?callback_port={callback_server.port}"
    webbrowser.open(auth_url)
    logger.info("Browser opened for authentication")
    
    print(f"Authenticating (callback on port {callback_server.port})...")
    
    # 3. Wait for callback
    try:
        token = callback_server.wait_for_callback(timeout=300)
        logger.info("Callback received successfully")
    except TimeoutError:
        logger.warning("Authentication timed out")
        print("Authentication timed out.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Authentication failed: {e}", exc_info=True)
        print(f"Authentication failed: {e}")
        sys.exit(1)
    
    # 4. Validate token
    backend_client = BackendClient(BACKEND_URL)
    try:
        user_data = backend_client.validate_token(token)
        logger.info(f"Token validated for user: {user_data.get('email')}")
    except TokenInvalidError as e:
        logger.error(f"Token validation failed: {e}")
        print(f"Validation failed: {e}")
        sys.exit(1)
    except BackendError as e:
        logger.error(f"Backend error: {e}")
        print(f"Cannot connect to server: {e}")
        sys.exit(1)
    
    # 5. Check access and launch
    if user_data.get('access'):
        logger.info("Access granted, launching main application")
        print(f"Welcome {user_data.get('email', 'User')}!")
        launch_main_app(user_data)
    else:
        logger.warning(f"Access denied for user: {user_data.get('email')}")
        print("Access denied.")
        sys.exit(1)


if __name__ == "__main__":
    main()
