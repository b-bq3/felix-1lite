"""Interactive FELIX chat."""
import sys
import os
sys.path.insert(0, '/home/clawdbot/.openclaw/workspace/felix-1lite')
from felix import chat

print("=" * 60)
print("FELIX-1lite — Interactive Chat")
print("اكتب سؤالك بالعربية. اكتب 'خروج' أو 'quit' للإنهاء.")
print("=" * 60)

while True:
    try:
        user_input = input("\n> ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "خروج", "q"):
            print("وداعاً!")
            break
        response = chat(user_input, checkpoint="felix-demo.pt", max_tokens=100, temperature=0.7)
        print(f"\nFELIX: {response}")
    except KeyboardInterrupt:
        print("\nوداعاً!")
        break
    except Exception as e:
        print(f"\nخطأ: {e}")