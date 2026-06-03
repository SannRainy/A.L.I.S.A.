import os
import sys
import uuid
import random

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.supabase_client import supabase

def create_dummies():
    genders = ["male", "female", "male", "female", "prefer_not_to_say"]
    countries = ["Indonesia", "Indonesia", "Indonesia", "Jepang", "Malaysia", "Singapura", "Amerika", "Australia"]
    purposes = ["akademik", "kerja", "hobi", "hobi", "wisata", "kerja", "lainnya"]
    levels = ["beginner", "beginner", "basic", "intermediate"]
    
    print("Mulai insert data dummy ke database...")
    
    dummy_users = []
    
    for i in range(50): # 50 random users
        user_uuid = uuid.uuid4().hex[:8]
        email = f"dummy_{user_uuid}@example.com"
        
        try:
            # 1. Create auth user (trigger akan otomatis buat profile)
            user = supabase.auth.admin.create_user({
                "email": email,
                "password": "Password123!",
                "email_confirm": True
            })
            user_id = user.user.id
            dummy_users.append(user_id)
            
            # 2. Update profile dengan data random
            age = random.randint(15, 45)
            xp = random.randint(0, 1500)
            level = (xp // 100) + 1
            
            data = {
                "full_name": f"User Dummy {i+1}",
                "age": age,
                "gender": random.choice(genders),
                "country": random.choice(countries),
                "study_purpose": random.choice(purposes),
                "japanese_level": random.choice(levels),
                "xp": xp,
                "level": level,
            }
            
            supabase.table("profiles").update(data).eq("id", user_id).execute()
            print(f"Berhasil create profile {i+1}/50: {email}")
            
        except Exception as e:
            print(f"Gagal create profile {i+1}: {e}")

    # Generate some random chat_logs
    modes = ["discovery", "discovery", "quiz", "quiz", "roleplay"]
    for _ in range(150):
        if not dummy_users: break
        user_id = random.choice(dummy_users)
        mode = random.choice(modes)
        log = {
            "user_id": user_id,
            "role": "user",
            "content": f"Pesan percakapan simulasi {uuid.uuid4().hex[:4]}",
            "mode": mode
        }
        try:
            supabase.table("chat_logs").insert(log).execute()
        except Exception as e:
            pass
            
    # Generate some random quest scores
    quests = ["level_1", "level_2", "level_3", "boss_1"]
    for _ in range(100):
        if not dummy_users: break
        user_id = random.choice(dummy_users)
        quest = random.choice(quests)
        score = random.randint(40, 100)
        qdata = {
            "user_id": user_id,
            "level_id": quest,
            "score": score
        }
        try:
            supabase.table("user_quests").insert(qdata).execute()
        except Exception as e:
            pass

    print("Selesai insert data dummy!")

if __name__ == "__main__":
    create_dummies()
