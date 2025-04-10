from django import forms
from .models import Instrument, Location, Department


class InstrumentForm(forms.ModelForm):
    class Meta:
        model = Instrument
        fields = [
            'name', 'serial_number', 'model', 'manufacturer',
            'category', 'location', 'department', 'status'
        ]
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': (
                        'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 '
                        'block w-full sm:text-sm border-gray-300 rounded-md'
                    )
                }
            ),
            'serial_number': forms.TextInput(
                attrs={
                    'class': (
                        'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 '
                        'block w-full sm:text-sm border-gray-300 rounded-md'
                    )
                }
            ),
            'model': forms.TextInput(
                attrs={
                    'class': (
                        'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 '
                        'block w-full sm:text-sm border-gray-300 rounded-md'
                    )
                }
            ),
            'manufacturer': forms.TextInput(
                attrs={
                    'class': (
                        'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 '
                        'block w-full sm:text-sm border-gray-300 rounded-md'
                    )
                }
            ),
            'category': forms.Select(
                attrs={
                    'class': (
                        'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 '
                        'block w-full sm:text-sm border-gray-300 rounded-md'
                    )
                }
            ),
            'location': forms.Select(
                attrs={
                    'class': (
                        'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 '
                        'block w-full sm:text-sm border-gray-300 rounded-md'
                    )
                }
            ),
            'department': forms.Select(
                attrs={
                    'class': (
                        'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 '
                        'block w-full sm:text-sm border-gray-300 rounded-md'
                    )
                }
            ),
            'status': forms.Select(
                attrs={
                    'class': (
                        'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 '
                        'block w-full sm:text-sm border-gray-300 rounded-md'
                    )
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].queryset = Location.objects.filter(site__is_active=True)
        self.fields['department'].queryset = Department.objects.all()
