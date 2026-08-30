from transformers import pipeline

smollm = pipeline(
    "text-generation",
    model="HuggingFaceTB/SmolLM2-360M-Instruct"
)

print("Obtendo resposta...")
response = smollm(
            "Explique o que é um LLM",
            clean_up_tokenization_spaces=False
            )

print(response)