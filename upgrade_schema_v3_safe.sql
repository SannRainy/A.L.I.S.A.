-- =========================================================================
-- SAFE DATABASE UPGRADE SCHEMA SCRIPT (V3 - ALL FEATURES)
-- JALANKAN DI SUPABASE SQL EDITOR
-- SCRIPT INI AMAN & TIDAK MENGHAPUS DATA LAMA (NO DROP FOR EXISTING TABLES)
-- =========================================================================

-- 1. Helper function is_admin (Mencegah error infinite recursion pada RLS profiles)
CREATE OR REPLACE FUNCTION public.is_admin(user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM public.profiles
    WHERE id = user_id AND role = 'admin'
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Tambah kolom-kolom baru ke tabel profiles jika belum ada
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS streak_days INTEGER DEFAULT 0;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS last_active_date DATE;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS longest_streak INTEGER DEFAULT 0;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS placement_completed BOOLEAN DEFAULT FALSE;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS preferred_study_mode TEXT DEFAULT 'discovery';

-- Set default value untuk baris data lama yang bernilai NULL
UPDATE public.profiles SET streak_days = 0 WHERE streak_days IS NULL;
UPDATE public.profiles SET longest_streak = 0 WHERE longest_streak IS NULL;
UPDATE public.profiles SET placement_completed = FALSE WHERE placement_completed IS NULL;
UPDATE public.profiles SET preferred_study_mode = 'discovery' WHERE preferred_study_mode IS NULL;

-- 3. Buat tabel-tabel baru untuk seluruh fitur proyek (jika belum ada)

-- A. SRS Items (Spaced Repetition System)
CREATE TABLE IF NOT EXISTS public.srs_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  node_id TEXT NOT NULL,            -- Neo4j node id (Vocab/Grammar/Kanji)
  node_type TEXT NOT NULL,          -- 'vocab', 'grammar', 'kanji'
  easiness_factor FLOAT8 DEFAULT 2.5,
  interval_days INTEGER DEFAULT 1,
  repetitions INTEGER DEFAULT 0,
  next_review TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_reviewed TIMESTAMP WITH TIME ZONE,
  last_quality INTEGER,             -- 0-5 SM-2 quality rating
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, node_id)
);

-- B. Study Streaks (Daily login/study tracker)
CREATE TABLE IF NOT EXISTS public.study_streaks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  study_date DATE NOT NULL DEFAULT CURRENT_DATE,
  study_minutes INTEGER DEFAULT 0,
  items_reviewed INTEGER DEFAULT 0,
  quests_completed INTEGER DEFAULT 0,
  xp_earned INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, study_date)
);

-- C. Learning Paths (Rekomendasi Jalur Belajar Graf)
CREATE TABLE IF NOT EXISTS public.learning_paths (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  path_name TEXT DEFAULT 'default',
  node_sequence JSONB NOT NULL,     -- Urutan node_id, node_type, status
  target_level TEXT DEFAULT 'N5',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- D. Placement Test Results (Hasil Tes Penempatan Awal)
CREATE TABLE IF NOT EXISTS public.placement_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  total_score INTEGER NOT NULL,
  total_questions INTEGER NOT NULL,
  estimated_level TEXT NOT NULL,    -- e.g. 'absolute_beginner', 'N5_low', etc.
  category_scores JSONB,           -- Detail skor per kategori
  placed_nodes JSONB,              -- Node yang ditandai MASTERED otomatis
  taken_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id)
);

-- E. Grammar Check Logs (Riwayat Pengecekan Tata Bahasa)
CREATE TABLE IF NOT EXISTS public.grammar_checks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  input_text TEXT NOT NULL,
  analysis JSONB,                  -- Token parser, kesalahan, & koreksi
  score FLOAT8,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- F. Writing Submissions (Tugas Menulis Kreatif harian)
CREATE TABLE IF NOT EXISTS public.writing_submissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  prompt TEXT NOT NULL,
  user_text TEXT NOT NULL,
  grammar_feedback JSONB,
  overall_score FLOAT8,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- G. Daily Goals Configuration (Target Belajar Harian Siswa)
CREATE TABLE IF NOT EXISTS public.daily_goals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  vocab_target INTEGER DEFAULT 10,
  grammar_target INTEGER DEFAULT 2,
  review_target INTEGER DEFAULT 5,
  study_minutes_target INTEGER DEFAULT 15,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id)
);

-- H. A/B Test Groups (Pengelompokan uji coba riset)
CREATE TABLE IF NOT EXISTS public.ab_test_groups (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  test_name TEXT NOT NULL,
  group_label TEXT NOT NULL,        -- 'control', 'treatment_a', 'treatment_b'
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  config JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(test_name, user_id)
);

-- I. Reading Sessions (Memastikan struktur tabel ada & aman)
CREATE TABLE IF NOT EXISTS public.reading_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  passage_id TEXT NOT NULL,
  unknown_words JSONB,
  comprehension_score INTEGER,
  time_spent_seconds INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Enable Row Level Security (RLS) pada seluruh tabel
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wiki_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_quests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reading_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.srs_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.study_streaks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.learning_paths ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.placement_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.grammar_checks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.writing_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daily_goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ab_test_groups ENABLE ROW LEVEL SECURITY;

-- 5. Perbarui / Buat RLS Policies secara bersih (menggunakan DROP & CREATE)

-- Profiles
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
CREATE POLICY "Users can view own profile" ON public.profiles 
  FOR SELECT USING (auth.uid() = id OR public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile" ON public.profiles 
  FOR UPDATE USING (auth.uid() = id);

DROP POLICY IF EXISTS "Allow insert for trigger" ON public.profiles;
CREATE POLICY "Allow insert for trigger" ON public.profiles 
  FOR INSERT WITH CHECK (true);

-- Chat Logs
DROP POLICY IF EXISTS "Users can view own chat logs" ON public.chat_logs;
CREATE POLICY "Users can view own chat logs" ON public.chat_logs 
  FOR SELECT USING (auth.uid() = user_id OR public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Users can insert own chat logs" ON public.chat_logs;
CREATE POLICY "Users can insert own chat logs" ON public.chat_logs 
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Wiki Notes
DROP POLICY IF EXISTS "Users can view own wiki notes" ON public.wiki_notes;
CREATE POLICY "Users can view own wiki notes" ON public.wiki_notes 
  FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own wiki notes" ON public.wiki_notes;
CREATE POLICY "Users can insert own wiki notes" ON public.wiki_notes 
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Achievements
DROP POLICY IF EXISTS "Users can view own achievements" ON public.achievements;
CREATE POLICY "Users can view own achievements" ON public.achievements 
  FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own achievements" ON public.achievements;
CREATE POLICY "Users can insert own achievements" ON public.achievements 
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- User Quests
DROP POLICY IF EXISTS "Users can view own quests" ON public.user_quests;
CREATE POLICY "Users can view own quests" ON public.user_quests 
  FOR SELECT USING (auth.uid() = user_id OR public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Users can insert own quests" ON public.user_quests;
CREATE POLICY "Users can insert own quests" ON public.user_quests 
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Reading Sessions
DROP POLICY IF EXISTS "Users manage own reading" ON public.reading_sessions;
CREATE POLICY "Users manage own reading" ON public.reading_sessions
  FOR ALL USING (auth.uid() = user_id);

-- SRS Items
DROP POLICY IF EXISTS "Users manage own SRS" ON public.srs_items;
CREATE POLICY "Users manage own SRS" ON public.srs_items
  FOR ALL USING (auth.uid() = user_id);

-- Study Streaks
DROP POLICY IF EXISTS "Users manage own streaks" ON public.study_streaks;
CREATE POLICY "Users manage own streaks" ON public.study_streaks
  FOR ALL USING (auth.uid() = user_id);

-- Learning Paths
DROP POLICY IF EXISTS "Users manage own paths" ON public.learning_paths;
CREATE POLICY "Users manage own paths" ON public.learning_paths
  FOR ALL USING (auth.uid() = user_id);

-- Placement Results
DROP POLICY IF EXISTS "Users manage own placement" ON public.placement_results;
CREATE POLICY "Users manage own placement" ON public.placement_results
  FOR ALL USING (auth.uid() = user_id);

-- Grammar Checks
DROP POLICY IF EXISTS "Users manage own grammar checks" ON public.grammar_checks;
CREATE POLICY "Users manage own grammar checks" ON public.grammar_checks
  FOR ALL USING (auth.uid() = user_id);

-- Writing Submissions
DROP POLICY IF EXISTS "Users manage own writing" ON public.writing_submissions;
CREATE POLICY "Users manage own writing" ON public.writing_submissions
  FOR ALL USING (auth.uid() = user_id);

-- Daily Goals
DROP POLICY IF EXISTS "Users manage own goals" ON public.daily_goals;
CREATE POLICY "Users manage own goals" ON public.daily_goals
  FOR ALL USING (auth.uid() = user_id);

-- A/B Test Groups
DROP POLICY IF EXISTS "Admin manage ab tests" ON public.ab_test_groups;
CREATE POLICY "Admin manage ab tests" ON public.ab_test_groups
  FOR ALL USING (public.is_admin(auth.uid()) OR auth.uid() = user_id);

-- 6. Buat Index untuk Optimasi Performa Query (Jika belum ada)
CREATE INDEX IF NOT EXISTS idx_srs_items_due ON public.srs_items(user_id, next_review);
CREATE INDEX IF NOT EXISTS idx_srs_items_node ON public.srs_items(user_id, node_id);
CREATE INDEX IF NOT EXISTS idx_study_streaks_date ON public.study_streaks(user_id, study_date);
CREATE INDEX IF NOT EXISTS idx_learning_paths_user ON public.learning_paths(user_id);
CREATE INDEX IF NOT EXISTS idx_grammar_checks_user ON public.grammar_checks(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_reading_sessions_user ON public.reading_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_writing_submissions_user ON public.writing_submissions(user_id);

-- 7. Update Fungsi Trigger handle_new_user dengan Mapping Demografis
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

-- Re-create trigger trigger_on_auth_user_created
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- 8. Reload PostgREST Cache
NOTIFY pgrst, 'reload schema';
