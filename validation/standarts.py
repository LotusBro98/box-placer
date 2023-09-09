MAX_HEIGHT = 2300  # millimeters


LONGITUDINAL_MAX_CG_BIAS_DATA = (  # Масса груза, т     Максимальное смещение центра тяжести, мм
"""10	3000
15	2480
20	2230
25	2070
30	1970
35	1890
40	1840
45	1800
50	1700
55	1330
60	860
62	690
67	300
70	110
>70	100""")

raw_LONGITUDINAL_MAX_CG_BIAS_BY_WEIGHT = [tuple(row.split("\t")) for row in LONGITUDINAL_MAX_CG_BIAS_DATA.split("\n")[:-1]]  # tons: millimeters
LONGITUDINAL_MAX_CG_BIAS_BY_WEIGHT = {}
for weight, max_bias in raw_LONGITUDINAL_MAX_CG_BIAS_BY_WEIGHT:
    LONGITUDINAL_MAX_CG_BIAS_BY_WEIGHT[float(weight)] = float(max_bias)

LAST_MAX_CG_BY_WEIGHT = 100


def calculate_long_max_cg_by_weight(weight: float) -> float:
    if weight in LONGITUDINAL_MAX_CG_BIAS_BY_WEIGHT:
        return LONGITUDINAL_MAX_CG_BIAS_BY_WEIGHT[weight]
    elif weight < 10:
        return LONGITUDINAL_MAX_CG_BIAS_BY_WEIGHT[10.0]
    elif weight > 70:
        return LAST_MAX_CG_BY_WEIGHT
    else:
        left_border_weight = None
        right_border_weight = None
        for index, current_weight in enumerate(LONGITUDINAL_MAX_CG_BIAS_BY_WEIGHT.keys()):
            if weight > current_weight:
                left_border_weight = current_weight
                right_border_weight = list(LONGITUDINAL_MAX_CG_BIAS_BY_WEIGHT.keys())[index+1]
        left_border_bias = LONGITUDINAL_MAX_CG_BIAS_BY_WEIGHT[left_border_weight]
        right_border_bias = LONGITUDINAL_MAX_CG_BIAS_BY_WEIGHT[right_border_weight]
        interpolated_bias = left_border_bias - (left_border_bias-right_border_bias)*(weight-left_border_weight)/(right_border_weight-left_border_weight)
        return interpolated_bias
