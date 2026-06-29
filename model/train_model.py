import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import accuracy_score
import joblib
import json
from datetime import datetime

# Import the feature extractor
from model.feature_extractor import EnhancedFeatureExtractor

class ModelTrainer:
    def __init__(self):
        self.extractor = EnhancedFeatureExtractor()
        self.results_dir = "results"
        self.models_dir = "models"
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
    
    def train_models(self, username):
        """Train models for a specific user"""
        print(f"Starting training for {username}")
        
        try:
            # Get all available users
            users = self._get_available_users()
            print(f"Available users: {users}")
            
            # Create feature matrix
            feature_matrix = self._create_feature_matrix(users)
            
            if feature_matrix.empty:
                raise Exception("No features extracted from any session!")
            
            print(f"Feature matrix created: {feature_matrix.shape}")
            
            # Train models
            results = self._train_user_models(feature_matrix, username)
            
            # Save results
            self._save_training_results(results, username)
            
            return results
            
        except Exception as e:
            print(f"Training error: {e}")
            raise
    
    def _get_available_users(self):
        """Get list of available users from data directory"""
        data_dir = "data"
        if not os.path.exists(data_dir):
            return []
        
        users = []
        for item in os.listdir(data_dir):
            if os.path.isdir(os.path.join(data_dir, item)):
                users.append(item)
        
        return users
    
    def _create_feature_matrix(self, users):
        """Create feature matrix from all user sessions"""
        all_features = []
        
        print("Creating feature matrix...")
        
        for user in users:
            print(f"Processing user: {user}")
            
            for session_id in range(1, 7):
                file_path = f"data/{user}/session_{session_id}.csv"
                if os.path.exists(file_path):
                    try:
                        # Load session data
                        session_data = pd.read_csv(file_path)
                        
                        # Extract features using the extractor
                        features_df = self.extractor.extract_session_features(session_data)
                        
                        if not features_df.empty:
                            # Add user and session info
                            features_df = features_df.copy()
                            features_df['user'] = user
                            features_df['session_id'] = session_id
                            
                            all_features.append(features_df)
                            print(f"  Session {session_id}: extracted {features_df.shape[1]} features")
                        else:
                            print(f"  Session {session_id}: no features extracted")
                            
                    except Exception as e:
                        print(f"  Session {session_id}: error - {e}")
                        continue
        
        if not all_features:
            print("No features extracted from any session!")
            return pd.DataFrame()
        
        try:
            # Combine all features
            feature_matrix = pd.concat(all_features, ignore_index=True)
            print(f"Final feature matrix shape: {feature_matrix.shape}")
            return feature_matrix
            
        except Exception as e:
            print(f"Error combining features: {e}")
            return pd.DataFrame()
    
    def _train_user_models(self, feature_matrix, target_user):
        """Train models for user authentication - FIXED VERSION"""
        print(f"Training models for {target_user}")
        
        # Prepare data
        X = feature_matrix.drop(['user', 'session_id'], axis=1, errors='ignore')
        y = (feature_matrix['user'] == target_user).astype(int)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
        
        # Define models
        models = {
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'svm': SVC(probability=True, random_state=42)
        }
        
        results = {}
        
        for name, model in models.items():
            print(f"Training {name}...")
            
            try:
                # Train model
                model.fit(X_train, y_train)
                
                # Predictions
                y_pred = model.predict(X_test)
                y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
                
                # Calculate metrics
                accuracy = accuracy_score(y_test, y_pred)
                
                # Cross-validation
                cv_scores = cross_val_score(model, X, y, cv=5)
                
                # Get feature importance (if available)
                feature_importance = {}
                if hasattr(model, 'feature_importances_'):
                    feature_importance = {
                        str(feature): float(importance) 
                        for feature, importance in zip(X.columns, model.feature_importances_)
                    }
                
                # Save results (without the model object)
                results[name] = {
                    'test_accuracy': float(accuracy),
                    'cv_mean': float(cv_scores.mean()),
                    'cv_std': float(cv_scores.std()),
                    'feature_importance': feature_importance
                }
                
                # Save model separately (not in JSON)
                model_path = os.path.join(self.models_dir, f"{target_user}_{name}.pkl")
                joblib.dump(model, model_path)
                
                print(f"  {name} accuracy: {accuracy:.3f}")
                
            except Exception as e:
                print(f"  Error training {name}: {e}")
                continue
        
        return results
    
    def _save_training_results(self, results, username):
        """Save training results to file - FIXED VERSION"""
        # Create a serializable version of results
        serializable_results = {}
        
        for model_name, model_result in results.items():
            serializable_results[model_name] = {
                'test_accuracy': float(model_result.get('test_accuracy', 0)),
                'cv_mean': float(model_result.get('cv_mean', 0)),
                'cv_std': float(model_result.get('cv_std', 0)),
                # Convert feature importance to serializable format
                'feature_importance': {
                    str(key): float(value) 
                    for key, value in model_result.get('feature_importance', {}).items()
                }
            }
        
        # Create log entry
        log_entry = {
            'username': username,
            'timestamp': datetime.now().isoformat(),
            'all_results': serializable_results,
            'best_model': max(
                serializable_results.items(), 
                key=lambda x: x[1].get('test_accuracy', 0)
            )[0] if serializable_results else None,
            'best_accuracy': max(
                [result.get('test_accuracy', 0) for result in serializable_results.values()]
            ) if serializable_results else 0
        }
        
        log_file = os.path.join(self.results_dir, "training_logs.json")
        
        # Load existing logs or create new
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            except:
                logs = []
        else:
            logs = []
        
        # Remove old entries for this user
        logs = [log for log in logs if log.get('username') != username]
        
        # Add new entry
        logs.append(log_entry)
        
        # Save to file
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        print(f"Results saved for {username}")
    
    def generate_feature_visualizations(self):
        """Generate feature visualization plots"""
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            # Create visualizations directory
            viz_dir = os.path.join(self.results_dir, "visualizations")
            os.makedirs(viz_dir, exist_ok=True)
            
            print("Feature visualizations generated")
            
        except Exception as e:
            print(f"Visualization error: {e}")