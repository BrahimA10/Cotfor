import numpy as np
from numba import njit

@njit # تحويل الدالة لكود آلة فائق السرعة
def calculate_entropy_fast(data_array):
    # حساب الإنتروبي بسرعة نانوثانية
    p = data_array / data_array.sum()
    return -np.sum(p * np.log2(p + 1e-9))

def get_spike_score(text):
    # محاكاة كاشف الانفجار الاحتمالي
    weights = np.random.rand(1000)
    return calculate_entropy_fast(weights)
