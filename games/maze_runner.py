import tkinter as tk
import random
from games.base import BaseGame

class MazeRunner(BaseGame):
    def __init__(self, parent_window, username: str, logger, on_game_complete: callable, session_id: int):
        super().__init__(parent_window, username, logger, on_game_complete, session_id)
        self.window.title("Maze Runner - Navigate to the exit! (Wall = Restart)")
        
        self.maze = []
        self.player = None
        self.exit = None
        self.player_size = 20
        self.cell_size = 40
        self.wall_hits = 0
        self.session_mazes = self._get_session_mazes()
    
    def _get_session_mazes(self):
        """Return 6 different maze designs for each session"""
        return {
            1: [  # Session 1: Simple maze - basic introduction
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,1,1,1,1,1,1,1,1,1,1,1,0,1],
                [1,0,1,0,0,0,0,0,0,0,0,0,1,0,1],
                [1,0,1,0,1,1,1,1,1,1,1,0,1,0,1],
                [1,0,1,0,1,0,0,0,0,0,1,0,1,0,1],
                [1,0,1,0,1,0,1,1,1,0,1,0,1,0,1],
                [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1],
                [1,0,1,0,1,0,1,1,1,0,1,0,1,0,1],
                [1,0,1,0,1,0,0,0,0,0,1,0,1,0,1],
                [1,0,1,0,1,1,1,1,1,1,1,0,1,0,1],
                [1,0,1,0,0,0,0,0,0,0,0,0,1,0,1],
                [1,0,1,1,1,1,1,1,1,1,1,1,1,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
            ],
            2: [  # Session 2: Spiral maze - forces circular movement
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,1,1,1,1,1,1,1,1,1,1,1,0,1],
                [1,0,1,0,0,0,0,0,0,0,0,0,1,0,1],
                [1,0,1,0,1,1,1,1,1,1,1,0,1,0,1],
                [1,0,1,0,1,0,0,0,0,0,1,0,1,0,1],
                [1,0,1,0,1,0,1,1,1,0,1,0,1,0,1],
                [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1],
                [1,0,1,0,1,0,1,1,1,0,1,0,1,0,1],
                [1,0,1,0,1,0,0,0,0,0,1,0,1,0,1],
                [1,0,1,0,1,1,1,1,1,1,1,0,1,0,1],
                [1,0,1,0,0,0,0,0,0,0,0,0,1,0,1],
                [1,0,1,1,1,1,1,1,1,1,1,1,1,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
            ],
            3: [  # Session 3: Complex corridors - multiple dead ends
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                [1,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
                [1,0,1,0,1,0,1,1,1,0,1,0,1,0,1],
                [1,0,1,0,0,0,1,0,0,0,1,0,1,0,1],
                [1,0,1,1,1,1,1,0,1,1,1,0,1,0,1],
                [1,0,0,0,0,0,0,0,1,0,0,0,1,0,1],
                [1,1,1,1,1,0,1,1,1,0,1,1,1,0,1],
                [1,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
                [1,0,1,0,1,1,1,1,1,0,1,0,1,1,1],
                [1,0,1,0,0,0,0,0,1,0,0,0,0,0,1],
                [1,0,1,1,1,1,1,0,1,1,1,1,1,0,1],
                [1,0,0,0,0,0,1,0,0,0,0,0,1,0,1],
                [1,1,1,1,1,0,1,1,1,1,1,0,1,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
            ],
            4: [  # Session 4: Zigzag pattern - requires frequent direction changes
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,1,1,1,1,0,1,1,1,1,1,0,1,1,1],
                [1,0,0,0,0,0,1,0,0,0,0,0,0,0,1],
                [1,0,1,1,1,1,1,0,1,1,1,1,1,0,1],
                [1,0,0,0,0,0,0,0,1,0,0,0,0,0,1],
                [1,1,1,1,1,0,1,1,1,0,1,1,1,1,1],
                [1,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
                [1,0,1,0,1,0,1,1,1,1,1,0,1,0,1],
                [1,0,1,0,0,0,0,0,0,0,0,0,1,0,1],
                [1,0,1,1,1,1,1,0,1,1,1,1,1,0,1],
                [1,0,0,0,0,0,1,0,1,0,0,0,0,0,1],
                [1,1,1,1,1,0,1,0,1,0,1,1,1,1,1],
                [1,0,0,0,0,0,1,0,0,0,0,0,0,0,1],
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
            ],
            5: [  # Session 5: Advanced puzzle - multiple paths, one correct
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                [1,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
                [1,0,1,0,1,0,1,1,1,0,1,0,1,0,1],
                [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1],
                [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1],
                [1,0,1,0,0,0,1,0,0,0,1,0,1,0,1],
                [1,0,1,1,1,1,1,1,1,1,1,0,1,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
                [1,0,1,1,1,1,1,1,1,1,1,1,1,0,1],
                [1,0,1,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,1,0,1,1,1,1,1,1,1,1,1,1,1],
                [1,0,1,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,1,1,1,1,1,1,1,1,1,1,1,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
            ],
            6: [  # Session 6: Expert level - maximum complexity
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                [1,0,0,0,0,0,1,0,0,0,0,0,0,0,1],
                [1,0,1,1,1,0,1,0,1,1,1,1,1,0,1],
                [1,0,1,0,0,0,1,0,0,0,0,0,1,0,1],
                [1,0,1,0,1,1,1,1,1,1,1,0,1,0,1],
                [1,0,1,0,0,0,0,0,0,0,1,0,1,0,1],
                [1,0,1,1,1,1,1,0,1,0,1,0,1,0,1],
                [1,0,0,0,0,0,1,0,1,0,1,0,1,0,1],
                [1,1,1,1,1,0,1,0,1,0,1,0,1,0,1],
                [1,0,0,0,1,0,1,0,1,0,1,0,1,0,1],
                [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1],
                [1,0,1,0,1,0,0,0,1,0,0,0,1,0,1],
                [1,0,1,0,1,1,1,1,1,1,1,1,1,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
            ]
        }
    
    def setup_game(self):
        """Set up the maze game based on session number"""
        self.canvas.delete("all")
        self.wall_hits = 0
        
        # Use the provided session_id to select maze
        session_num = self.session_id
        
        # Use session-specific maze
        if session_num in self.session_mazes:
            self.maze = self.session_mazes[session_num]
        else:
            self.maze = self.session_mazes[1]  # Default to session 1
        
        self.draw_maze()
        self.create_player()
        self.create_exit()
        
        # Game info
        self.info_text = self.canvas.create_text(
            400, 30, 
            text=f"Session {session_num} | Wall hits: {self.wall_hits}",
            font=('Arial', 14)
        )
    
    def draw_maze(self):
        """Draw the maze on canvas"""
        for row in range(len(self.maze)):
            for col in range(len(self.maze[0])):
                x1 = col * self.cell_size
                y1 = row * self.cell_size + 50  # Offset for info text
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                if self.maze[row][col] == 1:  # Wall
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='black')
                else:  # Path
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='lightgray')
    
    def create_player(self):
        """Create player at start position (always top-left path)"""
        # Find start position (first path cell in second row)
        start_row, start_col = 1, 1
        
        self.player_x = start_col * self.cell_size + self.cell_size // 2
        self.player_y = start_row * self.cell_size + self.cell_size // 2 + 50
        
        self.player = self.canvas.create_oval(
            self.player_x - self.player_size//2,
            self.player_y - self.player_size//2,
            self.player_x + self.player_size//2,
            self.player_y + self.player_size//2,
            fill='blue', tags="player"
        )
    
    def create_exit(self):
        """Create exit at end position (always bottom-right path)"""
        exit_row = len(self.maze) - 2
        exit_col = len(self.maze[0]) - 2
        
        x1 = exit_col * self.cell_size + 5
        y1 = exit_row * self.cell_size + 5 + 50
        x2 = x1 + self.cell_size - 10
        y2 = y1 + self.cell_size - 10
        
        self.exit = self.canvas.create_rectangle(x1, y1, x2, y2, fill='green', tags="exit")
    
    def move_player(self, dx, dy):
        """Move player if the move is valid"""
        new_x = self.player_x + dx
        new_y = self.player_y + dy
        
        # Check if new position is valid (not a wall)
        col = int(new_x // self.cell_size)
        row = int((new_y - 50) // self.cell_size)  # Adjust for offset
        
        if (0 <= row < len(self.maze) and 0 <= col < len(self.maze[0])):
            if self.maze[row][col] == 0:  # Valid move
                self.player_x = new_x
                self.player_y = new_y
                
                self.canvas.coords(
                    self.player,
                    self.player_x - self.player_size//2,
                    self.player_y - self.player_size//2,
                    self.player_x + self.player_size//2,
                    self.player_y + self.player_size//2
                )
                
                # Check if player reached exit
                player_coords = self.canvas.coords(self.player)
                exit_coords = self.canvas.coords(self.exit)
                
                if (player_coords[0] < exit_coords[2] and player_coords[2] > exit_coords[0] and
                    player_coords[1] < exit_coords[3] and player_coords[3] > exit_coords[1]):
                    self.canvas.create_text(
                        400, 300, 
                        text=f"Maze Completed!\nWall hits: {self.wall_hits}", 
                        font=('Arial', 24, 'bold'),
                        fill='green',
                        justify=tk.CENTER
                    )
                    self.window.after(2000, self.stop_game)
            else:
                # Hit a wall - restart!
                self.wall_hits += 1
                self.canvas.itemconfig(self.info_text, 
                                    text=f"Session {self.session_id} | Wall hits: {self.wall_hits}")
                
                # Visual feedback
                self.canvas.create_text(
                    self.player_x, self.player_y - 30,
                    text="WALL HIT!",
                    font=('Arial', 12, 'bold'),
                    fill='red'
                )
                
                # Restart player position
                self.restart_player()
    
    def restart_player(self):
        """Restart player at beginning"""
        start_row, start_col = 1, 1
        self.player_x = start_col * self.cell_size + self.cell_size // 2
        self.player_y = start_row * self.cell_size + self.cell_size // 2 + 50
        
        self.canvas.coords(
            self.player,
            self.player_x - self.player_size//2,
            self.player_y - self.player_size//2,
            self.player_x + self.player_size//2,
            self.player_y + self.player_size//2
        )
    
    def on_mouse_move(self, event):
        """Handle mouse movement"""
        pass
    
    def on_mouse_press(self, event):
        """Handle mouse press"""
        pass
    
    def on_mouse_release(self, event):
        """Handle mouse release"""
        pass
    
    def on_mouse_drag(self, event):
        """Handle mouse drag - use drag to control player movement"""
        if self.is_running:
            dx = (event.x - self.player_x) * 0.2
            dy = (event.y - self.player_y) * 0.2
            
            # Limit maximum movement per frame
            max_speed = 8
            dx = max(min(dx, max_speed), -max_speed)
            dy = max(min(dy, max_speed), -max_speed)
            
            self.move_player(dx, dy)