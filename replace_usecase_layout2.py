import re

with open('laporan_analisis_sistem_tvjp.md', 'r', encoding='utf-8') as f:
    text = f.read()

start_uc = text.find('## B. Perancangan Sistem')
end_uc = text.find('### 2. Activity Diagram')

if start_uc == -1 or end_uc == -1:
    print('Boundaries not found')
    exit(1)

new_content = """## B. Perancangan Sistem

Perancangan sistem pada penelitian ini dilakukan untuk menggambarkan bentuk dan alur kerja aplikasi Tutor Virtual Bahasa Jepang (TVJP) "A.L.I.S.A." berbasis *Knowledge Graph* dan *local Large Language Model* (LLM) untuk pembelajaran terstruktur dan evaluasi adaptif. Perancangan sistem menggunakan *Unified Modeling Language* (UML) agar kebutuhan sistem, interaksi pengguna, proses kerja, dan struktur data dapat dijelaskan secara lebih terarah. Diagram yang digunakan dalam perancangan ini meliputi *Use Case Diagram*, Skenario *Use Case*, dan *Activity Diagram* yang memetakan seluruh aktivitas fungsional pengguna dan administrator.

### 1. Use Case Diagram

*Use Case Diagram* digunakan untuk menggambarkan fungsionalitas sistem yang diharapkan dari sudut pandang aktor. Dalam perancangan ini, diagram berfokus pada alur fungsionalitas murni yang dikendalikan oleh aktor, tanpa menyertakan entitas arsitektur *backend* (*database* atau *engine*) di dalam kanvas *Use Case* demi menjaga tingkat abstraksi standar UML. 

Aktor utama dalam sistem ini terdiri atas *Admin* (dosen atau peneliti) dan *User* (mahasiswa atau pembelajar mandiri). Hubungan interaksi `<<include>>` dan `<<extend>>` disematkan secara spesifik pada fitur yang memiliki dependensi prasyarat (seperti *Register* yang mewajibkan *Placement Test*) maupun fungsionalitas opsional tambahan. *Use Case Diagram* terintegrasi yang memetakan seluruh alur kerja sistem dapat dilihat pada kode XML berikut.

```xml
<mxfile host="app.diagrams.net">
  <diagram name="Use Case Diagram" id="usecase-page">
    <mxGraphModel dx="1200" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1100" pageHeight="900" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        
        <!-- System Boundary -->
        <mxCell id="boundary" value="Sistem Tutor Virtual Bahasa Jepang A.L.I.S.A." style="shape=rect;fillColor=none;strokeColor=#000000;verticalAlign=top;align=center;fontStyle=1;fontSize=14;" vertex="1" parent="1">
          <mxGeometry x="200" y="30" width="650" height="770" as="geometry" />
        </mxCell>

        <!-- Main Actors (Opposite sides for clean layout) -->
        <mxCell id="actor_admin" value="Admin" style="shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;" vertex="1" parent="1">
          <mxGeometry x="80" y="300" width="30" height="60" as="geometry" />
        </mxCell>
        <mxCell id="actor_user" value="User" style="shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;" vertex="1" parent="1">
          <mxGeometry x="930" y="380" width="30" height="60" as="geometry" />
        </mxCell>

        <!-- Admin Use Cases (Left Column) -->
        <mxCell id="uc_8" value="Manage AI Models" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="240" y="100" width="160" height="40" as="geometry" />
        </mxCell>
        <mxCell id="uc_4" value="Monitor Users" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="240" y="200" width="160" height="40" as="geometry" />
        </mxCell>
        <mxCell id="uc_7" value="View Analytics" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="240" y="300" width="160" height="40" as="geometry" />
        </mxCell>
        <mxCell id="uc_5" value="Manage CSV File" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="240" y="500" width="160" height="40" as="geometry" />
        </mxCell>
        <mxCell id="uc_6" value="Ingest Neo4j Graph Data" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="240" y="600" width="160" height="40" as="geometry" />
        </mxCell>

        <!-- Shared Use Cases (Center Column) -->
        <mxCell id="uc_2" value="Login" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="445" y="350" width="160" height="40" as="geometry" />
        </mxCell>
        <mxCell id="uc_3" value="Logout" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="445" y="450" width="160" height="40" as="geometry" />
        </mxCell>

        <!-- User Use Cases (Right Column) -->
        <mxCell id="uc_1" value="Register" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="650" y="80" width="160" height="40" as="geometry" />
        </mxCell>
        <mxCell id="uc_9" value="Take Placement Test" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="650" y="150" width="160" height="40" as="geometry" />
        </mxCell>
        <mxCell id="uc_17" value="Manage Profile" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="650" y="220" width="160" height="40" as="geometry" />
        </mxCell>
        <mxCell id="uc_16" value="View Achievements" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="650" y="290" width="160" height="40" as="geometry" />
        </mxCell>
        <mxCell id="uc_10" value="Complete Quest" style="ellipse;whiteSpace=wrap;html=1;fontStyle=1" vertex="1" parent="1">
          <mxGeometry x="650" y="360" width="160" height="40" as="geometry" />
        </mxCell>
        <mxCell id="uc_11" value="Take Exam" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="650" y="430" width="160" height="40" as="geometry" />
        </mxCell>
        <mxCell id="uc_12" value="Review SRS" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="650" y="500" width="160" height="40" as="geometry" />
        </mxCell>
        <mxCell id="uc_13" value="Practice Speaking" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="650" y="570" width="160" height="40" as="geometry" />
        </mxCell>
        <mxCell id="uc_14" value="Practice Reading" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="650" y="640" width="160" height="40" as="geometry" />
        </mxCell>
        <mxCell id="uc_15" value="Practice Kanji" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="650" y="710" width="160" height="40" as="geometry" />
        </mxCell>

        <!-- Connections from Admin -->
        <mxCell id="ea_1" edge="1" parent="1" source="actor_admin" target="uc_8"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="ea_2" edge="1" parent="1" source="actor_admin" target="uc_4"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="ea_3" edge="1" parent="1" source="actor_admin" target="uc_7"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="ea_4" edge="1" parent="1" source="actor_admin" target="uc_5"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="ea_5" edge="1" parent="1" source="actor_admin" target="uc_6"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="ea_6" edge="1" parent="1" source="actor_admin" target="uc_2"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="ea_7" edge="1" parent="1" source="actor_admin" target="uc_3"><mxGeometry relative="1" as="geometry" /></mxCell>

        <!-- Connections from User -->
        <mxCell id="eu_1" edge="1" parent="1" source="actor_user" target="uc_1"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="eu_2" edge="1" parent="1" source="actor_user" target="uc_9"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="eu_3" edge="1" parent="1" source="actor_user" target="uc_17"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="eu_4" edge="1" parent="1" source="actor_user" target="uc_16"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="eu_5" edge="1" parent="1" source="actor_user" target="uc_10"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="eu_6" edge="1" parent="1" source="actor_user" target="uc_11"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="eu_7" edge="1" parent="1" source="actor_user" target="uc_12"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="eu_8" edge="1" parent="1" source="actor_user" target="uc_13"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="eu_9" edge="1" parent="1" source="actor_user" target="uc_14"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="eu_10" edge="1" parent="1" source="actor_user" target="uc_15"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="eu_11" edge="1" parent="1" source="actor_user" target="uc_2"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="eu_12" edge="1" parent="1" source="actor_user" target="uc_3"><mxGeometry relative="1" as="geometry" /></mxCell>

        <!-- Includes and Extends Relations -->
        <!-- Ingest <<include>> Manage CSV -->
        <mxCell id="rel_1" edge="1" parent="1" source="uc_6" target="uc_5" style="endArrow=open;endSize=12;dashed=1;html=1;" value="&lt;&lt;include&gt;&gt;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <!-- View Analytics <<extend>> Monitor Users -->
        <mxCell id="rel_2" edge="1" parent="1" source="uc_7" target="uc_4" style="endArrow=open;endSize=12;dashed=1;html=1;" value="&lt;&lt;extend&gt;&gt;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <!-- Register <<include>> Placement Test -->
        <mxCell id="rel_4" edge="1" parent="1" source="uc_1" target="uc_9" style="endArrow=open;endSize=12;dashed=1;html=1;" value="&lt;&lt;include&gt;&gt;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

#### 1.1 Skenario Use Case

Skenario *use case* menjelaskan secara rinci alur interaksi antara aktor dengan sistem untuk setiap fitur yang didefinisikan dalam *Use Case Diagram*. Setiap skenario disusun dengan membagi antara deskripsi awal, aksi pengguna (*user action*), dan reaksi sistem (*system response*) secara padat.

##### 1.1.1 Skenario *Use Case Register*
| Nama Use Case | *Register* |
| :--- | :--- |
| **Aktor** | User |
| **Deskripsi** | Pengguna mendaftarkan akun baru dan data profil demografis awal. |
| **Reaksi Sistem** | Supabase memvalidasi kredensial, mencatat UUID, dan mengaktifkan *trigger* profil. |
| **Aksi Alur** | **Reaksi Sistem** |
| 1. Pengguna mengisi surel dan demografi. | Sistem memverifikasi format keamanan. |
| 2. Pengguna menekan tombol daftar. | Supabase menerbitkan tiket sesi (*token*). |
| 3. Pengguna masuk ke sesi baru. | Sistem mengarahkan ke halaman *Placement Test*. |

##### 1.1.2 Skenario *Use Case Login*
| Nama Use Case | *Login* |
| :--- | :--- |
| **Aktor** | User, Admin |
| **Deskripsi** | Aktor masuk ke dalam sistem menggunakan otentikasi. |
| **Reaksi Sistem** | Sistem membaca atribut peran (*role*) dan memberikan akses dasbor terkait. |
| **Aksi Alur** | **Reaksi Sistem** |
| 1. Aktor menginput surel dan sandi. | Sistem Auth Supabase memvalidasi kecocokan data. |
| 2. Aktor menekan tombol masuk. | Sistem memuat preferensi pengguna dari basis data. |
| 3. Aktor masuk dengan sukses. | Sistem mengarahkan alur berdasar *role* (Admin/Student). |

##### 1.1.3 Skenario *Use Case Logout*
| Nama Use Case | *Logout* |
| :--- | :--- |
| **Aktor** | User, Admin |
| **Deskripsi** | Aktor mengakhiri sesi aktif untuk alasan keamanan. |
| **Reaksi Sistem** | Sistem memusnahkan (*revoke*) token *browser* dan menyimpan progres. |
| **Aksi Alur** | **Reaksi Sistem** |
| 1. Aktor menekan menu keluar. | Sistem mengirim sinyal pemutusan ke *backend*. |
| 2. Aktor mengonfirmasi keluar. | Sistem membersihkan *cache* token di tingkat lokal. |
| 3. Sesi telah diakhiri. | Sistem menampilkan layar autentikasi kembali. |

##### 1.1.4 Skenario *Use Case Monitor Users*
| Nama Use Case | *Monitor Users* |
| :--- | :--- |
| **Aktor** | Admin |
| **Deskripsi** | Admin meninjau data BKT pengguna dan mengubah kelompok eksperimen (A/B Test). |
| **Reaksi Sistem** | Sistem membaca basis data relasional dan memperbarui tabel `ab_test_groups`. |
| **Aksi Alur** | **Reaksi Sistem** |
| 1. Admin melihat tabel murid di dasbor. | Sistem merender status penguasaan materi BKT setiap murid. |
| 2. Admin menetapkan kelompok eksperimen. | Sistem menyimpan alokasi riset (A/B) baru. |
| 3. Admin menyimpan konfigurasi. | Sistem memberlakukan limitasi eksperimen pada akun terkait. |

##### 1.1.5 Skenario *Use Case Manage CSV File*
| Nama Use Case | *Manage CSV File* |
| :--- | :--- |
| **Aktor** | Admin |
| **Deskripsi** | Admin meninjau dan mengunggah CSV kurikulum materi N5. |
| **Reaksi Sistem** | Sistem menimpa berkas pada struktur peladen melalui FastAPI. |
| **Aksi Alur** | **Reaksi Sistem** |
| 1. Admin memeriksa menu *Data Pipeline*. | Sistem menampilkan daftar file CSV kurikulum. |
| 2. Admin mengunggah berkas CSV. | Sistem mengeksekusi operasi penulisan IO ke direktori. |
| 3. Admin meninjau konten di tabel *web*. | Sistem merender sel dari CSV. |

##### 1.1.6 Skenario *Use Case Ingest Neo4j Graph Data*
| Nama Use Case | *Ingest Neo4j Graph Data* |
| :--- | :--- |
| **Aktor** | Admin |
| **Deskripsi** | Admin menyinkronkan data CSV menjadi simpul graf ke dalam Neo4j. |
| **Reaksi Sistem** | Modul `ingest_n5.py` dieksekusi secara asinkron di latar belakang. |
| **Aksi Alur** | **Reaksi Sistem** |
| 1. Admin menekan tombol eksekusi injeksi. | Sistem memanggil mesin *Knowledge Graph*. |
| 2. Admin mengamati log proses eksekusi. | Sistem merender baris log proses (*nodes* & *edges*). |
| 3. Admin menerima notifikasi selesai. | Basis data graf Neo4j berhasil terstruktur. |

##### 1.1.7 Skenario *Use Case View Analytics*
| Nama Use Case | *View Analytics* |
| :--- | :--- |
| **Aktor** | Admin |
| **Deskripsi** | Admin mengevaluasi grafik analitik untuk keperluan kuantitatif skripsi. |
| **Reaksi Sistem** | Sistem menjumlahkan metrik profil dan merender *chart*. |
| **Aksi Alur** | **Reaksi Sistem** |
| 1. Admin membuka dasbor statistik. | Sistem memuat ringkasan data lalu lintas sistem. |
| 2. Admin memfilter parameter grafik. | Sistem menghitung agregat dan merender diagram secara reaktif. |
| 3. Admin mengunduh data mentah riset. | Sistem menghasilkan arsip *export* format JSON/CSV. |

##### 1.1.8 Skenario *Use Case Manage AI Models*
| Nama Use Case | *Manage AI Models* |
| :--- | :--- |
| **Aktor** | Admin |
| **Deskripsi** | Admin merotasi model LLM/TTS untuk optimalisasi performa *server*. |
| **Reaksi Sistem** | Sistem membongkar muatan VRAM aktif dan memuat ulang model pilihan. |
| **Aksi Alur** | **Reaksi Sistem** |
| 1. Admin menavigasi ke menu model AI. | Sistem mendeteksi daftar LLM terpasang di sistem luring. |
| 2. Admin mengganti model *dropdown*. | Sistem melakukan alokasi ulang VRAM. |
| 3. Admin mengetik pada *playground* AI. | Model merespons dan mengeluarkan arus token *stream*. |

##### 1.1.9 Skenario *Use Case Take Placement Test*
| Nama Use Case | *Take Placement Test* |
| :--- | :--- |
| **Aktor** | User |
| **Deskripsi** | Pengguna mengikuti tes kalibrasi awal penempatan tingkat bahasa. |
| **Reaksi Sistem** | Mesin BKT menghitung skor dan menandai prasyarat Neo4j menjadi *Mastered*. |
| **Aksi Alur** | **Reaksi Sistem** |
| 1. Pengguna memulai tes awal sistem. | Sistem mengumpulkan butir soal tingkat kesulitan dinamis. |
| 2. Pengguna menyerahkan jawaban soal. | Sistem mengukur akurasi kognitif awal. |
| 3. Pengguna melihat hasil klasifikasi. | Sistem membuka sebagian peta kurikulum secara permanen. |

##### 1.1.10 Skenario *Use Case Complete Quest*
| Nama Use Case | *Complete Quest* |
| :--- | :--- |
| **Aktor** | User |
| **Deskripsi** | Pengguna menjelajahi alur pembelajaran pada peta *Quest* graf kurikulum. |
| **Reaksi Sistem** | Mesin graf merutekan level prasyarat, LLM membuat soal adaptif, BKT menilai akurasi. |
| **Aksi Alur** | **Reaksi Sistem** |
| 1. Pengguna menekan *Node* materi di peta. | Sistem memastikan validitas prasyarat belum terkunci (*seed*). |
| 2. Pengguna menjawab soal interaktif. | LLM mengevaluasi struktur respons teks secara adaptif. |
| 3. Pengguna memenangkan *Quest*. | Probabilitas di tabel `user_quests` dimutakhirkan. |

##### 1.1.11 Skenario *Use Case Take Exam*
| Nama Use Case | *Take Exam* |
| :--- | :--- |
| **Aktor** | User |
| **Deskripsi** | Pengguna menguji kompetensi JLPT secara komprehensif dalam *Exam Dojo*. |
| **Reaksi Sistem** | Sistem memutar waktu mundur dan menilai akurasi secara ketat. |
| **Aksi Alur** | **Reaksi Sistem** |
| 1. Pengguna meluncurkan simulasi ujian. | Sistem menyusun bundel soal standar. |
| 2. Pengguna menyeleksi jawaban. | Sistem mengunci timer dan mencatat progres *cache*. |
| 3. Pengguna mengakhiri modul ujian. | Sistem menerbitkan skor kelulusan final. |

##### 1.1.12 Skenario *Use Case Review SRS*
| Nama Use Case | *Review SRS* |
| :--- | :--- |
| **Aktor** | User |
| **Deskripsi** | Pengguna mereviu kembali kartu kosa kata dengan metode pengulangan berjarak. |
| **Reaksi Sistem** | Algoritma `srs_service.py` memodifikasi tanggal jatuh tempo (*next_review*). |
| **Aksi Alur** | **Reaksi Sistem** |
| 1. Pengguna meluncurkan sesi SRS. | Sistem menyaring koleksi kartu yang telah kedaluwarsa hari itu. |
| 2. Pengguna menekan nilai kemudahan (1-5). | Sistem memodifikasi faktor SM-2 dan jarak interval hari. |
| 3. Pengguna mengosongkan antrian. | Metrik pembaruan kartu tercatat ke basis data. |

##### 1.1.13 Skenario *Use Case Practice Speaking*
| Nama Use Case | *Practice Speaking* |
| :--- | :--- |
| **Aktor** | User |
| **Deskripsi** | Pengguna berlatih dialog vokal terapan dengan agen pintar 3D (A.L.I.S.A.). |
| **Reaksi Sistem** | Memproses STT pengguna, merender balasan LLM, menyintesis TTS sinkron figur. |
| **Aksi Alur** | **Reaksi Sistem** |
| 1. Pengguna mengucapkan kalimat bahasa Jepang. | Sistem menerjemahkan audio menjadi teks (*STT*). |
| 2. Pengguna menunggu balasan. | Sistem LLM merancang teks respons. |
| 3. Pengguna menyimak tutor VRM. | Avatar memproyeksikan suara (*TTS*) beserta *lip-sync*. |

##### 1.1.14 Skenario *Use Case Practice Reading*
| Nama Use Case | *Practice Reading* |
| :--- | :--- |
| **Aktor** | User |
| **Deskripsi** | Pengguna memahami konstruksi bacaan paragraf dengan instrumen translasi *hover*. |
| **Reaksi Sistem** | Sistem mengurai kelas leksikal teks untuk anotasi terjemahan seketika. |
| **Aksi Alur** | **Reaksi Sistem** |
| 1. Pengguna melihat bacaan teks aksara murni. | Sistem memuat struktur referensi tata bahasa di latar. |
| 2. Pengguna melayangkan kursor pada *Kanji*. | Sistem merender indikator glosarium translasi mini (*tooltip*). |
| 3. Pengguna memecahkan kuis pemahaman. | Sistem mencatat akurasi membaca ke dalam riwayat. |

##### 1.1.15 Skenario *Use Case Practice Kanji*
| Nama Use Case | *Practice Kanji* |
| :--- | :--- |
| **Aktor** | User |
| **Deskripsi** | Pengguna berlatih coretan (*strokes*), *Onyomi*, dan *Kunyomi* sebuah huruf *Kanji*. |
| **Reaksi Sistem** | Animasi vektor SVG coretan dijalankan sambil membunyikan pelafalan aksara. |
| **Aksi Alur** | **Reaksi Sistem** |
| 1. Pengguna memilah simbol *Kanji* target. | Sistem memuat detail komponen garis dari basis kurikulum. |
| 2. Pengguna mengamati instruksi tulis. | Sistem menganimasi urutan coretan secara visual. |
| 3. Pengguna menandai huruf. | Status Kanji pada tabel preferensi dikonversi menjadi terhafal. |

##### 1.1.16 Skenario *Use Case View Achievements*
| Nama Use Case | *View Achievements* |
| :--- | :--- |
| **Aktor** | User |
| **Deskripsi** | Pengguna memvisualisasikan prestasi lencana, pangkat, serta progres *node graph*. |
| **Reaksi Sistem** | Papan galeri medali dirender berdasarkan kondisi logika peraihan pengguna. |
| **Aksi Alur** | **Reaksi Sistem** |
| 1. Pengguna beralih ke galeri pencapaian. | Sistem mengambil status peraihan syarat medali absolut. |
| 2. Pengguna memilih atribut emblem (*Title*). | Sistem memasang estetika baru pada preferensi figur profil. |
| 3. Pengguna melacak *Mastery Path*. | Sistem merender jaring graf topologis materi dari Neo4j. |

##### 1.1.17 Skenario *Use Case Manage Profile*
| Nama Use Case | *Manage Profile* |
| :--- | :--- |
| **Aktor** | User |
| **Deskripsi** | Pengguna mengatur target kedisiplinan harian dan meninjau keaktifan kalender. |
| **Reaksi Sistem** | Perekaman target termutakhir pada `daily_goals` dan matriks XP `study_streaks`. |
| **Aksi Alur** | **Reaksi Sistem** |
| 1. Pengguna menyesuaikan rasio belajar (menit/hari). | Sistem mendaftarkan perubahan konfigurasi rasio. |
| 2. Pengguna mengukur intensitas kalender *streak*. | Sistem memanipulasi rentang gradasi warna di *heatmap*. |
| 3. Pengguna memperbarui profil demografi. | Basis data merekam entitas pembaruan di tabel profil. |

"""

with open('laporan_analisis_sistem_tvjp.md', 'w', encoding='utf-8') as f:
    f.write(text[:start_uc] + new_content + text[end_uc:])

print('Successfully applied double-sided clean Use Case layout!')
