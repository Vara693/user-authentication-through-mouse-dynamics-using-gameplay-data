import tkinter as tk
import random
from games.base import BaseGame

class TargetHunt(BaseGame):
    def __init__(self, parent_window, username: str, logger, on_game_complete: callable, session_id: int):
        super().__init__(parent_window, username, logger, on_game_complete, session_id)
        self.window.title("Target Hunt - Click the target 15 times!")
        
        self.current_target = None
        self.targets_clicked = 0
        self.total_targets = 15
        self.game_time = 30  # 30 seconds time limit
        
        # Game info display
        self.info_text = self.canvas.create_text(
            400, 30, 
            text=f"Targets: {self.targets_clicked}/{self.total_targets} | Time: {self.game_time}s",
            font=('Arial', 14)
        )
    
    def setup_game(self):
        """Set up the game with initial target"""
        self.canvas.delete("target")
        self.targets_clicked = 0
        self.time_remaining = self.game_time
        
        # Create first target
        self._create_target()
        
        # Start timer
        self.update_timer()
        
        self._update_display()
    
    def _create_target(self):
        """Create a new target at random position"""
        if self.current_target:
            self.canvas.delete(self.current_target)
        
        x = random.randint(50, 750)
        y = random.randint(80, 550)
        radius = 30  # Slightly larger target
        
        self.current_target = self.canvas.create_oval(
            x-radius, y-radius, x+radius, y+radius,
            fill='red', tags="target", outline='darkred', width=3
        )
    
    def _update_display(self):
        """Update the game display"""
        self.canvas.itemconfig(
            self.info_text, 
            text=f"Targets: {self.targets_clicked}/{self.total_targets} | Time: {self.time_remaining}s"
        )
    
    def update_timer(self):
        """Update the game timer"""
        if self.is_running:
            self.time_remaining -= 1
            self._update_display()
            
            if self.time_remaining <= 0:
                # Time's up!
                self.canvas.create_text(
                    400, 300, 
                    text="Time's Up!\nGame Over!", 
                    font=('Arial', 24, 'bold'),
                    fill='red',
                    justify=tk.CENTER
                )
                self.window.after(2000, self.stop_game)
            else:
                # Continue timer
                self.window.after(1000, self.update_timer)
    
    def on_mouse_press(self, event):
        """Handle mouse clicks on target"""
        if not self.current_target or not self.is_running:
            return
            
        clicked_items = self.canvas.find_overlapping(event.x-5, event.y-5, event.x+5, event.y+5)
        
        if self.current_target in clicked_items:
            # Target hit!
            self.targets_clicked += 1
            
            # Visual feedback
            self.canvas.itemconfig(self.current_target, fill='green')
            self.window.after(100, lambda: self.canvas.itemconfig(self.current_target, fill='red'))
            
            # Create new target at different position
            self._create_target()
            
            self._update_display()
            
            # Check if game is complete
            if self.targets_clicked >= self.total_targets:
                self.canvas.create_text(
                    400, 300, 
                    text="Target Hunt Complete!\nExcellent!", 
                    font=('Arial', 24, 'bold'),
                    fill='green',
                    justify=tk.CENTER
                )
                self.window.after(1500, self.stop_game)
    
    def on_mouse_move(self, event):
        """Handle mouse movement"""
        pass
    
    def on_mouse_release(self, event):
        """Handle mouse release"""
        pass
    
    def on_mouse_drag(self, event):
        """Handle mouse drag"""
        pass