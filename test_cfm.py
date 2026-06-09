# test_cfm.py
# EKSPERIMEN FASE 3 — Pengujian Arsitektur Conditional Flow Matching (CFM)
# EKSPERIMEN SAJA — aman dihapus kapan saja tanpa efek ke proyek utama
#
# Cara menjalankan (dari root TVJP/):
#   pip install torchcfm        # jika belum terinstall
#   python test_cfm.py
#
# Yang diuji:
#   1. ResidualCouplingLayer CFM bisa diinisialisasi tanpa error
#   2. Forward pass (training mode, reverse=False) menghasilkan output valid
#   3. Reverse pass (inference mode, reverse=True) berjalan dengan ODE solver
#   4. Output numerik stabil (tidak ada NaN/Inf)
#   5. Kompatibilitas dtype FP16 (untuk kombinasi dengan TRT di Fase 2)
#   6. ResidualCouplingBlock (yang menggunakan ResidualCouplingLayer CFM) juga valid

import sys
import os

# ── Tambahkan path Style-Bert-VITS2 ke sys.path ───────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SBV2_DIR   = os.path.join(SCRIPT_DIR, "Style-Bert-VITS2")
if os.path.isdir(SBV2_DIR):
    sys.path.insert(0, SBV2_DIR)

# Fix UTF-8 untuk Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import torch

print("=" * 60)
print("  PENGUJIAN ARSITEKTUR CFM — Style-Bert-VITS2")
print("=" * 60)

# ── Parameter uji — sesuaikan dengan config model jika perlu ──
# Nilai default ini sesuai dengan default SBV2 config:
CHANNELS        = 192   # inter_channels di config.json
HIDDEN_CHANNELS = 192   # hidden_channels
KERNEL_SIZE     = 5     # kernel_size default flow
DILATION_RATE   = 1     # dilation_rate
N_LAYERS        = 4     # n_flow_layer default
GIN_CHANNELS    = 256   # gin_channels (speaker embedding)
BATCH_SIZE      = 1
SEQ_LEN         = 100   # Panjang sequence audio latent

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"\nDevice  : {DEVICE}")
print(f"PyTorch : {torch.__version__}")

# ── Cek torchcfm ──────────────────────────────────────────────
try:
    import torchcfm
    print(f"torchcfm: terinstall ✓")
    CFM_AVAILABLE = True
except ImportError:
    print("torchcfm: TIDAK TERINSTALL ⚠️")
    print("   Install: pip install torchcfm")
    print("   (Eksperimen tetap berjalan, tapi CFM training signal tidak aktif)")
    CFM_AVAILABLE = False

print()

# ── Import dari modules_cfm.py ────────────────────────────────
try:
    # Import dari path eksperimen (modules_cfm.py di Style-Bert-VITS2/style_bert_vits2/models/)
    sys.path.insert(0, os.path.join(SBV2_DIR if os.path.isdir(SBV2_DIR) else SCRIPT_DIR,
                                     "style_bert_vits2", "models"))
    from modules_cfm import ResidualCouplingLayer, ResidualCouplingBlock
    print("✅ Import dari modules_cfm.py berhasil.")
except ImportError as e:
    print(f"❌ Gagal import modules_cfm.py: {e}")
    print("   Pastikan modules_cfm.py ada di Style-Bert-VITS2/style_bert_vits2/models/")
    sys.exit(1)

# Helper: buat dummy mask (semua 1 = tidak ada padding)
def make_mask(batch, seq_len, device, dtype=torch.float32):
    return torch.ones(batch, 1, seq_len, device=device, dtype=dtype)

# Helper: cek NaN/Inf di tensor
def check_numerical_stability(tensor, name):
    has_nan = torch.isnan(tensor).any().item()
    has_inf = torch.isinf(tensor).any().item()
    if has_nan:
        print(f"   ❌ {name}: mengandung NaN")
        return False
    if has_inf:
        print(f"   ❌ {name}: mengandung Inf")
        return False
    print(f"   ✅ {name}: numerik stabil")
    return True

all_passed = True

# ══════════════════════════════════════════════════════════════
# UJI 1: Inisialisasi ResidualCouplingLayer CFM
# ══════════════════════════════════════════════════════════════
print("\n[1/6] Inisialisasi ResidualCouplingLayer (CFM)...")
try:
    layer = ResidualCouplingLayer(
        channels=CHANNELS,
        hidden_channels=HIDDEN_CHANNELS,
        kernel_size=KERNEL_SIZE,
        dilation_rate=DILATION_RATE,
        n_layers=N_LAYERS,
        gin_channels=GIN_CHANNELS,
        mean_only=True,  # Seperti konfigurasi di SBV2
    ).to(DEVICE)
    layer.eval()
    param_count = sum(p.numel() for p in layer.parameters())
    print(f"   ✅ ResidualCouplingLayer berhasil diinisialisasi")
    print(f"      Parameter count: {param_count:,}")
    print(f"      ODE steps (inference): {layer.N_ODE_STEPS}")
except Exception as e:
    print(f"   ❌ ERROR inisialisasi: {e}")
    all_passed = False

# ══════════════════════════════════════════════════════════════
# UJI 2: Forward pass (training mode, reverse=False)
# ══════════════════════════════════════════════════════════════
print("\n[2/6] Forward pass — training mode (reverse=False)...")
try:
    x_dummy  = torch.randn(BATCH_SIZE, CHANNELS, SEQ_LEN, device=DEVICE)
    x_mask   = make_mask(BATCH_SIZE, SEQ_LEN, DEVICE)
    g_dummy  = torch.randn(BATCH_SIZE, GIN_CHANNELS, 1, device=DEVICE)

    with torch.no_grad():
        result = layer(x_dummy, x_mask, g=g_dummy, reverse=False)

    # Harus return tuple (x_out, logdet)
    assert isinstance(result, tuple) and len(result) == 2, \
        f"Expected (x_out, logdet), got: {type(result)}"
    x_out, logdet = result

    print(f"   ✅ Forward pass berhasil. Output:")
    print(f"      x_out shape : {x_out.shape}   (expected: {list(x_dummy.shape)})")
    print(f"      logdet shape: {logdet.shape}  (expected: [{BATCH_SIZE}])")
    assert x_out.shape == x_dummy.shape, f"Shape mismatch: {x_out.shape} vs {x_dummy.shape}"

    ok1 = check_numerical_stability(x_out, "x_out (forward)")
    ok2 = check_numerical_stability(logdet, "logdet (forward)")
    if not (ok1 and ok2):
        all_passed = False

except Exception as e:
    import traceback
    print(f"   ❌ ERROR forward pass: {e}")
    traceback.print_exc()
    all_passed = False

# ══════════════════════════════════════════════════════════════
# UJI 3: Reverse pass (inference mode, reverse=True) dengan ODE solver
# ══════════════════════════════════════════════════════════════
print("\n[3/6] Reverse pass — inference mode (reverse=True, ODE solver)...")
try:
    # Buat z_p (latent dari prior) seperti yang dihasilkan SynthesizerTrn.infer()
    z_p_dummy = torch.randn(BATCH_SIZE, CHANNELS, SEQ_LEN, device=DEVICE)
    x_mask    = make_mask(BATCH_SIZE, SEQ_LEN, DEVICE)
    g_dummy   = torch.randn(BATCH_SIZE, GIN_CHANNELS, 1, device=DEVICE)

    import time
    t_start = time.perf_counter()
    with torch.no_grad():
        z_out = layer(z_p_dummy, x_mask, g=g_dummy, reverse=True)
    t_elapsed = time.perf_counter() - t_start

    print(f"   ✅ Reverse pass (ODE solver) berhasil.")
    print(f"      z_out shape  : {z_out.shape}  (expected: {list(z_p_dummy.shape)})")
    print(f"      ODE solve time: {t_elapsed:.4f}s  ({layer.N_ODE_STEPS} Euler steps)")
    assert z_out.shape == z_p_dummy.shape, f"Shape mismatch: {z_out.shape}"

    ok = check_numerical_stability(z_out, "z_out (reverse/ODE)")
    if not ok:
        all_passed = False

except Exception as e:
    import traceback
    print(f"   ❌ ERROR reverse pass: {e}")
    traceback.print_exc()
    all_passed = False

# ══════════════════════════════════════════════════════════════
# UJI 4: ResidualCouplingBlock (menggunakan ResidualCouplingLayer CFM)
# ══════════════════════════════════════════════════════════════
print("\n[4/6] Inisialisasi dan forward ResidualCouplingBlock (CFM)...")
try:
    block = ResidualCouplingBlock(
        channels=CHANNELS,
        hidden_channels=HIDDEN_CHANNELS,
        kernel_size=KERNEL_SIZE,
        dilation_rate=DILATION_RATE,
        n_layers=N_LAYERS,
        n_flows=4,           # Seperti konfigurasi default SBV2
        gin_channels=GIN_CHANNELS,
    ).to(DEVICE)
    block.eval()

    param_block = sum(p.numel() for p in block.parameters())
    print(f"   ✅ ResidualCouplingBlock berhasil diinisialisasi")
    print(f"      Parameter count: {param_block:,}")

    # Test forward (training, reverse=False)
    x_dummy = torch.randn(BATCH_SIZE, CHANNELS, SEQ_LEN, device=DEVICE)
    x_mask  = make_mask(BATCH_SIZE, SEQ_LEN, DEVICE)
    g_dummy = torch.randn(BATCH_SIZE, GIN_CHANNELS, 1, device=DEVICE)

    with torch.no_grad():
        x_fwd = block(x_dummy, x_mask, g=g_dummy, reverse=False)
    print(f"   ✅ Block forward (reverse=False): shape {x_fwd.shape}")
    check_numerical_stability(x_fwd, "block output (forward)")

    # Test reverse (inference, reverse=True)
    with torch.no_grad():
        z_rev = block(x_dummy, x_mask, g=g_dummy, reverse=True)
    print(f"   ✅ Block forward (reverse=True):  shape {z_rev.shape}")
    ok = check_numerical_stability(z_rev, "block output (reverse)")
    if not ok:
        all_passed = False

except Exception as e:
    import traceback
    print(f"   ❌ ERROR ResidualCouplingBlock: {e}")
    traceback.print_exc()
    all_passed = False

# ══════════════════════════════════════════════════════════════
# UJI 5: Kompatibilitas FP16
# ══════════════════════════════════════════════════════════════
print("\n[5/6] Kompatibilitas FP16 (untuk kombinasi dengan TRT)...")
try:
    if DEVICE == "cuda":
        layer_fp16 = ResidualCouplingLayer(
            channels=CHANNELS,
            hidden_channels=HIDDEN_CHANNELS,
            kernel_size=KERNEL_SIZE,
            dilation_rate=DILATION_RATE,
            n_layers=N_LAYERS,
            gin_channels=GIN_CHANNELS,
            mean_only=True,
        ).to(DEVICE).half()
        layer_fp16.eval()

        x_fp16 = torch.randn(BATCH_SIZE, CHANNELS, SEQ_LEN, device=DEVICE, dtype=torch.float16)
        m_fp16 = make_mask(BATCH_SIZE, SEQ_LEN, DEVICE, dtype=torch.float16)
        g_fp16 = torch.randn(BATCH_SIZE, GIN_CHANNELS, 1, device=DEVICE, dtype=torch.float16)

        with torch.no_grad():
            z_fp16 = layer_fp16(x_fp16, m_fp16, g=g_fp16, reverse=True)

        print(f"   ✅ FP16 reverse pass berhasil. dtype: {z_fp16.dtype}")
        ok = check_numerical_stability(z_fp16, "z_fp16 (reverse)")
        if not ok:
            all_passed = False
    else:
        print("   ⚠️  Skip (FP16 Tensor Cores memerlukan CUDA)")

except Exception as e:
    import traceback
    print(f"   ❌ ERROR FP16: {e}")
    traceback.print_exc()
    all_passed = False

# ══════════════════════════════════════════════════════════════
# UJI 6: Latensi ODE solver (referensi kecepatan)
# ══════════════════════════════════════════════════════════════
print("\n[6/6] Latensi ODE solver (referensi kecepatan, 10 iterasi)...")
try:
    import time
    import statistics

    layer_bench = ResidualCouplingLayer(
        channels=CHANNELS,
        hidden_channels=HIDDEN_CHANNELS,
        kernel_size=KERNEL_SIZE,
        dilation_rate=DILATION_RATE,
        n_layers=N_LAYERS,
        gin_channels=GIN_CHANNELS,
        mean_only=True,
    ).to(DEVICE).eval()

    # Gunakan FP16 jika CUDA tersedia, FP32 jika CPU
    if DEVICE == "cuda":
        layer_bench = layer_bench.half()
        x_b = torch.randn(1, CHANNELS, SEQ_LEN, device=DEVICE, dtype=torch.float16)
        m_b = make_mask(1, SEQ_LEN, DEVICE, dtype=torch.float16)
        g_b = torch.randn(1, GIN_CHANNELS, 1, device=DEVICE, dtype=torch.float16)
    else:
        x_b = torch.randn(1, CHANNELS, SEQ_LEN, device=DEVICE)
        m_b = make_mask(1, SEQ_LEN, DEVICE)
        g_b = torch.randn(1, GIN_CHANNELS, 1, device=DEVICE)

    # Warm-up
    with torch.no_grad():
        _ = layer_bench(x_b, m_b, g=g_b, reverse=True)

    latencies = []
    with torch.no_grad():
        for _ in range(10):
            if DEVICE == "cuda":
                torch.cuda.synchronize()
            t0 = time.perf_counter()
            _ = layer_bench(x_b, m_b, g=g_b, reverse=True)
            if DEVICE == "cuda":
                torch.cuda.synchronize()
            latencies.append(time.perf_counter() - t0)

    print(f"   Latensi per CFM layer (ODE, {layer.N_ODE_STEPS} steps):")
    print(f"   Median  : {statistics.median(latencies)*1000:.3f} ms")
    print(f"   Minimum : {min(latencies)*1000:.3f} ms")
    print(f"   ✅ Latensi benchmark selesai")

except Exception as e:
    import traceback
    print(f"   ❌ ERROR benchmark latensi: {e}")
    traceback.print_exc()
    all_passed = False

# ── KESIMPULAN AKHIR ──────────────────────────────────────────
print()
print("=" * 60)
if all_passed:
    print("  ✅ SEMUA UJI LULUS!")
    print()
    print("  Arsitektur CFM siap untuk benchmark latensi end-to-end.")
    print("  Langkah selanjutnya:")
    print("  1. Bandingkan kualitas audio CFM vs model asli secara subjektif")
    print("  2. Lakukan fine-tune dengan torchcfm.ConditionalFlowMatcher")
    print("     untuk melatih velocity network dengan data asli")
    print("  3. Jika kualitas memuaskan, integrasikan ke production:")
    print("     Ganti import modules di models.py dengan modules_cfm")
    if not CFM_AVAILABLE:
        print()
        print("  ⚠️  CATATAN: torchcfm belum terinstall.")
        print("     Training CFM tidak aktif (hanya inference ODE yang berjalan).")
        print("     Install: pip install torchcfm")
else:
    print("  ❌ ADA UJI YANG GAGAL!")
    print()
    print("  Perbaiki modules_cfm.py sesuai error di atas, lalu jalankan ulang.")
    print("  Panduan rollback: hapus modules_cfm.py dan test_cfm.py")
print("=" * 60)
