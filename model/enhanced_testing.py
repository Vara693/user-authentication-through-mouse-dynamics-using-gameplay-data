import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
import os
from model.multi_class_trainer import MultiClassTrainer

class EnhancedTestingWindow(tk.Toplevel):
    """Enhanced testing window for user identification"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("User Identification Testing")
        self.geometry("800x600")
        self.transient(parent)
        self.grab_set()
        
        self.trainer = MultiClassTrainer()
        self.model_loaded = False
        
        self._setup_ui()
        self._try_load_model()
    
    def _setup_ui(self):
        """Setup the enhanced testing interface"""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🧠 User Identification System", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Model Status
        status_frame = ttk.LabelFrame(main_frame, text="Model Status", padding="10")
        status_frame.pack(fill=tk.X, pady=10)
        
        self.status_label = ttk.Label(status_frame, text="Checking for trained model...")
        self.status_label.pack()
        
        # User Selection
        user_frame = ttk.LabelFrame(main_frame, text="Test Configuration", padding="10")
        user_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(user_frame, text="Select User to Test:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.user_var = tk.StringVar()
        self.user_combo = ttk.Combobox(user_frame, textvariable=self.user_var, state="readonly")
        self.user_combo.grid(row=0, column=1, pady=5, padx=5, sticky=tk.EW)
        
        ttk.Label(user_frame, text="Session:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=5)
        
        self.session_var = tk.StringVar()
        session_combo = ttk.Combobox(user_frame, textvariable=self.session_var, 
                                   values=["1", "2", "3", "4", "5", "6"], state="readonly")
        session_combo.grid(row=0, column=3, pady=5, padx=5)
        session_combo.set("6")  # Default to session 6
        
        # Test Controls
        controls_frame = ttk.LabelFrame(main_frame, text="Test Actions", padding="10")
        controls_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(controls_frame, text="Identify User", 
                  command=self.identify_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Test All Users", 
                  command=self.test_all_users).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Train New Model", 
                  command=self.train_model).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Load Model", 
                  command=self.load_model).pack(side=tk.LEFT, padx=5)
        
        # Results Area
        results_frame = ttk.LabelFrame(main_frame, text="Identification Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create text widget with scrollbar
        self.results_text = tk.Text(results_frame, height=15, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=self.destroy).pack(pady=10)
    
    def _try_load_model(self):
        """Try to load model on startup"""
        try:
            if self.trainer.load_model():
                self.model_loaded = True
                self.status_label.config(text="✅ Multi-class model loaded successfully!")
                self._update_user_list()
            else:
                self.status_label.config(text="❌ No trained model found. Please train first.")
        except Exception as e:
            self.status_label.config(text=f"❌ Error loading model: {str(e)}")
    
    def _update_user_list(self):
        """Update the user dropdown list"""
        try:
            users_dir = "data"
            if os.path.exists(users_dir):
                users = [d for d in os.listdir(users_dir) if os.path.isdir(os.path.join(users_dir, d))]
                self.user_combo['values'] = users
                if users:
                    self.user_var.set(users[0])
        except Exception as e:
            print(f"Error updating user list: {e}")
    
    def load_model(self):
        """Load model manually"""
        try:
            if self.trainer.load_model():
                self.model_loaded = True
                self.status_label.config(text="✅ Model loaded successfully!")
                self._update_user_list()
                messagebox.showinfo("Success", "Model loaded successfully!")
            else:
                messagebox.showerror("Error", "No trained model found!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model: {str(e)}")
    
    def train_model(self):
        """Train a new multi-class model"""
        try:
            self.status_label.config(text="🔄 Training model... This may take a few minutes.")
            self.update()
            
            accuracy = self.trainer.train_model()
            self.trainer.save_model()
            
            self.model_loaded = True
            self.status_label.config(text="✅ Model trained and saved successfully!")
            self._update_user_list()
            
            messagebox.showinfo("Training Complete", 
                              f"Model trained successfully!\n\nAccuracy: {accuracy:.2%}\n\nCheck 'results' folder for detailed reports and visualizations.")
            
        except Exception as e:
            messagebox.showerror("Training Error", f"Model training failed:\n{str(e)}")
            self.status_label.config(text="❌ Training failed")
    
    def identify_user(self):
        """Identify user from session data"""
        if not self.model_loaded:
            messagebox.showerror("Error", "No model loaded! Please train or load a model first.")
            return
        
        user = self.user_var.get()
        session = self.session_var.get()
        
        if not user:
            messagebox.showerror("Error", "Please select a user!")
            return
        
        session_path = f"data/{user}/session_{session}.csv"
        if not os.path.exists(session_path):
            messagebox.showerror("Error", f"Session {session} data not found for {user}!")
            return
        
        try:
            # Load session data
            session_data = pd.read_csv(session_path)
            
            # Extract features
            features_df = self.trainer.extractor.extract_session_features(session_data)
            
            if features_df.empty:
                messagebox.showerror("Error", "No features could be extracted from this session!")
                return
            
            # Predict
            X = features_df.values
            probabilities = self.trainer.model.predict_proba(X)[0]
            predicted_class_idx = np.argmax(probabilities)
            predicted_user = self.trainer.label_encoder.inverse_transform([predicted_class_idx])[0]
            confidence = probabilities[predicted_class_idx]
            
            # Get top 3 predictions
            top_3_indices = np.argsort(probabilities)[-3:][::-1]
            top_predictions = []
            for idx in top_3_indices:
                user_name = self.trainer.label_encoder.inverse_transform([idx])[0]
                user_prob = probabilities[idx]
                top_predictions.append((user_name, user_prob))
            
            # Display results
            self._display_results(user, predicted_user, confidence, top_predictions, session)
            
        except Exception as e:
            messagebox.showerror("Error", f"Identification failed: {str(e)}")
    
    def test_all_users(self):
        """Test model on all users and sessions"""
        if not self.model_loaded:
            messagebox.showerror("Error", "No model loaded! Please train or load a model first.")
            return
        
        try:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "🧪 Running comprehensive tests...\n\n")
            self.update()
            
            users_dir = "data"
            users = [d for d in os.listdir(users_dir) if os.path.isdir(os.path.join(users_dir, d))]
            
            total_tests = 0
            correct_predictions = 0
            
            for user in users:
                self.results_text.insert(tk.END, f"👤 Testing user: {user}\n")
                self.results_text.insert(tk.END, "-" * 40 + "\n")
                
                for session in range(1, 7):
                    session_path = f"data/{user}/session_{session}.csv"
                    if os.path.exists(session_path):
                        try:
                            session_data = pd.read_csv(session_path)
                            features_df = self.trainer.extractor.extract_session_features(session_data)
                            
                            if not features_df.empty:
                                X = features_df.values
                                probabilities = self.trainer.model.predict_proba(X)[0]
                                predicted_class_idx = np.argmax(probabilities)
                                predicted_user = self.trainer.label_encoder.inverse_transform([predicted_class_idx])[0]
                                confidence = probabilities[predicted_class_idx]
                                
                                is_correct = (predicted_user == user)
                                status = "✅" if is_correct else "❌"
                                
                                self.results_text.insert(tk.END, 
                                    f"Session {session}: {status} Predicted: {predicted_user} "
                                    f"(Confidence: {confidence:.2%})\n")
                                
                                total_tests += 1
                                if is_correct:
                                    correct_predictions += 1
                            else:
                                self.results_text.insert(tk.END, f"Session {session}: ❌ No features extracted\n")
                        except Exception as e:
                            self.results_text.insert(tk.END, f"Session {session}: ❌ Error: {str(e)}\n")
                
                self.results_text.insert(tk.END, "\n")
            
            # Summary
            accuracy = correct_predictions / total_tests if total_tests > 0 else 0
            self.results_text.insert(tk.END, "=" * 50 + "\n")
            self.results_text.insert(tk.END, f"📊 SUMMARY\n")
            self.results_text.insert(tk.END, f"Total Tests: {total_tests}\n")
            self.results_text.insert(tk.END, f"Correct Predictions: {correct_predictions}\n")
            self.results_text.insert(tk.END, f"Overall Accuracy: {accuracy:.2%}\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Comprehensive testing failed: {str(e)}")
    
    def _display_results(self, true_user, predicted_user, confidence, top_predictions, session):
        """Display identification results"""
        is_correct = (predicted_user == true_user)
        
        self.results_text.delete(1.0, tk.END)
        
        self.results_text.insert(tk.END, "🔍 USER IDENTIFICATION RESULTS\n")
        self.results_text.insert(tk.END, "=" * 50 + "\n\n")
        
        self.results_text.insert(tk.END, f"True User: {true_user}\n")
        self.results_text.insert(tk.END, f"Session Tested: {session}\n\n")
        
        self.results_text.insert(tk.END, f"🧠 Model Prediction:\n")
        self.results_text.insert(tk.END, f"  👤 Identified as: {predicted_user}\n")
        self.results_text.insert(tk.END, f"  📊 Confidence: {confidence:.2%}\n")
        self.results_text.insert(tk.END, f"  ✅ Status: {'CORRECT' if is_correct else 'INCORRECT'}\n\n")
        
        self.results_text.insert(tk.END, "🏆 Top 3 Predictions:\n")
        for i, (user, prob) in enumerate(top_predictions, 1):
            self.results_text.insert(tk.END, f"  {i}. {user}: {prob:.2%}\n")
        
        # Color coding
        if is_correct:
            self.results_text.tag_configure("correct", foreground="green", font=('Arial', 10, 'bold'))
            self.results_text.insert(tk.END, "\n🎉 SUCCESS: User correctly identified!\n", "correct")
        else:
            self.results_text.tag_configure("incorrect", foreground="red", font=('Arial', 10, 'bold'))
            self.results_text.insert(tk.END, "\n❌ FAILED: Wrong user identified!\n", "incorrect")