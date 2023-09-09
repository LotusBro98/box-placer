from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import int_list_validator
from django.db import models
from django.utils import timezone

from validation.models import Box as BoxBase, Carriage as CarriageBase


class Shipment(models.Model):
    name = models.CharField(max_length=200, help_text='Наименование груза')
    length = models.IntegerField(help_text='Длина (мм)')
    width = models.IntegerField(help_text='Ширина (мм)')
    height = models.IntegerField(help_text='Высота (мм)')
    weight = models.FloatField(help_text='Вес (кг)')
    amount = models.IntegerField(help_text='Количество (шт)', default=1)
    order = models.ForeignKey("Order", on_delete=models.CASCADE)
    coords_of_cg = models.CharField(validators=[int_list_validator], default="0,0,0", max_length=200)
    primary_key = True

    # Metadata
    class Meta:
        ordering = ['id']

    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return self.name

    @property
    def to_box(self) -> BoxBase:
        return BoxBase(dimensions=(int(self.length), int(self.width), int(self.height)), weight=float(self.weight), coords_of_cg=tuple(int(v) for v in (self.coords_of_cg.split(",") or [])))


class Carriage(models.Model):
    name = models.CharField(max_length=200, help_text='Наименование вагона')
    floor_length: int = models.IntegerField(help_text='Длина пола (мм)')
    floor_width: int = models.IntegerField(help_text='Ширина пола (мм)')
    weight: float = models.FloatField(help_text='Масса тары (т)')  # in tons
    height_from_rails: int = models.IntegerField(help_text='Высота пола от УГР (мм)')  # in millimeters
    cg_height_from_rails: int = models.IntegerField(help_text='Высота центра тяжести от УГР (мм)')  # in millimeters. C.G. - center of gravity
    base_length: int = models.IntegerField(help_text='База платформы (мм)')  # in millimeters
    s_side_surface_meters: float = models.FloatField(help_text='Площадь наветренной поверхности вагона (м²)')
    primary_key = True

    # Metadata
    class Meta:
        ordering = ['id']

    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return self.name

    @property
    def to_base_model(self) -> CarriageBase:
        return CarriageBase(floor_length=self.floor_length, floor_width=self.floor_width, weight=self.weight, height_from_rails=self.height_from_rails, cg_height_from_rails=self.cg_height_from_rails, base_length=self.base_length, length_to_cg=self.floor_length/2, s_side_surface_meters=self.s_side_surface_meters)


class Order(models.Model):
    name = models.CharField(max_length=200, help_text='Наименование заказа')
    carriage = models.ForeignKey(Carriage, on_delete=models.CASCADE, help_text='Тип вагона')
    created_at = models.DateField(default=timezone.now, help_text='Дата создания заказа')
    shipments = GenericRelation(Shipment)
    primary_key = True

    # Metadata
    class Meta:
        ordering = ['id']

    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return self.name
