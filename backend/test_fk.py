import os
import sys
import uuid

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.supabase_client import supabase

def check_fk():
    user_id = str(uuid.uuid4())
    data = {
        "id": user_id,
        "username": "test_dummy",
        "email": "test_dummy@example.com",
        "full_name": "Test Dummy",
        "role": "student",
    }
    print("Testing insert to profiles...")
    try:
        response = supabase.table("profiles").insert(data).execute()
        print("Success:", response)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    check_fk()
