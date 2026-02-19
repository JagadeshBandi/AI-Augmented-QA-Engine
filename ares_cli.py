#!/usr/bin/env python3
"""
ARES CLI - Professional Command Line Interface
Enterprise-grade command-line tool for AI-Augmented QA Engine
Demonstrates professional software engineering for UK/US market
"""

import argparse
import sys
import os
import json
import time
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import asdict

# Import ARES components
try:
    from src.model.advanced_vision_healer import get_advanced_vision_healer
    from src.model.risk_predictor import get_risk_predictor
    from src.model.vision_healer import get_vision_healer
    from src.model.predictor import get_defect_predictor
    from src.utils.metrics_collector import get_metrics_collector
    ARES_AVAILABLE = True
except ImportError:
    ARES_AVAILABLE = False
    print("Warning: ARES components not available. Running in demo mode.")


class ARESCLI:
    """Professional CLI for ARES AI-Augmented QA Engine"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.ares_available = ARES_AVAILABLE
        
        # Initialize ARES components
        if self.ares_available:
            self.vision_healer = get_advanced_vision_healer()
            self.risk_predictor = get_risk_predictor()
            self.metrics_collector = get_metrics_collector()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup professional logging"""
        logger = logging.getLogger('ARES-CLI')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def run_smoke_tests(self, args):
        """Run smoke tests with AI healing"""
        self.logger.info("Running ARES smoke tests with AI healing...")
        
        if not self.ares_available:
            self.logger.error("ARES components not available")
            return False
        
        try:
            # Run smoke tests
            cmd = [
                'python', '-m', 'pytest', 
                'tests/test_login.py::test_basic_login_functionality',
                '-v', '--tb=short'
            ]
            
            if args.headless:
                cmd.extend(['--headless'])
            
            if args.output:
                cmd.extend(['--html', args.output, '--self-contained-html'])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Smoke tests passed successfully")
                print(result.stdout)
                return True
            else:
                self.logger.error("Smoke tests failed")
                print(result.stderr)
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to run smoke tests: {e}")
            return False
    
    def run_vision_tests(self, args):
        """Run vision healing tests"""
        self.logger.info("Running ARES vision healing tests...")
        
        if not self.ares_available:
            self.logger.error("ARES components not available")
            return False
        
        try:
            # Test vision healing capabilities
            performance = self.vision_healer.get_performance_report()
            
            print("=== ARES Vision Healing Performance ===")
            print(f"Total Healings: {performance['total_healings']}")
            print(f"Success Rate: {performance['overall_success_rate']:.2%}")
            print(f"Average Confidence: {performance['average_confidence']:.2f}")
            print(f"MTTR Reduction: {performance['mttr_reduction']:.1%}")
            print(f"Available Templates: {performance['templates_count']}")
            
            print("\n=== Method Success Rates ===")
            for method, rate in performance['method_success_rates'].items():
                print(f"{method}: {rate:.2%}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to run vision tests: {e}")
            return False
    
    def run_risk_analysis(self, args):
        """Run predictive risk analysis"""
        self.logger.info("Running ARES predictive risk analysis...")
        
        if not self.ares_available:
            self.logger.error("ARES components not available")
            return False
        
        try:
            # Get git features
            features = self.risk_predictor.extract_git_features('.', since_days=args.days)
            
            print(f"=== Risk Analysis for Last {args.days} Days ===")
            print(f"Commits Analyzed: {len(features)}")
            
            # Predict risks for modules
            modules = ['authentication', 'payment_processing', 'user_registration', 'api_endpoints']
            if args.modules:
                modules = args.modules
            
            predictions = self.risk_predictor.predict_batch_risks(modules)
            
            print("\n=== Risk Predictions ===")
            high_risk_count = 0
            
            for pred in predictions:
                print(f"{pred.module_name}:")
                print(f"  Risk Level: {pred.risk_level.value}")
                print(f"  Risk Score: {pred.risk_score:.2f}")
                print(f"  Confidence: {pred.confidence:.2f}")
                
                if pred.contributing_factors:
                    print(f"  Top Factors: {pred.contributing_factors[:2]}")
                
                if pred.risk_level.value in ['HIGH', 'CRITICAL']:
                    high_risk_count += 1
                    print(f"  RECOMMENDATIONS: {pred.recommended_actions[:2]}")
                
                print()
            
            print(f"=== Summary ===")
            print(f"High Risk Modules: {high_risk_count}/{len(modules)}")
            
            # Save report
            if args.output:
                report_data = {
                    'timestamp': datetime.now().isoformat(),
                    'days_analyzed': args.days,
                    'commits_analyzed': len(features),
                    'predictions': [asdict(pred) for pred in predictions],
                    'high_risk_count': high_risk_count
                }
                
                with open(args.output, 'w') as f:
                    json.dump(report_data, f, indent=2)
                
                print(f"Report saved to: {args.output}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to run risk analysis: {e}")
            return False
    
    def run_dashboard(self, args):
        """Launch executive dashboard"""
        self.logger.info("Launching ARES Executive Dashboard...")
        
        try:
            cmd = ['streamlit', 'run', 'Dashboard/executive_dashboard.py']
            
            if args.port:
                cmd.extend(['--server.port', str(args.port)])
            
            if args.headless:
                cmd.extend(['--server.headless', 'true'])
            
            print("=== ARES Executive Dashboard ===")
            print(f"Launching on port: {args.port or 8501}")
            print("Dashboard features:")
            print("  - AI Confidence Scores")
            print("  - Vision Healing Statistics")
            print("  - Predictive Analytics")
            print("  - Real-time Metrics")
            print("  - Quality Scoring")
            print()
            print("Press Ctrl+C to stop the dashboard")
            
            subprocess.run(cmd)
            
        except Exception as e:
            self.logger.error(f"Failed to launch dashboard: {e}")
            return False
    
    def run_metrics(self, args):
        """Show metrics and analytics"""
        self.logger.info("Generating ARES metrics report...")
        
        if not self.ares_available:
            self.logger.error("ARES components not available")
            return False
        
        try:
            print("=== ARES Metrics Report ===")
            print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
            # Vision Healing Metrics
            vision_performance = self.vision_healer.get_performance_report()
            print("=== Vision Healing Metrics ===")
            print(f"Total Healings: {vision_performance['total_healings']}")
            print(f"Success Rate: {vision_performance['overall_success_rate']:.2%}")
            print(f"Average Confidence: {vision_performance['average_confidence']:.2f}")
            print(f"MTTR Reduction: {vision_performance['mttr_reduction']:.1%}")
            print()
            
            # Risk Prediction Metrics
            risk_dashboard = self.risk_predictor.get_risk_dashboard_data()
            print("=== Risk Prediction Metrics ===")
            print(f"Model Version: {risk_dashboard['model_version']}")
            print(f"Model Trained: {risk_dashboard['is_trained']}")
            print(f"Training Accuracy: {risk_dashboard['training_accuracy']:.2f}")
            print(f"Feature Count: {risk_dashboard['feature_count']}")
            print(f"Historical Data: {risk_dashboard['historical_data_count']} records")
            print()
            
            # Performance Metrics
            perf_metrics = risk_dashboard['performance_metrics']
            print("=== Performance Metrics ===")
            print(f"Total Predictions: {perf_metrics['total_predictions']}")
            print(f"Model Accuracy: {perf_metrics['model_accuracy']:.2f}")
            print(f"Precision: {perf_metrics['precision']:.2f}")
            print(f"Recall: {perf_metrics['recall']:.2f}")
            print(f"F1 Score: {perf_metrics['f1_score']:.2f}")
            print(f"AUC Score: {perf_metrics['auc_score']:.2f}")
            print()
            
            # Save metrics report
            if args.output:
                metrics_data = {
                    'timestamp': datetime.now().isoformat(),
                    'vision_healing': vision_performance,
                    'risk_prediction': risk_dashboard,
                    'performance': perf_metrics
                }
                
                with open(args.output, 'w') as f:
                    json.dump(metrics_data, f, indent=2)
                
                print(f"Metrics report saved to: {args.output}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to generate metrics: {e}")
            return False
    
    def run_train(self, args):
        """Train AI models"""
        self.logger.info("Training ARES AI models...")
        
        if not self.ares_available:
            self.logger.error("ARES components not available")
            return False
        
        try:
            print("=== Training ARES AI Models ===")
            
            # Train risk prediction model
            print("Training Risk Prediction Model...")
            training_results = self.risk_predictor.train_risk_models(args.data)
            
            if 'error' in training_results:
                print(f"Training failed: {training_results['error']}")
                return False
            
            print(f"Training Results:")
            print(f"  Ensemble Accuracy: {training_results.get('ensemble_accuracy', 0):.2f}")
            print(f"  Training Samples: {training_results.get('training_samples', 0)}")
            print(f"  Test Samples: {training_results.get('test_samples', 0)}")
            print(f"  Feature Count: {training_results.get('feature_count', 0)}")
            
            print("\n=== Model Performance ===")
            for model, results in training_results.get('model_results', {}).items():
                if results.get('trained'):
                    print(f"{model}:")
                    print(f"  Accuracy: {results.get('accuracy', 0):.2f}")
                    print(f"  CV Mean: {results.get('cv_mean', 0):.2f}")
                    print(f"  CV Std: {results.get('cv_std', 0):.2f}")
                    if 'auc' in results:
                        print(f"  AUC: {results['auc']:.2f}")
            
            print("\n=== Training Complete ===")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to train models: {e}")
            return False
    
    def run_status(self, args):
        """Show system status"""
        self.logger.info("Checking ARES system status...")
        
        print("=== ARES System Status ===")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Component Status
        print("=== Component Status ===")
        print(f"ARES CLI: Online")
        print(f"Python Environment: {sys.version.split()[0]}")
        print(f"Working Directory: {os.getcwd()}")
        
        if self.ares_available:
            print(f"Vision Healer: Online")
            print(f"Risk Predictor: Online")
            print(f"Metrics Collector: Online")
        else:
            print(f"ARES Components: Offline")
        
        print()
        
        # File System Status
        print("=== File System Status ===")
        required_dirs = ['src/model', 'tests', 'Dashboard', 'data', 'assets']
        for dir_name in required_dirs:
            if Path(dir_name).exists():
                print(f"{dir_name}: Exists")
            else:
                print(f"{dir_name}: Missing")
        
        print()
        
        # Git Repository Status
        try:
            import git
            repo = git.Repo('.')
            print("=== Git Repository Status ===")
            print(f"Repository: {repo.remotes.origin.url if repo.remotes else 'No remote'}")
            print(f"Branch: {repo.active_branch.name}")
            print(f"Last Commit: {repo.head.commit.message.split()[0]}")
            print(f"Total Commits: {len(list(repo.iter_commits()))}")
        except:
            print("Git Repository: Not available")
        
        print()
        
        # Docker Status (if available)
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("=== Docker Status ===")
                print(f"Docker: {result.stdout.split()[2]}")
                
                # Check for running containers
                result = subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}'], capture_output=True, text=True)
                containers = result.stdout.strip().split('\n')[1:]  # Skip header
                
                if containers and containers[0]:
                    print(f"Running Containers: {len(containers)}")
                    for container in containers[:5]:  # Show first 5
                        print(f"  - {container}")
                else:
                    print("Running Containers: None")
        except:
            print("Docker: Not available")
        
        print()
        print("=== Status Complete ===")
        return True
    
    def run_install(self, args):
        """Install ARES dependencies"""
        self.logger.info("Installing ARES dependencies...")
        
        try:
            print("=== Installing ARES Dependencies ===")
            
            # Install Python dependencies
            print("Installing Python packages...")
            subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True)
            
            # Install Playwright
            print("Installing Playwright browsers...")
            subprocess.run(['playwright', 'install'], check=True)
            subprocess.run(['playwright', 'install-deps'], check=True)
            
            # Create directories
            print("Creating required directories...")
            directories = ['data/models', 'assets/templates', 'reports', 'logs']
            for dir_name in directories:
                Path(dir_name).mkdir(parents=True, exist_ok=True)
                print(f"  Created: {dir_name}")
            
            print("=== Installation Complete ===")
            print("ARES is ready to use!")
            print()
            print("Next steps:")
            print("  1. Run 'ares-cli status' to verify installation")
            print("  2. Run 'ares-cli train' to train AI models")
            print("  3. Run 'ares-cli smoke' to run smoke tests")
            print("  4. Run 'ares-cli dashboard' to launch executive dashboard")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Installation failed: {e}")
            return False


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='ARES CLI - Professional AI-Augmented QA Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ares-cli smoke                    Run smoke tests
  ares-cli vision --headless        Run vision healing tests
  ares-cli risk --days 7            Run risk analysis for last 7 days
  ares-cli dashboard --port 8501    Launch dashboard on port 8501
  ares-cli metrics --output report.json  Generate metrics report
  ares-cli train --data data.csv    Train AI models with custom data
  ares-cli status                   Show system status
  ares-cli install                  Install dependencies
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Smoke tests command
    smoke_parser = subparsers.add_parser('smoke', help='Run smoke tests with AI healing')
    smoke_parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    smoke_parser.add_argument('--output', help='Output HTML report file')
    
    # Vision tests command
    vision_parser = subparsers.add_parser('vision', help='Run vision healing tests')
    vision_parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    
    # Risk analysis command
    risk_parser = subparsers.add_parser('risk', help='Run predictive risk analysis')
    risk_parser.add_argument('--days', type=int, default=7, help='Days to analyze (default: 7)')
    risk_parser.add_argument('--modules', nargs='+', help='Specific modules to analyze')
    risk_parser.add_argument('--output', help='Output JSON report file')
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Launch executive dashboard')
    dashboard_parser.add_argument('--port', type=int, default=8501, help='Port number (default: 8501)')
    dashboard_parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    
    # Metrics command
    metrics_parser = subparsers.add_parser('metrics', help='Show metrics and analytics')
    metrics_parser.add_argument('--output', help='Output JSON report file')
    
    # Train command
    train_parser = subparsers.add_parser('train', help='Train AI models')
    train_parser.add_argument('--data', help='Custom training data file')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install dependencies')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CLI
    cli = ARESCLI()
    
    # Execute command
    if args.command == 'smoke':
        success = cli.run_smoke_tests(args)
    elif args.command == 'vision':
        success = cli.run_vision_tests(args)
    elif args.command == 'risk':
        success = cli.run_risk_analysis(args)
    elif args.command == 'dashboard':
        success = cli.run_dashboard(args)
    elif args.command == 'metrics':
        success = cli.run_metrics(args)
    elif args.command == 'train':
        success = cli.run_train(args)
    elif args.command == 'status':
        success = cli.run_status(args)
    elif args.command == 'install':
        success = cli.run_install(args)
    else:
        parser.print_help()
        return
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
