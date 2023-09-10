from io import BytesIO

import matplotlib.pyplot as plt

from validation.formulas import l_c_shipments_calculation

latex_formula = r'$l_c = 0.5*L - \frac{\sum Q_i*l_i}{\sum Q_i}$'

# Создайте графический объект для формулы
fig, ax = plt.subplots(figsize=(10, 16))  # Размер изображения (ширина x высота)

# Отключите оси и метки
ax.axis('off')

# Вставьте формулу LaTeX
ax.text(0.3, 0.9, latex_formula, size=12, ha='center')
ax.text(0.01, 0.85, "= "+l_c_shipments_calculation, ha='left')

# Сохраните изображение
plt.savefig('formula.pdf', format="pdf", dpi=300, bbox_inches='tight', pad_inches=0.1)


def generate_pdf_report_bytes(**kwargs):
    sio = BytesIO()
    plt.savefig(sio, format="pdf", dpi=300, bbox_inches='tight', pad_inches=0.1)
    sio.seek(0)
    b = sio.read()
    return b
