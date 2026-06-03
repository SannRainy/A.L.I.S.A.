-- =========================================================================
-- MIGRATION SCRIPT FOR TVJP DATABASE SCHEMA (V2 - DEMOGRAPHICS & ADMIN)
-- JALANKAN DI SUPABASE SQL EDITOR
-- SCRIPT INI AMAN & TIDAK MENGHAPUS DATA USER YANG SUDAH ADA (NO DROP TABLES)
-- =========================================================================

-- 1. Tambah kolom demographics & role ke tabel profiles yang sudah ada
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS age INTEGER;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS gender TEXT DEFAULT 'prefer_not_to_say';
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS country TEXT DEFAULT 'Indonesia';
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS study_purpose TEXT;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS japanese_level TEXT DEFAULT 'beginner';
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'student';

-- 2. Update trigger function handle_new_user agar merekam metadata registrasi baru
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  BEGIN
    INSERT INTO public.profiles (
      id, email, username, full_name,
      age, gender, country, study_purpose, japanese_level,
      role, xp, level
    )
    VALUES (
      new.id,
      new.email,
      COALESCE(new.raw_user_meta_data->>'username', split_part(new.email, '@', 1)),
      COALESCE(new.raw_user_meta_data->>'full_name', 'User Baru'),
      (new.raw_user_meta_data->>'age')::INTEGER,
      COALESCE(new.raw_user_meta_data->>'gender', 'prefer_not_to_say'),
      COALESCE(new.raw_user_meta_data->>'country', 'Indonesia'),
      new.raw_user_meta_data->>'study_purpose',
      COALESCE(new.raw_user_meta_data->>'japanese_level', 'beginner'),
      'student',
      0,
      1
    )
    ON CONFLICT (id) DO NOTHING;
  EXCEPTION
    WHEN OTHERS THEN
      RAISE LOG 'handle_new_user error: %', SQLERRM;
  END;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. Hapus dan re-create trigger untuk memastikan menggunakan fungsi terbaru
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- 4. Update RLS Policies agar admin bisa memonitor semua data
-- Drop policies lama jika ada, lalu create ulang dengan admin bypass
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
CREATE POLICY "Users can view own profile" ON public.profiles 
  FOR SELECT USING (
    auth.uid() = id
    OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
  );

DROP POLICY IF EXISTS "Users can view own chat logs" ON public.chat_logs;
CREATE POLICY "Users can view own chat logs" ON public.chat_logs 
  FOR SELECT USING (
    auth.uid() = user_id
    OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
  );

DROP POLICY IF EXISTS "Users can view own quests" ON public.user_quests;
CREATE POLICY "Users can view own quests" ON public.user_quests 
  FOR SELECT USING (
    auth.uid() = user_id
    OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
  );

-- 5. SET Krisna Satya sebagai Super Admin Pertama
UPDATE public.profiles 
SET role = 'admin' 
WHERE email = 'krisnasatyaarisandy@gmail.com';

-- 6. Reload cache skema PostgREST agar kolom baru langsung dikenali oleh API
NOTIFY pgrst, 'reload schema';
