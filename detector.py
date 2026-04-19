# detector.py
import pickle
import numpy as np

# تحميل الموديل
with open("ids_model.pkl", "rb") as f:
    model = pickle.load(f)

def predict(syscall_window):
    """بتاخد list من syscall numbers وترجع normal/attack"""
    num_syscalls = 400
    freq = np.zeros(num_syscalls)
    
    for syscall in syscall_window:
        if syscall < num_syscalls:
            freq[syscall] += 1
    
    prediction = model.predict([freq])[0]
    confidence = model.predict_proba([freq])[0]
    
    if prediction == 1:
        print(f"🚨 ANOMALY DETECTED! Confidence: {confidence[1]:.2%}")
    else:
        print(f"✅ Normal behavior. Confidence: {confidence[0]:.2%}")
    
    return prediction