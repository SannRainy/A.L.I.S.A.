import os
import sys
import uuid
import random

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.supabase_client import supabase

def check_signup():
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    print(f"Testing signup for {email}...")
    try:
        response = supabase.auth.sign_up({"email": email, "password": "DummyPassword123!"})
        if response.user:
            print("Success! User ID:", response.user.id)
            # Try updating the profile
            data = {"full_name": "Test User", "age": 25, "gender": "male"}
            upd = supabase.table("profiles").update(data).eq("id", response.user.id).execute()
            print("Profile updated:", upd)
        else:
            print("No user returned")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    check_signup()
