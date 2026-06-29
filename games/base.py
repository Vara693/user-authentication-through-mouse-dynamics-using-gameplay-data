import tkinter as tk
from abc import ABC, abstractmethod
from typing import Callable

class BaseGame(ABC):
    def __init__(self, parent_window, username: str, logger, on_game_complete: Callable, session_id: int):
        self.parent = parent_window
        self.username = username
        self.logger = logger
        self.on_game_complete = on_game_complete
        self.session_id = session_id
        
        self.window = tk.Toplevel(parent_window)
        self.window.title("Mouse Dynamics Game")
        self.window.geometry("800x600")
        self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        self.canvas = tk.Canvas(self.window, bg='white', width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<ButtonPress>", self._on_mouse_press)
        self.canvas.bind("<ButtonRelease>", self._on_mouse_release)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        
        self.is_running = False
        self.start_time = None
    
    def _on_mouse_move(self, event):
        """Handle mouse movement"""
        if self.is_running:
            self.logger.log_event('motion', event.x, event.y)
            self.on_mouse_move(event)
    
    def _on_mouse_press(self, event):
        """Handle mouse button press"""
        if self.is_running:
            self.logger.log_event('click', event.x, event.y, button='left', pressed=True)
            self.on_mouse_press(event)
    
    def _on_mouse_release(self, event):
        """Handle mouse button release"""
        if self.is_running:
            self.logger.log_event('click', event.x, event.y, button='left', pressed=False)
            self.on_mouse_release(event)
    
    def _on_mouse_drag(self, event):
        """Handle mouse drag"""
        if self.is_running:
            self.logger.log_event('drag', event.x, event.y)
            self.on_mouse_drag(event)
    
    def _on_window_close(self):
        """Handle window close event"""
        self.stop_game()
    
    def start_game(self):
        """Start the game"""
        self.is_running = True
        self.setup_game()
    
    def stop_game(self):
        """Stop the game"""
        self.is_running = False
        if self.window:
            self.window.destroy()
        self.on_game_complete()
    
    @abstractmethod
    def setup_game(self):
        """Set up the game elements - to be implemented by subclasses"""
        pass
    
    @abstractmethod
    def on_mouse_move(self, event):
        """Handle mouse movement - to be implemented by subclasses"""
        pass
    
    @abstractmethod
    def on_mouse_press(self, event):
        """Handle mouse press - to be implemented by subclasses"""
        pass
    
    @abstractmethod
    def on_mouse_release(self, event):
        """Handle mouse release - to be implemented by subclasses"""
        pass
    
    @abstractmethod
    def on_mouse_drag(self, event):
        """Handle mouse drag - to be implemented by subclasses"""
        pass