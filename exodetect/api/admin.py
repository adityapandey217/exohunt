"""
Django admin configuration for ExoHunt API models
"""
from django.contrib import admin
from .models import (
    LightCurveFile, KOIParameters, Prediction, ExplainabilityData,
    UserFeedback, TransitDetection, AnalysisSession, BatchJob, ModelMetrics
)


@admin.register(LightCurveFile)
class LightCurveFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'kepid', 'flux_points', 'duration_days', 'data_quality_score', 'uploaded_at']
    list_filter = ['uploaded_at', 'flux_type']
    search_fields = ['kepid']
    readonly_fields = ['id', 'uploaded_at']


@admin.register(KOIParameters)
class KOIParametersAdmin(admin.ModelAdmin):
    list_display = ['kepid', 'koi_period', 'koi_prad', 'koi_disposition', 'koi_score']
    list_filter = ['koi_disposition', 'koi_pdisposition']
    search_fields = ['kepid']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ['id', 'predicted_class_name', 'confidence', 'model_version', 'created_at']
    list_filter = ['predicted_class', 'model_version', 'created_at']
    search_fields = ['id', 'light_curve__kepid']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'


@admin.register(ExplainabilityData)
class ExplainabilityDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'prediction', 'uncertainty_epistemic', 'uncertainty_aleatoric', 'created_at']
    readonly_fields = ['id', 'created_at']


@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'prediction', 'verdict', 'corrected_class', 'confidence_in_correction', 'used_in_training', 'created_at']
    list_filter = ['verdict', 'used_in_training', 'created_at']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'


@admin.register(TransitDetection)
class TransitDetectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'light_curve', 'period_days', 'depth_ppm', 'snr', 'is_anomaly', 'detection_algorithm']
    list_filter = ['is_anomaly', 'detection_algorithm', 'created_at']
    readonly_fields = ['id', 'created_at']


@admin.register(AnalysisSession)
class AnalysisSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'user', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'notes']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(BatchJob)
class BatchJobAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'progress_percentage', 'total_files', 'processed_files', 'failed_files', 'created_at']
    list_filter = ['status', 'created_at']
    readonly_fields = ['id', 'created_at', 'started_at', 'completed_at']
    date_hierarchy = 'created_at'


@admin.register(ModelMetrics)
class ModelMetricsAdmin(admin.ModelAdmin):
    list_display = ['model_version', 'accuracy', 'f1_score_weighted', 'validation_set_size', 'training_date']
    list_filter = ['model_version', 'training_date']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'training_date'
