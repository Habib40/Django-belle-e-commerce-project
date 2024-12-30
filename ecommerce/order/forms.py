from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            'first_name', 'last_name', 'phone', 'email', 
            'address_line_1', 'address_line_2', 
            'country', 'state', 'city', 'order_note'
        )
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter address'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter address'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter country name'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter state name'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter city name'}),
            'order_note': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Add any special instructions or notes', 'rows': 3}),
        }
def clean_phone(self):
    phone = self.cleaned_data.get('phone')

    # Check if the phone number is provided
    if not phone:
        raise forms.ValidationError('This field is required.')

    # Remove any non-numeric characters
    phone = ''.join(filter(str.isdigit, phone))

    # Validate the length of the phone number
    if len(phone)  != 11:
        raise forms.ValidationError('Number should not be more than 11 digits.')

    return phone
def clean_email(self):
    email = self.cleaned_data.get('email')
    if not email:
        raise forms.ValidationError("Please enter a valid email address.")
    return email