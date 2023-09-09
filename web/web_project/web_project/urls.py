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

from web_app.views import CarriageCreateView, CarriageDetailView, CarriageListView, ShipmentCreateView, \
    ShipmentDetailView, ShipmentListView
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('shipments/', ShipmentListView.as_view(), name='shipment_list'),
    path('shipments/<int:pk>/', ShipmentDetailView.as_view(), name='shipment_detail'),
    path('shipments/create/', ShipmentCreateView.as_view(), name='shipment_create'),
    path('carriages/', CarriageListView.as_view(), name='carriage_list'),
    path('carriages/<int:pk>/', CarriageDetailView.as_view(), name='carriage_detail'),
    path('carriages/create/', CarriageCreateView.as_view(), name='carriage_create'),
    # Другие URL-маршруты вашего приложения...
]
