import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Rescaling

# Path configurations relative to the script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(SCRIPT_DIR, "model")
GLOBAL_MODEL_PATH = os.path.join(MODEL_DIR, "global_model.h5")

def get_base_model():
    """Creates a basic CNN model if no global model exists."""
    model = Sequential([
        Rescaling(1./255, input_shape=(224, 224, 3)),
        Conv2D(32, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(4, activation='softmax') # 4 classes as per labels.txt
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def train_local_model(data, model_path):
    """Loads the model, trains on local data, and returns weights."""
    if os.path.exists(model_path):
        try:
            model = load_model(model_path)
            # Re-compile to avoid optimizer state issues during local training
            model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        except Exception as e:
            print(f"Error loading model from {model_path}: {e}. Initializing base model.")
            model = get_base_model()
    else:
        print(f"Model path {model_path} not found. Initializing base model for local training.")
        model = get_base_model()

    # Simple one-epoch training on provided data
    model.fit(data["x"], data["y"], epochs=1, batch_size=16, verbose=0)
    return model.get_weights()

def federated_average(client_weights):
    """Performs FedAvg: simple averaging of weights across clients."""
    if not client_weights:
        return None
    
    avg_weights = []
    for weights_list_tuple in zip(*client_weights):
        # Calculate the mean across the clients for each layer
        avg_weights.append(np.mean(np.array(weights_list_tuple), axis=0))
    return avg_weights

def run_federated_learning():
    """Main orchestration for federated learning."""
    # Ensure model directory exists
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        print(f"Created directory: {MODEL_DIR}")

    # Generate dummy data for 3 clients (simulating local datasets)
    # Shape: (10 samples, 224x224 RGB), 4 classes (one-hot)
    client1 = {"x": np.random.rand(10, 224, 224, 3), "y": np.eye(4)[np.random.choice(4, 10)]}
    client2 = {"x": np.random.rand(10, 224, 224, 3), "y": np.eye(4)[np.random.choice(4, 10)]}
    client3 = {"x": np.random.rand(10, 224, 224, 3), "y": np.eye(4)[np.random.choice(4, 10)]}

    clients_data = [client1, client2, client3]
    client_updates = []

    print("Starting local training on clients...")
    for i, data in enumerate(clients_data):
        print(f"Training Client {i+1}...")
        # We use the current global model as the starting point for each client
        weights = train_local_model(data, GLOBAL_MODEL_PATH)
        client_updates.append(weights)

    print("Performing Federated Averaging...")
    global_weights = federated_average(client_updates)

    # Load the global model to update it, or create it if it's the first time
    if os.path.exists(GLOBAL_MODEL_PATH):
        model = load_model(GLOBAL_MODEL_PATH)
    else:
        print("Global model file not found. Initializing a new one.")
        model = get_base_model()

    # Update global model with aggregated weights
    model.set_weights(global_weights)

    # Save the updated global model
    model.save(GLOBAL_MODEL_PATH)
    print(f"Federated Learning Completed - Global Model Saved at: {GLOBAL_MODEL_PATH}")

if __name__ == "__main__":
    run_federated_learning()
