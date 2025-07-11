"""
Forms for equipment app
"""
from django import forms
from datetime import date, timedelta

# Equipment categories and status choices
EQUIPMENT_CATEGORIES = [
    ('weapons', 'Weapons'),
    ('vehicles', 'Vehicles'),
    ('communications', 'Communications'),
    ('protective-gear', 'Protective Gear'),
    ('medical', 'Medical'),
    ('electronics', 'Electronics'),
]

EQUIPMENT_STATUS = [
    ('operational', 'Operational'),
    ('maintenance', 'Maintenance'),
    ('damaged', 'Damaged'),
    ('decommissioned', 'Decommissioned'),
]

CLASSIFICATION_LEVELS = [
    ('unclassified', 'Unclassified'),
    ('confidential', 'Confidential'),
    ('secret', 'Secret'),
]


class EquipmentForm(forms.Form):
    """Form for creating and updating equipment"""
    name = forms.CharField(
        label='Equipment Name', 
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control military-input'})
    )
    category = forms.ChoiceField(
        label='Category',
        choices=EQUIPMENT_CATEGORIES,
        widget=forms.Select(attrs={'class': 'form-select military-select'})
    )
    status = forms.ChoiceField(
        label='Status',
        choices=EQUIPMENT_STATUS,
        widget=forms.Select(attrs={'class': 'form-select military-select'})
    )
    location = forms.CharField(
        label='Location', 
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control military-input'})
    )
    serial_number = forms.CharField(
        label='Serial Number', 
        max_length=50, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control military-input'})
    )
    classification_level = forms.ChoiceField(
        label='Classification Level',
        choices=CLASSIFICATION_LEVELS,
        initial='unclassified',
        widget=forms.Select(attrs={'class': 'form-select military-select'})
    )
    assigned_unit = forms.CharField(
        label='Assigned Unit', 
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control military-input'})
    )
    assigned_personnel = forms.CharField(
        label='Assigned Personnel', 
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control military-input'})
    )
    purchase_date = forms.DateField(
        label='Purchase Date',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control military-input'})
    )
    last_maintenance = forms.DateField(
        label='Last Maintenance',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control military-input'})
    )
    next_maintenance_due = forms.DateField(
        label='Next Maintenance Due',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control military-input'})
    )
    condition_rating = forms.IntegerField(
        label='Condition Rating (1-5)',
        min_value=1,
        max_value=5,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control military-input'})
    )

    def clean_serial_number(self):
        serial_number = self.cleaned_data.get('serial_number')
        if serial_number and len(serial_number) < 5:
            raise forms.ValidationError("Serial number must be at least 5 characters long.")
        return serial_number

    def clean_last_maintenance(self):
        last_maintenance = self.cleaned_data.get('last_maintenance')
        if last_maintenance and last_maintenance > date.today():
            raise forms.ValidationError("Last maintenance date cannot be in the future.")
        return last_maintenance


class MaintenanceLogForm(forms.Form):
    """Form for creating maintenance logs"""
    maintenance_date = forms.DateField(
        label='Maintenance Date',
        initial=date.today,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control military-input'})
    )
    maintenance_type = forms.ChoiceField(
        label='Maintenance Type',
        choices=[
            ('preventive', 'Preventive'),
            ('corrective', 'Corrective'),
            ('diagnostic', 'Diagnostic'),
            ('upgrade', 'Upgrade'),
            ('overhaul', 'Overhaul'),
        ],
        widget=forms.Select(attrs={'class': 'form-select military-select'})
    )
    description = forms.CharField(
        label='Description',
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control military-textarea'})
    )
    performed_by = forms.CharField(
        label='Performed By',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control military-input'})
    )
    notes = forms.CharField(
        label='Notes',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control military-textarea'})
    )

    def clean_maintenance_date(self):
        maintenance_date = self.cleaned_data.get('maintenance_date')
        if maintenance_date and maintenance_date > date.today():
            raise forms.ValidationError("Maintenance date cannot be in the future.")
        return maintenance_date


class EquipmentAssignmentForm(forms.Form):
    """Form for assigning equipment to units and personnel"""
    assigned_unit = forms.ChoiceField(
        label='Assigned Unit',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select military-select'})
    )
    assigned_personnel = forms.CharField(
        label='Assigned Personnel',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control military-input'})
    )

    def __init__(self, *args, **kwargs):
        units = kwargs.pop('units', [])
        super().__init__(*args, **kwargs)
        
        unit_choices = [('', '--- Unassign ---')] + [(unit, unit) for unit in units]
        self.fields['assigned_unit'].choices = unit_choices


class SearchForm(forms.Form):
    """Form for searching equipment"""
    query = forms.CharField(
        label='Search',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control military-search',
            'placeholder': 'Search by name, serial number, or category...'
        })
    )
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + EQUIPMENT_CATEGORIES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select military-select'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + EQUIPMENT_STATUS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select military-select'})
    )

    def get_search_params(self):
        """Returns a dictionary of cleaned search parameters."""
        if not self.is_valid():
            return {}

        params = {}
        if self.cleaned_data.get('query'):
            params['query'] = self.cleaned_data['query']
        if self.cleaned_data.get('category'):
            params['category'] = self.cleaned_data['category']
        if self.cleaned_data.get('status'):
            params['status'] = self.cleaned_data['status']
        return params
