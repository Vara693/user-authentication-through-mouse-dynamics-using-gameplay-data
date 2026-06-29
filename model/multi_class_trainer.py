import os
import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
from model.feature_extractor import EnhancedFeatureExtractor

class MultiClassTrainer:
    def __init__(self):
        self.extractor = EnhancedFeatureExtractor()
        self.model = None
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        
    def prepare_training_data(self):
        """Prepare training data from all users' sessions"""
        print("🔍 Preparing training data from all users...")
        
        users_dir = "data"
        if not os.path.exists(users_dir):
            raise Exception("No data directory found!")
        
        all_features = []
        all_labels = []
        
        users = [d for d in os.listdir(users_dir) if os.path.isdir(os.path.join(users_dir, d))]
        
        if len(users) < 2:
            raise Exception(f"Need at least 2 users for training. Found: {len(users)}")
        
        print(f"📊 Found {len(users)} users: {users}")
        
        for user in users:
            user_dir = os.path.join(users_dir, user)
            session_files = [f for f in os.listdir(user_dir) if f.startswith('session_') and f.endswith('.csv')]
            
            print(f"  Processing {user}: {len(session_files)} sessions")
            
            for session_file in session_files:
                session_path = os.path.join(user_dir, session_file)
                try:
                    # Load session data
                    session_data = pd.read_csv(session_path)
                    
                    # Extract features
                    features_df = self.extractor.extract_session_features(session_data)
                    
                    if not features_df.empty:
                        all_features.append(features_df.values[0])
                        all_labels.append(user)
                        print(f"    ✅ {session_file}: {len(features_df.columns)} features")
                    else:
                        print(f"    ❌ {session_file}: No features extracted")
                        
                except Exception as e:
                    print(f"    ❌ {session_file}: Error - {e}")
                    continue
        
        if len(all_features) == 0:
            raise Exception("No features could be extracted from any session!")
        
        # Convert to arrays
        X = np.array(all_features)
        y = np.array(all_labels)
        
        print(f"🎯 Final dataset: {X.shape[0]} samples, {X.shape[1]} features")
        print(f"👥 Users distribution: {pd.Series(y).value_counts().to_dict()}")
        
        return X, y
    
    def train_model(self, test_size=0.2):
        """Train the multi-class classification model"""
        X, y = self.prepare_training_data()
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=test_size, random_state=42, stratify=y_encoded
        )
        
        print("🤖 Training Random Forest classifier...")
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✅ Model trained successfully!")
        print(f"📈 Test Accuracy: {accuracy:.2%}")
        
        # Generate detailed report
        self._generate_training_report(X_test, y_test, y_pred)
        
        return accuracy
    
    def _generate_training_report(self, X_test, y_test, y_pred):
        """Generate comprehensive training report"""
        os.makedirs('results/plots', exist_ok=True)
        os.makedirs('results/tables', exist_ok=True)
        
        # Classification report
        report = classification_report(y_test, y_pred, target_names=self.label_encoder.classes_, output_dict=True)
        report_df = pd.DataFrame(report).transpose()
        report_df.to_csv('results/tables/classification_report.csv')
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': [f'feature_{i}' for i in range(len(self.model.feature_importances_))],
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        feature_importance.to_csv('results/tables/feature_importance.csv', index=False)
        
        # Create visualizations
        self._create_visualizations(y_test, y_pred, feature_importance)
    
    def _create_visualizations(self, y_test, y_pred, feature_importance):
        """Create training visualizations"""
        # Accuracy by user
        user_accuracy = {}
        for user in self.label_encoder.classes_:
            user_idx = self.label_encoder.transform([user])[0]
            user_mask = (y_test == user_idx)
            if user_mask.any():
                user_acc = accuracy_score(y_test[user_mask], y_pred[user_mask])
                user_accuracy[user] = user_acc
        
        # Plot 1: User Accuracy
        plt.figure(figsize=(10, 6))
        plt.bar(user_accuracy.keys(), user_accuracy.values())
        plt.title('Model Accuracy by User')
        plt.xlabel('User')
        plt.ylabel('Accuracy')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('results/plots/user_accuracy.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot 2: Feature Importance
        plt.figure(figsize=(12, 8))
        top_features = feature_importance.head(20)
        plt.barh(top_features['feature'], top_features['importance'])
        plt.title('Top 20 Most Important Features')
        plt.xlabel('Importance')
        plt.tight_layout()
        plt.savefig('results/plots/feature_importance.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("📊 Visualizations saved to results/plots/")
    
    def save_model(self, filename='model/multi_class_model.pkl'):
        """Save trained model"""
        os.makedirs('model', exist_ok=True)
        
        model_data = {
            'model': self.model,
            'label_encoder': self.label_encoder,
            'feature_names': self.feature_names
        }
        
        with open(filename, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"💾 Model saved to {filename}")
    
    def load_model(self, filename='model/multi_class_model.pkl'):
        """Load trained model"""
        if not os.path.exists(filename):
            raise Exception("No trained model found!")
        
        with open(filename, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.label_encoder = model_data['label_encoder']
        self.feature_names = model_data.get('feature_names', [])
        
        print("🔧 Model loaded successfully!")
        return True