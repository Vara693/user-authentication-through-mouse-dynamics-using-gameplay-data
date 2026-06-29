import tkinter as tk
import random
from games.base import BaseGame

class DragDrop(BaseGame):
    def __init__(self, parent_window, username: str, logger, on_game_complete: callable, session_id: int):
        super().__init__(parent_window, username, logger, on_game_complete, session_id)
        self.window.title("Drag & Drop - Drag items to matching zones!")
        
        self.draggable_items = []
        self.drop_zones = []
        self.dragged_item = None
        self.items_placed = 0
        self.total_items = 5
        
        # Colors for matching
        self.colors = ['red', 'blue', 'green', 'yellow', 'purple']
    
    def setup_game(self):
        """Set up drag and drop game"""
        self.canvas.delete("all")
        self.draggable_items = []
        self.drop_zones = []
        self.items_placed = 0
        
        # Create drop zones
        zone_width = 100
        zone_height = 80
        margin = 50
        
        for i, color in enumerate(self.colors):
            x = margin + i * (zone_width + margin)
            y = 500
            zone = self.canvas.create_rectangle(
                x, y, x + zone_width, y + zone_height,
                fill=color, tags="drop_zone", outline='black', width=2
            )
            self.drop_zones.append((zone, color))
        
        # Create draggable items
        for i, color in enumerate(self.colors):
            x = random.randint(50, 700)
            y = random.randint(100, 400)
            radius = 25
            
            item = self.canvas.create_oval(
                x-radius, y-radius, x+radius, y+radius,
                fill=color, tags="draggable", outline='black', width=2
            )
            self.draggable_items.append((item, color))
        
        # Game info
        self.info_text = self.canvas.create_text(
            400, 30, 
            text=f"Items placed: {self.items_placed}/{self.total_items}",
            font=('Arial', 14)
        )
    
    def on_mouse_press(self, event):
        """Handle mouse press on draggable items"""
        clicked_items = self.canvas.find_overlapping(event.x-5, event.y-5, event.x+5, event.y+5)
        
        for item in clicked_items:
            for draggable, color in self.draggable_items:
                if item == draggable:
                    self.dragged_item = (draggable, color)
                    break
    
    def on_mouse_release(self, event):
        """Handle mouse release - check if item is in correct zone"""
        if not self.dragged_item:
            return
        
        item, item_color = self.dragged_item
        
        # Check if item is over any drop zone
        item_coords = self.canvas.coords(item)
        item_center_x = (item_coords[0] + item_coords[2]) / 2
        item_center_y = (item_coords[1] + item_coords[3]) / 2
        
        for zone, zone_color in self.drop_zones:
            zone_coords = self.canvas.coords(zone)
            
            if (zone_coords[0] <= item_center_x <= zone_coords[2] and 
                zone_coords[1] <= item_center_y <= zone_coords[3]):
                
                # Check if colors match
                if item_color == zone_color:
                    # Correct placement!
                    self.items_placed += 1
                    
                    # Remove the placed item
                    self.canvas.delete(item)
                    self.draggable_items = [(i, c) for i, c in self.draggable_items if i != item]
                    
                    # Update display
                    self.canvas.itemconfig(self.info_text, 
                                         text=f"Items placed: {self.items_placed}/{self.total_items}")
                    
                    # Check if game is complete
                    if self.items_placed >= self.total_items:
                        self.canvas.create_text(
                            400, 300, 
                            text="All items placed!", 
                            font=('Arial', 24, 'bold'),
                            fill='green'
                        )
                        self.window.after(1500, self.stop_game)
                
                break
        
        self.dragged_item = None
    
    def on_mouse_drag(self, event):
        """Handle mouse drag - move the dragged item"""
        if self.dragged_item:
            item, color = self.dragged_item
            # Move item to current mouse position
            self.canvas.coords(item, event.x-25, event.y-25, event.x+25, event.y+25)
    
    def on_mouse_move(self, event):
        """Handle mouse movement"""
        pass