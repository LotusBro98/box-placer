from validation.models import platform, boxes
from validation.standarts import LONGITUDINAL_MAX_CG_BY_WEIGHT

l_c = 0.5*platform.floor_length - sum(box.weight*box.coords_of_cg[0] for box in boxes)/sum(box.weight for box in boxes)
print("1. Смещение ЦТ грузов в вагоне:", l_c)
print("Критерий:", l_c < LONGITUDINAL_MAX_CG_BY_WEIGHT[15])
