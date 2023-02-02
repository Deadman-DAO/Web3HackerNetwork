from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch

# Initialize the tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

# Stream your text here
text_stream = [
    "This is the first sentence of the stream",
    "This is the second sentence of the stream",
    "This is the third sentence of the stream",
    # Add more sentences as needed
]

# Preprocess the text stream
input_ids = [tokenizer.encode(sent, return_tensors="pt") for sent in text_stream]

# Set the model in training mode
model.train()

# Define your optimizer and criterion
optimizer = torch.optim.Adam(model.parameters(), lr=2e-5)
criterion = torch.nn.CrossEntropyLoss()

# Train the model on the text stream
for i in range(num_steps):
    input_ids = torch.cat(input_ids, dim=0)
    outputs = model(input_ids, labels=input_ids)
    loss = outputs[0]
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()
