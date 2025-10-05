import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from bitsandbytes import BitsAndBytesConfig

# Path to the model directory
model_path = "bloom-560m"

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_path)

# 8-bit quantization configuration for CPU
bnb_config = BitsAndBytesConfig(
    load_in_8bit=True,
    # Other parameters can remain default for CPU
)

# Load model with quantization config
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    device_map="cpu",
    quantization_config=bnb_config,
    torch_dtype=torch.float16
)

model.eval()

def generate(prompt: str, max_new_tokens: int = 100) -> str:
    inputs = tokenizer(prompt, return_tensors="pt").to("cpu")
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            top_p=0.9,
            temperature=0.7,
            pad_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.decode(output[0], skip_special_tokens=True)

if __name__ == "__main__":
    user_prompt = "Explain the concept of quantum computing in simple terms."
    result = generate(user_prompt, max_new_tokens=150)
    print("\n=== Generated text ===\n")
    print(result)