from code_processor.codet5_handler import CodeT5Handler

if __name__ == "__main__":
    handler = CodeT5Handler()
    print(handler.generate("Translate comment to code"))
