import { writable } from 'svelte/store';
import { supabase } from '../lib/supabase';
import { clearChat } from './chat_store';

export const user = writable(null);
export const session = writable(null);

export const initAuth = async () => {
    const { data } = await supabase.auth.getSession();
    session.set(data.session);
    user.set(data.session?.user ?? null);

    supabase.auth.onAuthStateChange((_event, _session) => {
        session.set(_session);
        user.set(_session?.user ?? null);
    });
};

export const login = async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw error;
    return data.user;
};

export const register = async (email, password, metadata = {}) => {
    const response = await fetch("http://localhost:8000/api/v1/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            email,
            password,
            full_name: metadata.full_name || "",
            age: metadata.age || null,
            gender: metadata.gender || "prefer_not_to_say",
            country: metadata.country || "Indonesia",
            study_purpose: metadata.study_purpose || "",
            japanese_level: metadata.japanese_level || "beginner",
        })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Registrasi gagal.");
};

export const logout = async () => {
    await supabase.auth.signOut();
    if (typeof window !== "undefined") {
        localStorage.removeItem("tvjp_is_demo_mode");
        window.location.reload();
    }
};
