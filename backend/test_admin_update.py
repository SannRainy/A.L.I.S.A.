import os
import sys
import uuid

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.supabase_client import supabase

def check_admin_update():
    print("Testing admin create and update...")
    try:
        user = supabase.auth.admin.create_user({
            "email": f"dummy_{uuid.uuid4().hex[:8]}@example.com",
            "password": "Password123!",
            "email_confirm": True
        })
        print("Created User ID:", user.user.id)
        
        # Try updating the profile using the same client
        data = {"full_name": "Test Update Admin", "age": 30, "gender": "female", "country": "Jepang"}
        upd = supabase.table("profiles").update(data).eq("id", user.user.id).execute()
        print("Profile updated:", upd)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    check_admin_update()
