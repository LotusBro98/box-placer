from validation.models import platform, boxes
from validation.standarts import calculate_long_max_cg_by_weight, MAX_HEIGHT

print("Габариты грузов: не выходят за пределы")

boxes_weight = round(sum(box.weight for box in boxes), 3)
l_c_shipments = 0.5 * platform.floor_length - sum(box.weight * box.coords_of_cg[0] for box in boxes) / boxes_weight
max_permissible_l_c_shipments = calculate_long_max_cg_by_weight(boxes_weight)
print(f"1. Смещение ЦТ грузов в вагоне:\n"
      f"Продольное смещение:\n"
      f"0.5*{platform.floor_length} - ({' + '.join(f'{box.weight}*{box.coords_of_cg[0]}' for box in boxes)})/ {boxes_weight}")
print("1. Смещение ЦТ грузов в вагоне:", round(l_c_shipments), "мм <", max_permissible_l_c_shipments, "мм")
is_longitudinal_bias_permissible = l_c_shipments < max_permissible_l_c_shipments
print("Смещение:", "допустимо" if is_longitudinal_bias_permissible else "НЕ ДОПУСТИМО!")
print()
l_c_overall = 0.5 * platform.floor_length - (
            sum((box.weight * box.coords_of_cg[0]) for box in boxes) + platform.weight * platform.length_to_cg) / (
                          sum(box.weight for box in boxes) + platform.weight)
print("Продольное смещение грузов с вагоном:", round(l_c_overall), " мм")
print()
h_shipments_overall = sum(box.weight * (box.h_of_cg + platform.height_from_rails) for box in boxes) / sum(
    box.weight for box in boxes)
# print(
#     f"h_shipments_overall = sum({' + '.join(f'{box.weight}*({box.h_of_cg}+{platform.height_from_rails})' for box in boxes)}/{sum(box.weight for box in boxes)}")
print(
    f"2. Общая высота ЦТ грузов в вагоне: H_ct = sum({' + '.join(f'{box.weight}*{box.h_of_cg + platform.height_from_rails}' for box in boxes)}/{sum(box.weight for box in boxes)}"
    f"\n = {round(h_shipments_overall)}мм < {MAX_HEIGHT}")
print()
h_overall = (sum(box.weight * (box.h_of_cg + platform.height_from_rails) for box in
                 boxes) + platform.weight * platform.cg_height_from_rails) / (
                        sum(box.weight for box in boxes) + platform.weight)
print("Общая высота ЦТ")
print(f"({' + '.join(f'{box.weight} * {str(box.h_of_cg + platform.height_from_rails)}' for box in boxes)} "
      f"+ {platform.weight} * {platform.cg_height_from_rails}) /"
      f" ({' + '.join(str(box.weight) for box in boxes)} + {platform.weight})\n = {round(h_overall)}мм < {MAX_HEIGHT}мм")

print("Устойчивость грузов с вагоном:")
s_side_surface = sum(box.s_side_surface_meters for box in boxes) + platform.s_side_surface_meters
print(
    f"s_side_surface = {' + '.join(str(box.s_side_surface_meters) for box in boxes)} + {platform.s_side_surface_meters} = {s_side_surface}м2 < {50}м2")

is_transverse_need_check = h_overall > MAX_HEIGHT or s_side_surface > 50
print("Требуется ли проверка поперечной устойчивости груженого вагона:", "требуется" if is_transverse_need_check else "не требуется")
# TODO: вычислить поперечную устойчивость, если требуется
