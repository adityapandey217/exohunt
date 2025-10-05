#!/usr/bin/env python3
"""
Frontend-Backend Integration Test
Tests all API endpoints used by the React frontend
"""

import requests
import json
import os
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000"
API_BASE = f"{BACKEND_URL}/api"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, passed, details=""):
    """Print test result with color"""
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"{status} | {name}")
    if details:
        print(f"       {details}")

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/dashboard/stats/", timeout=5)
        return response.status_code in [200, 404]  # 404 is ok if no data yet
    except requests.exceptions.ConnectionError:
        return False
    except Exception:
        return False

def test_dashboard_stats():
    """Test dashboard stats endpoint"""
    try:
        response = requests.get(f"{API_BASE}/dashboard/stats/")
        data = response.json()
        required_fields = ['total_predictions', 'confirmed_count', 'candidate_count', 'false_positive_count']
        has_fields = all(field in data for field in required_fields)
        print_test("Dashboard Stats API", response.status_code == 200 and has_fields, 
                  f"Total predictions: {data.get('total_predictions', 0)}")
        return response.status_code == 200 and has_fields
    except Exception as e:
        print_test("Dashboard Stats API", False, str(e))
        return False

def test_recent_predictions():
    """Test recent predictions endpoint"""
    try:
        response = requests.get(f"{API_BASE}/dashboard/recent-predictions/?limit=5")
        data = response.json()
        print_test("Recent Predictions API", response.status_code == 200,
                  f"Retrieved {len(data)} predictions")
        return response.status_code == 200
    except Exception as e:
        print_test("Recent Predictions API", False, str(e))
        return False

def test_predict_single():
    """Test single prediction endpoint with a FITS file"""
    # Find a test FITS file
    lightcurves_dir = Path(__file__).parent / 'lightcurves'
    fits_files = list(lightcurves_dir.glob('*.fits'))
    
    if not fits_files:
        print_test("Single Prediction API", False, "No FITS files found in lightcurves/")
        return False
    
    test_file = fits_files[0]
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'application/fits')}
            data = {
                'koi_period': '3.52',
                'koi_depth': '1234.5',
            }
            response = requests.post(f"{API_BASE}/predict/single/", files=files, data=data)
        
        if response.status_code == 201:
            result = response.json()
            disposition = result.get('predicted_disposition', 'Unknown')
            confidence = result.get('confidence', 0) * 100
            print_test("Single Prediction API", True,
                      f"Predicted: {disposition} ({confidence:.1f}% confidence)")
            return True
        else:
            print_test("Single Prediction API", False, 
                      f"Status {response.status_code}: {response.text[:100]}")
            return False
    except Exception as e:
        print_test("Single Prediction API", False, str(e))
        return False

def test_cors_headers():
    """Test CORS headers for frontend"""
    try:
        response = requests.options(f"{API_BASE}/dashboard/stats/", 
                                   headers={'Origin': 'http://localhost:5173'})
        has_cors = 'access-control-allow-origin' in response.headers
        print_test("CORS Headers", has_cors,
                  f"Origin allowed: {response.headers.get('access-control-allow-origin', 'None')}")
        return has_cors
    except Exception as e:
        print_test("CORS Headers", False, str(e))
        return False

def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}ExoHunt Frontend-Backend Integration Test{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    # Test 1: Backend health
    backend_up = test_backend_health()
    if not backend_up:
        print_test("Backend Health", False, "Django server not running on port 8000")
        print(f"\n{Colors.RED}ERROR: Backend is not running!{Colors.END}")
        print(f"Start it with: {Colors.YELLOW}cd exodetect && python manage.py runserver{Colors.END}\n")
        return
    else:
        print_test("Backend Health", True, "Django server is running")
    
    print()
    
    # Test 2: Dashboard stats
    test_dashboard_stats()
    
    # Test 3: Recent predictions
    test_recent_predictions()
    
    # Test 4: Single prediction (full workflow)
    print()
    print(f"{Colors.BLUE}Testing full prediction workflow...{Colors.END}")
    test_predict_single()
    
    # Test 5: CORS
    print()
    test_cors_headers()
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}Integration tests complete!{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    print("Next steps:")
    print(f"1. Start frontend: {Colors.YELLOW}cd frontend && npm run dev{Colors.END}")
    print(f"2. Open browser: {Colors.YELLOW}http://localhost:5173{Colors.END}")
    print(f"3. Navigate to Analyze page and upload a FITS file")
    print()

if __name__ == "__main__":
    main()
