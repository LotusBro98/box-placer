from dataclasses import dataclass

from validation.standarts import calculate_long_max_cg_by_weight, MAX_HEIGHT


@dataclass
class CalculatedReport:
    boxes_weight: float
    l_c_shipments: float
    max_permissible_l_c_shipments: float
    l_c_shipments_calculation: str
    is_longitudinal_bias_permissible: bool

    l_c_overall: float
    l_c_overall_calculation: str

    h_shipments_overall: float
    h_shipments_overall_calculation: str

    h_overall: float
    h_overall_calculation: str

    s_side_surface: float
    s_side_surface_calculation: str

    is_transverse_need_check: bool


def calculate_formulas(boxes, platform) -> CalculatedReport:
    boxes_weight = round(sum(box.weight for box in boxes), 3)
    l_c_shipments = 0.5 * platform.floor_length - sum(box.weight * box.coords_of_cg[0] for box in boxes) / boxes_weight
    max_permissible_l_c_shipments = calculate_long_max_cg_by_weight(boxes_weight)
    print("1. Смещение ЦТ грузов в вагоне:")
    print("Продольное смещение:")
    l_c_shipments_calculation = f"0.5*{platform.floor_length} - ({' + '.join(f'{box.weight}*{box.coords_of_cg[0]}' for box in boxes)})/ {boxes_weight} = {round(l_c_shipments)} мм < {max_permissible_l_c_shipments} мм"
    print(l_c_shipments_calculation)
    is_longitudinal_bias_permissible = l_c_shipments < max_permissible_l_c_shipments
    print("Смещение:", "допустимо" if is_longitudinal_bias_permissible else "НЕ ДОПУСТИМО!")
    print()
    l_c_overall = 0.5 * platform.floor_length - (
            sum((box.weight * box.coords_of_cg[0]) for box in boxes) + platform.weight * platform.length_to_cg) / (
                          sum(box.weight for box in boxes) + platform.weight)
    l_c_overall_calculation = f"({' + '.join(f'{box.weight}*{box.coords_of_cg[0]}' for box in boxes)} + {platform.weight}*{platform.length_to_cg})/({boxes_weight} + {platform.weight}) = {round(l_c_overall)} мм"
    print("Продольное смещение грузов с вагоном:", round(l_c_overall), " мм")
    print()
    h_shipments_overall = sum(box.weight * (box.h_of_cg + platform.height_from_rails) for box in boxes) / sum(
        box.weight for box in boxes)
    print("2. Общая высота ЦТ грузов в вагоне:")
    h_shipments_overall_calculation = (
        f"({' + '.join(f'{box.weight}*{box.h_of_cg + platform.height_from_rails}' for box in boxes)})/{boxes_weight}"
        f"\n = {round(h_shipments_overall)}мм < {MAX_HEIGHT}мм")
    print("H_ct = ", h_shipments_overall_calculation)
    h_overall = (sum(box.weight * (box.h_of_cg + platform.height_from_rails) for box in
                     boxes) + platform.weight * platform.cg_height_from_rails) / (boxes_weight + platform.weight)
    print("Общая высота ЦТ")
    h_overall_calculation = (
        f"({' + '.join(f'{box.weight} * {str(box.h_of_cg + platform.height_from_rails)}' for box in boxes)} "
        f"+ {platform.weight} * {platform.cg_height_from_rails}) /"
        f" ({' + '.join(str(box.weight) for box in boxes)} + {platform.weight})\n = {round(h_overall)}мм < {MAX_HEIGHT}мм")
    print(h_overall_calculation)

    print("Устойчивость грузов с вагоном:")
    s_side_surface = sum(box.s_side_surface_meters for box in boxes) + platform.s_side_surface_meters
    s_side_surface_calculation = (
        f"{' + '.join(str(box.s_side_surface_meters) for box in boxes)} + {platform.s_side_surface_meters} = {s_side_surface}м2 < {50}м2")
    print(s_side_surface_calculation)
    is_transverse_need_check = h_overall > MAX_HEIGHT or s_side_surface > 50
    print("Требуется ли проверка поперечной устойчивости груженого вагона:",
          "требуется" if is_transverse_need_check else "не требуется")
    return CalculatedReport(boxes_weight=boxes_weight,
                            l_c_shipments=l_c_shipments,
                            max_permissible_l_c_shipments=max_permissible_l_c_shipments,
                            l_c_shipments_calculation=l_c_shipments_calculation,
                            is_longitudinal_bias_permissible=is_longitudinal_bias_permissible,

                            l_c_overall=l_c_overall,
                            l_c_overall_calculation=l_c_overall_calculation,

                            h_shipments_overall=h_shipments_overall,
                            h_shipments_overall_calculation=h_shipments_overall_calculation,

                            h_overall=h_overall,
                            h_overall_calculation=h_overall_calculation,

                            s_side_surface=s_side_surface,
                            s_side_surface_calculation=s_side_surface_calculation,

                            is_transverse_need_check=is_transverse_need_check)


if __name__ == "__main__":
    from validation.models import platform, boxes

    calculate_formulas(boxes, platform)
