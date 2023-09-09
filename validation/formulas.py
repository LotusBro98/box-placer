from validation.models import platform, boxes
from validation.standarts import LONGITUDINAL_MAX_CG_BY_WEIGHT, MAX_HEIGHT

print("Габариты грузов не выходят за пределы")

l_c_shipments = 0.5 * platform.floor_length - sum(box.weight * box.coords_of_cg[0] for box in boxes) / sum(
    box.weight for box in boxes)
print("1. Смещение ЦТ грузов в вагоне:", round(l_c_shipments), "мм <", LONGITUDINAL_MAX_CG_BY_WEIGHT[15], "мм")
left_longitudinal_max_permissible_bias = 1
right_longitudinal_max_permissible_bias = 2
longitudinal_max_permissible_bias = 3
is_longitudinal_bias_permissible = l_c_shipments < longitudinal_max_permissible_bias
print("Смещение:", "допустимое" if is_longitudinal_bias_permissible else "НЕ ДОПУСТИМОЕ!")

l_c_overall = 0.5 * platform.floor_length - (
            sum((box.weight * box.coords_of_cg[0]) for box in boxes) + platform.weight * platform.length_to_cg) / (
                          sum(box.weight for box in boxes) + platform.weight)
print("Продольное смещение грузов с вагоном:", round(l_c_overall), " мм")

h_shipments_overall = sum(box.weight * (box.h_of_cg + platform.height_from_rails) for box in boxes) / sum(
    box.weight for box in boxes)
print(
    f"h_shipments_overall = sum({' + '.join(f'{box.weight}*({box.h_of_cg}+{platform.height_from_rails})' for box in boxes)}/{sum(box.weight for box in boxes)}")
print(
    f"h_shipments_overall = sum({' + '.join(f'{box.weight}*({box.h_of_cg + platform.height_from_rails})' for box in boxes)}/{sum(box.weight for box in boxes)}")
print("Общая высота ЦТ грузов в вагоне:", round(h_shipments_overall), "<", MAX_HEIGHT)
print("Критерий: ", h_shipments_overall < MAX_HEIGHT)

h_overall = (sum(box.weight * (box.h_of_cg + platform.height_from_rails) for box in
                 boxes) + platform.weight * platform.cg_height_from_rails) / (
                        sum(box.weight for box in boxes) + platform.weight)
print(f"({' + '.join(f'{box.weight} * {str(box.h_of_cg + platform.height_from_rails)}' for box in boxes)} "
      f"+ {platform.weight} * {platform.cg_height_from_rails}) /"
      f" ({' + '.join(str(box.weight) for box in boxes)} + {platform.weight})")
print("Общая высота ЦТ:", round(h_overall), "<", MAX_HEIGHT)

print("Устойчивость грузов с вагоном:")
s_side_surface = sum(box.s_side_surface_meters for box in boxes) + platform.s_side_surface_meters
print(
    f"s_side_surface = {' + '.join(str(box.s_side_surface_meters) for box in boxes)} + {platform.s_side_surface_meters} = {s_side_surface}м2 < {50}м2")

is_transverse_need_check = h_overall > MAX_HEIGHT or s_side_surface > 50
print("Требуется ли проверка поперечной устойчивости груженого вагона:", is_transverse_need_check)
# TODO: вычислить поперечную устойчивость, если требуется
