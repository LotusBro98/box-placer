from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .models import Shipment
from .forms import ShipmentForm


class ShipmentListView(ListView):
    model = Shipment
    template_name = 'shipment/shipment_list.html'  # Замените на ваш шаблон
    context_object_name = 'shipments'


class ShipmentDetailView(DetailView):
    model = Shipment
    template_name = 'shipment/shipment_detail.html'  # Замените на ваш шаблон
    context_object_name = 'shipment'


class ShipmentCreateView(CreateView):
    model = Shipment
    form_class = ShipmentForm
    template_name = 'shipment/shipment_form.html'  # Замените на ваш шаблон формы
    success_url = reverse_lazy('shipment_list')  # Замените 'shipment_list' на URL для списка грузов
