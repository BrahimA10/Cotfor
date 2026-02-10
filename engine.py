import numpy as np
from numba import njit

@njit(fastmath=True)
def calculate_advanced_entropy(data):
    """حساب الإنتروبي الرياضي للبيانات بسرعة البرق"""
    # تحويل النص رمزياً إلى أرقام لمعالجتها كمصفوفات
    p = data / (np.sum(data) + 1e-9)
    entropy = -np.sum(p * np.log2(p + 1e-9))
    return entropy

def get_spike_score(text_data):
    """تحويل معطيات المباراة إلى مصفوفة احتمالات وحساب قوتها"""
    # توليد بصمة رقمية من نص المباراة (Simulated Vectorization)
    seed = sum(ord(char) for char in text_data) % 1000
    np.random.seed(seed)
    
    # مصفوفة احتمالات عشوائية تعتمد على "بصمة المباراة"
    statistical_sample = np.random.dirichlet(np.ones(10), size=1)[0]
    
    # حساب الإنتروبي - كلما قل الإنتروبي زادت ثبات التوقع (Spike)
    entropy_val = calculate_advanced_entropy(statistical_sample)
    
    # تحويل القيمة إلى مقياس من 0 إلى 1
    score = np.clip(1.0 - (entropy_val / 3.32), 0, 1)
    return score
