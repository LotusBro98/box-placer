from django import forms
from .models import Shipment, Carriage, Order


class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = ["name", "length", "width", "height", "weight", "order"]
        # widgets = {'order': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Установить label каждого поля равным его help_text
        for field_name, field in self.fields.items():
            field.label = field.help_text


class CarriageForm(forms.ModelForm):
    class Meta:
        model = Carriage
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Установить label каждого поля равным его help_text
        for field_name, field in self.fields.items():
            field.label = field.help_text


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'carriage']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Установить label каждого поля равным его help_text
        for field_name, field in self.fields.items():
            field.label = field.help_text
