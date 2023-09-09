from io import BytesIO

from django.core.files.base import ContentFile
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from .models import Carriage, Shipment
from .forms import CarriageForm, ShipmentForm
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import Order
from .forms import OrderForm


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


class ShipmentUpdateView(UpdateView):
    model = Shipment
    form_class = ShipmentForm
    template_name = 'shipment/shipment_form.html'  # Используйте существующий шаблон формы
    context_object_name = 'shipment'
    success_url = reverse_lazy('shipment_list')  # URL-адрес для перенаправления после успешного обновления


class CarriageListView(ListView):
    model = Carriage
    template_name = 'carriage/carriage_list.html'  # Создайте соответствующий шаблон
    context_object_name = 'carriages'


class CarriageDetailView(DetailView):
    model = Carriage
    template_name = 'carriage/carriage_detail.html'  # Создайте соответствующий шаблон
    context_object_name = 'carriage'


class CarriageCreateView(CreateView):
    model = Carriage
    form_class = CarriageForm
    template_name = 'carriage/carriage_form.html'  # Создайте соответствующий шаблон
    success_url = reverse_lazy('carriage_list')  # Замените 'carriage_list' на URL для списка вагонов


class CarriageUpdateView(UpdateView):
    model = Carriage
    form_class = CarriageForm
    template_name = 'carriage/carriage_form.html'  # Используйте существующий шаблон формы
    context_object_name = 'carriage'
    success_url = reverse_lazy('carriage_list')  # URL-адрес для перенаправления после успешного обновления


class OrderListView(ListView):
    model = Order
    template_name = 'order/order_list.html'  # Создайте соответствующий шаблон
    context_object_name = 'orders'


class OrderDetailView(DetailView):
    model = Order
    template_name = 'order/order_detail.html'  # Создайте соответствующий шаблон
    context_object_name = 'order'


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'order/order_form.html'  # Создайте соответствующий шаблон
    success_url = reverse_lazy('order_list')  # URL-адрес для перенаправления после успешного создания


class OrderUpdateView(UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'order/order_form.html'  # Создайте соответствующий шаблон
    context_object_name = 'order'
    success_url = reverse_lazy('order_list')  # URL-адрес для перенаправления после успешного обновления


def get_order_drawing(request, pk: int):
    order = Order.objects.get(pk=pk)
    shipments_data = Shipment.objects.filter(order=order)
    # Input for drawer:
    boxes = [shipment.to_box for shipment in shipments_data]
    carriage = order.carriage.to_base_model
    # Output of drawer:
    file_stream = BytesIO()
    file_to_send = ContentFile(file_stream)
    response = HttpResponse(file_to_send, 'image/svg+xml')
    response['Content-Length'] = file_to_send.size
    response['Content-Disposition'] = 'attachment; filename="somefile.svg"'
    return response
