from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from eshop_app.models import Item

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal'),
)


class CheckOutForm(forms.ModelForm):
    address = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': "Address"
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': "Apartment address"
    }))
    country = CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(attrs={
        'class': 'col-12'
    }))
    zip_code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': "Zip code"
    }))
    same_billing_address = forms.BooleanField(widget=forms.CheckboxInput(attrs={
                            'class': 'form-check-input',
                            'type': 'checkbox',
                            'value': '',
                            'id': 'flexCheckDefault'
                        }), required=False)

    save_info = forms.BooleanField(widget=forms.CheckboxInput(attrs={
                            'class': 'form-check-input',
                            'type': 'checkbox',
                            'value': '',
                            'id': 'flexCheckChecked'
                        }), required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)

    class Meta:
        model = Item
        fields = ('address', 'apartment_address')
