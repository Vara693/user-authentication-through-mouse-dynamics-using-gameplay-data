import tkinter as tk
import random
from games.base import BaseGame

class CookieCatcher(BaseGame):
    def __init__(self, parent_window, username: str, logger, on_game_complete: callable, session_id: int):
        super().__init__(parent_window, username, logger, on_game_complete, session_id)
        self.window.title("Cookie Catcher - Multiple Cookies")
        
        self.cookies_caught = 0
        self.cookies_missed = 0
        self.total_cookies = 15
        self.max_misses = 5
        self.basket_x = 400
        
        # Track all active cookies
        self.active_cookies = []
        self.cookie_spawn_timer = None
        
    def setup_game(self):
        """Setup with multiple cookies falling at once"""
        self.canvas.delete("all")
        
        # Create basket
        self.basket = self.canvas.create_rectangle(350, 550, 450, 570, fill='brown')
        
        # Instructions and stats
        self.canvas.create_text(400, 100, text=f"Catch {self.total_cookies} cookies to win!", font=('Arial', 16))
        self.canvas.create_text(400, 130, text="Move mouse to move basket", font=('Arial', 12))
        self.stats_text = self.canvas.create_text(400, 160, text=f"Caught: {self.cookies_caught}/{self.total_cookies} | Missed: {self.cookies_missed}/{self.max_misses}", font=('Arial', 12))
        
        # Clear any existing cookies
        self.active_cookies = []
        
        # Start spawning multiple cookies
        self.start_cookie_spawning()
    
    def start_cookie_spawning(self):
        """Start spawning cookies at regular intervals"""
        if self.cookies_caught < self.total_cookies and self.cookies_missed < self.max_misses and self.is_running:
            self.create_cookie()
            # Schedule next cookie spawn (every 1-2 seconds)
            self.cookie_spawn_timer = self.window.after(random.randint(1000, 2000), self.start_cookie_spawning)
    
    def create_cookie(self):
        """Create a new cookie and add it to active cookies"""
        if self.cookies_caught >= self.total_cookies or self.cookies_missed >= self.max_misses:
            return
            
        x = random.randint(50, 750)
        cookie_id = self.canvas.create_oval(x-15, 100, x+15, 130, fill='gold')
        
        # Add cookie to active list with its properties
        self.active_cookies.append({
            'id': cookie_id,
            'x': x,
            'y': 115,
            'speed': random.uniform(2, 5)  # Random speed for variety
        })
        
        # Start the falling process if not already running
        if len(self.active_cookies) == 1:  # Only start if this is the first cookie
            self.fall_cookies()
    
    def fall_cookies(self):
        """Make all active cookies fall"""
        if not self.is_running:
            return
            
        cookies_to_remove = []
        
        for cookie in self.active_cookies:
            # Move cookie down
            cookie['y'] += cookie['speed']
            self.canvas.coords(cookie['id'], 
                             cookie['x']-15, cookie['y']-15, 
                             cookie['x']+15, cookie['y']+15)
            
            # Check if cookie reached the bottom
            if cookie['y'] + 15 >= 550:
                if abs(cookie['x'] - self.basket_x) < 50:  # Caught!
                    self.cookies_caught += 1
                    self.canvas.delete(cookie['id'])
                    cookies_to_remove.append(cookie)
                    self.update_stats()
                    
                    # Check win condition
                    if self.cookies_caught >= self.total_cookies:
                        self.canvas.create_text(400, 300, text="You Win!", font=('Arial', 24), fill='green')
                        self.window.after(1500, self.stop_game)
                        return
                else:  # Missed
                    self.cookies_missed += 1
                    self.canvas.delete(cookie['id'])
                    cookies_to_remove.append(cookie)
                    self.update_stats()
                    
                    # Check lose condition
                    if self.cookies_missed >= self.max_misses:
                        self.canvas.create_text(400, 300, text="Too many misses! Restarting...", font=('Arial', 18), fill='red')
                        self.window.after(2000, self.restart_game)
                        return
        
        # Remove processed cookies
        for cookie in cookies_to_remove:
            if cookie in self.active_cookies:
                self.active_cookies.remove(cookie)
        
        # Continue falling if there are still active cookies or game is ongoing
        if (self.active_cookies or 
            (self.cookies_caught < self.total_cookies and self.cookies_missed < self.max_misses)):
            self.window.after(50, self.fall_cookies)
    
    def update_stats(self):
        """Update the statistics display"""
        self.canvas.itemconfig(self.stats_text, text=f"Caught: {self.cookies_caught}/{self.total_cookies} | Missed: {self.cookies_missed}/{self.max_misses}")
    
    def restart_game(self):
        """Restart the game after too many misses"""
        # Clear any pending timers
        if self.cookie_spawn_timer:
            self.window.after_cancel(self.cookie_spawn_timer)
        
        self.cookies_caught = 0
        self.cookies_missed = 0
        self.active_cookies = []
        self.setup_game()
    
    def stop_game(self):
        """Stop the game and clean up"""
        # Clear any pending timers
        if self.cookie_spawn_timer:
            self.window.after_cancel(self.cookie_spawn_timer)
        
        # Clear active cookies
        for cookie in self.active_cookies:
            self.canvas.delete(cookie['id'])
        self.active_cookies = []
        
        super().stop_game()
    
    def on_mouse_move(self, event):
        """Move basket with mouse"""
        self.basket_x = event.x
        self.canvas.coords(self.basket, self.basket_x-50, 550, self.basket_x+50, 570)
    
    def on_mouse_press(self, event):
        pass
    
    def on_mouse_release(self, event):
        pass
    
    def on_mouse_drag(self, event):
        self.on_mouse_move(event)