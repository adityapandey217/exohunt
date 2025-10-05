"""
Django REST Framework views for ExoHunt API
Comprehensive endpoints for prediction, visualization, and analysis
"""
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models import Count, Avg, Q
from django.utils import timezone

import os
import uuid
import tempfile
from pathlib import Path
from typing import Dict, List
import pandas as pd
import lightkurve as lk
from astropy.io import fits as astropy_fits
import requests

from .cache_utils import get_cached_fits, save_to_cache


def fast_download_lightcurve(kepid: int) -> str:
    """
    Fast light curve download with caching and local file support.
    Priority: local example_lightcurves > local lightcurves > cache > lightkurve download
    
    Args:
        kepid: Kepler ID
        
    Returns:
        Path to FITS file
    """
    # Check example_lightcurves directory first (for curated examples, deployment-ready)
    example_lightcurves_dir = os.path.join(settings.BASE_DIR, 'example_lightcurves')
    local_fits = os.path.join(example_lightcurves_dir, f'{kepid}.fits')
    if os.path.exists(local_fits):
        print(f"✅ Using example FITS file for KepID {kepid}")
        return local_fits
    
    # Check parent lightcurves directory (for development)
    lightcurves_dir = os.path.join(settings.BASE_DIR, '..', 'lightcurves')
    local_fits = os.path.join(lightcurves_dir, f'{kepid}.fits')
    if os.path.exists(local_fits):
        print(f"✅ Using local FITS file for KepID {kepid}")
        return local_fits
    
    # Check cache second
    cached_path = get_cached_fits(kepid)
    if cached_path and os.path.exists(cached_path):
        print(f"✅ Using cached FITS for KepID {kepid}")
        return cached_path
    
    print(f"⬇️ Downloading FITS for KepID {kepid}...")
    
    # Use lightkurve but with quick download
    try:
        # Quick search with minimal timeout
        search_result = lk.search_lightcurve(f'KIC {kepid}', mission='Kepler')
        
        if len(search_result) == 0:
            raise ValueError(f'No light curves found for KepID {kepid}')
        
        # Download ONLY first quarter (fast!)
        lc = search_result[0].download()
        
        # Save to cache
        temp_path = os.path.join(tempfile.gettempdir(), f"lc_{kepid}_{uuid.uuid4()}.fits")
        lc.to_fits(temp_path, overwrite=True)
        
        # Copy to cache for future use
        cached_path = save_to_cache(kepid, temp_path)
        
        print(f"✅ Downloaded and cached KepID {kepid}")
        return cached_path
        
    except Exception as e:
        raise Exception(f"Failed to download light curve for KepID {kepid}: {str(e)}")





from .models import (
    LightCurveFile, KOIParameters, Prediction, ExplainabilityData,
    UserFeedback, TransitDetection, AnalysisSession, BatchJob, ModelMetrics
)
from .serializers import (
    LightCurveFileSerializer, KOIParametersSerializer, PredictionSerializer,
    ExplainabilityDataSerializer, UserFeedbackSerializer, TransitDetectionSerializer,
    AnalysisSessionSerializer, BatchJobSerializer, ModelMetricsSerializer,
    PredictionRequestSerializer, VisualizationRequestSerializer,
    PhaseFoldRequestSerializer, TransitSearchRequestSerializer
)
from .inference import ExoplanetPredictor, extract_light_curve_metadata
from .visualization import (
    create_interactive_plot, detect_transits, phase_fold_light_curve,
    calculate_periodogram, detect_anomalies, compare_light_curves
)


# Initialize global predictor (loaded once)
PREDICTOR = None

def get_predictor():
    """Lazy load the predictor"""
    global PREDICTOR
    if PREDICTOR is None:
        model_path = os.path.join(settings.BASE_DIR, '..', 'training', 'exoplanet_hybrid.pth')
        scaler_path = os.path.join(settings.BASE_DIR, '..', 'training', 'koi_scaler.joblib')
        features_path = os.path.join(settings.BASE_DIR, '..', 'training', 'tab_features_list.joblib')
        cache_dir = os.path.join(settings.BASE_DIR, '..', 'training', 'lc_cache_npy')
        
        PREDICTOR = ExoplanetPredictor(
            model_path=model_path,
            scaler_path=scaler_path,
            features_path=features_path,
            seq_len=2000
        )
    return PREDICTOR


# ============================================================================
# PREDICTION ENDPOINTS
# ============================================================================

@api_view(['POST'])
def predict_single(request):
    """
    POST /api/predict/single/
    
    Upload a FITS file OR provide a KepID to get exoplanet classification prediction.
    Optionally include KOI parameters for better accuracy.
    """
    serializer = PredictionRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    temp_path = None  # Initialize temp_path
    
    # Determine if using uploaded file or download via lightkurve
    if data.get('fits_file'):
        fits_file = data['fits_file']
        use_lightkurve = False
        kepid_param = data.get('kepid')
    elif data.get('kepid'):
        # Download FITS via fast cached method
        kepid_param = data['kepid']
        use_lightkurve = True
        
        try:
            fits_path_to_use = fast_download_lightcurve(kepid_param)
            
            print(f"Successfully downloaded and saved light curve for KepID {kepid_param}")
            
        except Exception as e:
            return Response(
                {'error': f'Failed to download light curve via lightkurve: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        return Response(
            {'error': 'Either fits_file or kepid must be provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Save uploaded file temporarily (if uploaded)
    if not use_lightkurve:
        temp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.fits")
        with open(temp_path, 'wb+') as destination:
            for chunk in fits_file.chunks():
                destination.write(chunk)
        fits_path_to_use = temp_path
    
    try:
        # Extract metadata
        metadata = extract_light_curve_metadata(fits_path_to_use)
        
        # Ensure all required fields have default values
        kepid = kepid_param or metadata.get('kepid')
        flux_points = metadata.get('flux_points') or 0
        duration_days = metadata.get('duration_days')
        data_quality_score = metadata.get('data_quality_score') or 0.0
        gaps_detected = metadata.get('gaps_detected') or 0
        flux_type = metadata.get('flux_type') or 'PDCSAP_FLUX'
        
        # Save to database
        if use_lightkurve:
            # For lightkurve downloads, create a reference but don't duplicate
            lc_file = LightCurveFile.objects.create(
                file=None,  # Don't duplicate file
                kepid=kepid,
                flux_points=flux_points,
                duration_days=duration_days,
                data_quality_score=data_quality_score,
                gaps_detected=gaps_detected,
                flux_type=flux_type,
                uploaded_by=request.user if request.user.is_authenticated else None
            )
        else:
            lc_file = LightCurveFile.objects.create(
                file=fits_file,
                kepid=kepid,
                flux_points=flux_points,
                duration_days=duration_days,
                data_quality_score=data_quality_score,
                gaps_detected=gaps_detected,
                flux_type=flux_type,
                uploaded_by=request.user if request.user.is_authenticated else None
            )
        
        # Prepare KOI parameters
        koi_params = {}
        koi_feature_fields = [
            'koi_period', 'koi_duration', 'koi_depth', 'koi_prad', 'koi_ror',
            'koi_model_snr', 'koi_num_transits', 'koi_steff', 'koi_slogg',
            'koi_srad', 'koi_smass', 'koi_kepmag', 'koi_insol', 'koi_dor',
            'koi_count'
            # 'koi_score' REMOVED - data leakage (0.89 correlation with label)
        ]
        for field in koi_feature_fields:
            if field in data and data[field] is not None:
                koi_params[field] = data[field]
        
        # Get predictor and make prediction
        predictor = get_predictor()
        cache_dir = os.path.join(settings.BASE_DIR, '..', 'training', 'lc_cache_npy')
        
        result = predictor.predict(
            fits_path_to_use,
            koi_params=koi_params,
            cache_dir=cache_dir
        )
        
        # Get or create session
        session = None
        if data.get('session_id'):
            session = AnalysisSession.objects.filter(id=data['session_id']).first()
        
        # Save prediction
        prediction = Prediction.objects.create(
            light_curve=lc_file,
            session=session,
            predicted_class=result['predicted_class'],
            predicted_class_name=result['predicted_class_name'],
            prob_false_positive=result['probabilities']['FALSE_POSITIVE'],
            prob_candidate=result['probabilities']['CANDIDATE'],
            prob_confirmed=result['probabilities']['CONFIRMED'],
            confidence=result['confidence'],
            model_version=result['model_version'],
            processing_time_ms=result['processing_time_ms']
        )
        
        # Build response
        response_data = {
            'prediction_id': str(prediction.id),
            'kepid': lc_file.kepid,
            'prediction': {
                'class': result['predicted_class_name'],
                'probabilities': result['probabilities'],
                'confidence': result['confidence']
            },
            'metadata': {
                'processing_time_ms': result['processing_time_ms'],
                'model_version': result['model_version'],
                'timestamp': prediction.created_at.isoformat()
            },
            'light_curve': {
                'points': lc_file.flux_points,
                'duration_days': lc_file.duration_days,
                'gaps_detected': lc_file.gaps_detected,
                'quality_score': lc_file.data_quality_score
            },
            'features_used': koi_params,
            'links': {
                'visualize': f'/api/lightcurve/visualize/?prediction_id={prediction.id}',
                'explain': f'/api/explain/feature-importance/?prediction_id={prediction.id}',
                'feedback': f'/api/feedback/submit/?prediction_id={prediction.id}'
            }
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        import traceback
        return Response(
            {'error': f'Prediction error: {str(e)}', 'traceback': traceback.format_exc()},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    finally:
        # Clean up temporary file only if we created one
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# ============================================================================
# VISUALIZATION ENDPOINTS
# ============================================================================

@api_view(['GET', 'POST'])
def visualize_lightcurve(request):
    """
    GET/POST /api/lightcurve/visualize/
    
    Get interactive light curve visualization data.
    Provide either prediction_id, kepid, or upload FITS file.
    Uses lightkurve to download from MAST when needed.
    """
    temp_path = None
    
    if request.method == 'GET':
        # GET method with prediction_id or kepid query param
        prediction_id = request.query_params.get('prediction_id')
        kepid_param = request.query_params.get('kepid')
        
        if prediction_id:
            try:
                prediction = Prediction.objects.get(id=prediction_id)
                if prediction.light_curve.file:
                    fits_path = prediction.light_curve.file.path
                    title = f"KepID {prediction.light_curve.kepid} - {prediction.predicted_class_name}"
                else:
                    # Download using lightkurve
                    kepid_param = prediction.light_curve.kepid
                    title = f"KepID {kepid_param} - {prediction.predicted_class_name}"
            except Prediction.DoesNotExist:
                return Response(
                    {'error': 'Prediction not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        elif kepid_param:
            title = f"KepID {kepid_param}"
        else:
            return Response(
                {'error': 'prediction_id or kepid parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If kepid_param is set, download via fast cached method
        if kepid_param:
            try:
                fits_path = fast_download_lightcurve(kepid_param)
                
            except Exception as e:
                return Response(
                    {'error': f'Failed to download light curve: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
    
    else:  # POST
        # Check if kepid or fits_file provided
        kepid_param = request.data.get('kepid')
        fits_file = request.data.get('fits_file')
        prediction_id = request.data.get('prediction_id')
        
        if prediction_id:
            try:
                prediction = Prediction.objects.get(id=prediction_id)
                if prediction.light_curve.file:
                    fits_path = prediction.light_curve.file.path
                else:
                    kepid_param = prediction.light_curve.kepid
                title = f"KepID {prediction.light_curve.kepid}"
            except Prediction.DoesNotExist:
                return Response(
                    {'error': 'Prediction not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Download via fast cached method if kepid provided
        if kepid_param:
            try:
                fits_path = fast_download_lightcurve(kepid_param)
                title = f"KepID {kepid_param}"
                
            except Exception as e:
                return Response(
                    {'error': f'Failed to download light curve: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        elif fits_file:
            # Save uploaded temp file
            temp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.fits")
            with open(temp_path, 'wb+') as destination:
                for chunk in fits_file.chunks():
                    destination.write(chunk)
            fits_path = temp_path
            title = "Uploaded Light Curve"
        else:
            return Response(
                {'error': 'Either prediction_id, kepid, or fits_file must be provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    try:
        import numpy as np
        import base64
        from .flux_utils import get_flux_from_lc, get_time_from_lc
        
        # Load light curve to extract metadata
        lc = lk.read(fits_path)
        
        time = get_time_from_lc(lc)
        flux = get_flux_from_lc(lc)
        
        # Remove NaNs
        valid_mask = ~np.isnan(flux)
        time_clean = time[valid_mask]
        flux_clean = flux[valid_mask]
        
        # Create visualization PNG
        plot_img_bytes = create_interactive_plot(fits_path, title=title)
        
        # Convert to base64 for JSON response
        plot_img_base64 = base64.b64encode(plot_img_bytes).decode('utf-8')
        
        # Extract metadata
        duration = float(time_clean.max() - time_clean.min()) if len(time_clean) > 0 else 0
        
        response_data = {
            'plot_image': f'data:image/png;base64,{plot_img_base64}',
            'metadata': {
                'flux_points': len(time_clean),
                'duration_days': duration,
                'flux_mean': float(np.mean(flux_clean)),
                'flux_std': float(np.std(flux_clean)),
                'flux_median': float(np.median(flux_clean)),
                'data_quality_score': float(1.0 - (np.sum(~valid_mask) / len(flux))),
                'gaps_detected': int(np.sum(np.diff(time_clean) > np.median(np.diff(time_clean)) * 3)),
                'flux_type': 'PDCSAP' if hasattr(lc, 'pdcsap_flux') or 'pdcsap_flux' in [c.lower() for c in lc.colnames] else 'SAP'
            }
        }
        
        # Add kepid if available
        if kepid_param:
            response_data['kepid'] = int(kepid_param)
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        import traceback
        return Response(
            {'error': f'Visualization error: {str(e)}', 'traceback': traceback.format_exc()},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@api_view(['POST'])
def phase_fold(request):
    """
    POST /api/lightcurve/phase-fold/
    
    Phase-fold a light curve by a given period.
    """
    serializer = PhaseFoldRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    period = data['period']
    epoch = data.get('epoch')
    
    # Get FITS file
    if data.get('prediction_id'):
        try:
            prediction = Prediction.objects.get(id=data['prediction_id'])
            fits_path = prediction.light_curve.file.path
        except Prediction.DoesNotExist:
            return Response(
                {'error': 'Prediction not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        fits_file = data['fits_file']
        temp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.fits")
        with open(temp_path, 'wb+') as destination:
            for chunk in fits_file.chunks():
                destination.write(chunk)
        fits_path = temp_path
    
    try:
        folded_data = phase_fold_light_curve(fits_path, period, epoch)
        return Response(folded_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    finally:
        if not data.get('prediction_id') and os.path.exists(temp_path):
            os.remove(temp_path)


@api_view(['POST'])
def analyze_transits(request):
    """
    POST /api/lightcurve/analyze/
    
    Detect and analyze transits in light curve.
    """
    serializer = TransitSearchRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    # Get FITS file
    if data.get('prediction_id'):
        try:
            prediction = Prediction.objects.get(id=data['prediction_id'])
            fits_path = prediction.light_curve.file.path
            lc_file = prediction.light_curve
        except Prediction.DoesNotExist:
            return Response(
                {'error': 'Prediction not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        fits_file = data['fits_file']
        temp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.fits")
        with open(temp_path, 'wb+') as destination:
            for chunk in fits_file.chunks():
                destination.write(chunk)
        fits_path = temp_path
        lc_file = None
    
    try:
        transits = detect_transits(
            fits_path,
            period_min=data.get('period_min', 0.5),
            period_max=data.get('period_max', 50.0),
            snr_threshold=data.get('snr_threshold', 7.0)
        )
        
        # Save to database if we have a light curve file
        if lc_file and transits:
            for transit in transits:
                TransitDetection.objects.create(
                    light_curve=lc_file,
                    start_time=0,  # Would need to calculate from period
                    end_time=0,
                    duration_hours=transit.get('duration_hours', 0),
                    depth_ppm=transit.get('depth_ppm', 0),
                    snr=transit['snr'],
                    period_days=transit.get('period_days'),
                    period_confidence=transit.get('period_confidence'),
                    is_anomaly=transit.get('is_anomaly', False),
                    detection_algorithm=transit.get('detection_algorithm', 'BLS')
                )
        
        # Also calculate periodogram
        periodogram = calculate_periodogram(fits_path)
        
        response_data = {
            'transits_detected': len(transits),
            'transits': transits,
            'periodogram': periodogram
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    finally:
        if not data.get('prediction_id') and os.path.exists(temp_path):
            os.remove(temp_path)


# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@api_view(['GET'])
def dashboard_stats(request):
    """
    GET /api/dashboard/stats/
    
    Get overall dashboard statistics.
    """
    total_predictions = Prediction.objects.count()
    
    # Class distribution
    class_counts = Prediction.objects.values('predicted_class_name').annotate(
        count=Count('id')
    )
    
    # Recent activity (last 7 days)
    from datetime import timedelta
    week_ago = timezone.now() - timedelta(days=7)
    recent_predictions = Prediction.objects.filter(created_at__gte=week_ago).count()
    
    # Average confidence
    avg_confidence = Prediction.objects.aggregate(Avg('confidence'))['confidence__avg']
    
    # Latest model metrics
    latest_metrics = ModelMetrics.objects.first()
    
    stats = {
        'total_predictions': total_predictions,
        'recent_predictions_7d': recent_predictions,
        'average_confidence': round(avg_confidence, 3) if avg_confidence else 0,
        'class_distribution': {item['predicted_class_name']: item['count'] for item in class_counts},
        'model_performance': {
            'accuracy': latest_metrics.accuracy if latest_metrics else None,
            'f1_score': latest_metrics.f1_score_weighted if latest_metrics else None,
            'version': latest_metrics.model_version if latest_metrics else None
        } if latest_metrics else None
    }
    
    return Response(stats, status=status.HTTP_200_OK)


@api_view(['GET'])
def recent_predictions(request):
    """
    GET /api/dashboard/recent-predictions/
    
    Get recent predictions with pagination.
    """
    limit = int(request.query_params.get('limit', 50))
    offset = int(request.query_params.get('offset', 0))
    
    predictions = Prediction.objects.all().order_by('-created_at')[offset:offset+limit]
    serializer = PredictionSerializer(predictions, many=True)
    
    return Response({
        'count': Prediction.objects.count(),
        'results': serializer.data
    }, status=status.HTTP_200_OK)


# ============================================================================
# FEEDBACK ENDPOINTS
# ============================================================================

@api_view(['POST'])
def submit_feedback(request):
    """
    POST /api/feedback/submit/
    
    Submit user feedback on a prediction.
    """
    serializer = UserFeedbackSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    feedback = serializer.save(
        user=request.user if request.user.is_authenticated else None
    )
    
    return Response(
        UserFeedbackSerializer(feedback).data,
        status=status.HTTP_201_CREATED
    )


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

class AnalysisSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing analysis sessions"""
    queryset = AnalysisSession.objects.all()
    serializer_class = AnalysisSessionSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user if self.request.user.is_authenticated else None)
    
    @action(detail=True, methods=['get'])
    def predictions(self, request, pk=None):
        """Get all predictions in this session"""
        session = self.get_object()
        predictions = session.predictions.all()
        serializer = PredictionSerializer(predictions, many=True)
        return Response(serializer.data)


# ============================================================================
# HELPER ENDPOINTS - KepID Search & Examples
# ============================================================================

@api_view(['GET'])
def search_by_kepid(request):
    """
    GET /api/search-kepid/?kepid=10797460
    
    Search for KOI parameters by KepID.
    Returns KOI parameters. FITS file will be downloaded via lightkurve when needed.
    """
    kepid = request.query_params.get('kepid')
    if not kepid:
        return Response(
            {'error': 'kepid parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        kepid = int(kepid)
    except ValueError:
        return Response(
            {'error': 'kepid must be an integer'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Load KOI data
    koi_csv_path = os.path.join(settings.BASE_DIR, '..', 'dataset', 'koi.csv')
    if not os.path.exists(koi_csv_path):
        return Response(
            {'error': 'KOI dataset not found'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    try:
        df = pd.read_csv(koi_csv_path)
        koi_data = df[df['kepid'] == kepid]
        
        if koi_data.empty:
            return Response(
                {'error': f'No KOI data found for KepID {kepid}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get first matching row
        row = koi_data.iloc[0]
        
        # Helper function to safely get string values (handle NaN)
        def safe_str(value):
            if pd.isna(value):
                return None
            return str(value) if value != '' else None
        
        # Extract parameters
        params = {
            'kepid': int(kepid),
            'koi_period': float(row['koi_period']) if pd.notna(row.get('koi_period')) else None,
            'koi_duration': float(row['koi_duration']) if pd.notna(row.get('koi_duration')) else None,
            'koi_depth': float(row['koi_depth']) if pd.notna(row.get('koi_depth')) else None,
            'koi_prad': float(row['koi_prad']) if pd.notna(row.get('koi_prad')) else None,
            'koi_ror': float(row['koi_ror']) if pd.notna(row.get('koi_ror')) else None,
            'koi_model_snr': float(row['koi_model_snr']) if pd.notna(row.get('koi_model_snr')) else None,
            'koi_num_transits': int(row['koi_num_transits']) if pd.notna(row.get('koi_num_transits')) else None,
            'koi_steff': float(row['koi_steff']) if pd.notna(row.get('koi_steff')) else None,
            'koi_slogg': float(row['koi_slogg']) if pd.notna(row.get('koi_slogg')) else None,
            'koi_srad': float(row['koi_srad']) if pd.notna(row.get('koi_srad')) else None,
            'koi_smass': float(row['koi_smass']) if pd.notna(row.get('koi_smass')) else None,
            'koi_kepmag': float(row['koi_kepmag']) if pd.notna(row.get('koi_kepmag')) else None,
            'koi_insol': float(row['koi_insol']) if pd.notna(row.get('koi_insol')) else None,
            'koi_dor': float(row['koi_dor']) if pd.notna(row.get('koi_dor')) else None,
            'koi_count': int(row['koi_count']) if pd.notna(row.get('koi_count')) else None,
            # 'koi_score' REMOVED - data leakage (0.89 correlation with label)
            'koi_disposition': safe_str(row.get('koi_disposition')),
            'kepler_name': safe_str(row.get('kepler_name')),
        }
        
        return Response({
            'success': True,
            'kepid': kepid,
            'parameters': params,
            'fits_source': 'lightkurve',  # Will be downloaded via lightkurve
            'message': f'Found data for KepID {kepid}. FITS file will be downloaded from MAST archive.'
        })
    
    except Exception as e:
        return Response(
            {'error': f'Error searching KOI data: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Curated list of examples with local FITS files
# Mix of CONFIRMED, CANDIDATE, and FALSE POSITIVE for hackathon demos
EXAMPLE_KEPIDS = [
    10797460,  # CONFIRMED - Kepler-444 (period ~9.48 days)
    10854555,  # CONFIRMED (period ~2.52 days)
    10872983,  # CONFIRMED (period ~11.09 days)
    10811496,  # CANDIDATE (period ~19.89 days)
    11818800,  # CANDIDATE (period ~40.41 days)
    11918099,  # CANDIDATE (period ~7.24 days)
    10848459,  # FALSE POSITIVE (period ~1.73 days)
    6721123,   # FALSE POSITIVE (period ~7.36 days)
    10419211,  # FALSE POSITIVE (period ~11.52 days)
]


@api_view(['GET'])
def get_example_data(request):
    """
    GET /api/get-example/
    
    Get a random example from curated list with local FITS files.
    Uses pre-selected KepIDs with good mix of classifications for instant loading.
    """
    import random
    
    koi_csv_path = os.path.join(settings.BASE_DIR, '..', 'dataset', 'koi.csv')
    # First check exodetect/example_lightcurves (for deployment), then fallback to parent lightcurves
    example_lightcurves_dir = os.path.join(settings.BASE_DIR, 'example_lightcurves')
    lightcurves_dir = os.path.join(settings.BASE_DIR, '..', 'lightcurves')
    
    if not os.path.exists(koi_csv_path):
        return Response(
            {'error': 'KOI dataset not found'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    try:
        # Randomly select from curated examples
        kepid = random.choice(EXAMPLE_KEPIDS)
        
        # Check if local FITS file exists (prioritize example_lightcurves for deployment)
        local_fits = os.path.join(example_lightcurves_dir, f'{kepid}.fits')
        if not os.path.exists(local_fits):
            # Fallback to parent lightcurves directory
            local_fits = os.path.join(lightcurves_dir, f'{kepid}.fits')
        fits_available = os.path.exists(local_fits)
        
        # Load parameters from koi.csv
        df = pd.read_csv(koi_csv_path)
        example = df[df['kepid'] == kepid]
        
        if example.empty:
            return Response(
                {'error': f'KepID {kepid} not found in dataset'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        example = example.iloc[0]
        
        # Helper function to safely get string values (handle NaN)
        def safe_str(value):
            if pd.isna(value):
                return None
            return str(value) if value != '' else None
        
        params = {
            'kepid': kepid,
            'koi_period': float(example['koi_period']) if pd.notna(example.get('koi_period')) else None,
            'koi_duration': float(example['koi_duration']) if pd.notna(example.get('koi_duration')) else None,
            'koi_depth': float(example['koi_depth']) if pd.notna(example.get('koi_depth')) else None,
            'koi_prad': float(example['koi_prad']) if pd.notna(example.get('koi_prad')) else None,
            'koi_ror': float(example['koi_ror']) if pd.notna(example.get('koi_ror')) else None,
            'koi_model_snr': float(example['koi_model_snr']) if pd.notna(example.get('koi_model_snr')) else None,
            'koi_num_transits': int(example['koi_num_transits']) if pd.notna(example.get('koi_num_transits')) else None,
            'koi_steff': float(example['koi_steff']) if pd.notna(example.get('koi_steff')) else None,
            'koi_slogg': float(example['koi_slogg']) if pd.notna(example.get('koi_slogg')) else None,
            'koi_srad': float(example['koi_srad']) if pd.notna(example.get('koi_srad')) else None,
            'koi_smass': float(example['koi_smass']) if pd.notna(example.get('koi_smass')) else None,
            'koi_kepmag': float(example['koi_kepmag']) if pd.notna(example.get('koi_kepmag')) else None,
            'koi_insol': float(example['koi_insol']) if pd.notna(example.get('koi_insol')) else None,
            'koi_dor': float(example['koi_dor']) if pd.notna(example.get('koi_dor')) else None,
            'koi_count': int(example['koi_count']) if pd.notna(example.get('koi_count')) else None,
            # 'koi_score' REMOVED - data leakage (0.89 correlation with label)
            'koi_disposition': safe_str(example.get('koi_disposition')),
            'kepler_name': safe_str(example.get('kepler_name')),
        }
        
        # Get display name for message
        kepler_name = safe_str(example.get('kepler_name'))
        display_name = kepler_name if kepler_name else f"KepID {kepid}"
        disposition = safe_str(example.get('koi_disposition')) or 'UNKNOWN'
        
        return Response({
            'success': True,
            'kepid': kepid,
            'parameters': params,
            'fits_source': 'local' if fits_available else 'lightkurve',
            'message': f'Example: {display_name} ({disposition}). {"Instant loading from local FITS!" if fits_available else "FITS will be downloaded from MAST."}'
        })
    
    except Exception as e:
        return Response(
            {'error': f'Error getting example: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        """Get all predictions in a session"""
        session = self.get_object()
        predictions = session.predictions.all()
        serializer = PredictionSerializer(predictions, many=True)
        return Response(serializer.data)
