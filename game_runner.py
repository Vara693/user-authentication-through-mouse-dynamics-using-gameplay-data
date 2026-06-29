import tkinter as tk
from tkinter import messagebox
from typing import List, Callable

from games.target_hunt import TargetHunt
from games.drag_drop import DragDrop
from games.cookie_catcher import CookieCatcher
from games.maze_runner import MazeRunner

class GameRunner:
    def __init__(self, parent_window, username: str, logger, on_session_complete: Callable, session_id: int):
        self.parent = parent_window
        self.username = username
        self.logger = logger
        self.on_session_complete = on_session_complete
        self.session_id = session_id
        
        self.games = [TargetHunt, DragDrop, CookieCatcher, MazeRunner]
        self.current_game_index = 0
        self.current_game_instance = None
        
    def start_session(self):
        """Start the game session"""
        self._start_next_game()
    
    def _start_next_game(self):
        """Start the next game in sequence"""
        if self.current_game_index < len(self.games):
            game_class = self.games[self.current_game_index]
            self.current_game_instance = game_class(
                self.parent, 
                self.username, 
                self.logger,
                self._on_game_complete,
                self.session_id  # Pass session ID to games
            )
            self.current_game_instance.start_game()
        else:
            self._on_session_complete()
    
    def _on_game_complete(self):
        """Called when a game completes"""
        self.current_game_index += 1
        self._start_next_game()
    
    def _on_session_complete(self):
        """Called when all games are complete"""
        messagebox.showinfo("Session Complete", 
                          f"Session {self.session_id} completed! Data has been logged.")
        self.on_session_complete()