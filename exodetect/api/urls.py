"""
URL configuration for ExoHunt API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router for ViewSets
router = DefaultRouter()
router.register(r'sessions', views.AnalysisSessionViewSet, basename='session')

urlpatterns = [
    # Prediction endpoints
    path('predict/single/', views.predict_single, name='predict-single'),
    
    # Helper endpoints
    path('search-kepid/', views.search_by_kepid, name='search-kepid'),
    path('get-example/', views.get_example_data, name='get-example'),
    
    # Light curve visualization
    path('lightcurve/visualize/', views.visualize_lightcurve, name='visualize-lightcurve'),
    path('lightcurve/phase-fold/', views.phase_fold, name='phase-fold'),
    path('lightcurve/analyze/', views.analyze_transits, name='analyze-transits'),
    
    # Dashboard
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
    path('dashboard/recent-predictions/', views.recent_predictions, name='recent-predictions'),
    
    # Feedback
    path('feedback/submit/', views.submit_feedback, name='submit-feedback'),
    
    # Include router URLs (sessions)
    path('', include(router.urls)),
]
