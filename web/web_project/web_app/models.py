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
