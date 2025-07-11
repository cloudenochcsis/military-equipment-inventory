"""
Views for equipment app
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator
from .api import api_client, APIError
from .forms import EquipmentForm, MaintenanceLogForm, EquipmentAssignmentForm


def dashboard(request):
    """Command Center dashboard with operational readiness status"""
    try:
        stats = api_client.get_equipment_stats()
        maintenance_items = api_client.get_maintenance_equipment(page_size=5)
        context = {
            'stats': stats,
            'maintenance_items': maintenance_items.get('data', []),
            'active_nav': 'dashboard'
        }
        return render(request, 'equipment/dashboard.html', context)
    except APIError as e:
        messages.error(request, f"API Error: {str(e)}")
        context = {'active_nav': 'dashboard'}
        return render(request, 'equipment/dashboard.html', context)


def equipment_list(request):
    """Equipment roster with filtering capabilities"""
    try:
        page = int(request.GET.get('page', 1))
        status = request.GET.get('status', None)
        category = request.GET.get('category', None)
        classification = request.GET.get('classification', None)
        
        # Get equipment list with filters
        result = api_client.get_equipment_list(
            page=page, 
            page_size=20,
            status=status,
            category=category,
            classification=classification
        )
        
        context = {
            'equipment_list': result['data'],
            'total_items': result['total'],
            'current_page': result['page'],
            'pages': range(1, (result['total'] // result['page_size']) + 2),
            'status_filter': status,
            'category_filter': category,
            'classification_filter': classification,
            'active_nav': 'roster'
        }
        return render(request, 'equipment/equipment_list.html', context)
    except APIError as e:
        messages.error(request, f"API Error: {str(e)}")
        return render(request, 'equipment/equipment_list.html', {'active_nav': 'roster'})


def equipment_detail(request, equipment_id):
    """Equipment detail view"""
    try:
        equipment = api_client.get_equipment(equipment_id)
        maintenance_logs = api_client.get_maintenance_logs(equipment_id)
        
        context = {
            'equipment': equipment,
            'maintenance_logs': maintenance_logs,
            'active_nav': 'roster'
        }
        return render(request, 'equipment/equipment_detail.html', context)
    except APIError as e:
        messages.error(request, f"API Error: {str(e)}")
        return redirect('equipment:equipment_list')


def equipment_create(request):
    """Create new equipment entry"""
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            try:
                api_client.create_equipment(form.cleaned_data)
                messages.success(request, "Equipment created successfully")
                return redirect('equipment:equipment_list')
            except APIError as e:
                messages.error(request, f"API Error: {str(e)}")
    else:
        form = EquipmentForm()
    
    context = {
        'form': form,
        'title': 'Add New Equipment',
        'active_nav': 'roster'
    }
    return render(request, 'equipment/equipment_form.html', context)


def equipment_update(request, equipment_id):
    """Update equipment details"""
    try:
        equipment = api_client.get_equipment(equipment_id)
        
        if request.method == 'POST':
            form = EquipmentForm(request.POST)
            if form.is_valid():
                try:
                    api_client.update_equipment(equipment_id, form.cleaned_data)
                    messages.success(request, "Equipment updated successfully")
                    return redirect('equipment:equipment_detail', equipment_id=equipment_id)
                except APIError as e:
                    messages.error(request, f"API Error: {str(e)}")
        else:
            form = EquipmentForm(initial=equipment)
        
        context = {
            'form': form,
            'equipment': equipment,
            'title': 'Edit Equipment',
            'active_nav': 'roster'
        }
        return render(request, 'equipment/equipment_form.html', context)
    except APIError as e:
        messages.error(request, f"API Error: {str(e)}")
        return redirect('equipment:equipment_list')


def equipment_delete(request, equipment_id):
    """Delete (decommission) equipment"""
    try:
        if request.method == 'POST':
            api_client.delete_equipment(equipment_id)
            messages.success(request, "Equipment decommissioned successfully")
            return redirect('equipment:equipment_list')
        
        # Get equipment details for confirmation
        equipment = api_client.get_equipment(equipment_id)
        return render(request, 'equipment/equipment_delete.html', {
            'equipment': equipment,
            'active_nav': 'roster'
        })
    except APIError as e:
        messages.error(request, f"API Error: {str(e)}")
        return redirect('equipment:equipment_list')


def equipment_search(request):
    """Search equipment by name/category/serial"""
    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    results = None

    try:
        if query:
            results = api_client.search_equipment(query=query, page=page)
    except APIError as e:
        messages.error(request, f"API Error: {str(e)}")

    context = {
        'query': query,
        'results': results,
        'active_nav': 'roster'
    }
    return render(request, 'equipment/equipment_search.html', context)


def maintenance_list(request):
    """Maintenance schedule and overdue items"""
    try:
        page = int(request.GET.get('page', 1))
        result = api_client.get_maintenance_equipment(page=page, page_size=20)
        
        context = {
            'maintenance_schedule': result.get('data', []),
            'active_nav': 'maintenance'
        }
        return render(request, 'equipment/maintenance_list.html', context)
    except APIError as e:
        messages.error(request, f"API Error: {str(e)}")
        return render(request, 'equipment/maintenance_list.html', {'active_nav': 'maintenance'})


def maintenance_add(request, equipment_id):
    """Add maintenance log entry"""
    try:
        equipment = api_client.get_equipment(equipment_id)
        
        if request.method == 'POST':
            form = MaintenanceLogForm(request.POST)
            if form.is_valid():
                try:
                    data = form.cleaned_data
                    data['equipment_id'] = equipment_id
                    api_client.create_maintenance_log(data)
                    messages.success(request, "Maintenance log added successfully")
                    return redirect('equipment:equipment_detail', equipment_id=equipment_id)
                except APIError as e:
                    messages.error(request, f"API Error: {str(e)}")
        else:
            form = MaintenanceLogForm()
        
        context = {
            'form': form,
            'equipment': equipment,
            'active_nav': 'maintenance'
        }
        return render(request, 'equipment/maintenance_form.html', context)
    except APIError as e:
        messages.error(request, f"API Error: {str(e)}")
        return redirect('equipment:maintenance_list')


def maintenance_history(request, equipment_id):
    """View maintenance history for equipment"""
    try:
        equipment = api_client.get_equipment(equipment_id)
        logs = api_client.get_maintenance_logs(equipment_id)
        
        context = {
            'equipment': equipment,
            'logs': logs,
            'active_nav': 'maintenance'
        }
        return render(request, 'equipment/maintenance_history.html', context)
    except APIError as e:
        messages.error(request, f"API Error: {str(e)}")
        return redirect('equipment:maintenance_list')


def unit_list(request):
    """List all units with assigned equipment."""
    try:
        units = api_client.get_units()
        context = {
            'units': sorted(units),
            'active_nav': 'units'
        }
        return render(request, 'equipment/unit_list.html', context)
    except APIError as e:
        messages.error(request, f"API Error: {str(e)}")
        return render(request, 'equipment/unit_list.html', {'active_nav': 'units'})


def unit_detail(request, unit_id):
    """Unit detail with assigned equipment"""
    try:
        equipment_list = api_client.get_equipment_by_unit(unit_id)
        
        context = {
            'unit_id': unit_id,
            'equipment_list': equipment_list,
            'active_nav': 'units'
        }
        return render(request, 'equipment/unit_detail.html', context)
    except APIError as e:
        messages.error(request, f"API Error: {str(e)}")
        return redirect('equipment:unit_list')


def equipment_assign(request, equipment_id):
    """Assign equipment to unit/personnel"""
    try:
        equipment = api_client.get_equipment(equipment_id)
        units = api_client.get_units()

        if request.method == 'POST':
            form = EquipmentAssignmentForm(request.POST, units=units)
            if form.is_valid():
                try:
                    api_client.assign_equipment(
                        equipment_id,
                        form.cleaned_data['assigned_unit'],
                        form.cleaned_data['assigned_personnel']
                    )
                    messages.success(request, "Equipment assigned successfully")
                    return redirect('equipment:equipment_detail', equipment_id=equipment_id)
                except APIError as e:
                    messages.error(request, f"API Error: {str(e)}")
        else:
            initial_data = {
                'assigned_unit': equipment.get('assigned_unit'),
                'assigned_personnel': equipment.get('assigned_personnel')
            }
            form = EquipmentAssignmentForm(initial=initial_data, units=units)

        context = {
            'form': form,
            'equipment': equipment,
            'active_nav': 'units'
        }
        return render(request, 'equipment/equipment_assign.html', context)
    except APIError as e:
        messages.error(request, f"API Error: {str(e)}")
        return redirect('equipment:equipment_list')


def reports(request):
    """Reports dashboard"""
    try:
        stats = api_client.get_equipment_stats()
        
        context = {
            'stats': stats,
            'active_nav': 'reports'
        }
        return render(request, 'equipment/reports.html', context)
    except APIError as e:
        messages.error(request, f"API Error: {str(e)}")
        return render(request, 'equipment/reports.html', {'active_nav': 'reports'})


def readiness_report(request):
    """Detailed readiness report"""
    try:
        stats = api_client.get_equipment_stats()
        # Get all operational equipment
        operational = api_client.get_equipment_list(status='operational', page_size=500)
        
        context = {
            'stats': stats,
            'equipment': operational['data'],
            'active_nav': 'reports'
        }
        return render(request, 'equipment/readiness_report.html', context)
    except APIError as e:
        messages.error(request, f"API Error: {str(e)}")
        return render(request, 'equipment/dashboard.html', {'active_nav': 'dashboard'})
