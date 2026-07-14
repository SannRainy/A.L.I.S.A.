import { writable } from 'svelte/store';
import { browser } from '$app/environment';

const initialTheme = browser ? (localStorage.getItem('tvjp_theme') || 'dark') : 'dark';
export const themeStore = writable(initialTheme);

if (browser) {
    themeStore.subscribe(value => {
        localStorage.setItem('tvjp_theme', value);
        if (value === 'light') {
            document.body.classList.add('light');
            document.body.classList.remove('dark');
        } else {
            document.body.classList.add('dark');
            document.body.classList.remove('light');
        }
    });
}
