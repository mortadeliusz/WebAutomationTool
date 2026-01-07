"""
Task Manager Worker Thread - Persistent thread for task configuration with own browser
"""

from PyQt6.QtCore import QThread, pyqtSignal
from core.browser_controller import BrowserController
from core.element_picker import ElementPicker

class TaskManagerWorkerThread(QThread):
    """Persistent worker thread for Task Manager with own browser lifecycle"""
    
    # Signals
    browser_ready = pyqtSignal(bool)  # browser launch success/failure
    navigation_complete = pyqtSignal(bool)  # navigation success/failure
    element_picked = pyqtSignal(dict)  # element picker result
    error_occurred = pyqtSignal(str)  # error messages
    
    def __init__(self):
        super().__init__()
        self.browser_controller = None
        self.should_stop = False
        self.pending_requests = []
    
    def run(self):
        """Main thread loop - stays alive for Task Manager lifetime"""
        print("🔧 Task Manager worker thread started")
        
        # Create own browser controller
        self.browser_controller = BrowserController()
        
        # Main event loop
        while not self.should_stop:
            # Process pending requests
            if self.pending_requests:
                request = self.pending_requests.pop(0)
                self._handle_request(request)
            
            # Small sleep to prevent busy waiting
            self.msleep(100)
        
        # Cleanup on exit
        if self.browser_controller:
            try:
                print("🧹 Task Manager worker cleaning up browser...")
                self.browser_controller.stop()
            except Exception as e:
                print(f"Warning: Task Manager browser cleanup error: {e}")
        
        print("🔧 Task Manager worker thread stopped")
    
    def stop_worker(self):
        """Stop the worker thread"""
        self.should_stop = True
    
    def is_browser_running(self):
        """Check if browser is running"""
        return (self.browser_controller and 
                self.browser_controller.is_browser_running())
    
    def launch_browser(self, browser_type='chrome'):
        """Request browser launch"""
        self.pending_requests.append({
            'type': 'launch_browser',
            'browser_type': browser_type
        })
    
    def navigate_to(self, url):
        """Request navigation"""
        self.pending_requests.append({
            'type': 'navigate',
            'url': url
        })
    
    def pick_element(self):
        """Request element picking"""
        self.pending_requests.append({
            'type': 'pick_element'
        })
    
    def _handle_request(self, request):
        """Handle different types of requests"""
        try:
            if request['type'] == 'launch_browser':
                success = self.browser_controller.launch_browser(request['browser_type'])
                self.browser_ready.emit(success)
                
            elif request['type'] == 'navigate':
                success = self.browser_controller.navigate(request['url'])
                self.navigation_complete.emit(success)
                
            elif request['type'] == 'pick_element':
                page = self.browser_controller.pages.get('main')
                if page:
                    picker = ElementPicker(page)
                    result = picker.pick_element()
                    self.element_picked.emit(result)
                else:
                    self.error_occurred.emit("No browser page available")
                    
        except Exception as e:
            self.error_occurred.emit(str(e))