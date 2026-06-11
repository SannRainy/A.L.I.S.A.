-- =============================================================================
-- SQL ROLLBACK — Clean Up Database for Deleted/Rolled-back Features
-- Drops tables and columns for SRS, Streaks, KG, Placement, Grammar, and Writing.
-- KEEPING ACTIVE FEATURES: Reading Comprehension is preserved.
-- =============================================================================

-- 1. Drop tables for deleted features (cascade drops related policies & indexes)
DROP TABLE IF EXISTS public.srs_items CASCADE;
DROP TABLE IF EXISTS public.writing_submissions CASCADE;
DROP TABLE IF EXISTS public.ab_test_groups CASCADE;
DROP TABLE IF EXISTS public.grammar_checks CASCADE;
DROP TABLE IF EXISTS public.study_streaks CASCADE;
DROP TABLE IF EXISTS public.daily_goals CASCADE;
DROP TABLE IF EXISTS public.placement_results CASCADE;
DROP TABLE IF EXISTS public.learning_paths CASCADE;

-- 2. Drop columns added to profiles for the rolled-back features
ALTER TABLE public.profiles DROP COLUMN IF EXISTS streak_days;
ALTER TABLE public.profiles DROP COLUMN IF EXISTS last_active_date;
ALTER TABLE public.profiles DROP COLUMN IF EXISTS longest_streak;
ALTER TABLE public.profiles DROP COLUMN IF EXISTS placement_completed;
ALTER TABLE public.profiles DROP COLUMN IF EXISTS preferred_study_mode;

-- 3. Reload schema cache for PostgREST
NOTIFY pgrst, 'reload schema';
