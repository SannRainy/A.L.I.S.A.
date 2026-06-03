-- =========================
-- 1. HAPUS TABLE LAMA (OPTIONAL - CLEAN INSTALL)
-- =========================
DROP TABLE IF EXISTS public.chat_logs CASCADE;
DROP TABLE IF EXISTS public.wiki_notes CASCADE;
DROP TABLE IF EXISTS public.achievements CASCADE;
DROP TABLE IF EXISTS public.user_quests CASCADE;
DROP TABLE IF EXISTS public.profiles CASCADE;

-- =========================
-- 2. BUAT TABLE PROFILES (Extended with Demographics)
-- =========================
CREATE TABLE public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT,
  username TEXT NOT NULL,
  full_name TEXT DEFAULT 'User Baru',
  age INTEGER,
  gender TEXT DEFAULT 'prefer_not_to_say',
  country TEXT DEFAULT 'Indonesia',
  study_purpose TEXT,
  japanese_level TEXT DEFAULT 'beginner',
  role TEXT DEFAULT 'student',
  xp INTEGER DEFAULT 0,
  level INTEGER DEFAULT 1,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =========================
-- 3. BUAT TABEL GAMIFIKASI & WIKI (NEW MODULES)
-- =========================
CREATE TABLE public.chat_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  mode TEXT DEFAULT 'discovery',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE public.wiki_notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE public.achievements (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE public.user_quests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  level_id TEXT NOT NULL,
  score INTEGER NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =========================
-- 4. ENABLE RLS (ROW LEVEL SECURITY)
-- =========================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wiki_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_quests ENABLE ROW LEVEL SECURITY;

-- =========================
-- 5. RLS POLICIES (with Admin override)
-- =========================
-- PROFILES
CREATE POLICY "Users can view own profile" ON public.profiles FOR SELECT USING (
  auth.uid() = id
  OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);
CREATE POLICY "Users can update own profile" ON public.profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Allow insert for trigger" ON public.profiles FOR INSERT WITH CHECK (true);

-- CHAT LOGS
CREATE POLICY "Users can view own chat logs" ON public.chat_logs FOR SELECT USING (
  auth.uid() = user_id
  OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);
CREATE POLICY "Users can insert own chat logs" ON public.chat_logs FOR INSERT WITH CHECK (auth.uid() = user_id);

-- WIKI NOTES
CREATE POLICY "Users can view own wiki notes" ON public.wiki_notes FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own wiki notes" ON public.wiki_notes FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ACHIEVEMENTS
CREATE POLICY "Users can view own achievements" ON public.achievements FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own achievements" ON public.achievements FOR INSERT WITH CHECK (auth.uid() = user_id);

-- USER QUESTS
CREATE POLICY "Users can view own quests" ON public.user_quests FOR SELECT USING (
  auth.uid() = user_id
  OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);
CREATE POLICY "Users can insert own quests" ON public.user_quests FOR INSERT WITH CHECK (auth.uid() = user_id);

-- =========================
-- 6. HAPUS TRIGGER LAMA
-- =========================
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- =========================
-- 7. FUNCTION HANDLE NEW USER (with Demographics)
-- =========================
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

-- =========================
-- 8. BUAT TRIGGER
-- =========================
CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW
EXECUTE PROCEDURE public.handle_new_user();

-- =========================
-- 9. SET ADMIN (Jalankan setelah user terdaftar)
-- =========================
-- UPDATE public.profiles SET role = 'admin' WHERE email = 'krisnasatyaarisandy@gmail.com';

-- =========================
-- 10. MIGRATION SCRIPT (Untuk database yang sudah ada)
-- Jalankan ini jika tabel profiles sudah ada dan hanya ingin menambah kolom baru
-- =========================
-- ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS age INTEGER;
-- ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS gender TEXT DEFAULT 'prefer_not_to_say';
-- ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS country TEXT DEFAULT 'Indonesia';
-- ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS study_purpose TEXT;
-- ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS japanese_level TEXT DEFAULT 'beginner';
-- ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'student';

-- =========================
-- 11. RELOAD SCHEMA CACHE
-- =========================
NOTIFY pgrst, 'reload schema';
