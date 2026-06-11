-- =============================================================================
-- TVJP Migration V3 — All Feature Upgrades
-- SRS, Streaks, Learning Paths, Placement Test, Grammar Check, Reading, Writing
-- =============================================================================

-- 1. SRS Items — Spaced Repetition Schedule per item per user
CREATE TABLE IF NOT EXISTS public.srs_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  node_id TEXT NOT NULL,            -- Neo4j node id (Vocab/Grammar/Kanji)
  node_type TEXT NOT NULL,          -- 'vocab', 'grammar', 'kanji'
  easiness_factor FLOAT DEFAULT 2.5,
  interval_days INTEGER DEFAULT 1,
  repetitions INTEGER DEFAULT 0,
  next_review TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_reviewed TIMESTAMP WITH TIME ZONE,
  last_quality INTEGER,             -- 0-5 SM-2 quality rating
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, node_id)
);

-- 2. Study Streaks — Daily login/study tracking
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

-- 3. Learning Paths — Generated paths per user
CREATE TABLE IF NOT EXISTS public.learning_paths (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  path_name TEXT DEFAULT 'default',
  node_sequence JSONB NOT NULL,     -- ordered list of {node_id, node_type, status}
  target_level TEXT DEFAULT 'N5',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Placement Test Results
CREATE TABLE IF NOT EXISTS public.placement_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  total_score INTEGER NOT NULL,
  total_questions INTEGER NOT NULL,
  estimated_level TEXT NOT NULL,    -- 'absolute_beginner', 'N5_low', 'N5_mid', 'N5_high'
  category_scores JSONB,           -- { "kanji": 3, "vocab": 5, "grammar": 4, "listening": 2 }
  placed_nodes JSONB,              -- node_ids marked as MASTERED based on placement
  taken_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id)                  -- one placement per user
);

-- 5. Grammar Check Logs
CREATE TABLE IF NOT EXISTS public.grammar_checks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  input_text TEXT NOT NULL,
  analysis JSONB,                  -- parsed tokens, errors found, corrections
  score FLOAT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Reading Sessions
CREATE TABLE IF NOT EXISTS public.reading_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  passage_id TEXT NOT NULL,
  unknown_words JSONB,             -- words user didn't know
  comprehension_score INTEGER,
  time_spent_seconds INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. Writing Submissions
CREATE TABLE IF NOT EXISTS public.writing_submissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  prompt TEXT NOT NULL,
  user_text TEXT NOT NULL,
  grammar_feedback JSONB,
  overall_score FLOAT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. Daily Goals Configuration
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

-- 9. A/B Test Groups (Admin)
CREATE TABLE IF NOT EXISTS public.ab_test_groups (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  test_name TEXT NOT NULL,
  group_label TEXT NOT NULL,        -- 'control', 'treatment_a', 'treatment_b'
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  config JSONB,                     -- custom config per group
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(test_name, user_id)
);

-- ── Add new columns to profiles ──────────────────────────────────────────
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS streak_days INTEGER DEFAULT 0;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS last_active_date DATE;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS longest_streak INTEGER DEFAULT 0;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS placement_completed BOOLEAN DEFAULT FALSE;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS preferred_study_mode TEXT DEFAULT 'discovery';

-- ── RLS for new tables ──────────────────────────────────────────────────
ALTER TABLE public.srs_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.study_streaks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.learning_paths ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.placement_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.grammar_checks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reading_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.writing_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daily_goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ab_test_groups ENABLE ROW LEVEL SECURITY;

-- ── RLS Policies ────────────────────────────────────────────────────────
-- SRS Items
CREATE POLICY "Users manage own SRS" ON public.srs_items
  FOR ALL USING (auth.uid() = user_id);

-- Study Streaks
CREATE POLICY "Users manage own streaks" ON public.study_streaks
  FOR ALL USING (auth.uid() = user_id);

-- Learning Paths
CREATE POLICY "Users manage own paths" ON public.learning_paths
  FOR ALL USING (auth.uid() = user_id);

-- Placement Results
CREATE POLICY "Users manage own placement" ON public.placement_results
  FOR ALL USING (auth.uid() = user_id);

-- Grammar Checks
CREATE POLICY "Users manage own grammar checks" ON public.grammar_checks
  FOR ALL USING (auth.uid() = user_id);

-- Reading Sessions
CREATE POLICY "Users manage own reading" ON public.reading_sessions
  FOR ALL USING (auth.uid() = user_id);

-- Writing Submissions
CREATE POLICY "Users manage own writing" ON public.writing_submissions
  FOR ALL USING (auth.uid() = user_id);

-- Daily Goals
CREATE POLICY "Users manage own goals" ON public.daily_goals
  FOR ALL USING (auth.uid() = user_id);

-- A/B Test Groups (admin read all, users read own)
CREATE POLICY "Admin manage ab tests" ON public.ab_test_groups
  FOR ALL USING (
    EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
    OR auth.uid() = user_id
  );

-- ── Indexes for performance ─────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_srs_items_due ON public.srs_items(user_id, next_review);
CREATE INDEX IF NOT EXISTS idx_srs_items_node ON public.srs_items(user_id, node_id);
CREATE INDEX IF NOT EXISTS idx_study_streaks_date ON public.study_streaks(user_id, study_date);
CREATE INDEX IF NOT EXISTS idx_learning_paths_user ON public.learning_paths(user_id);
CREATE INDEX IF NOT EXISTS idx_grammar_checks_user ON public.grammar_checks(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_reading_sessions_user ON public.reading_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_writing_submissions_user ON public.writing_submissions(user_id);

-- ── Reload schema ───────────────────────────────────────────────────────
NOTIFY pgrst, 'reload schema';
