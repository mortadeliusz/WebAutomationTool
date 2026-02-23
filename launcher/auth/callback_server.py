"""
Callback server for receiving auth callbacks
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading


class CallbackError(Exception):
    """Callback error"""
    pass


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for auth callbacks"""
    
    def do_GET(self):
        """Handle GET request"""
        parsed = urlparse(self.path)
        
        if parsed.path == '/callback':
            # Extract token from query params
            params = parse_qs(parsed.query)
            token = params.get('token', [None])[0]
            
            if token:
                # Store token in server instance
                self.server.received_token = token
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html = """
                <html>
                <body style="font-family: sans-serif; text-align: center; padding: 40px;">
                    <h1>✅ Authentication Complete!</h1>
                    <p>You can close this window and return to the app.</p>
                    <script>setTimeout(() => window.close(), 2000);</script>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
            else:
                # No token in callback
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress log messages"""
        pass


class CallbackServer:
    """HTTP server for receiving auth callbacks"""
    
    def __init__(self, port: int = 0):
        """
        Initialize callback server
        
        Args:
            port: Port to listen on (0 = OS assigns available port)
        """
        self.port = port
        self.server = None
        self.received_token = None
        self.event = threading.Event()
    
    def start(self) -> None:
        """Start HTTP server on localhost with OS-assigned port"""
        # Port 0 = OS assigns any available port
        self.server = HTTPServer(('127.0.0.1', self.port), CallbackHandler)
        self.port = self.server.server_address[1]  # Get actual port assigned
        
        # Start server in background thread
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
    
    def _run_server(self):
        """Run server until token received"""
        while not self.received_token:
            self.server.handle_request()
            if hasattr(self.server, 'received_token'):
                self.received_token = self.server.received_token
                self.event.set()
    
    def wait_for_callback(self, timeout: int = 300) -> str:
        """
        Wait for browser callback
        
        Args:
            timeout: Max seconds to wait
        
        Returns:
            Token string from callback
        
        Raises:
            TimeoutError: No callback within timeout
            CallbackError: Invalid callback data
        """
        if not self.event.wait(timeout):
            raise TimeoutError("Authentication timed out")
        
        if not self.received_token:
            raise CallbackError("No token received")
        
        return self.received_token
    
    def stop(self) -> None:
        """Stop HTTP server (no-op - daemon thread will exit automatically)"""
        pass
