from django.db import models
# from django.urls import reverse


class Shipment(models.Model):
    name = models.CharField(max_length=200, help_text='Наименование груза')
    length = models.IntegerField(help_text='Длина (мм)')
    width = models.IntegerField(help_text='Ширина (мм)')
    height = models.IntegerField(help_text='Высота (мм)')
    weight = models.FloatField(help_text='Вес (кг)')
    amount = models.IntegerField(help_text='Количество (шт)', default=1)
    primary_key = True

    # Metadata
    class Meta:
        ordering = ['id']

    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return self.name


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
