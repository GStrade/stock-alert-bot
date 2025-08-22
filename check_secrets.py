import os

def main():
    token = os.getenv("TOKEN_STOCKS")
    chat_id = os.getenv("CHAT_ID")

    print("=== בדיקת טעינת Secrets ===")
    if not token:
        print("❌ TOKEN_STOCKS לא נטען")
    else:
        print(f"✅ TOKEN_STOCKS נטען (אורך: {len(token)} תווים)")

    if not chat_id:
        print("❌ CHAT_ID לא נטען")
    else:
        print(f"✅ CHAT_ID נטען: {chat_id}")

if __name__ == "__main__":
    main()
