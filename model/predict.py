import os
import pandas as pd
import numpy as np
import pickle
from typing import Dict, Tuple, Optional
from model.feature_extractor import EnhancedFeatureExtractor

class EnhancedAuthenticationSystem:
    """Enhanced authentication system with comprehensive features"""
    
    def __init__(self, model_dir: str = "model"):
        self.model_dir = model_dir
        self.feature_extractor = EnhancedFeatureExtractor()
        self.loaded_models = {}
        
    def load_user_model(self, username: str) -> bool:
        """Load a user's trained model"""
        model_path = os.path.join(self.model_dir, f"{username}_model.pkl")
        
        if not os.path.exists(model_path):
            print(f"No trained model found for user {username}")
            return False
        
        try:
            with open(model_path, 'rb') as f:
                self.loaded_models[username] = pickle.load(f)
            print(f"Loaded model for user {username}")
            return True
        except Exception as e:
            print(f"Error loading model for {username}: {e}")
            return False
    
    def load_multi_class_model(self) -> bool:
        """Load multi-class model"""
        model_path = os.path.join(self.model_dir, "multi_class_model.pkl")
        
        if not os.path.exists(model_path):
            print("No multi-class model found")
            return False
        
        try:
            with open(model_path, 'rb') as f:
                self.loaded_models['multi_class'] = pickle.load(f)
            print("Loaded multi-class model")
            return True
        except Exception as e:
            print(f"Error loading multi-class model: {e}")
            return False
    
    def authenticate_session(self, username: str, session_data: pd.DataFrame, 
                           confidence_threshold: float = 0.7) -> Dict[str, any]:
        """Authenticate session using binary classifier"""
        if username not in self.loaded_models:
            if not self.load_user_model(username):
                return self._error_result("No trained model available")
        
        model = self.loaded_models[username]
        
        # Extract features
        features_df = self.feature_extractor.extract_session_features(session_data)
        if features_df.empty:
            return self._error_result("No features could be extracted")
        
        # Predict
        X = features_df.values
        prediction = model.predict(X)[0]
        confidence = model.predict_proba(X)[0][1]  # Probability of genuine
        
        is_genuine = (prediction == 1) and (confidence >= confidence_threshold)
        
        return {
            'authenticated': bool(is_genuine),
            'confidence': float(confidence),
            'prediction': int(prediction),
            'threshold_used': float(confidence_threshold),
            'reason': 'GENUINE_USER' if is_genuine else 'LOW_CONFIDENCE' if prediction == 1 else 'IMPOSTOR_DETECTED',
            'features_extracted': len(features_df.columns),
            'session_duration': session_data['timestamp'].max() - session_data['timestamp'].min()
        }
    
    def identify_user(self, session_data: pd.DataFrame) -> Dict[str, any]:
        """Identify user using multi-class classification"""
        if 'multi_class' not in self.loaded_models:
            if not self.load_multi_class_model():
                return self._error_result("No multi-class model available")
        
        model_data = self.loaded_models['multi_class']
        model = model_data['model']
        label_encoder = model_data['label_encoder']
        
        # Extract features
        features_df = self.feature_extractor.extract_session_features(session_data)
        if features_df.empty:
            return self._error_result("No features could be extracted")
        
        # Ensure feature alignment
        X = self._align_features(features_df, model_data['feature_names'])
        
        # Predict
        probabilities = model.predict_proba(X)[0]
        predicted_class = np.argmax(probabilities)
        confidence = probabilities[predicted_class]
        username = label_encoder.inverse_transform([predicted_class])[0]
        
        # Get top predictions
        top_indices = np.argsort(probabilities)[::-1][:3]
        top_predictions = [
            {
                'username': label_encoder.inverse_transform([i])[0],
                'confidence': float(probabilities[i])
            }
            for i in top_indices
        ]
        
        return {
            'identified_user': username,
            'confidence': float(confidence),
            'top_predictions': top_predictions,
            'all_probabilities': {
                label_encoder.inverse_transform([i])[0]: float(probabilities[i])
                for i in range(len(probabilities))
            },
            'features_extracted': len(features_df.columns)
        }
    
    def _align_features(self, features_df: pd.DataFrame, expected_features: list) -> np.ndarray:
        """Align features with model's expected feature set"""
        aligned_features = []
        for feature in expected_features:
            if feature in features_df.columns:
                aligned_features.append(features_df[feature].values[0])
            else:
                aligned_features.append(0.0)  # Default value for missing features
        
        return np.array([aligned_features])
    
    def _error_result(self, reason: str) -> Dict[str, any]:
        """Create standardized error result"""
        return {
            'authenticated': False,
            'confidence': 0.0,
            'reason': reason,
            'error': True
        }
    
    def get_model_info(self, username: str = None) -> Dict[str, any]:
        """Get information about trained models"""
        if username:
            if username not in self.loaded_models:
                if not self.load_user_model(username):
                    return {'error': f'No model found for {username}'}
            
            model = self.loaded_models[username]
            return {
                'username': username,
                'model_type': type(model.named_steps['classifier']).__name__,
                'is_fitted': hasattr(model, 'classes_'),
                'feature_count': len(model.named_steps['scaler'].feature_names_in_) if hasattr(model.named_steps['scaler'], 'feature_names_in_') else 'unknown'
            }
        else:
            # Return info about all available models
            models_info = {}
            model_files = [f for f in os.listdir(self.model_dir) if f.endswith('.pkl')]
            
            for model_file in model_files:
                username = model_file.replace('_model.pkl', '')
                models_info[username] = self.get_model_info(username)
            
            return models_info

# Update main.py to use enhanced authentication
def update_main_for_enhanced_auth():
    """Example of how to update main.py for enhanced authentication"""
    
    # In your main.py, replace the existing _prompt_model_training method with:
    """
    def _prompt_model_training(self):
        \"\"\"Enhanced model training prompt\"\"\"
        session_count = self.user_manager.get_user_session_count(self.current_user)
        
        if session_count >= 4:
            response = messagebox.askyesno(
                "Model Training", 
                f\"You have {session_count} sessions. Train authentication model now?\\n\\n"
                \"This will:\\n"
                \"• Extract comprehensive features from your mouse data\\n"
                \"• Train multiple machine learning models\\n"
                \"• Generate evaluation reports and visualizations\"
            )
            
            if response:
                try:
                    from model.train_model import ModelTrainer
                    trainer = ModelTrainer()
                    
                    # Train binary classifier for this user
                    results = trainer.train_models(self.current_user)
                    
                    # Generate feature visualizations
                    trainer.generate_feature_visualizations()
                    
                    messagebox.showinfo(
                        "Training Complete", 
                        f\"Model trained successfully!\\n\\n"
                        f\"Best AUC Score: {results['best_score']:.3f}\\n"
                        f\"Check the 'results' folder for detailed reports and plots.\"
                    )
                    
                except Exception as e:
                    messagebox.showerror("Training Error", f\"Error during training: {str(e)}\")
    """
    
    pass