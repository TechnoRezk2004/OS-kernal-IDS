import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

DATASET_PATH = "/home/f/Downloads/archive (1)/ADFA-LD"
NUM_SYSCALLS = 400
WINDOW_SIZE = 50

def load_sequences(folder, label):
    sequences = []
    labels = []
    
    for root, dirs, files in os.walk(folder):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r') as f:
                    syscalls = list(map(int, f.read().split()))
                    if len(syscalls) > 0:
                        sequences.append(syscalls)
                        labels.append(label)
            except:
                continue
    
    return sequences, labels

def extract_features(sequences):
    features = []
    for seq in sequences:
        freq = np.zeros(NUM_SYSCALLS)
        for s in seq[:WINDOW_SIZE]:
            if s < NUM_SYSCALLS:
                freq[s] += 1
        features.append(freq)
    return np.array(features)

# تحميل الـ data
print("Loading data...")
normal_seq, normal_labels = load_sequences(
    os.path.join(DATASET_PATH, "Training_Data_Master"), 0
)
attack_seq, attack_labels = load_sequences(
    os.path.join(DATASET_PATH, "Attack_Data_Master"), 1
)

print(f"Normal samples: {len(normal_seq)}")
print(f"Attack samples: {len(attack_seq)}")

# دمج الـ data
all_seq = normal_seq + attack_seq
all_labels = normal_labels + attack_labels

# استخراج الـ features
print("Extracting features...")
X = extract_features(all_seq)
y = np.array(all_labels)

# تقسيم الـ data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# تدريب الموديل
print("Training model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# تقييم الموديل
print("\n=== Model Evaluation ===")
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred, target_names=["Normal", "Attack"]))

# حفظ الموديل
with open("ids_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model saved as ids_model.pkl")


# حساب الـ metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f"✅ Accuracy:  {accuracy:.2%}")
print(f"✅ Precision: {precision:.2%}")
print(f"✅ Recall:    {recall:.2%}")
print(f"✅ F1 Score:  {f1:.2%}")

# رسم الـ Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6,4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=["Normal", "Attack"],
            yticklabels=["Normal", "Attack"])
plt.title("Confusion Matrix")
plt.ylabel("Actual")
plt.xlabel("Predicted")
plt.tight_layout()
plt.savefig("confusion_matrix.png")
print("✅ Confusion Matrix saved!")
