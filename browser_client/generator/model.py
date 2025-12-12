def load_model(model_name=None):
    print("WARNING: Using stub load_model. Real model.py is missing.")
    return None, None, "cpu"

def build_prompt_from_seper_output(data):
    return "STUB PROMPT"

def generate_with_prompt(tokenizer, model, device, formatted_prompt):
    import json
    return json.dumps({"code": "print('Hello from stub')", "non_code": "Stub output"})

def parse_model_json_output(raw_output):
    import json
    try:
        return json.loads(raw_output)
    except:
        return {}

def save_generated_output(json_unit, output_dir="output"):
    print(f"Stub save to {output_dir}")

def mock_generate_json_unit(data):
    return {}
