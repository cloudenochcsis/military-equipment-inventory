"""
URL patterns for equipment app
"""
from django.urls import path
from . import views

app_name = 'equipment'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Equipment list and detail
    path('roster/', views.equipment_list, name='equipment_list'),
    path('detail/<int:equipment_id>/', views.equipment_detail, name='equipment_detail'),
    
    # Equipment CRUD
    path('add/', views.equipment_create, name='equipment_create'),
    path('edit/<int:equipment_id>/', views.equipment_update, name='equipment_update'),
    path('delete/<int:equipment_id>/', views.equipment_delete, name='equipment_delete'),
    
    # Search
    path('search/', views.equipment_search, name='equipment_search'),
    
    # Maintenance
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('maintenance/add/<int:equipment_id>/', views.maintenance_add, name='maintenance_add'),
    path('maintenance/history/<int:equipment_id>/', views.maintenance_history, name='maintenance_history'),
    
    # Unit assignments
    path('units/', views.unit_list, name='unit_list'),
    path('unit/<str:unit_id>/', views.unit_detail, name='unit_detail'),
    path('assign/<int:equipment_id>/', views.equipment_assign, name='equipment_assign'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
    path('reports/readiness/', views.readiness_report, name='readiness_report'),
]
