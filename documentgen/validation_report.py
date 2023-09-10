from io import BytesIO

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from validation.formulas import calculate_formulas
# from validation.formulas import l_c_shipments_calculation
from validation.models import Box, Carriage

# latex_formula = r'$l_c = 0.5*L - \frac{\sum Q_i*l_i}{\sum Q_i}$'


def add_formula(ax: Figure, formula: str, current_row_height) -> float:
    ax.text(0.3, current_row_height, formula, size=12, ha='center')
    return current_row_height - 0.06


def add_text(ax: Figure, text: str, current_row_height, **kwargs) -> float:
    params = {**{"x": 0.01, "y": current_row_height, "s": text, "ha": "left"}, **kwargs}
    ax.text(**params)
    return current_row_height - 0.04


# Сохранить PDF file
# plt.savefig('formula.pdf', format="pdf", dpi=300, bbox_inches='tight', pad_inches=0.1)


def _generate_pdf_figure(order, boxes: list[Box], carriage: Carriage) -> None:
    current_row_height = 0.95
    report = calculate_formulas(boxes=boxes, platform=carriage)
    # Создайте графический объект
    fig, ax = plt.subplots(figsize=(10, 16))  # Размер изображения (ширина x высота)

    # Отключите оси и метки
    ax.axis('off')

    current_row_height = add_text(ax, "Расчетно-пояснительная записка к схеме размещения", x=0.2,size=16, current_row_height=current_row_height)
    current_row_height = add_text(ax, f"и крепления \"{order.name}\"", x=0.3, size=16, current_row_height=current_row_height)
    current_row_height = add_text(ax, "1. Смещение ЦТ грузов в вагоне:", current_row_height=current_row_height)
    current_row_height = add_text(ax, "Продольное смещение:", current_row_height=current_row_height)
    current_row_height = add_formula(ax, r'$l_c = 0.5*L - \frac{\sum Q_i*l_i}{\sum Q_i}$', current_row_height=current_row_height)
    current_row_height = add_text(ax, "= " +report.l_c_shipments_calculation, current_row_height=current_row_height)
    current_row_height = add_text(ax, "Смещение: " + ("допустимо" if report.is_longitudinal_bias_permissible else "НЕ ДОПУСТИМО!"), current_row_height=current_row_height)
    current_row_height = add_text(ax, "Продольное смещение грузов с вагоном:", current_row_height=current_row_height)
    current_row_height = add_formula(ax, r'$l_c = 0.5*L - \frac{\sum Q_i*l_i + Q_в*l_в}{\sum Q_i + Q_в}$', current_row_height=current_row_height)
    current_row_height = add_text(ax, "= " +report.l_c_overall_calculation, current_row_height=current_row_height)

    current_row_height = add_text(ax, "2. Общая высота ЦТ:", current_row_height=current_row_height)
    current_row_height = add_formula(ax, r'$H_цт = \frac{\sum Q_i*h_i}{\sum Q_i}$', current_row_height=current_row_height)
    current_row_height = add_text(ax, "= " +report.h_shipments_overall_calculation, current_row_height=current_row_height)

    current_row_height = add_text(ax, "3. Устойчивость грузов с вагоном:", current_row_height=current_row_height)
    current_row_height = add_text(ax, "3.1. Общая высота ЦТ:", current_row_height=current_row_height)
    current_row_height = add_formula(ax, r'$H^0_цт = \frac{\sum Q_i*h_i + Q_в*h_в}{\sum Q_i + Q_в}$', current_row_height=current_row_height)
    current_row_height = add_text(ax, "= " +report.h_overall_calculation, current_row_height=current_row_height)

    current_row_height = add_text(ax, "3.2. Расчёт наветреной поверхности:", current_row_height=current_row_height)
    current_row_height = add_formula(ax, r'$S_бок = \sum S_i$ + S_в', current_row_height=current_row_height)
    current_row_height = add_text(ax, "= " +report.s_side_surface_calculation, current_row_height=current_row_height)
    current_row_height = add_text(ax, ("Требуется ли проверка поперечной устойчивости груженого вагона: "+  "требуется" if report.is_transverse_need_check else "не требуется"), current_row_height=current_row_height)


def generate_pdf_report_bytes(**kwargs):
    _generate_pdf_figure(**kwargs)
    sio = BytesIO()
    plt.savefig(sio, format="pdf", dpi=300, bbox_inches='tight', pad_inches=0.1)
    sio.seek(0)
    b = sio.read()
    return b
