import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import pandas as pd
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from user_manager import UserManager
from game_runner import GameRunner
from logger import MouseLogger
from model.enhanced_testing import EnhancedTestingWindow

class MouseAuthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Dynamics Authentication System")
        self.root.geometry("700x500")
        
        self.user_manager = UserManager()
        self.logger = MouseLogger()
        self.current_user = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the main UI"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Mouse Dynamics Authentication", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Login Frame
        self.login_frame = ttk.LabelFrame(main_frame, text="Login", padding="10")
        self.login_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(self.login_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(self.login_frame, width=20)
        self.username_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(self.login_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*", width=20)
        self.password_entry.bind('<Return>', lambda e: self.login())
        self.password_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(self.login_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Login", command=self.login).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Register", command=self.register).grid(row=0, column=1, padx=5)
        
        # User info frame (hidden initially)
        self.user_frame = ttk.LabelFrame(main_frame, text="User Session", padding="10")
        self.user_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        self.user_frame.grid_remove()
        
        self.user_info_label = ttk.Label(self.user_frame, text="", justify=tk.LEFT)
        self.user_info_label.grid(row=0, column=0, columnspan=2, pady=5, sticky=tk.W)
        
        # Action buttons
        action_frame = ttk.Frame(self.user_frame)
        action_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(action_frame, text="Start Game Session", 
                  command=self.start_game_session).grid(row=0, column=0, padx=5)
        
        ttk.Button(action_frame, text="Test Authentication", 
                  command=self.open_testing_interface).grid(row=0, column=1, padx=5)
        
        ttk.Button(action_frame, text="View Model Results", 
                  command=self.open_results_viewer).grid(row=0, column=2, padx=5)
        
        # Admin buttons
        admin_frame = ttk.Frame(self.user_frame)
        admin_frame.grid(row=2, column=0, columnspan=2, pady=5)
        
        # FIXED: Changed from command-self_prompt_model_training to command=self._prompt_model_training
        ttk.Button(admin_frame, text="Train My Model", 
                  command=self._prompt_model_training).grid(row=0, column=0, padx=5)
        
        ttk.Button(admin_frame, text="Reset Progress", 
                  command=self.reset_progress).grid(row=0, column=1, padx=5)
        
        ttk.Button(admin_frame, text="Logout", 
                  command=self.logout).grid(row=0, column=2, padx=5)
    
    def _prompt_model_training(self):
        """Prompt user to train their model"""
        if not self.current_user:
            messagebox.showerror("Error", "Please login first")
            return
        
        progress = self.user_manager.get_user_progress(self.current_user)
        
        if progress['completed_sessions'] < 4:
            messagebox.showwarning(
                "Insufficient Data", 
                f"You need at least 4 sessions to train a model.\n\n"
                f"Current sessions: {progress['completed_sessions']}/4\n"
                f"Please complete more game sessions first."
            )
            return
        
        response = messagebox.askyesno(
            "Model Training", 
            f"""Train your authentication model now?

This will:
• Extract behavioral features from your mouse data
• Train machine learning models  
• Validate performance
• Generate accuracy reports

Training takes 1-2 minutes.

Continue?"""
        )
        
        if response:
            self._train_and_validate_model()
    
    def login(self):
        """Handle user login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        success, message = self.user_manager.authenticate_user(username, password)
        if success:
            self.current_user = username
            self._show_user_interface()
        else:
            messagebox.showerror("Error", message)
    
    def register(self):
        """Handle user registration"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        if len(password) < 4:
            messagebox.showerror("Error", "Password must be at least 4 characters long")
            return
        
        success, message = self.user_manager.register_user(username, password)
        if success:
            messagebox.showinfo("Success", message)
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", message)
    
    def _show_user_interface(self):
        """Show user interface after login"""
        self.login_frame.grid_remove()
        
        progress = self.user_manager.get_user_progress(self.current_user)
        
        if progress['phase'] == 'completed':
            user_info = f"""Welcome, {self.current_user}!
🎉 All 6 sessions completed! 🎉

Progress: {progress['progress_percentage']:.1f}%

You can now:
• Test authentication with Session 6
• View model performance results
• Use the authentication system"""
        else:
            phase_descriptions = {
                'training': 'Training Data Collection',
                'validation': 'Model Validation',
                'testing': 'System Testing'
            }
            
            user_info = f"""Welcome, {self.current_user}!

Sessions completed: {progress['completed_sessions']}/6
Current Phase: {phase_descriptions[progress['phase']]}
Next Session: {progress['current_session']}
Progress: {progress['progress_percentage']:.1f}%"""
        
        self.user_info_label.config(text=user_info)
        self.user_frame.grid()
        
        # Auto-prompt for training after 4 sessions
        if progress['completed_sessions'] == 4:
            self.root.after(1000, self._auto_prompt_training)
    
    def _auto_prompt_training(self):
        """Automatically prompt for training after 4 sessions"""
        response = messagebox.askyesno(
            "Model Training Available", 
            f"""You have completed 4 sessions! 

Would you like to train your authentication model now?

This will:
• Extract behavioral features from your mouse data
• Train machine learning models
• Validate performance using Session 5
• Generate accuracy reports

Training takes 1-2 minutes."""
        )
        
        if response:
            self._train_and_validate_model()
    
    def _train_and_validate_model(self):
        """Train model and validate with session 5"""
        try:
            from model.train_model import ModelTrainer
            
            # Show progress window
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Training in Progress")
            progress_window.geometry("300x150")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            progress_label = ttk.Label(progress_window, text="Training model...", font=('Arial', 12))
            progress_label.pack(pady=20)
            
            progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
            progress_bar.pack(pady=10, padx=20, fill=tk.X)
            progress_bar.start()
            
            def train_model():
                try:
                    trainer = ModelTrainer()
                    results = trainer.train_models(self.current_user)
                    
                    # Generate visualizations
                    trainer.generate_feature_visualizations()
                    
                    self.root.after(0, lambda: self._show_training_results(progress_window, results))
                    
                except Exception as e:
                    # FIX: Capture the exception in the lambda to avoid scope issues
                    error_msg = str(e)
                    self.root.after(0, lambda: self._show_training_error(progress_window, error_msg))
            
            import threading
            thread = threading.Thread(target=train_model)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Training Error", f"Could not start training: {str(e)}")
            
    
    def _show_training_results(self, progress_window, results):
        """Show training results"""
        progress_window.destroy()
        
        # Extract accuracy from results
        best_score = results.get('best_score', 0)
        accuracy = results.get('all_results', {}).get('random_forest', {}).get('test_accuracy', 0)
        
        messagebox.showinfo(
            "Training Complete", 
            f"""🎉 Model Training Complete!

Validation Accuracy: {accuracy:.2%}
Best AUC Score: {best_score:.3f}

Your model is now ready for testing with Session 6.

Check the 'results' folder for detailed reports and visualizations."""
        )
        
        # Refresh UI
        self._show_user_interface()
    
    def _show_training_error(self, progress_window, error_msg):
        """Show training error"""
        progress_window.destroy()
        messagebox.showerror("Training Error", f"Training failed:\n{error_msg}")
    
    def start_game_session(self):
        """Start a game session"""
        if not self.current_user:
            return
        
        # Get current session from user manager
        session_id = self.user_manager.get_current_session(self.current_user)
        
        # Check if user has completed all sessions
        if session_id > 6:
            messagebox.showinfo("Completed", "You have completed all 6 sessions! No more sessions available.")
            return
        
        # Start logging
        self.logger.start_logging(self.current_user, session_id)
        
        # Start game session
        self.game_runner = GameRunner(
            self.root, 
            self.current_user, 
            self.logger,
            self._on_session_complete,
            session_id
        )
        self.game_runner.start_session()
    
    def _on_session_complete(self):
        """Called when game session completes"""
        # Stop logging
        self.logger.stop_logging()
        
        # Update session count
        new_count = self.user_manager.increment_user_session(self.current_user)
        
        # Update UI
        self._show_user_interface()
        
        # Auto-prompt for testing after 6 sessions
        if new_count == 6:
            self.root.after(1000, self._auto_prompt_testing)
    
    def _auto_prompt_testing(self):
        """Automatically prompt for testing after 6 sessions"""
        response = messagebox.askyesno(
            "Testing Available", 
            f"""You have completed all 6 sessions! 

Would you like to test your authentication model now?

This will:
• Use your trained model to analyze Session 6
• Show authentication accuracy
• Display confidence scores
• Generate performance reports"""
        )
        
        if response:
            self.open_testing_interface()
    
    def open_testing_interface(self):
        """Open the enhanced testing interface"""
        if not self.current_user:
            messagebox.showerror("Error", "Please login first")
            return
        
        EnhancedTestingWindow(self.root)
    
    def open_results_viewer(self):
        """Open the results viewer"""
        if not self.current_user:
            messagebox.showerror("Error", "Please login first")
            return
        
        ResultsViewer(self.root, self.current_user)
    
    def reset_progress(self):
        """Reset user progress for testing purposes"""
        if self.current_user and messagebox.askyesno("Reset Progress", 
                                                   "Are you sure you want to reset your session progress?\nThis will clear all your completed sessions."):
            if self.user_manager.reset_user_sessions(self.current_user):
                messagebox.showinfo("Reset Complete", "Your progress has been reset.")
                self._show_user_interface()
    
    def logout(self):
        """Handle user logout"""
        self.current_user = None
        self.user_frame.grid_remove()
        self.login_frame.grid()
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

class TestingWindow(tk.Toplevel):
    """Window for testing authentication with Session 6"""
    
    def __init__(self, parent, username):
        super().__init__(parent)
        self.username = username
        self.title(f"Authentication Testing - {username}")
        self.geometry("600x400")
        self.transient(parent)
        self.grab_set()
        
        self.auth_system = None
        self.test_results = None
        
        self._setup_ui()
        
        # Auto-load model
        self._load_model()
    
    def _setup_ui(self):
        """Setup testing interface"""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Authentication Testing", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Model status
        self.status_frame = ttk.LabelFrame(main_frame, text="Model Status", padding="10")
        self.status_frame.pack(fill=tk.X, pady=10)
        
        self.status_label = ttk.Label(self.status_frame, text="Loading model...")
        self.status_label.pack()
        
        # Test controls
        controls_frame = ttk.LabelFrame(main_frame, text="Test Controls", padding="10")
        controls_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(controls_frame, text="Test with Session 6", 
                  command=self._test_with_session6).pack(pady=5)
        
        ttk.Button(controls_frame, text="Run Comprehensive Test", 
                  command=self._run_comprehensive_test).pack(pady=5)
        
        # Results area
        self.results_frame = ttk.LabelFrame(main_frame, text="Test Results", padding="10")
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.results_text = tk.Text(self.results_frame, height=10, width=60)
        scrollbar = ttk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=self.destroy).pack(pady=10)
    
    def _load_model(self):
        """Load the user's model"""
        try:
            from model.predict import EnhancedAuthenticationSystem
            self.auth_system = EnhancedAuthenticationSystem()
            
            if self.auth_system.load_user_model(self.username):
                self.status_label.config(text="✅ Model loaded successfully")
            else:
                self.status_label.config(text="❌ No trained model found. Please train first.")
        except Exception as e:
            self.status_label.config(text=f"❌ Error loading model: {str(e)}")
    
    def _test_with_session6(self):
        """Test authentication with Session 6"""
        if not self.auth_system:
            messagebox.showerror("Error", "Model not loaded")
            return
        
        session6_path = f"data/{self.username}/session_6.csv"
        if not os.path.exists(session6_path):
            messagebox.showerror("Error", "Session 6 data not found")
            return
        
        try:
            session_data = pd.read_csv(session6_path)
            result = self.auth_system.authenticate_session(self.username, session_data)
            
            self._display_result("Session 6 Test Result", result)
            
            # Store for reporting
            self.test_results = {
                'test_type': 'session6',
                'result': result,
                'correct': result['authenticated']  # Should be True for genuine user
            }
            
        except Exception as e:
            messagebox.showerror("Error", f"Testing failed: {str(e)}")
    
    def _run_comprehensive_test(self):
        """Run comprehensive cross-user testing"""
        try:
            from model_evaluator import ModelEvaluator
            evaluator = ModelEvaluator()
            results = evaluator.comprehensive_test()
            
            # Display summary
            summary = evaluator.generate_summary_report(results)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, summary)
            
            # Store for reporting
            self.test_results = {
                'test_type': 'comprehensive',
                'results': results
            }
            
        except Exception as e:
            messagebox.showerror("Error", f"Comprehensive test failed: {str(e)}")
    
    def _display_result(self, title, result):
        """Display authentication result"""
        self.results_text.delete(1.0, tk.END)
        
        output = f"{title}\n"
        output += "=" * 50 + "\n\n"
        output += f"Authenticated: {'✅ YES' if result['authenticated'] else '❌ NO'}\n"
        output += f"Confidence: {result['confidence']:.2%}\n"
        output += f"Reason: {result['reason']}\n"
        output += f"Features Extracted: {result.get('features_extracted', 'N/A')}\n"
        
        if result['authenticated']:
            output += "\n🎉 SUCCESS: User correctly authenticated!\n"
        else:
            output += "\n🚫 FAILED: User authentication failed!\n"
        
        self.results_text.insert(tk.END, output)

class ResultsViewer(tk.Toplevel):
    """Window for viewing model results and graphs"""
            
    def __init__(self, parent, username):
        super().__init__(parent)
        self.username = username
        self.title(f"Model Results - {username}")
        self.geometry("800x600")
        self.transient(parent)
        
        self._setup_ui()
        self._load_results()
    
    def _setup_ui(self):
        """Setup results viewer interface"""
        # Notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Summary tab
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="Summary")
        
        # Plots tab
        self.plots_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.plots_frame, text="Visualizations")
        
        # Setup summary tab
        self._setup_summary_tab()
    
    def _setup_summary_tab(self):
        """Setup summary tab content"""
        # Summary text
        self.summary_text = tk.Text(self.summary_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(self.summary_frame, orient=tk.VERTICAL, command=self.summary_text.yview)
        self.summary_text.configure(yscrollcommand=scrollbar.set)
        
        self.summary_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
    
    def _load_results(self):
        """Load and display results"""
        try:
            # Load training logs
            log_file = "results/training_logs.json"
            if os.path.exists(log_file):
                import json
                with open(log_file, 'r') as f:
                    logs = json.load(f)
                
                user_logs = [log for log in logs if log.get('username') == self.username]
                if user_logs:
                    self._display_training_logs(user_logs)
            
            # Load results files
            self._load_result_files()
            
        except Exception as e:
            self.summary_text.insert(tk.END, f"Error loading results: {str(e)}")
    
    def _display_training_logs(self, logs):
        """Display training logs in summary"""
        self.summary_text.insert(tk.END, "📊 TRAINING HISTORY\n")
        self.summary_text.insert(tk.END, "=" * 50 + "\n\n")
        
        for log in logs:
            self.summary_text.insert(tk.END, f"Model: {log.get('model', 'N/A')}\n")
            self.summary_text.insert(tk.END, f"Accuracy: {log.get('accuracy', 0):.2%}\n")
            self.summary_text.insert(tk.END, f"AUC: {log.get('auc', 0):.3f}\n")
            self.summary_text.insert(tk.END, f"CV Score: {log.get('cv_mean', 0):.3f} ± {log.get('cv_std', 0):.3f}\n")
            self.summary_text.insert(tk.END, f"Timestamp: {log.get('timestamp', 'N/A')}\n")
            self.summary_text.insert(tk.END, "-" * 30 + "\n\n")
    
    def _load_result_files(self):
        """Load and display result files"""
        results_dir = "results/tables"
        if os.path.exists(results_dir):
            result_files = [f for f in os.listdir(results_dir) if self.username in f]
            
            for file in result_files:
                file_path = os.path.join(results_dir, file)
                try:
                    df = pd.read_csv(file_path)
                    self.summary_text.insert(tk.END, f"\n📁 {file}\n")
                    self.summary_text.insert(tk.END, "=" * 30 + "\n")
                    self.summary_text.insert(tk.END, df.to_string() + "\n\n")
                except Exception as e:
                    self.summary_text.insert(tk.END, f"Error reading {file}: {str(e)}\n")

def main():
    root = tk.Tk()
    app = MouseAuthApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()