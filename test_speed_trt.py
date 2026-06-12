# test_speed_trt.py
# EKSPERIMEN SAJA — aman dihapus kapan saja tanpa efek ke proyek utama
#
# Tujuan: Benchmark latensi inferensi Style-Bert-VITS2 dengan Torch-TensorRT FP16
# vs baseline FP32 biasa, untuk melihat apakah median < 1.0 detik tercapai.
#
# Cara menjalankan (dari direktori Style-Bert-VITS2/):
#   python ../test_speed_trt.py
# ATAU dari root TVJP/ dengan mengatur sys.path (sudah otomatis di script ini)

import sys
import os
import time
import statistics

# ── Tambahkan path Style-Bert-VITS2 ke sys.path ───────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SBV2_DIR = os.path.join(SCRIPT_DIR, "Style-Bert-VITS2")
if os.path.isdir(SBV2_DIR):
    sys.path.insert(0, SBV2_DIR)
elif os.path.isfile(os.path.join(SCRIPT_DIR, "style_bert_vits2", "__init__.py")):
    # Sudah berada di dalam direktori Style-Bert-VITS2
    pass
else:
    print("❌ Tidak bisa menemukan direktori Style-Bert-VITS2.")
    print("   Jalankan script ini dari root TVJP/ atau dari Style-Bert-VITS2/")
    sys.exit(1)

# Fix UTF-8 untuk Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import torch

# ─── KONFIGURASI — SESUAIKAN BAGIAN INI ──────────────────────────────────────
# Pilih salah satu model dari model_assets/ yang tersedia:
MODEL_NAME   = "Alisa_Voice"               # Nama folder di model_assets/
MODEL_FILE   = "Yokohama_Aoba.safetensors" # File model dalam folder tersebut
SPEAKER_ID   = 0                           # Speaker ID (0 jika hanya 1 speaker)
TEXT_SAMPLE  = "こんにちは、お元気ですか？今日も一緒に日本語を勉強しましょう。"
N_RUNS       = 2   # Iterasi benchmark (lebih banyak = lebih akurat secara statistik)

# WORKSPACE_SIZE: Sesuaikan dengan output check_env.py
# VRAM < 5GB  → 1 << 30  (1 GB)
# VRAM 5–8GB  → 2 << 30  (2 GB)
# VRAM >= 8GB → 4 << 30  (4 GB) atau hapus parameter ini
WORKSPACE_SIZE = 1 << 30   # ← UBAH SESUAI HASIL check_env.py
# ─────────────────────────────────────────────────────────────────────────────


def build_dummy_inputs(hps, device, dtype=torch.float32):
    """
    Buat dummy input tensor yang kompatibel dengan SynthesizerTrn.infer().
    Menggunakan TEXT_SAMPLE untuk mendapatkan phone sequence asli.
    """
    from style_bert_vits2.models.infer import get_text
    from style_bert_vits2.constants import Languages

    # Pre-load BERT model (diperlukan oleh get_text)
    from style_bert_vits2.nlp import bert_models
    bert_models.load_model(Languages.JP, device_map=device)
    bert_models.load_tokenizer(Languages.JP)

    bert, ja_bert, en_bert, phones, tones, lang_ids = get_text(
        TEXT_SAMPLE, Languages.JP, hps, device
    )

    x_tst          = phones.to(device).unsqueeze(0)
    tones_t         = tones.to(device).unsqueeze(0)
    lang_ids_t      = lang_ids.to(device).unsqueeze(0)
    bert_t          = bert.to(device).unsqueeze(0)
    ja_bert_t       = ja_bert.to(device).unsqueeze(0)
    en_bert_t       = en_bert.to(device).unsqueeze(0)
    x_tst_lengths   = torch.LongTensor([phones.size(0)]).to(device)
    sid_t           = torch.LongTensor([SPEAKER_ID]).to(device)

    # Style vec: muat dari npy atau gunakan zeros
    import numpy as np
    style_vec_path = os.path.join(
        SBV2_DIR if os.path.isdir(SBV2_DIR) else SCRIPT_DIR,
        "model_assets", MODEL_NAME, "style_vectors.npy"
    )
    if os.path.isfile(style_vec_path):
        style_vectors = np.load(style_vec_path)
        style_vec = torch.from_numpy(style_vectors[0]).to(device).unsqueeze(0)
    else:
        style_vec = torch.zeros(1, 256, device=device)

    # Konversi ke dtype yang diminta (fp16 untuk TRT)
    if dtype == torch.float16:
        bert_t      = bert_t.half()
        ja_bert_t   = ja_bert_t.half()
        en_bert_t   = en_bert_t.half()
        style_vec   = style_vec.half()

    return (x_tst, x_tst_lengths, sid_t, tones_t, lang_ids_t,
            bert_t, ja_bert_t, en_bert_t, style_vec)


class SynthInferWrapper(torch.nn.Module):
    def __init__(self, net_g):
        super().__init__()
        self.net_g = net_g

    def forward(self, *args, **kwargs):
        return self.net_g.infer(*args, **kwargs)


def run_infer(net_g, inputs, is_jp_extra=False):
    """Jalankan satu kali inferensi. Return audio tensor."""
    (x_tst, x_tst_lengths, sid_t, tones_t, lang_ids_t,
     bert_t, ja_bert_t, en_bert_t, style_vec) = inputs

    if isinstance(net_g, SynthInferWrapper) or (hasattr(net_g, "forward") and not hasattr(net_g, "infer")):
        if is_jp_extra:
            output = net_g(
                x_tst, x_tst_lengths, sid_t, tones_t, lang_ids_t, ja_bert_t,
                style_vec=style_vec, length_scale=1.0,
                sdp_ratio=0.2, noise_scale=0.6, noise_scale_w=0.8,
            )
        else:
            output = net_g(
                x_tst, x_tst_lengths, sid_t, tones_t, lang_ids_t,
                bert_t, ja_bert_t, en_bert_t,
                style_vec=style_vec, length_scale=1.0,
                sdp_ratio=0.2, noise_scale=0.6, noise_scale_w=0.8,
            )
    else:
        if is_jp_extra:
            output = net_g.infer(
                x_tst, x_tst_lengths, sid_t, tones_t, lang_ids_t, ja_bert_t,
                style_vec=style_vec, length_scale=1.0,
                sdp_ratio=0.2, noise_scale=0.6, noise_scale_w=0.8,
            )
        else:
            output = net_g.infer(
                x_tst, x_tst_lengths, sid_t, tones_t, lang_ids_t,
                bert_t, ja_bert_t, en_bert_t,
                style_vec=style_vec, length_scale=1.0,
                sdp_ratio=0.2, noise_scale=0.6, noise_scale_w=0.8,
            )
    return output[0][0, 0]


def benchmark_baseline(net_g, inputs, is_jp_extra, n_runs):
    """Benchmark model FP32 baseline (tanpa TRT)."""
    print(f"\n[BASELINE] Menjalankan benchmark FP32 ({n_runs} iterasi)...")
    latencies = []
    with torch.no_grad():
        for i in range(n_runs):
            torch.cuda.synchronize()
            t0 = time.perf_counter()
            _ = run_infer(net_g, inputs, is_jp_extra)
            torch.cuda.synchronize()
            t1 = time.perf_counter()
            latencies.append(t1 - t0)
            print(f"  Iterasi {i+1:02d}/{n_runs}: {latencies[-1]:.4f}s")
    return latencies


def benchmark_trt(optimized_model, inputs, is_jp_extra, n_runs):
    """Benchmark model TRT FP16 (setelah torch.compile)."""
    print(f"\n[TRT FP16] Menjalankan benchmark ({n_runs} iterasi)...")
    latencies = []
    with torch.no_grad():
        for i in range(n_runs):
            torch.cuda.synchronize()
            t0 = time.perf_counter()
            _ = run_infer(optimized_model, inputs, is_jp_extra)
            torch.cuda.synchronize()
            t1 = time.perf_counter()
            latencies.append(t1 - t0)
            print(f"  Iterasi {i+1:02d}/{n_runs}: {latencies[-1]:.4f}s")
    return latencies


def print_stats(label, latencies):
    """Cetak statistik benchmark."""
    print(f"\n{'=' * 55}")
    print(f"  [HASIL BENCHMARK — {label}]")
    print(f"  Median  : {statistics.median(latencies):.4f} detik")
    print(f"  Minimum : {min(latencies):.4f} detik")
    print(f"  Maximum : {max(latencies):.4f} detik")
    print(f"  Std Dev : {statistics.stdev(latencies):.4f} detik")
    print(f"  P95     : {sorted(latencies)[int(len(latencies)*0.95)]:.4f} detik")
    print(f"{'=' * 55}")


def main():
    # ── CEK VERSI ─────────────────────────────────────────────
    print("=" * 55)
    print(f"  BENCHMARK TensorRT FP16 — Style-Bert-VITS2")
    print("=" * 55)
    print(f"PyTorch versi    : {torch.__version__}")

    try:
        import torch_tensorrt
        print(f"Torch-TRT versi  : {torch_tensorrt.__version__}")
        if torch.__version__ < "2.1.0":
            raise RuntimeError("PyTorch harus >= 2.1.0 untuk backend torch_tensorrt")
        if torch_tensorrt.__version__ < "2.1.0":
            raise RuntimeError("Torch-TRT harus >= 2.1.0")
    except ImportError:
        print("❌ torch_tensorrt tidak terinstall. Jalankan check_env.py terlebih dahulu.")
        sys.exit(1)

    if not torch.cuda.is_available():
        print("❌ CUDA tidak tersedia. GPU dibutuhkan untuk eksperimen ini.")
        sys.exit(1)

    device = "cuda"
    print(f"GPU              : {torch.cuda.get_device_name(0)}")
    print(f"VRAM Total       : {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    print("=" * 55)

    # ── MUAT HYPERPARAMETER ───────────────────────────────────
    from style_bert_vits2.models.hyper_parameters import HyperParameters
    assets_base = os.path.join(
        SBV2_DIR if os.path.isdir(SBV2_DIR) else SCRIPT_DIR,
        "model_assets", MODEL_NAME
    )
    config_path = os.path.join(assets_base, "config.json")
    model_path  = os.path.join(assets_base, MODEL_FILE)

    if not os.path.isfile(config_path):
        print(f"❌ config.json tidak ditemukan: {config_path}")
        sys.exit(1)
    if not os.path.isfile(model_path):
        print(f"❌ Model tidak ditemukan: {model_path}")
        sys.exit(1)

    print(f"\n[1/6] Memuat HyperParameters dari {config_path}...")
    hps = HyperParameters.load_from_json(config_path)
    is_jp_extra = hps.version.endswith("JP-Extra")
    print(f"      Versi model : {hps.version}")
    print(f"      JP-Extra    : {is_jp_extra}")

    # ── MUAT MODEL BASELINE (FP32) ────────────────────────────
    print(f"\n[2/6] Memuat model FP32 ke GPU...")
    from style_bert_vits2.models.infer import get_net_g
    net_g = get_net_g(model_path=model_path, version=hps.version, device=device, hps=hps)
    net_g.eval()
    print(f"      Model berhasil dimuat ({sum(p.numel() for p in net_g.parameters()):,} parameters)")

    # ── SIAPKAN DUMMY INPUT ───────────────────────────────────
    print(f"\n[3/6] Menyiapkan input teks: '{TEXT_SAMPLE[:30]}...'")
    print("      (Pre-loading BERT tokenizer dan model...)")
    inputs_fp32 = build_dummy_inputs(hps, device, dtype=torch.float32)
    print("      Input FP32 siap.")

    # ── BENCHMARK BASELINE ────────────────────────────────────
    print(f"\n[4/6] Benchmark BASELINE FP32 ({N_RUNS} iterasi)...")
    # Warm-up baseline
    with torch.no_grad():
        _ = run_infer(net_g, inputs_fp32, is_jp_extra)
        _ = run_infer(net_g, inputs_fp32, is_jp_extra)
    baseline_latencies = benchmark_baseline(net_g, inputs_fp32, is_jp_extra, N_RUNS)
    print_stats("BASELINE FP32", baseline_latencies)

    # ── KOMPILASI MODEL DENGAN TORCH-TRT ─────────────────────
    print(f"\n[5/6] Mengompilasi model via Torch-TensorRT FP16...")
    print("      (Proses ini bisa memakan 3–10 menit pada kompilasi pertama)")
    print("      Cache hasil kompilasi disimpan otomatis di ./trt_cache/")

    # Set cache environment variables SEBELUM compile
    cache_dir = os.path.join(SCRIPT_DIR, "trt_cache")
    os.makedirs(cache_dir, exist_ok=True)
    os.environ["TORCHINDUCTOR_CACHE_DIR"]         = cache_dir
    os.environ["TORCH_TENSORRT_ENGINE_CACHE_DIR"] = cache_dir

    # Kompilasi model asli (FP32) dengan presisi target FP16 untuk subgraf TRT.
    # Cara ini membuat compiler melempar operasi spline transform yang tidak stabil kembali
    # ke PyTorch dalam FP32, sedangkan layer berat (Conv/Linear) dikompilasi ke TRT FP16.
    try:
        wrapper = SynthInferWrapper(net_g)
        optimized_model = torch.compile(
            wrapper,
            backend="torch_tensorrt",
            options={
                "precision": torch.float16,
                "truncate_long_and_double": True,  # Konversi Long/Double ke Int/Float
                "dynamic_shapes": True,             # WAJIB True: panjang kalimat TTS dinamis
                "workspace_size": WORKSPACE_SIZE,   # Sesuai VRAM GPU (lihat check_env.py)
            }
        )
        print("      Kompilasi (graph capture) siap.")

        # ── WARM-UP TRT ─────────────────────────────────────────
        print("\n      Warm-up TRT inference (inisialisasi grafis TRT, ini sekali saja)...")
        with torch.no_grad():
            torch.cuda.synchronize()
            _ = run_infer(optimized_model, inputs_fp32, is_jp_extra)
            torch.cuda.synchronize()
        print("      Warm-up selesai. Grafis TRT sudah terinisialisasi.")
        print(f"      Cache TRT engine disimpan di: {cache_dir}")

        # ── BENCHMARK TRT ────────────────────────────────────────
        trt_latencies = benchmark_trt(optimized_model, inputs_fp32, is_jp_extra, N_RUNS)
        print_stats("TRT FP16", trt_latencies)

        # ── PERBANDINGAN ─────────────────────────────────────────
        base_median = statistics.median(baseline_latencies)
        trt_median  = statistics.median(trt_latencies)
        speedup     = base_median / trt_median if trt_median > 0 else 0

        print(f"\n{'=' * 55}")
        print(f"  PERBANDINGAN KECEPATAN")
        print(f"  Baseline FP32 median : {base_median:.4f} detik")
        print(f"  TRT FP16 median      : {trt_median:.4f} detik")
        print(f"  Speedup              : {speedup:.2f}x lebih cepat")
        print(f"{'=' * 55}")

        # ── KEPUTUSAN ────────────────────────────────────────────
        print()
        if trt_median < 1.0:
            print("✅ EKSPERIMEN BERHASIL — TRT FP16 median < 1.0 detik!")
            print("   Rekomendasi: Integrasikan torch.compile ke server_fastapi.py")
            print("   Tambahkan blok ini ke load_models() di server_fastapi.py:")
            print("""
    # Tambahkan setelah model.load():
    import os, torch_tensorrt
    os.makedirs('./trt_cache', exist_ok=True)
    os.environ['TORCHINDUCTOR_CACHE_DIR'] = './trt_cache'
    os.environ['TORCH_TENSORRT_ENGINE_CACHE_DIR'] = './trt_cache'
    model.net_g = model.net_g.half()
    model.net_g = torch.compile(
        model.net_g,
        backend='torch_tensorrt',
        options={
            'precision': torch.float16,
            'truncate_long_and_double': True,
            'dynamic_shapes': True,
            'workspace_size': WORKSPACE_SIZE,  # sesuai GPU
        }
    )
""")
        elif trt_median < 1.5:
            print("⚠️  MARGINAL — median 1.0–1.5 detik")
            print("   Pertimbangkan tradeoff: kompleksitas integrasi vs gain kecepatan")
            print("   Lanjutkan ke Fase 3 (CFM) untuk alternatif optimasi")
        else:
            print("❌ TIDAK SIGNIFIKAN — median > 1.5 detik")
            print("   Hapus test_speed_trt.py dan trt_cache/, proyek bersih.")
            print("   Lanjutkan ke Fase 3 (CFM) untuk alternatif optimasi.")

    except Exception as e:
        print(f"\n❌ ERROR saat kompilasi/benchmark TRT: {type(e).__name__}: {e}")
        print("\nKemungkinan penyebab:")
        print("  1. VRAM tidak cukup → kurangi WORKSPACE_SIZE di bagian KONFIGURASI")
        print("  2. Versi Torch-TRT tidak kompatibel dengan PyTorch-mu")
        print("  3. Dynamic shapes tidak didukung untuk model ini")
        print("\nLangkah:")
        print("  - Jalankan check_env.py terlebih dahulu untuk verifikasi kompatibilitas")
        print("  - Sesuaikan WORKSPACE_SIZE sesuai output check_env.py")
        print("  - Hapus trt_cache/ jika ada cache korup: rm -rf ./trt_cache")
        import traceback
        print("\n── Traceback Detail ──")
        traceback.print_exc()


if __name__ == "__main__":
    main()
