import warnings


warnings.filterwarnings('ignore')


def bmi_id(bmi):
    float(bmi)
    if bmi < 18.5:
        bmi_id = 1
    elif 18.5 <= bmi < 25:
        bmi_id = 2
    elif 25 <= bmi < 30:
        bmi_id = 3
    else:
        bmi_id = 4
    return int(bmi_id)



