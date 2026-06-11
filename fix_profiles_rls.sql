-- =========================================================================
-- SQL FIX FOR "infinite recursion detected in policy for relation profiles"
-- JALANKAN DI SUPABASE SQL EDITOR
-- SCRIPT INI AMAN & MEMPERBAIKI BUG REKURSI RLS PADA TABEL PROFILES
-- =========================================================================

-- 1. Buat fungsi helper untuk mengecek role admin secara aman
-- SECURITY DEFINER membuat fungsi ini berjalan melewati RLS (bypassing RLS)
CREATE OR REPLACE FUNCTION public.is_admin(user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM public.profiles
    WHERE id = user_id AND role = 'admin'
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Hapus policy lama pada profiles
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;

-- 3. Buat policy baru tanpa rekursi menggunakan helper is_admin
CREATE POLICY "Users can view own profile" ON public.profiles 
  FOR SELECT USING (
    auth.uid() = id
    OR public.is_admin(auth.uid())
  );

-- 4. Perbarui policy pada chat_logs agar menggunakan helper is_admin
DROP POLICY IF EXISTS "Users can view own chat logs" ON public.chat_logs;
CREATE POLICY "Users can view own chat logs" ON public.chat_logs 
  FOR SELECT USING (
    auth.uid() = user_id
    OR public.is_admin(auth.uid())
  );

-- 5. Perbarui policy pada user_quests agar menggunakan helper is_admin
DROP POLICY IF EXISTS "Users can view own quests" ON public.user_quests;
CREATE POLICY "Users can view own quests" ON public.user_quests 
  FOR SELECT USING (
    auth.uid() = user_id
    OR public.is_admin(auth.uid())
  );

-- 6. Perbarui policy pada ab_test_groups agar menggunakan helper is_admin
DROP POLICY IF EXISTS "Admin manage ab tests" ON public.ab_test_groups;
CREATE POLICY "Admin manage ab tests" ON public.ab_test_groups
  FOR ALL USING (
    public.is_admin(auth.uid())
    OR auth.uid() = user_id
  );

-- 7. Reload cache skema PostgREST agar policy baru langsung dikenali oleh API
NOTIFY pgrst, 'reload schema';
