"""
Django REST Framework serializers for API endpoints
"""
from rest_framework import serializers
from .models import (
    LightCurveFile, KOIParameters, Prediction, ExplainabilityData,
    UserFeedback, TransitDetection, AnalysisSession, BatchJob, ModelMetrics
)


class LightCurveFileSerializer(serializers.ModelSerializer):
    """Serializer for light curve file uploads"""
    class Meta:
        model = LightCurveFile
        fields = [
            'id', 'file', 'kepid', 'uploaded_at', 'flux_points',
            'duration_days', 'data_quality_score', 'gaps_detected', 'flux_type'
        ]
        read_only_fields = [
            'id', 'uploaded_at', 'flux_points', 'duration_days',
            'data_quality_score', 'gaps_detected', 'flux_type'
        ]


class KOIParametersSerializer(serializers.ModelSerializer):
    """Serializer for KOI tabular parameters"""
    class Meta:
        model = KOIParameters
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class PredictionSerializer(serializers.ModelSerializer):
    """Serializer for model predictions"""
    probabilities = serializers.SerializerMethodField()
    light_curve_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Prediction
        fields = [
            'id', 'predicted_class', 'predicted_class_name',
            'probabilities', 'confidence', 'model_version',
            'processing_time_ms', 'created_at', 'batch_id',
            'light_curve_details', 'session'
        ]
        read_only_fields = fields
    
    def get_probabilities(self, obj):
        return obj.get_probabilities_dict()
    
    def get_light_curve_details(self, obj):
        if obj.light_curve:
            return {
                'id': str(obj.light_curve.id),
                'kepid': obj.light_curve.kepid,
                'flux_points': obj.light_curve.flux_points,
                'duration_days': obj.light_curve.duration_days,
                'data_quality_score': obj.light_curve.data_quality_score,
            }
        return None


class ExplainabilityDataSerializer(serializers.ModelSerializer):
    """Serializer for explainability data"""
    class Meta:
        model = ExplainabilityData
        fields = [
            'id', 'prediction', 'gradcam_heatmap', 'shap_values',
            'feature_importance', 'attention_weights',
            'uncertainty_epistemic', 'uncertainty_aleatoric', 'created_at'
        ]
        read_only_fields = fields


class UserFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for user feedback"""
    class Meta:
        model = UserFeedback
        fields = [
            'id', 'prediction', 'verdict', 'corrected_class',
            'notes', 'confidence_in_correction', 'created_at', 'used_in_training'
        ]
        read_only_fields = ['id', 'created_at', 'used_in_training']


class TransitDetectionSerializer(serializers.ModelSerializer):
    """Serializer for detected transits"""
    class Meta:
        model = TransitDetection
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class AnalysisSessionSerializer(serializers.ModelSerializer):
    """Serializer for analysis sessions"""
    predictions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalysisSession
        fields = ['id', 'name', 'created_at', 'updated_at', 'notes', 'predictions_count']
        read_only_fields = ['id', 'created_at', 'updated_at', 'predictions_count']
    
    def get_predictions_count(self, obj):
        return obj.predictions.count()


class BatchJobSerializer(serializers.ModelSerializer):
    """Serializer for batch prediction jobs"""
    progress_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = BatchJob
        fields = [
            'id', 'status', 'total_files', 'processed_files', 'failed_files',
            'progress_percentage', 'created_at', 'started_at', 'completed_at',
            'results_file', 'error_log'
        ]
        read_only_fields = [
            'id', 'status', 'processed_files', 'failed_files', 'progress_percentage',
            'created_at', 'started_at', 'completed_at', 'results_file', 'error_log'
        ]


class ModelMetricsSerializer(serializers.ModelSerializer):
    """Serializer for model performance metrics"""
    class Meta:
        model = ModelMetrics
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class PredictionRequestSerializer(serializers.Serializer):
    """Serializer for prediction requests"""
    fits_file = serializers.FileField(required=True)
    kepid = serializers.IntegerField(required=False, allow_null=True)
    
    # Optional KOI parameters
    koi_period = serializers.FloatField(required=False, allow_null=True)
    koi_duration = serializers.FloatField(required=False, allow_null=True)
    koi_depth = serializers.FloatField(required=False, allow_null=True)
    koi_prad = serializers.FloatField(required=False, allow_null=True)
    koi_ror = serializers.FloatField(required=False, allow_null=True)
    koi_model_snr = serializers.FloatField(required=False, allow_null=True)
    koi_num_transits = serializers.IntegerField(required=False, allow_null=True)
    koi_steff = serializers.FloatField(required=False, allow_null=True)
    koi_slogg = serializers.FloatField(required=False, allow_null=True)
    koi_srad = serializers.FloatField(required=False, allow_null=True)
    koi_smass = serializers.FloatField(required=False, allow_null=True)
    koi_kepmag = serializers.FloatField(required=False, allow_null=True)
    koi_insol = serializers.FloatField(required=False, allow_null=True)
    koi_dor = serializers.FloatField(required=False, allow_null=True)
    koi_count = serializers.IntegerField(required=False, allow_null=True)
    koi_score = serializers.FloatField(required=False, allow_null=True)
    
    session_id = serializers.UUIDField(required=False, allow_null=True)


class VisualizationRequestSerializer(serializers.Serializer):
    """Serializer for visualization requests"""
    prediction_id = serializers.UUIDField(required=False, allow_null=True)
    fits_file = serializers.FileField(required=False, allow_null=True)
    
    def validate(self, data):
        if not data.get('prediction_id') and not data.get('fits_file'):
            raise serializers.ValidationError(
                "Either prediction_id or fits_file must be provided"
            )
        return data


class PhaseFoldRequestSerializer(serializers.Serializer):
    """Serializer for phase-folding requests"""
    prediction_id = serializers.UUIDField(required=False, allow_null=True)
    fits_file = serializers.FileField(required=False, allow_null=True)
    period = serializers.FloatField(required=True)
    epoch = serializers.FloatField(required=False, allow_null=True)
    
    def validate(self, data):
        if not data.get('prediction_id') and not data.get('fits_file'):
            raise serializers.ValidationError(
                "Either prediction_id or fits_file must be provided"
            )
        return data


class TransitSearchRequestSerializer(serializers.Serializer):
    """Serializer for transit search requests"""
    prediction_id = serializers.UUIDField(required=False, allow_null=True)
    fits_file = serializers.FileField(required=False, allow_null=True)
    period_min = serializers.FloatField(default=0.5)
    period_max = serializers.FloatField(default=50.0)
    snr_threshold = serializers.FloatField(default=7.0)
    
    def validate(self, data):
        if not data.get('prediction_id') and not data.get('fits_file'):
            raise serializers.ValidationError(
                "Either prediction_id or fits_file must be provided"
            )
        return data
