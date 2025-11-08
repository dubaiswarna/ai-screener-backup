import pickle
from pathlib import Path

model_path = Path("../Nifty200_Models_Pro/ensemble_RELIANCE.pkl")

with open(model_path, 'rb') as f:
    model_data = pickle.load(f)

print("Model data keys:")
print(model_data.keys())
print("\nModel data structure:")
for key in model_data.keys():
    print(f"  {key}: {type(model_data[key])}")

