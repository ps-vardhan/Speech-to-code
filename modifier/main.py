import json
import seper
import sys

def interactive_mode():
    print("--- Interactive Mode ---")
    print("Type your text and press Enter to see the split result.")
    print("Type 'exit' or 'quit' to stop.\n")
    
    while True:
        try:
            # Use input() to get text from user
            text = input("Input > ")
            
            if text.lower() in ("exit", "quit"):
                print("Exiting...")
                break
                
            if not text:
                continue
                
            result = seper.process_string(text)
            print("Output:", json.dumps(result, indent=2))
            print("-" * 20)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

def run_tests():
    # Keep the hardcoded tests for quick verification if needed
    test_cases = [
        "This is chat text now the code function foo() {}",
        "Just chat no code at all here.",
    ]
    print("\n--- Running Quick Check ---")
    for text in test_cases:
        res = seper.process_string(text)
        print(f"In: {text!r} -> Code start: {res['code'][:15]}...")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        interactive_mode()
