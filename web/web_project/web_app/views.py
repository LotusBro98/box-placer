from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from documentgen.drawing import generate_drawing
from documentgen.validation_report import generate_pdf_report_bytes
from topology.main import calculate_optimal_placement
from .forms import CarriageForm, OrderForm, ShipmentForm
from .models import Carriage, Order, Shipment


class ShipmentListView(ListView):
    model = Shipment
    template_name = 'shipment/shipment_list.html'
    context_object_name = 'shipments'


class ShipmentDetailView(DetailView):
    model = Shipment
    template_name = 'shipment/shipment_detail.html'
    context_object_name = 'shipment'


class ShipmentCreateView(CreateView):
    model = Shipment
    form_class = ShipmentForm
    template_name = 'shipment/shipment_form.html'  # Замените на ваш шаблон формы
    success_url = reverse_lazy('order_detail')  # Замените 'shipment_list' на URL для списка грузов

    def get_success_url(self):
        order_id = self.kwargs["order_id"]
        order = Order.objects.get(pk=order_id)
        order.calculation_success = False
        order.save()
        return reverse("order_detail", kwargs={"pk": order_id})


class ShipmentUpdateView(UpdateView):
    model = Shipment
    form_class = ShipmentForm
    template_name = 'shipment/shipment_form.html'
    context_object_name = 'shipment'

    def get_success_url(self):
        order_id = self.kwargs["order_id"]
        order = Order.objects.get(pk=order_id)
        order.calculation_success = False
        order.save()
        return reverse("order_detail", kwargs={"pk": order_id})


class CarriageListView(ListView):
    model = Carriage
    template_name = 'carriage/carriage_list.html'
    context_object_name = 'carriages'


class CarriageDetailView(DetailView):
    model = Carriage
    template_name = 'carriage/carriage_detail.html'
    context_object_name = 'carriage'


class CarriageCreateView(CreateView):
    model = Carriage
    form_class = CarriageForm
    template_name = 'carriage/carriage_form.html'
    success_url = reverse_lazy('carriage_list')


class CarriageUpdateView(UpdateView):
    model = Carriage
    form_class = CarriageForm
    template_name = 'carriage/carriage_form.html'
    context_object_name = 'carriage'
    success_url = reverse_lazy('carriage_list')


class OrderListView(ListView):
    model = Order
    template_name = 'order/order_list.html'
    context_object_name = 'orders'


class OrderDetailView(DetailView):
    model = Order
    template_name = 'order/order_detail.html'
    context_object_name = 'order'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        shipments = Shipment.objects.filter(order=self.object)
        context["shipments"] = shipments
        if "success_message" in request.session:
            context["success_message"] = request.session["success_message"]
            del request.session["success_message"]
        return self.render_to_response(context)


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'order/order_form.html'
    success_url = reverse_lazy('order_list')


class OrderUpdateView(UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'order/order_form.html'
    context_object_name = 'order'
    success_url = reverse_lazy('order_list')


def update_shipment_coordinates(request, pk: int):
    order = Order.objects.get(pk=pk)
    shipments_data = list(Shipment.objects.filter(order=order))
    # Input for calculator:
    boxes = [shipment.to_box for shipment in shipments_data]
    carriage = order.carriage.to_base_model
    calculate_optimal_placement(platform=carriage, boxes=boxes)
    # Save output of calculator:
    for index, box in enumerate(boxes):
        shipments_data[index].update_coords_from_box(box)
        shipments_data[index].save()
    order = Order.objects.get(pk=pk)
    order.calculation_success = True
    order.save()
    request.session['success_message'] = "Координаты размещения грузов на платформе были успешно пересчитаны!"
    return redirect(reverse('order_detail', kwargs={'pk': pk}))


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
    print(order.name)
    response['Content-Disposition'] = f'attachment; filename="result-drawing.svg"'
    return response


def get_order_validation_report(request, pk: int):
    order = Order.objects.get(pk=pk)
    shipments_data = Shipment.objects.filter(order=order)
    # Input for drawer:
    boxes = [shipment.to_box for shipment in shipments_data]
    carriage = order.carriage.to_base_model
    # Output of drawer:
    file = generate_pdf_report_bytes(boxes=boxes, carriage=carriage)
    file_to_send = ContentFile(file)
    response = HttpResponse(file_to_send, 'application/x-pdf')
    response['Content-Length'] = file_to_send.size
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    return response
