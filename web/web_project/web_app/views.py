from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from documentgen.drawing import generate_drawing
from .forms import CarriageForm, OrderForm, ShipmentForm
from .models import Carriage, Order, Shipment


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

    def get_success_url(self):
        order_id = self.kwargs["order_id"]
        return reverse("order_detail", kwargs={"pk": order_id})

    # def get(self, request, pk, *args, **kwargs):
    #     self.object = self.get_object()
    #     self.success_url = reverse_lazy('shipment_list', kwargs={"pk": pk})  # URL-адрес для перенаправления после успешного обновления
    #     return super().get(request, *args, **kwargs)


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

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        shipments = Shipment.objects.filter(order=self.object)
        context["shipments"] = shipments
        return self.render_to_response(context)


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
    file = generate_drawing(boxes=boxes, carriage=carriage)
    file_to_send = ContentFile(file)
    response = HttpResponse(file_to_send, 'image/svg+xml')
    response['Content-Length'] = file_to_send.size
    response['Content-Disposition'] = 'attachment; filename="somefile.svg"'
    return response
