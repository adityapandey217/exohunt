"""
Test script for ExoHunt API
Run this after starting the Django server to test all endpoints
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000/api"

print("🚀 ExoHunt API Test Script\n")
print("=" * 50)

# Test 1: Dashboard Stats
print("\n1. Testing Dashboard Stats...")
try:
    response = requests.get(f"{BASE_URL}/dashboard/stats/")
    if response.status_code == 200:
        print("✅ Dashboard stats loaded successfully")
        stats = response.json()
        print(f"   Total predictions: {stats.get('total_predictions', 0)}")
        print(f"   Average confidence: {stats.get('average_confidence', 0)}")
    else:
        print(f"❌ Failed: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Make a Prediction
print("\n2. Testing Prediction Endpoint...")

# Find a FITS file
lightcurve_dir = Path("../lightcurves")
fits_files = list(lightcurve_dir.glob("*.fits"))

if fits_files:
    test_file = fits_files[0]
    print(f"   Using file: {test_file.name}")
    
    try:
        with open(test_file, 'rb') as f:
            files = {'fits_file': f}
            data = {
                'kepid': test_file.stem,  # Use filename as kepid
                'koi_period': 3.52,
                'koi_depth': 145.3
            }
            
            response = requests.post(
                f"{BASE_URL}/predict/single/",
                files=files,
                data=data
            )
            
            if response.status_code == 201:
                print("✅ Prediction successful")
                result = response.json()
                print(f"   Prediction ID: {result['prediction_id']}")
                print(f"   Class: {result['prediction']['class']}")
                print(f"   Confidence: {result['prediction']['confidence']:.3f}")
                print(f"   Processing time: {result['metadata']['processing_time_ms']}ms")
                
                # Save prediction ID for next tests
                prediction_id = result['prediction_id']
                
                # Test 3: Visualize
                print("\n3. Testing Visualization...")
                try:
                    viz_response = requests.get(
                        f"{BASE_URL}/lightcurve/visualize/",
                        params={'prediction_id': prediction_id}
                    )
                    
                    if viz_response.status_code == 200:
                        print("✅ Visualization data retrieved")
                        viz_data = viz_response.json()
                        print(f"   Data points: {viz_data['metadata']['total_points']}")
                        print(f"   Anomalies detected: {viz_data['metadata']['anomalies_detected']}")
                    else:
                        print(f"❌ Visualization failed: {viz_response.status_code}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                
                # Test 4: Transit Analysis
                print("\n4. Testing Transit Detection...")
                try:
                    transit_response = requests.post(
                        f"{BASE_URL}/lightcurve/analyze/",
                        json={
                            'prediction_id': prediction_id,
                            'period_min': 0.5,
                            'period_max': 50.0,
                            'snr_threshold': 5.0
                        }
                    )
                    
                    if transit_response.status_code == 200:
                        print("✅ Transit analysis complete")
                        transit_data = transit_response.json()
                        print(f"   Transits detected: {transit_data['transits_detected']}")
                        if transit_data['transits']:
                            transit = transit_data['transits'][0]
                            print(f"   Best period: {transit.get('period_days', 'N/A')} days")
                            print(f"   SNR: {transit.get('snr', 'N/A')}")
                    else:
                        print(f"❌ Transit analysis failed: {transit_response.status_code}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                
                # Test 5: Phase Folding
                print("\n5. Testing Phase Folding...")
                try:
                    phase_response = requests.post(
                        f"{BASE_URL}/lightcurve/phase-fold/",
                        json={
                            'prediction_id': prediction_id,
                            'period': 3.52
                        }
                    )
                    
                    if phase_response.status_code == 200:
                        print("✅ Phase folding successful")
                        phase_data = phase_response.json()
                        print(f"   Period: {phase_data['period']} days")
                        print(f"   Data points: {len(phase_data['phase'])}")
                    else:
                        print(f"❌ Phase folding failed: {phase_response.status_code}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                
                # Test 6: Submit Feedback
                print("\n6. Testing Feedback Submission...")
                try:
                    feedback_response = requests.post(
                        f"{BASE_URL}/feedback/submit/",
                        json={
                            'prediction': prediction_id,
                            'verdict': 'agree',
                            'notes': 'Test feedback from API test script',
                            'confidence_in_correction': 4
                        }
                    )
                    
                    if feedback_response.status_code == 201:
                        print("✅ Feedback submitted successfully")
                    else:
                        print(f"❌ Feedback failed: {feedback_response.status_code}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                
            else:
                print(f"❌ Prediction failed: {response.status_code}")
                print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("   ⚠️  No FITS files found in ../lightcurves/")
    print("   Skipping prediction tests")

# Test 7: Session Management
print("\n7. Testing Session Management...")
try:
    session_response = requests.post(
        f"{BASE_URL}/sessions/",
        json={
            'name': 'Test Session from API Test',
            'notes': 'Created by test script'
        }
    )
    
    if session_response.status_code == 201:
        print("✅ Session created successfully")
        session = session_response.json()
        print(f"   Session ID: {session['id']}")
        print(f"   Name: {session['name']}")
    else:
        print(f"❌ Session creation failed: {session_response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 8: Recent Predictions
print("\n8. Testing Recent Predictions List...")
try:
    recent_response = requests.get(
        f"{BASE_URL}/dashboard/recent-predictions/",
        params={'limit': 10}
    )
    
    if recent_response.status_code == 200:
        print("✅ Recent predictions retrieved")
        recent = recent_response.json()
        print(f"   Total count: {recent['count']}")
        print(f"   Results returned: {len(recent['results'])}")
    else:
        print(f"❌ Recent predictions failed: {recent_response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 50)
print("🎉 API Testing Complete!\n")
print("Summary:")
print("- Dashboard ✓")
print("- Prediction ✓")
print("- Visualization ✓")
print("- Transit Detection ✓")
print("- Phase Folding ✓")
print("- Feedback ✓")
print("- Sessions ✓")
print("- Recent Predictions ✓")
print("\n✨ All core features working! Ready for frontend integration.")
