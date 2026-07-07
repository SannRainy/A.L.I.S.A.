import os

target = r"c:\Users\satya\OneDrive\Desktop\TVJP\Feature.md"

tahap3_content = """

---

## Tahap 3: Pemetaan Antarmuka Visual (SvelteKit Frontend)

Sisi klien dibangun menggunakan *framework* SvelteKit yang menerapkan konsep *Single Page Application* (SPA) dengan pendekatan *Component-Driven*. Seluruh fitur utama (User) dipusatkan di root routing (`/`), sedangkan operasi administratif diisolasi secara absolut di rute `/admin`.

### 1. Rute Utama (User Dashboard - `/`)
File utama `src/routes/+page.svelte` bertindak sebagai pengontrol status (*state controller*) yang me-render komponen spesifik secara dinamis berdasarkan navigasi sesi pengguna, tanpa melakukan muat ulang (*reload*) halaman. Berikut pemetaan komponen pembentuk fitur utama:

#### A. Modul Evaluasi & Pembelajaran (Quest & Ujian)
- **`PlacementTest.svelte`**: Tampilan interaktif untuk mengevaluasi siswa baru.
- **`QuestMap.svelte`**: Peta rute visual gamifikasi (*Node Graph View*).
- **`QuestEngine.svelte` & `QuestMode.svelte`**: Area kerja interaktif tempat soal pilihan ganda, *drag-drop*, atau isian LLM dirender.
- **`QuestResult.svelte`**: Layar *summary* XP, naik level, dan persentase BKT (*Mastery*) usai kuis.
- **`ExamEngine.svelte`**: Mode ujian tertutup yang lebih formal.

#### B. Modul Interaksi & Latihan Keterampilan
- **`VoiceMode.svelte`**: Modul *flagship* yang menampung Model 3D Avatar (VRM). Komponen ini secara konstan bertukar aliran audio (STT & TTS) dengan backend untuk percakapan lisan waktu-nyata (*real-time*).
- **`KanjiStudyMode.svelte` & `KanjiFlashcard.svelte`**: Area spesifik untuk mencoret (*strokes*) dan menghafal *onyomi*/*kunyomi* karakter Kanji.
- **`ReadingMode.svelte`**: Antarmuka untuk membaca paragraf bahasa Jepang komprehensif.

#### C. Modul Visualisasi Progres & Gamifikasi
- **`Profile.svelte`**: Halaman biodata dan konfigurasi *Daily Goal*.
- **`MasteryPath.svelte`**: Visualisasi pohon keterampilan (*skill tree*) dari graf Neo4j.
- **`Achievement.svelte` & `AchievementBadges.svelte`**: Galeri medali/lencana penghargaan yang terbuka berdasarkan *quest*.
- **`EquippedEmblems.svelte`**: *Title* kehormatan (contoh: "Ronin", "Samurai") yang disematkan di sebelah avatar pengguna.
- **`RadarChart.svelte`**: Grafik jaring laba-laba untuk menampilkan penguasaan kategori linguistik.

### 2. Rute Terisolasi (Admin Dashboard - `/admin`)
Panel khusus ini memiliki perlindungan otorisasi yang terikat langsung pada tabel Supabase. Dirancang menggunakan desain modular bertab (*Tabbed Layout*):
- **`UsersTab.svelte`**: Tabel pengawasan daftar murid (metrik login, statistik BKT per individu).
- **`AiModelsTab.svelte`**: Panel operasional (*switch*) untuk mengganti atau mematikan model LLM/TTS di VRAM *backend*.
- **`DataPipelineTab.svelte` & `IngestTab.svelte`**: Panel krusial (*Root Feature*) di mana Admin dapat mengunggah CSV tabel kurikulum baru dan menekan tombol *Ingest* yang mengeksekusi skrip Python Neo4j di backend tanpa perlu mematikan peladen.
- **`AnalyticsTab.svelte`**: Layar visualisasi data agregat performa sistem, *A/B Test results*, dan kepadatan *Traffic*.
"""

with open(target, 'a', encoding='utf-8') as f:
    f.write(tahap3_content)

print("Tahap 3 berhasil ditambahkan!")
