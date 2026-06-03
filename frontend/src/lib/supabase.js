import { createClient } from '@supabase/supabase-js'

// Mengambil variabel dari .env (Vite context)
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

// Validasi sederhana agar tidak error jika env belum terpasang
if (!supabaseUrl || !supabaseAnonKey) {
    console.error("⚠️ Supabase URL atau Anon Key hilang di file .env!")
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)