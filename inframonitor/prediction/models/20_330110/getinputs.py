import numpy as np

from holidays import Austria

def get_inputs(timesteps, **kwargs):
    aut_holidays = Austria()

    # MODEL TAKES: TIME, WEEKDAY, HOLIDAY
    times = np.vectorize(lambda dt_value: dt_value.hour)(timesteps)
    weekdays = np.vectorize(lambda dt_value: dt_value.weekday())(timesteps)
    holidays = np.vectorize(lambda dt_value: dt_value in aut_holidays)(timesteps)

    x = np.column_stack([times, weekdays, holidays])
    x = np.expand_dims(x, 1)
    return x
