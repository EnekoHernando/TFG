from transformers import AutoModelForCausalLM, AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
input_text = "Hello, how are you?"
input_ids = tokenizer.encode(input_text + tokenizer.eos_token, return_tensors="pt")
output = model.generate(input_ids, max_length=50)
response = tokenizer.decode(output[:, input_ids.shape[-1]:][0], skip_special_tokens=True)
print(response)
