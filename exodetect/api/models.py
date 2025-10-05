"""
Django models for ExoHunt API
Stores predictions, user uploads, analysis sessions, and feedback
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import uuid


class LightCurveFile(models.Model):
    """Stores uploaded FITS light curve files"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(
        upload_to='lightcurves/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['fits', 'fit', 'fits.gz'])]
    )
    kepid = models.IntegerField(null=True, blank=True, db_index=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, db_index=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Metadata extracted from FITS file
    flux_points = models.IntegerField(null=True, blank=True)
    duration_days = models.FloatField(null=True, blank=True)
    data_quality_score = models.FloatField(null=True, blank=True)
    gaps_detected = models.IntegerField(default=0)
    flux_type = models.CharField(max_length=20, default='PDCSAP_FLUX')  # PDCSAP_FLUX or SAP_FLUX
    
    # Cache path for preprocessed numpy array
    cache_path = models.CharField(max_length=500, null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['kepid', 'uploaded_at']),
        ]
    
    def __str__(self):
        return f"LC-{self.kepid or 'Unknown'} ({self.id})"


class KOIParameters(models.Model):
    """Tabular features for a KOI (Kepler Object of Interest)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kepid = models.IntegerField(unique=True, db_index=True)
    
    # Orbital parameters
    koi_period = models.FloatField(null=True, blank=True, help_text="Orbital period (days)")
    koi_duration = models.FloatField(null=True, blank=True, help_text="Transit duration (hours)")
    koi_depth = models.FloatField(null=True, blank=True, help_text="Transit depth (ppm)")
    koi_prad = models.FloatField(null=True, blank=True, help_text="Planetary radius (Earth radii)")
    koi_ror = models.FloatField(null=True, blank=True, help_text="Planet-star radius ratio")
    koi_model_snr = models.FloatField(null=True, blank=True, help_text="Transit signal-to-noise")
    koi_num_transits = models.IntegerField(null=True, blank=True, help_text="Number of transits")
    koi_insol = models.FloatField(null=True, blank=True, help_text="Insolation flux (Earth flux)")
    koi_dor = models.FloatField(null=True, blank=True, help_text="Planet-star distance over star radius")
    
    # Stellar parameters
    koi_steff = models.FloatField(null=True, blank=True, help_text="Stellar effective temperature (K)")
    koi_slogg = models.FloatField(null=True, blank=True, help_text="Stellar surface gravity")
    koi_srad = models.FloatField(null=True, blank=True, help_text="Stellar radius (solar radii)")
    koi_smass = models.FloatField(null=True, blank=True, help_text="Stellar mass (solar masses)")
    koi_kepmag = models.FloatField(null=True, blank=True, help_text="Kepler magnitude")
    
    # Metadata
    koi_count = models.IntegerField(null=True, blank=True, help_text="Number of KOIs for this star")
    koi_score = models.FloatField(null=True, blank=True, help_text="Disposition score")
    koi_pdisposition = models.CharField(max_length=20, null=True, blank=True, help_text="Pipeline disposition")
    koi_disposition = models.CharField(max_length=20, null=True, blank=True, help_text="Final disposition")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "KOI Parameters"
        verbose_name_plural = "KOI Parameters"
    
    def __str__(self):
        return f"KOI-{self.kepid}"


class AnalysisSession(models.Model):
    """Groups related predictions into research sessions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, default="Untitled Session")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} ({self.created_at.strftime('%Y-%m-%d')})"


class Prediction(models.Model):
    """Stores model predictions and results"""
    
    CLASS_CHOICES = [
        (0, 'FALSE POSITIVE'),
        (1, 'CANDIDATE'),
        (2, 'CONFIRMED'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Input data
    light_curve = models.ForeignKey(LightCurveFile, on_delete=models.CASCADE, related_name='predictions')
    koi_params = models.ForeignKey(KOIParameters, on_delete=models.SET_NULL, null=True, blank=True)
    session = models.ForeignKey(AnalysisSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='predictions')
    
    # Prediction results
    predicted_class = models.IntegerField(choices=CLASS_CHOICES, db_index=True)
    predicted_class_name = models.CharField(max_length=20, db_index=True)
    
    # Confidence scores (probabilities for each class)
    prob_false_positive = models.FloatField()
    prob_candidate = models.FloatField()
    prob_confirmed = models.FloatField()
    confidence = models.FloatField(db_index=True, help_text="Max probability")
    
    # Metadata
    model_version = models.CharField(max_length=50, default="v1.0")
    processing_time_ms = models.IntegerField(help_text="Inference time in milliseconds")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # For batch predictions
    batch_id = models.UUIDField(null=True, blank=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['predicted_class', 'confidence']),
            models.Index(fields=['batch_id', 'created_at']),
        ]
    
    def __str__(self):
        return f"Prediction {self.predicted_class_name} ({self.confidence:.2f})"
    
    def get_probabilities_dict(self):
        return {
            'FALSE_POSITIVE': float(self.prob_false_positive),
            'CANDIDATE': float(self.prob_candidate),
            'CONFIRMED': float(self.prob_confirmed),
        }


class ExplainabilityData(models.Model):
    """Stores explainability artifacts (Grad-CAM, SHAP, attention)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prediction = models.OneToOneField(Prediction, on_delete=models.CASCADE, related_name='explanation')
    
    # Grad-CAM data
    gradcam_heatmap = models.JSONField(null=True, blank=True, help_text="1D array of attention weights")
    
    # Feature importance (SHAP values)
    shap_values = models.JSONField(null=True, blank=True, help_text="Dict of feature: SHAP value")
    feature_importance = models.JSONField(null=True, blank=True, help_text="Dict of feature: importance score")
    
    # Attention weights from model
    attention_weights = models.JSONField(null=True, blank=True, help_text="Attention scores across time")
    
    # Uncertainty estimates
    uncertainty_epistemic = models.FloatField(null=True, blank=True, help_text="Model uncertainty")
    uncertainty_aleatoric = models.FloatField(null=True, blank=True, help_text="Data uncertainty")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Explanation for {self.prediction.id}"


class UserFeedback(models.Model):
    """Collects user feedback on predictions for active learning"""
    
    VERDICT_CHOICES = [
        ('agree', 'Agree with prediction'),
        ('disagree', 'Disagree with prediction'),
        ('uncertain', 'Uncertain'),
    ]
    
    CORRECTED_CLASS_CHOICES = [
        (0, 'FALSE POSITIVE'),
        (1, 'CANDIDATE'),
        (2, 'CONFIRMED'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    verdict = models.CharField(max_length=20, choices=VERDICT_CHOICES)
    corrected_class = models.IntegerField(choices=CORRECTED_CLASS_CHOICES, null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Expert notes on the decision")
    confidence_in_correction = models.IntegerField(
        default=3,
        help_text="1-5 scale, how confident is the user in their correction"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Track if this feedback was used in retraining
    used_in_training = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['prediction', 'user']
    
    def __str__(self):
        return f"Feedback: {self.verdict} on {self.prediction.id}"


class TransitDetection(models.Model):
    """Stores detected transit events in light curves"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    light_curve = models.ForeignKey(LightCurveFile, on_delete=models.CASCADE, related_name='transits')
    
    # Transit characteristics
    start_time = models.FloatField(help_text="Transit start (BJD or relative time)")
    end_time = models.FloatField(help_text="Transit end")
    duration_hours = models.FloatField()
    depth_ppm = models.FloatField(help_text="Transit depth in parts per million")
    snr = models.FloatField(help_text="Signal-to-noise ratio")
    
    # Periodicity
    period_days = models.FloatField(null=True, blank=True)
    period_confidence = models.FloatField(null=True, blank=True)
    
    # Quality flags
    is_anomaly = models.BooleanField(default=False, help_text="Flagged as potential artifact")
    detection_algorithm = models.CharField(max_length=50, default="BLS")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['start_time']
    
    def __str__(self):
        return f"Transit at {self.start_time:.2f} (depth={self.depth_ppm:.1f}ppm)"


class BatchJob(models.Model):
    """Tracks batch prediction jobs"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    total_files = models.IntegerField(default=0)
    processed_files = models.IntegerField(default=0)
    failed_files = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Results
    results_file = models.FileField(upload_to='batch_results/', null=True, blank=True)
    error_log = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Batch {self.id} - {self.status} ({self.processed_files}/{self.total_files})"
    
    @property
    def progress_percentage(self):
        if self.total_files == 0:
            return 0
        return (self.processed_files / self.total_files) * 100


class ModelMetrics(models.Model):
    """Stores model performance metrics over time"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model_version = models.CharField(max_length=50, db_index=True)
    
    # Overall metrics
    accuracy = models.FloatField()
    f1_score_weighted = models.FloatField()
    
    # Per-class metrics
    precision_false_positive = models.FloatField()
    precision_candidate = models.FloatField()
    precision_confirmed = models.FloatField()
    
    recall_false_positive = models.FloatField()
    recall_candidate = models.FloatField()
    recall_confirmed = models.FloatField()
    
    f1_false_positive = models.FloatField()
    f1_candidate = models.FloatField()
    f1_confirmed = models.FloatField()
    
    # ROC/AUC
    roc_auc_false_positive = models.FloatField(null=True, blank=True)
    roc_auc_candidate = models.FloatField(null=True, blank=True)
    roc_auc_confirmed = models.FloatField(null=True, blank=True)
    
    # Confusion matrix (stored as JSON)
    confusion_matrix = models.JSONField()
    
    # Metadata
    validation_set_size = models.IntegerField()
    training_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Model Metrics"
    
    def __str__(self):
        return f"Metrics {self.model_version} (acc={self.accuracy:.3f})"
