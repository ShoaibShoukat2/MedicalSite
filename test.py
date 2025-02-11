from transformers import pipeline

chatbot = pipeline("text-generation", model="gpt2")
response = chatbot("Hello, how are you?", max_length=50)
print(response)
