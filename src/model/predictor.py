"""
AI Brain Predictive Layer for ARES QA Engine
Advanced defect prediction using machine learning and historical data analysis
"""

import os
import json
import pickle
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.feature_extraction.text import TfidfVectorizer
import git

from src.utils.metrics_collector import get_metrics_collector


@dataclass
class TestRiskPrediction:
    """Data class for test risk prediction results"""
    test_name: str
    risk_score: float
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    confidence: float
    contributing_factors: List[str]
    recommended_actions: List[str]
    prediction_timestamp: datetime


@dataclass
class CodeChangeFeatures:
    """Features extracted from code changes"""
    files_changed: List[str]
    authors: List[str]
    commit_count: int
    lines_added: int
    lines_removed: int
    file_types: Dict[str, int]
    time_of_day: int
    day_of_week: int
    complex_changes: bool
    test_files_touched: bool
    config_files_touched: bool


class DefectPredictor:
    """
    Advanced AI-powered defect prediction system
    Uses machine learning to predict test failures based on code changes
    """
    
    def __init__(self, model_path: str = "data/models", enable_training: bool = True):
        self.model_path = Path(model_path)
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        # ML models
        self.rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
        # Feature extractors
        self.tfidf_vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        
        # Model metadata
        self.feature_names = []
        self.model_version = "1.0.0"
        self.last_training_date = None
        self.accuracy_score = 0.0
        
        # Historical data
        self.historical_data = []
        self.predictions_cache = {}
        
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        
        # Load existing models if available
        self._load_models()
        
        # Training data collection
        if enable_training:
            self._initialize_training_data()
    
    def _initialize_training_data(self):
        """Initialize with sample training data if no historical data exists"""
        training_file = self.model_path / "training_data.json"
        
        if not training_file.exists():
            # Create sample training data based on common patterns
            sample_data = [
                {
                    "test_name": "test_login_functionality",
                    "files_changed": ["src/auth/login.py", "src/auth/user.py"],
                    "authors": ["developer1"],
                    "commit_count": 3,
                    "lines_added": 45,
                    "lines_removed": 12,
                    "time_of_day": 14,
                    "day_of_week": 2,
                    "complex_changes": True,
                    "test_files_touched": False,
                    "config_files_touched": False,
                    "failed": True,
                    "failure_reason": "Authentication logic changed"
                },
                {
                    "test_name": "test_payment_processing",
                    "files_changed": ["src/payment/processor.py"],
                    "authors": ["developer2"],
                    "commit_count": 1,
                    "lines_added": 15,
                    "lines_removed": 5,
                    "time_of_day": 10,
                    "day_of_week": 3,
                    "complex_changes": False,
                    "test_files_touched": False,
                    "config_files_touched": False,
                    "failed": False,
                    "failure_reason": None
                },
                {
                    "test_name": "test_user_registration",
                    "files_changed": ["src/auth/user.py", "src/database/models.py", "config/database.yaml"],
                    "authors": ["developer1", "developer3"],
                    "commit_count": 5,
                    "lines_added": 120,
                    "lines_removed": 45,
                    "time_of_day": 16,
                    "day_of_week": 4,
                    "complex_changes": True,
                    "test_files_touched": True,
                    "config_files_touched": True,
                    "failed": True,
                    "failure_reason": "Database schema changes"
                },
                {
                    "test_name": "test_search_functionality",
                    "files_changed": ["src/search/index.py"],
                    "authors": ["developer4"],
                    "commit_count": 2,
                    "lines_added": 25,
                    "lines_removed": 8,
                    "time_of_day": 11,
                    "day_of_week": 1,
                    "complex_changes": False,
                    "test_files_touched": False,
                    "config_files_touched": False,
                    "failed": False,
                    "failure_reason": None
                }
            ]
            
            with open(training_file, 'w') as f:
                json.dump(sample_data, f, indent=2)
            
            self.historical_data = sample_data
            self.logger.info(f"Created sample training data with {len(sample_data)} records")
        else:
            self._load_historical_data()
    
    def extract_git_features(self, repo_path: str = ".", since_days: int = 7) -> List[CodeChangeFeatures]:
        """
        Extract features from recent git commits
        """
        try:
            repo = git.Repo(repo_path)
            
            # Get commits from the last N days
            since_date = datetime.now() - timedelta(days=since_days)
            commits = list(repo.iter_commits(since=since_date))
            
            features_list = []
            
            for commit in commits:
                # Get changed files
                changed_files = []
                file_types = {}
                lines_added = 0
                lines_removed = 0
                
                for diff in commit.diff(commit.parents[0] if commit.parents else None):
                    file_path = diff.a_path if diff.a_path else diff.b_path
                    changed_files.append(file_path)
                    
                    # Count file types
                    ext = Path(file_path).suffix
                    file_types[ext] = file_types.get(ext, 0) + 1
                    
                    # Count lines changed
                    if diff.diff:
                        lines_added += len(diff.diff)
                        lines_removed += len(diff.diff)
                
                # Determine complexity
                complex_changes = (
                    len(changed_files) > 5 or
                    lines_added > 100 or
                    any(ext in ['.py', '.js', '.java'] for ext in file_types.keys())
                )
                
                # Check for test/config files
                test_files_touched = any('test' in f or 'spec' in f for f in changed_files)
                config_files_touched = any(
                    f.endswith(('.yml', '.yaml', '.json', '.conf', '.ini')) 
                    for f in changed_files
                )
                
                features = CodeChangeFeatures(
                    files_changed=changed_files,
                    authors=[commit.author.name],
                    commit_count=1,
                    lines_added=lines_added,
                    lines_removed=lines_removed,
                    file_types=file_types,
                    time_of_day=commit.committed_datetime.hour,
                    day_of_week=commit.committed_datetime.weekday(),
                    complex_changes=complex_changes,
                    test_files_touched=test_files_touched,
                    config_files_touched=config_files_touched
                )
                
                features_list.append(features)
            
            return features_list
            
        except Exception as e:
            self.logger.error(f"Failed to extract git features: {e}")
            return []
    
    def features_to_vector(self, features: CodeChangeFeatures, test_name: str) -> np.ndarray:
        """
        Convert features to numerical vector for ML model
        """
        feature_vector = []
        
        # Basic numerical features
        feature_vector.extend([
            len(features.files_changed),
            features.commit_count,
            features.lines_added,
            features.lines_removed,
            features.time_of_day,
            features.day_of_week,
            int(features.complex_changes),
            int(features.test_files_touched),
            int(features.config_files_touched)
        ])
        
        # File type features
        common_extensions = ['.py', '.js', '.ts', '.java', '.go', '.rb', '.php', '.yml', '.yaml', '.json', '.md']
        for ext in common_extensions:
            feature_vector.append(features.file_types.get(ext, 0))
        
        # Author encoding (simplified)
        author_hash = hash(features.authors[0]) % 100 if features.authors else 0
        feature_vector.append(author_hash)
        
        # Test name features
        test_features = self._extract_test_name_features(test_name)
        feature_vector.extend(test_features)
        
        return np.array(feature_vector)
    
    def _extract_test_name_features(self, test_name: str) -> List[float]:
        """Extract features from test name"""
        features = []
        
        # Test type indicators
        features.append(float('login' in test_name.lower()))
        features.append(float('payment' in test_name.lower()))
        features.append(float('auth' in test_name.lower()))
        features.append(float('search' in test_name.lower()))
        features.append(float('api' in test_name.lower()))
        features.append(float('ui' in test_name.lower()))
        features.append(float('integration' in test_name.lower()))
        features.append(float('performance' in test_name.lower()))
        features.append(float('security' in test_name.lower()))
        
        # Test complexity indicators
        features.append(float(len(test_name.split('_'))))  # Number of parts
        features.append(float(len(test_name)))  # Length of name
        
        return features
    
    def train_models(self) -> Dict[str, float]:
        """
        Train the predictive models on historical data
        """
        if len(self.historical_data) < 5:
            self.logger.warning("Insufficient training data")
            return {"error": "Insufficient training data"}
        
        try:
            # Convert historical data to DataFrame
            df = pd.DataFrame(self.historical_data)
            
            # Prepare features and target
            X = []
            y = []
            
            for _, row in df.iterrows():
                # Reconstruct features
                features = CodeChangeFeatures(
                    files_changed=row.get('files_changed', []),
                    authors=row.get('authors', ['unknown']),
                    commit_count=row.get('commit_count', 1),
                    lines_added=row.get('lines_added', 0),
                    lines_removed=row.get('lines_removed', 0),
                    file_types=row.get('file_types', {}),
                    time_of_day=row.get('time_of_day', 12),
                    day_of_week=row.get('day_of_week', 3),
                    complex_changes=row.get('complex_changes', False),
                    test_files_touched=row.get('test_files_touched', False),
                    config_files_touched=row.get('config_files_touched', False)
                )
                
                feature_vector = self.features_to_vector(features, row['test_name'])
                X.append(feature_vector)
                y.append(row.get('failed', False))
            
            X = np.array(X)
            y = np.array(y)
            
            if len(X) == 0:
                return {"error": "No features extracted"}
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train models
            self.rf_model.fit(X_train_scaled, y_train)
            self.gb_model.fit(X_train_scaled, y_train)
            
            # Evaluate models
            rf_score = self.rf_model.score(X_test_scaled, y_test)
            gb_score = self.gb_model.score(X_test_scaled, y_test)
            
            # Cross-validation
            rf_cv = cross_val_score(self.rf_model, X_train_scaled, y_train, cv=3)
            gb_cv = cross_val_score(self.gb_model, X_train_scaled, y_train, cv=3)
            
            # Store feature names
            self.feature_names = [
                'files_changed_count', 'commit_count', 'lines_added', 'lines_removed',
                'time_of_day', 'day_of_week', 'complex_changes', 'test_files_touched',
                'config_files_touched'
            ] + [f'file_type_{ext}' for ext in ['.py', '.js', '.ts', '.java', '.go', '.rb', '.php', '.yml', '.yaml', '.json', '.md']] + [
                'author_hash'
            ] + [
                'has_login', 'has_payment', 'has_auth', 'has_search', 'has_api',
                'has_ui', 'has_integration', 'has_performance', 'has_security',
                'test_name_parts', 'test_name_length'
            ]
            
            # Save models
            self._save_models()
            
            # Update metadata
            self.last_training_date = datetime.now()
            self.accuracy_score = max(rf_score, gb_score)
            
            results = {
                "random_forest_score": rf_score,
                "gradient_boosting_score": gb_score,
                "rf_cv_mean": rf_cv.mean(),
                "rf_cv_std": rf_cv.std(),
                "gb_cv_mean": gb_cv.mean(),
                "gb_cv_std": gb_cv.std(),
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "model_accuracy": self.accuracy_score
            }
            
            self.logger.info(f"Models trained successfully. RF: {rf_score:.3f}, GB: {gb_score:.3f}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Model training failed: {e}")
            return {"error": str(e)}
    
    def predict_test_failure_risk(self, test_name: str, features: Optional[CodeChangeFeatures] = None) -> TestRiskPrediction:
        """
        Predict the risk of test failure for a specific test
        """
        # Check cache first
        cache_key = f"{test_name}_{hash(str(features)) if features else 'no_features'}"
        if cache_key in self.predictions_cache:
            cached_prediction = self.predictions_cache[cache_key]
            # Check if cache is still valid (less than 1 hour old)
            if datetime.now() - cached_prediction.prediction_timestamp < timedelta(hours=1):
                return cached_prediction
        
        # Extract features if not provided
        if features is None:
            git_features = self.extract_git_features()
            features = git_features[0] if git_features else CodeChangeFeatures(
                files_changed=[], authors=['unknown'], commit_count=0, lines_added=0,
                lines_removed=0, file_types={}, time_of_day=12, day_of_week=3,
                complex_changes=False, test_files_touched=False, config_files_touched=False
            )
        
        try:
            # Convert to vector
            feature_vector = self.features_to_vector(features, test_name)
            feature_vector = feature_vector.reshape(1, -1)
            
            # Scale features
            feature_vector_scaled = self.scaler.transform(feature_vector)
            
            # Get predictions from both models
            rf_proba = self.rf_model.predict_proba(feature_vector_scaled)[0]
            gb_proba = self.gb_model.predict_proba(feature_vector_scaled)[0]
            
            # Ensemble prediction (weighted average)
            ensemble_proba = 0.6 * rf_proba + 0.4 * gb_proba
            risk_score = ensemble_proba[1]  # Probability of failure
            
            # Determine risk level
            if risk_score < 0.3:
                risk_level = "low"
            elif risk_score < 0.6:
                risk_level = "medium"
            elif risk_score < 0.8:
                risk_level = "high"
            else:
                risk_level = "critical"
            
            # Calculate confidence
            confidence = max(rf_proba.max(), gb_proba.max())
            
            # Determine contributing factors
            contributing_factors = self._analyze_contributing_factors(features, feature_vector[0])
            
            # Generate recommended actions
            recommended_actions = self._generate_recommendations(risk_level, contributing_factors, features)
            
            prediction = TestRiskPrediction(
                test_name=test_name,
                risk_score=risk_score,
                risk_level=risk_level,
                confidence=confidence,
                contributing_factors=contributing_factors,
                recommended_actions=recommended_actions,
                prediction_timestamp=datetime.now()
            )
            
            # Cache the prediction
            self.predictions_cache[cache_key] = prediction
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Prediction failed for {test_name}: {e}")
            # Return fallback prediction
            return TestRiskPrediction(
                test_name=test_name,
                risk_score=0.5,
                risk_level="medium",
                confidence=0.5,
                contributing_factors=["Model prediction failed"],
                recommended_actions=["Manual review recommended"],
                prediction_timestamp=datetime.now()
            )
    
    def _analyze_contributing_factors(self, features: CodeChangeFeatures, feature_vector: np.ndarray) -> List[str]:
        """Analyze what factors contribute most to the risk"""
        factors = []
        
        if features.complex_changes:
            factors.append("Complex code changes detected")
        
        if len(features.files_changed) > 5:
            factors.append(f"High number of files changed ({len(features.files_changed)})")
        
        if features.lines_added > 100:
            factors.append(f"Large code addition ({features.lines_added} lines)")
        
        if features.config_files_touched:
            factors.append("Configuration files modified")
        
        if not features.test_files_touched and len(features.files_changed) > 0:
            factors.append("No test files updated with code changes")
        
        if features.time_of_day < 9 or features.time_of_day > 17:
            factors.append("Changes made outside business hours")
        
        # Check file type risks
        risky_extensions = ['.py', '.js', '.java', '.go']
        for ext in risky_extensions:
            if ext in features.file_types and features.file_types[ext] > 2:
                factors.append(f"Multiple {ext} files changed")
        
        return factors
    
    def _generate_recommendations(self, risk_level: str, factors: List[str], features: CodeChangeFeatures) -> List[str]:
        """Generate recommended actions based on risk level and factors"""
        recommendations = []
        
        if risk_level in ["high", "critical"]:
            recommendations.extend([
                "Run targeted tests first",
                "Consider manual verification",
                "Increase test coverage for changed areas"
            ])
        
        if "Complex code changes detected" in factors:
            recommendations.append("Review code complexity and consider refactoring")
        
        if "Configuration files modified" in factors:
            recommendations.append("Verify configuration changes in test environment")
        
        if "No test files updated" in factors:
            recommendations.append("Add tests for new functionality")
        
        if risk_level == "critical":
            recommendations.append("Consider rolling back changes")
        
        # Add specific recommendations based on file types
        if '.py' in features.file_types:
            recommendations.append("Run Python static analysis tools")
        
        if features.lines_added > 200:
            recommendations.append("Split large changes into smaller commits")
        
        return list(set(recommendations))  # Remove duplicates
    
    def predict_batch_risks(self, test_names: List[str]) -> List[TestRiskPrediction]:
        """
        Predict risk for multiple tests at once
        """
        predictions = []
        git_features = self.extract_git_features()
        features = git_features[0] if git_features else None
        
        for test_name in test_names:
            prediction = self.predict_test_failure_risk(test_name, features)
            predictions.append(prediction)
        
        return predictions
    
    def get_risk_summary(self, predictions: List[TestRiskPrediction]) -> Dict[str, Any]:
        """
        Get a summary of risk predictions
        """
        if not predictions:
            return {"error": "No predictions provided"}
        
        risk_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        total_risk = 0
        high_risk_tests = []
        
        for prediction in predictions:
            risk_counts[prediction.risk_level] += 1
            total_risk += prediction.risk_score
            
            if prediction.risk_level in ["high", "critical"]:
                high_risk_tests.append({
                    "test_name": prediction.test_name,
                    "risk_score": prediction.risk_score,
                    "risk_level": prediction.risk_level,
                    "top_factors": prediction.contributing_factors[:3]
                })
        
        avg_risk = total_risk / len(predictions)
        
        return {
            "total_tests": len(predictions),
            "risk_distribution": risk_counts,
            "average_risk_score": avg_risk,
            "high_risk_tests": high_risk_tests,
            "risk_trend": "increasing" if avg_risk > 0.6 else "stable",
            "recommendations": self._get_batch_recommendations(risk_counts, avg_risk)
        }
    
    def _get_batch_recommendations(self, risk_counts: Dict[str, int], avg_risk: float) -> List[str]:
        """Generate recommendations for a batch of tests"""
        recommendations = []
        
        if risk_counts["critical"] > 0:
            recommendations.append(f"URGENT: {risk_counts['critical']} critical risk tests detected")
        
        if risk_counts["high"] > 2:
            recommendations.append("Consider running tests in priority order")
        
        if avg_risk > 0.7:
            recommendations.append("High overall risk - consider additional testing")
        
        if risk_counts["low"] > risk_counts["medium"] + risk_counts["high"] + risk_counts["critical"]:
            recommendations.append("Low risk environment - suitable for rapid deployment")
        
        return recommendations
    
    def _save_models(self):
        """Save trained models to disk"""
        try:
            # Save models
            with open(self.model_path / "rf_model.pkl", 'wb') as f:
                pickle.dump(self.rf_model, f)
            
            with open(self.model_path / "gb_model.pkl", 'wb') as f:
                pickle.dump(self.gb_model, f)
            
            with open(self.model_path / "scaler.pkl", 'wb') as f:
                pickle.dump(self.scaler, f)
            
            # Save metadata
            metadata = {
                "model_version": self.model_version,
                "last_training_date": self.last_training_date.isoformat() if self.last_training_date else None,
                "accuracy_score": self.accuracy_score,
                "feature_names": self.feature_names
            }
            
            with open(self.model_path / "metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.info("Models saved successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to save models: {e}")
    
    def _load_models(self):
        """Load trained models from disk"""
        try:
            # Load models
            rf_model_path = self.model_path / "rf_model.pkl"
            gb_model_path = self.model_path / "gb_model.pkl"
            scaler_path = self.model_path / "scaler.pkl"
            metadata_path = self.model_path / "metadata.json"
            
            if rf_model_path.exists():
                with open(rf_model_path, 'rb') as f:
                    self.rf_model = pickle.load(f)
            
            if gb_model_path.exists():
                with open(gb_model_path, 'rb') as f:
                    self.gb_model = pickle.load(f)
            
            if scaler_path.exists():
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
            
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    self.model_version = metadata.get("model_version", "1.0.0")
                    self.accuracy_score = metadata.get("accuracy_score", 0.0)
                    self.feature_names = metadata.get("feature_names", [])
                    
                    if metadata.get("last_training_date"):
                        self.last_training_date = datetime.fromisoformat(metadata["last_training_date"])
            
            self.logger.info("Models loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load models: {e}")
    
    def _load_historical_data(self):
        """Load historical training data"""
        try:
            training_file = self.model_path / "training_data.json"
            if training_file.exists():
                with open(training_file, 'r') as f:
                    self.historical_data = json.load(f)
                self.logger.info(f"Loaded {len(self.historical_data)} historical records")
        except Exception as e:
            self.logger.error(f"Failed to load historical data: {e}")
    
    def add_test_result(self, test_name: str, features: CodeChangeFeatures, failed: bool, failure_reason: str = None):
        """
        Add a test result to historical data for continuous learning
        """
        record = {
            "test_name": test_name,
            "files_changed": features.files_changed,
            "authors": features.authors,
            "commit_count": features.commit_count,
            "lines_added": features.lines_added,
            "lines_removed": features.lines_removed,
            "file_types": features.file_types,
            "time_of_day": features.time_of_day,
            "day_of_week": features.day_of_week,
            "complex_changes": features.complex_changes,
            "test_files_touched": features.test_files_touched,
            "config_files_touched": features.config_files_touched,
            "failed": failed,
            "failure_reason": failure_reason,
            "timestamp": datetime.now().isoformat()
        }
        
        self.historical_data.append(record)
        
        # Save updated historical data
        training_file = self.model_path / "training_data.json"
        with open(training_file, 'w') as f:
            json.dump(self.historical_data, f, indent=2)
        
        # Retrain models if we have enough new data
        if len(self.historical_data) % 10 == 0:  # Retrain every 10 new records
            self.train_models()
        
        self.logger.info(f"Added test result for {test_name}: {'FAILED' if failed else 'PASSED'}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current models"""
        return {
            "model_version": self.model_version,
            "last_training_date": self.last_training_date.isoformat() if self.last_training_date else None,
            "accuracy_score": self.accuracy_score,
            "feature_count": len(self.feature_names),
            "training_samples": len(self.historical_data),
            "cache_size": len(self.predictions_cache),
            "feature_names": self.feature_names[:10]  # Show first 10 features
        }


# Global predictor instance
_predictor_instance = None


def get_defect_predictor() -> DefectPredictor:
    """Get or create the global defect predictor instance"""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = DefectPredictor()
    return _predictor_instance
