from code_processor.codet5_handler import CodeT5Handler

def test_codet5_stub():
    h = CodeT5Handler()
    out = h.generate("hello")
    assert "[CodeT5 stub]" in out
