import os
import sys
import uuid
import random

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.supabase_client import supabase

def check_admin_auth():
    print("Testing admin create_user...")
    try:
        user = supabase.auth.admin.create_user({
            "email": f"dummy_{uuid.uuid4().hex[:8]}@example.com",
            "password": "Password123!",
            "email_confirm": True,
            "user_metadata": {"full_name": "Test User"}
        })
        print("Success:", user)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    check_admin_auth()
