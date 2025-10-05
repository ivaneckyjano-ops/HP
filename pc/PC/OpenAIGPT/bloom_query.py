import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "bigscience/bloom-560m"

# Load tokenizer and model (CPU)
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float32,
    device_map="cpu"
)
device = torch.device("cpu")
model.to(device)

# ---- Your question ----
prompt = "Enter your question here"

# Tokenization including attention_mask
inputs = tokenizer(prompt, return_tensors="pt")
input_ids = inputs["input_ids"].to(device)
attention_mask = inputs["attention_mask"].to(device)

# Generation (no gradients, shorter output)
with torch.no_grad():
    output_ids = model.generate(
        input_ids,
        attention_mask=attention_mask,
        max_new_tokens=80,
        do_sample=True,
        top_p=0.9,
        temperature=0.7,
        pad_token_id=tokenizer.eos_token_id,
        early_stopping=False
    )

# Decode and print
answer = tokenizer.decode(output_ids[0], skip_special_tokens=True)
print("\n=== Bloom‑560 Answer ===\n")
print(answer)