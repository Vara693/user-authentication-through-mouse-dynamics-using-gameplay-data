import pandas as pd
import numpy as np
from scipy import stats
from scipy.signal import find_peaks
import warnings
warnings.filterwarnings('ignore')

class EnhancedFeatureExtractor:
    """Enhanced feature extraction for mouse dynamics - FIXED VERSION"""
    
    def __init__(self):
        self.feature_names = []
    
    def extract_session_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract comprehensive features from a session - FIXED"""
        if len(df) < 5:  # Minimum events for meaningful features
            return pd.DataFrame()
            
        features = {}
        
        try:
            # Basic session info
            features.update(self._extract_session_metadata(df))
            
            # Movement features
            movement_features = self._extract_movement_features(df)
            features.update(movement_features)
            
            # Click features
            click_features = self._extract_click_features(df)
            features.update(click_features)
            
            # Timing features
            timing_features = self._extract_timing_features(df)
            features.update(timing_features)
            
            # Only extract complex features if we have enough data
            if len(df) > 20:
                trajectory_features = self._extract_trajectory_features(df)
                features.update(trajectory_features)
                
                behavioral_features = self._extract_behavioral_features(df)
                features.update(behavioral_features)
                
                statistical_features = self._extract_statistical_features(df)
                features.update(statistical_features)
            
            # Ensure all features are scalar values (not arrays)
            features = self._ensure_scalar_features(features)
            
            # Create DataFrame with proper column names
            if features:
                feature_df = pd.DataFrame([features])
                return feature_df
            else:
                return pd.DataFrame()
            
        except Exception as e:
            print(f"Feature extraction error: {e}")
            return pd.DataFrame()
    
    def _ensure_scalar_features(self, features):
        """Ensure all feature values are scalars, not arrays"""
        cleaned_features = {}
        for key, value in features.items():
            if hasattr(value, '__len__') and not isinstance(value, (str, bytes)):
                # If it's an array or list, take the first element or mean
                if len(value) > 0:
                    cleaned_features[key] = float(value[0]) if len(value) == 1 else float(np.mean(value))
                else:
                    cleaned_features[key] = 0.0
            else:
                cleaned_features[key] = float(value) if isinstance(value, (int, float, np.number)) else value
        return cleaned_features
    
    def _extract_session_metadata(self, df: pd.DataFrame) -> dict:
        """Extract basic session metadata"""
        if len(df) == 0:
            return {}
        
        duration = df['timestamp'].max() - df['timestamp'].min()
        
        return {
            'session_duration': float(duration),
            'total_events': int(len(df)),
            'events_per_second': float(len(df) / duration if duration > 0 else 0),
            'unique_x_positions': int(df['x'].nunique()),
            'unique_y_positions': int(df['y'].nunique())
        }
    
    def _extract_movement_features(self, df: pd.DataFrame) -> dict:
        """Extract comprehensive movement features"""
        movement_df = df[df['event_type'].isin(['motion', 'drag'])].copy()
        
        if len(movement_df) < 2:
            return {}
        
        # Use numpy arrays for faster computation
        x_vals = movement_df['x'].values
        y_vals = movement_df['y'].values
        t_vals = movement_df['timestamp'].values
        
        # Calculate movement metrics
        dx = np.diff(x_vals)
        dy = np.diff(y_vals)
        dt = np.diff(t_vals)
        dt = np.where(dt == 0, 0.001, dt)  # Avoid division by zero
        
        distances = np.sqrt(dx**2 + dy**2)
        velocities = distances / dt
        
        features = {
            # Distance metrics
            'movement_total_distance': float(np.sum(distances)),
            'movement_mean_distance': float(np.mean(distances)),
            'movement_std_distance': float(np.std(distances)),
            
            # Velocity metrics
            'movement_mean_velocity': float(np.mean(velocities)),
            'movement_std_velocity': float(np.std(velocities)),
            'movement_max_velocity': float(np.max(velocities) if len(velocities) > 0 else 0),
            'movement_min_velocity': float(np.min(velocities) if len(velocities) > 0 else 0),
        }
        
        # Only compute complex features if we have enough data
        if len(velocities) > 2:
            features['movement_velocity_skew'] = float(stats.skew(velocities))
        
        if len(velocities) > 3:
            features['movement_velocity_kurtosis'] = float(stats.kurtosis(velocities))
        
        # Acceleration and directional features for larger datasets
        if len(velocities) > 3:
            accelerations = np.diff(velocities) / dt[1:]
            features.update({
                'movement_mean_acceleration': float(np.mean(accelerations)),
                'movement_std_acceleration': float(np.std(accelerations)),
                'movement_max_acceleration': float(np.max(accelerations) if len(accelerations) > 0 else 0),
            })
            
            # Directional features (simplified)
            angles = np.arctan2(dy, dx)
            features['movement_directional_consistency'] = float(np.std(angles) if len(angles) > 0 else 0)
        
        # Peak detection for larger datasets
        if len(velocities) > 10:
            try:
                peaks, _ = find_peaks(velocities, height=np.mean(velocities))
                features['movement_peak_velocity_count'] = int(len(peaks))
            except:
                features['movement_peak_velocity_count'] = 0
        
        return features
    
    def _extract_click_features(self, df: pd.DataFrame) -> dict:
        """Extract click behavior features"""
        click_events = df[df['event_type'] == 'click']
        press_events = click_events[click_events['pressed'] == True]
        release_events = click_events[click_events['pressed'] == False]
        
        if len(press_events) == 0:
            return {}
        
        features = {
            'clicks_total_count': int(len(press_events)),
            'clicks_per_minute': float(len(press_events) / (df['timestamp'].max() / 60) if df['timestamp'].max() > 0 else 0),
        }
        
        # Click spatial patterns
        if len(press_events) > 1:
            features.update({
                'click_positions_std_x': float(press_events['x'].std()),
                'click_positions_std_y': float(press_events['y'].std()),
            })
            
            # Click distances
            click_distances = np.sqrt(np.diff(press_events['x'])**2 + np.diff(press_events['y'])**2)
            features.update({
                'clicks_mean_distance': float(np.mean(click_distances)),
                'clicks_std_distance': float(np.std(click_distances)),
            })
        
        # Click durations (optimized)
        if len(press_events) > 0 and len(release_events) > 0:
            click_durations = self._calculate_click_durations_optimized(press_events, release_events)
            if len(click_durations) > 0:
                features.update({
                    'clicks_mean_duration': float(np.mean(click_durations)),
                    'clicks_std_duration': float(np.std(click_durations)),
                })
        
        return features
    
    def _calculate_click_durations_optimized(self, press_events, release_events):
        """Calculate click durations - OPTIMIZED VERSION"""
        durations = []
        release_times = release_events['timestamp'].values
        release_x = release_events['x'].values
        release_y = release_events['y'].values
        
        for _, press in press_events.iterrows():
            # Find nearest release after press
            time_diff = release_times - press['timestamp']
            valid_releases = (time_diff > 0) & (time_diff < 2.0)  # Max 2 second duration
            
            if np.any(valid_releases):
                # Find the closest release in both time and space
                spatial_dist = np.sqrt((release_x - press['x'])**2 + (release_y - press['y'])**2)
                combined_score = time_diff[valid_releases] + spatial_dist[valid_releases] * 0.01
                best_match_idx = np.argmin(combined_score)
                
                original_indices = np.where(valid_releases)[0]
                best_idx = original_indices[best_match_idx]
                
                duration = release_times[best_idx] - press['timestamp']
                if 0.01 < duration < 2.0:  # Reasonable click duration
                    durations.append(duration)
        
        return durations
    
    def _extract_timing_features(self, df: pd.DataFrame) -> dict:
        """Extract timing patterns"""
        if len(df) < 2:
            return {}
        
        time_diffs = np.diff(df['timestamp'].values)
        time_diffs = time_diffs[time_diffs > 0]  # Remove zeros
        
        if len(time_diffs) == 0:
            return {}
        
        features = {
            'timing_session_duration': float(df['timestamp'].max() - df['timestamp'].min()),
            'timing_mean_interval': float(np.mean(time_diffs)),
            'timing_std_interval': float(np.std(time_diffs)),
            'timing_min_interval': float(np.min(time_diffs)),
            'timing_max_interval': float(np.max(time_diffs)),
        }
        
        if len(time_diffs) > 2:
            features['timing_interval_skew'] = float(stats.skew(time_diffs))
        
        if len(time_diffs) > 3:
            features['timing_interval_kurtosis'] = float(stats.kurtosis(time_diffs))
        
        return features
    
    def _extract_trajectory_features(self, df: pd.DataFrame) -> dict:
        """Extract mouse trajectory features"""
        movement_df = df[df['event_type'].isin(['motion', 'drag'])]
        
        if len(movement_df) < 10:
            return {}
        
        x = movement_df['x'].values
        y = movement_df['y'].values
        
        # Straightness and complexity
        total_distance = np.sum(np.sqrt(np.diff(x)**2 + np.diff(y)**2))
        direct_distance = np.sqrt((x[-1] - x[0])**2 + (y[-1] - y[0])**2)
        
        # Area coverage
        area_covered = (np.max(x) - np.min(x)) * (np.max(y) - np.min(y))
        
        features = {
            'trajectory_straightness': float(direct_distance / total_distance if total_distance > 0 else 0),
            'trajectory_complexity': float(total_distance / direct_distance if direct_distance > 0 else 0),
            'trajectory_covered_area': float(area_covered),
        }
        
        # Only compute curvature for larger datasets
        if len(x) > 20:
            features['trajectory_mean_curvature'] = float(self._calculate_mean_curvature_simple(x, y))
        
        return features
    
    def _calculate_mean_curvature_simple(self, x: np.ndarray, y: np.ndarray) -> float:
        """Calculate simplified mean curvature"""
        if len(x) < 3:
            return 0.0
        
        # Simplified curvature calculation
        dx = np.diff(x)
        dy = np.diff(y)
        ddx = np.diff(dx)
        ddy = np.diff(dy)
        
        # Use only every 5th point to reduce computation
        if len(ddx) > 10:
            step = max(1, len(ddx) // 10)
            ddx = ddx[::step]
            ddy = ddy[::step]
            dx = dx[:len(ddx)*step:step]
            dy = dy[:len(ddy)*step:step]
        
        curvature = np.abs(ddx * dy - dx * ddy) / (dx**2 + dy**2)**1.5
        curvature = curvature[~np.isnan(curvature)]
        curvature = curvature[~np.isinf(curvature)]
        
        return float(np.mean(curvature) if len(curvature) > 0 else 0)
    
    def _extract_behavioral_features(self, df: pd.DataFrame) -> dict:
        """Extract behavioral pattern features"""
        if len(df) < 10:
            return {}
        
        # Activity distribution (simplified to halves)
        session_duration = df['timestamp'].max() - df['timestamp'].min()
        if session_duration == 0:
            return {}
        
        half_time = session_duration / 2
        first_half = len(df[df['timestamp'] < half_time])
        second_half = len(df) - first_half
        total = len(df)
        
        if total == 0:
            return {}
        
        return {
            'activity_first_half': float(first_half / total),
            'activity_second_half': float(second_half / total),
            'activity_concentration': float(abs(first_half - second_half) / total),
        }
    
    def _extract_statistical_features(self, df: pd.DataFrame) -> dict:
        """Extract statistical moment features"""
        movement_df = df[df['event_type'].isin(['motion', 'drag'])]
        
        if len(movement_df) < 5:
            return {}
        
        # Velocity moments (simplified)
        dx = np.diff(movement_df['x'].values)
        dy = np.diff(movement_df['y'].values)
        dt = np.diff(movement_df['timestamp'].values)
        dt = np.where(dt == 0, 0.001, dt)
        
        velocities = np.sqrt(dx**2 + dy**2) / dt
        
        if len(velocities) > 3:
            return {
                'velocity_skewness': float(stats.skew(velocities)),
                'velocity_kurtosis': float(stats.kurtosis(velocities) if len(velocities) > 3 else 0),
            }
        
        return {}