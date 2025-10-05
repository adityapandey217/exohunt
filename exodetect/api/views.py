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
    
    Upload a FITS file and get exoplanet classification prediction.
    Optionally include KOI parameters for better accuracy.
    """
    serializer = PredictionRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    fits_file = data['fits_file']
    
    # Save uploaded file temporarily
    temp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.fits")
    with open(temp_path, 'wb+') as destination:
        for chunk in fits_file.chunks():
            destination.write(chunk)
    
    try:
        # Extract metadata
        metadata = extract_light_curve_metadata(temp_path)
        
        # Save to database
        lc_file = LightCurveFile.objects.create(
            file=fits_file,
            kepid=data.get('kepid') or metadata.get('kepid'),
            flux_points=metadata.get('flux_points'),
            duration_days=metadata.get('duration_days'),
            data_quality_score=metadata.get('data_quality_score'),
            gaps_detected=metadata.get('gaps_detected'),
            flux_type=metadata.get('flux_type'),
            uploaded_by=request.user if request.user.is_authenticated else None
        )
        
        # Prepare KOI parameters
        koi_params = {}
        koi_feature_fields = [
            'koi_period', 'koi_duration', 'koi_depth', 'koi_prad', 'koi_ror',
            'koi_model_snr', 'koi_num_transits', 'koi_steff', 'koi_slogg',
            'koi_srad', 'koi_smass', 'koi_kepmag', 'koi_insol', 'koi_dor',
            'koi_count', 'koi_score'
        ]
        for field in koi_feature_fields:
            if field in data and data[field] is not None:
                koi_params[field] = data[field]
        
        # Get predictor and make prediction
        predictor = get_predictor()
        cache_dir = os.path.join(settings.BASE_DIR, '..', 'training', 'lc_cache_npy')
        
        result = predictor.predict(
            temp_path,
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
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ============================================================================
# VISUALIZATION ENDPOINTS
# ============================================================================

@api_view(['GET', 'POST'])
def visualize_lightcurve(request):
    """
    GET/POST /api/lightcurve/visualize/
    
    Get interactive light curve visualization data.
    Provide either prediction_id (GET param) or upload FITS file (POST).
    """
    if request.method == 'GET':
        prediction_id = request.query_params.get('prediction_id')
        if not prediction_id:
            return Response(
                {'error': 'prediction_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            prediction = Prediction.objects.get(id=prediction_id)
            fits_path = prediction.light_curve.file.path
            title = f"KepID {prediction.light_curve.kepid} - {prediction.predicted_class_name}"
        except Prediction.DoesNotExist:
            return Response(
                {'error': 'Prediction not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    else:  # POST
        serializer = VisualizationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        if data.get('prediction_id'):
            try:
                prediction = Prediction.objects.get(id=data['prediction_id'])
                fits_path = prediction.light_curve.file.path
                title = f"KepID {prediction.light_curve.kepid}"
            except Prediction.DoesNotExist:
                return Response(
                    {'error': 'Prediction not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Save temp file
            fits_file = data['fits_file']
            temp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.fits")
            with open(temp_path, 'wb+') as destination:
                for chunk in fits_file.chunks():
                    destination.write(chunk)
            fits_path = temp_path
            title = "Uploaded Light Curve"
    
    try:
        plot_data = create_interactive_plot(fits_path, title=title)
        
        # Detect anomalies for highlighting
        anomalies = detect_anomalies(fits_path)
        
        response_data = {
            'plot_data': plot_data,
            'anomalies': anomalies,
            'metadata': {
                'total_points': len(plot_data['time']),
                'anomalies_detected': len(anomalies)
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    finally:
        if request.method == 'POST' and not data.get('prediction_id'):
            if os.path.exists(temp_path):
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
    
    predictions = Prediction.objects.all()[offset:offset+limit]
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
        """Get all predictions in a session"""
        session = self.get_object()
        predictions = session.predictions.all()
        serializer = PredictionSerializer(predictions, many=True)
        return Response(serializer.data)
