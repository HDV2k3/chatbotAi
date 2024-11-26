import numpy as np
import random
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import time  # Import time for sleep
from nltk_utils import bag_of_words, tokenize, stem_word
from model import NeuralNet
import logging
# Load intents.json file
with open('intents.json', 'r', encoding='utf-8') as f:
    intents = json.load(f)

# Prepare data
all_words = []
tags = []
xy = []

# Loop through each sentence in our intents patterns
for intent in intents['intents']:
    tag = intent['tag']
    tags.append(tag)
    for pattern in intent['patterns']:
        w = tokenize(pattern)  # Tokenize each word in the sentence
        all_words.extend(w)  # Add to the list of all words
        xy.append((w, tag))  # Add to the xy pair for training

# Stem and lower each word
ignore_words = ['?', '.', '!']
all_words = [stem_word(w) for w in all_words if w not in ignore_words]

# Remove duplicates and sort the words and tags
all_words = sorted(set(all_words))
tags = sorted(set(tags))

print(f'{len(xy)} patterns')
print(f'{len(tags)} tags:', tags)
print(f'{len(all_words)} unique stemmed words:', all_words)

# Create training data
X_train = []
y_train = []
for (pattern_sentence, tag) in xy:
    # X: bag of words for each pattern_sentence
    bag = bag_of_words(pattern_sentence, all_words)
    X_train.append(bag)
    
    # y: Class labels (not one-hot encoded)
    label = tags.index(tag)  # Add index to class label
    y_train.append(label)

X_train = np.array(X_train)
y_train = np.array(y_train)

# Hyperparameters
num_epochs = 1000
batch_size = 8
learning_rate = 0.001
input_size = len(X_train[0])
hidden_size = 8
output_size = len(tags)
print(f'Input size: {input_size}, Output size: {output_size}')

# Custom Dataset
class ChatDataset(Dataset):
    def __init__(self):
        self.n_samples = len(X_train)
        self.x_data = X_train
        self.y_data = y_train

    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]

    def __len__(self):
        return self.n_samples

# DataLoader
dataset = ChatDataset()
train_loader = DataLoader(dataset=dataset,
                          batch_size=batch_size,
                          shuffle=True,
                          num_workers=0)

# Choose the device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Initialize the model
model = NeuralNet(input_size, hidden_size, output_size).to(device)

# Loss and optimizer
criterion = nn.CrossEntropyLoss()  # Includes softmax activation internally
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

# Function to train the model
def train_model():
    print("Training model...")
    for epoch in range(num_epochs):
        for (words, labels) in train_loader:
            words = words.to(device)
            labels = labels.to(dtype=torch.long).to(device)
            
            # Forward pass
            outputs = model(words)
            
            # Calculate loss
            loss = criterion(outputs, labels)
            
            # Backward pass and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
        if (epoch+1) % 100 == 0:
            print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')
    
    print(f'Final loss: {loss.item():.4f}')
    return model

# Function to save model
def save_model(model):
    data = {
        "model_state": model.state_dict(),
        "input_size": input_size,
        "hidden_size": hidden_size,
        "output_size": output_size,
        "all_words": all_words,
        "tags": tags
    }
    FILE = "data.pth"
    torch.save(data, FILE)
    print(f'Training complete. Model saved to {FILE}')
# if __name__ == "__main__":
#     # Train the model
#     trained_model = train_model()
    
#     # Save the trained model
#     save_model(trained_model)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    logging.info("Starting training process...")
    trained_model = train_model()
    save_model(trained_model)
    logging.info("Training process complete.")

if __name__ == "__main__":
    main()
