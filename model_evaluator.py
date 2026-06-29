import pandas as pd
import numpy as np
import os
from model.predict import EnhancedAuthenticationSystem

class ModelEvaluator:
    """Comprehensive model evaluation system"""
    
    def __init__(self):
        self.auth_system = EnhancedAuthenticationSystem()
    
    def comprehensive_test(self):
        """Run comprehensive testing across all users"""
        # Get all trained users
        model_files = [f for f in os.listdir('model') if f.endswith('_model.pkl')]
        users = [f.replace('_model.pkl', '') for f in model_files]
        
        print(f"🔍 Testing {len(users)} users...")
        
        results = []
        
        for true_user in users:
            # Load user's model
            if not self.auth_system.load_user_model(true_user):
                continue
            
            # Test with user's OWN sessions (should accept)
            for session_num in [5, 6]:
                session_path = f"data/{true_user}/session_{session_num}.csv"
                if os.path.exists(session_path):
                    try:
                        data = pd.read_csv(session_path)
                        result = self.auth_system.authenticate_session(true_user, data)
                        
                        results.append({
                            'true_user': true_user,
                            'claimed_user': true_user,
                            'session': session_num,
                            'authenticated': result['authenticated'],
                            'confidence': result['confidence'],
                            'should_be': 'ACCEPT',
                            'correct': result['authenticated'],
                            'test_type': 'genuine'
                        })
                    except Exception as e:
                        print(f"Error testing {true_user} session {session_num}: {e}")
            
            # Test with OTHER users' sessions (should reject)
            for other_user in users:
                if other_user != true_user:
                    for session_num in [5, 6]:
                        session_path = f"data/{other_user}/session_{session_num}.csv"
                        if os.path.exists(session_path):
                            try:
                                data = pd.read_csv(session_path)
                                result = self.auth_system.authenticate_session(true_user, data)
                                
                                results.append({
                                    'true_user': other_user,
                                    'claimed_user': true_user,
                                    'session': session_num,
                                    'authenticated': result['authenticated'],
                                    'confidence': result['confidence'],
                                    'should_be': 'REJECT',
                                    'correct': not result['authenticated'],
                                    'test_type': 'impostor'
                                })
                            except Exception as e:
                                print(f"Error testing {other_user} as {true_user}: {e}")
        
        return results
    
    def generate_summary_report(self, results):
        """Generate comprehensive summary report"""
        if not results:
            return "No results available"
        
        df = pd.DataFrame(results)
        
        # Calculate metrics
        overall_accuracy = df['correct'].mean()
        
        genuine_tests = df[df['test_type'] == 'genuine']
        impostor_tests = df[df['test_type'] == 'impostor']
        
        genuine_accuracy = genuine_tests['correct'].mean() if len(genuine_tests) > 0 else 0
        impostor_accuracy = impostor_tests['correct'].mean() if len(impostor_tests) > 0 else 0
        
        avg_confidence_genuine = genuine_tests['confidence'].mean() if len(genuine_tests) > 0 else 0
        avg_confidence_impostor = impostor_tests['confidence'].mean() if len(impostor_tests) > 0 else 0
        
        # Generate report
        report = "📊 COMPREHENSIVE TEST RESULTS\n"
        report += "=" * 60 + "\n\n"
        report += f"Overall Accuracy: {overall_accuracy:.2%}\n"
        report += f"Genuine User Accuracy: {genuine_accuracy:.2%}\n"
        report += f"Impostor Rejection Accuracy: {impostor_accuracy:.2%}\n"
        report += f"Average Confidence (Genuine): {avg_confidence_genuine:.2%}\n"
        report += f"Average Confidence (Impostor): {avg_confidence_impostor:.2%}\n\n"
        
        report += f"Total Tests: {len(df)}\n"
        report += f"Genuine Tests: {len(genuine_tests)}\n"
        report += f"Impostor Tests: {len(impostor_tests)}\n\n"
        
        # Per-user performance
        report += "PER-USER PERFORMANCE:\n"
        report += "-" * 40 + "\n"
        
        for user in df['claimed_user'].unique():
            user_tests = df[df['claimed_user'] == user]
            user_accuracy = user_tests['correct'].mean()
            user_genuine = user_tests[user_tests['test_type'] == 'genuine']
            user_impostor = user_tests[user_tests['test_type'] == 'impostor']
            
            genuine_acc = user_genuine['correct'].mean() if len(user_genuine) > 0 else 0
            impostor_acc = user_impostor['correct'].mean() if len(user_impostor) > 0 else 0
            
            report += f"{user:15} | Overall: {user_accuracy:6.2%} | Genuine: {genuine_acc:6.2%} | Impostor: {impostor_acc:6.2%}\n"
        
        return report
    
    def generate_visualizations(self, results):
        """Generate visualization plots"""
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        df = pd.DataFrame(results)
        
        # Create plots directory
        os.makedirs('results/plots/testing', exist_ok=True)
        
        # Confidence distribution plot
        plt.figure(figsize=(10, 6))
        for test_type in ['genuine', 'impostor']:
            data = df[df['test_type'] == test_type]['confidence']
            plt.hist(data, alpha=0.7, label=test_type, bins=20)
        
        plt.xlabel('Confidence')
        plt.ylabel('Frequency')
        plt.title('Confidence Distribution: Genuine vs Impostor')
        plt.legend()
        plt.savefig('results/plots/testing/confidence_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Accuracy by user plot
        user_accuracy = df.groupby('claimed_user')['correct'].mean().sort_values()
        
        plt.figure(figsize=(12, 8))
        user_accuracy.plot(kind='barh')
        plt.xlabel('Accuracy')
        plt.title('Authentication Accuracy by User')
        plt.tight_layout()
        plt.savefig('results/plots/testing/user_accuracy.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Testing visualizations generated in results/plots/testing/")