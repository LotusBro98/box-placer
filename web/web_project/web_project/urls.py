"""
URL configuration for web_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from web_app.views import CarriageCreateView, CarriageDetailView, CarriageListView, CarriageUpdateView, \
    OrderCreateView, OrderDetailView, OrderListView, OrderUpdateView, ShipmentCreateView, \
    ShipmentDetailView, ShipmentUpdateView, get_order_drawing, get_order_validation_report, \
    update_shipment_coordinates
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='order_list', permanent=False)),
    path('shipments/<int:pk>/', ShipmentDetailView.as_view(), name='shipment_detail'),
    path('orders/<int:order_id>/shipments/create/', ShipmentCreateView.as_view(), name='shipment_create'),
    path('orders/<int:pk>/shipments/update-coordinates/', update_shipment_coordinates, name='update_shipment_coordinates'),
    path('orders/<int:order_id>/shipments/<int:pk>/edit/', ShipmentUpdateView.as_view(), name='shipment_edit'),
    path('carriages/', CarriageListView.as_view(), name='carriage_list'),
    path('carriages/<int:pk>/', CarriageDetailView.as_view(), name='carriage_detail'),
    path('carriages/create/', CarriageCreateView.as_view(), name='carriage_create'),
    path('carriages/<int:pk>/edit/', CarriageUpdateView.as_view(), name='carriage_edit'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/edit/', OrderUpdateView.as_view(), name='order_edit'),
    path('orders/<int:pk>/drawing/', get_order_drawing, name='get_order_drawing'),
    path('orders/<int:pk>/validation-report/', get_order_validation_report, name='get_order_validation_report'),
    # Другие URL-маршруты вашего приложения...
]
