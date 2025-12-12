from modifier import seper
from .generator import model

# Load model once at import time so it is reused for all requests
# Using None for model_name relies on defaults in model.py (likely DeepSeek-Coder-1.3B)
_tokenizer, _llm, _device = model.load_model(model_name=None)


def generate_code_from_raw_text(raw_text: str) -> dict:
    """
    Final end-to-end method.

    Input  : raw natural language (possibly with some pseudo / code mixed in)
    Output : JSON unit from the model (includes 'code' field you can show)

    This is what your browser should ultimately call.
    """

    # 1) Split the text into description + code using your separator
    split = seper.process_string(raw_text)  # {'non_code': ..., 'code': ...}

    seper_data = {
        "non_code_text": split.get("non_code", ""),
        "code_text": split.get("code", ""),
    }

    # 2) Build the LLM prompt
    prompt = model.build_prompt_from_seper_output(seper_data)

    # 3) Call the DeepSeek model
    raw_output = model.generate_with_prompt(
        tokenizer=_tokenizer,
        model=_llm,
        device=_device,
        formatted_prompt=prompt,
    )

    # 4) Parse JSON and save to global file (optional)
    json_unit = model.parse_model_json_output(raw_output)
    # Ensure output directory exists is handled by save_generated_output or externally
    model.save_generated_output(json_unit, output_dir="output")

    # 5) Return everything; frontend will use json_unit["code"]
    return json_unit
