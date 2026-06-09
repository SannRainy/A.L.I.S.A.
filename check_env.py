# check_env.py — Jalankan sekali untuk verifikasi kompatibilitas
# EKSPERIMEN SAJA — aman dihapus kapan saja tanpa efek ke proyek utama
#
# Cara menjalankan:
#   cd Style-Bert-VITS2
#   python ../check_env.py
# ATAU dari root proyek TVJP:
#   python check_env.py

import sys
import os

print("=" * 60)
print("  VERIFIKASI LINGKUNGAN — TTS TensorRT + CFM Experiment")
print("=" * 60)

# ── Versi Python ─────────────────────────────────────────────
print(f"\nPython      : {sys.version}")

# ── Verifikasi PyTorch ────────────────────────────────────────
try:
    import torch
    print(f"PyTorch     : {torch.__version__}")

    if torch.__version__ < "2.1.0":
        print("⚠️  PyTorch HARUS >= 2.1.0 untuk backend torch_tensorrt!")
        print("   Upgrade: pip install torch>=2.1.0")
    else:
        print("✅ PyTorch versi memenuhi syarat (>= 2.1.0)")
except ImportError:
    print("❌ PyTorch TIDAK TERINSTALL — install dulu sebelum lanjut")
    sys.exit(1)

# ── Verifikasi CUDA ───────────────────────────────────────────
print(f"\nCUDA tersedia: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    gpu_name = torch.cuda.get_device_name(0)
    props = torch.cuda.get_device_properties(0)
    total_vram = props.total_memory / 1e9
    free_vram_bytes = torch.cuda.mem_get_info(0)[0]
    free_vram = free_vram_bytes / 1e9

    print(f"GPU         : {gpu_name}")
    print(f"VRAM Total  : {total_vram:.1f} GB")
    print(f"VRAM Bebas  : {free_vram:.1f} GB  (saat idle)")
    print(f"CUDA versi  : {torch.version.cuda}")
    print(f"cuDNN versi : {torch.backends.cudnn.version()}")

    # ── Rekomendasi workspace_size adaptif berdasarkan VRAM ──
    print()
    if total_vram < 5.0:
        ws_gb = 1
        print(f"⚠️  VRAM < 5GB terdeteksi → workspace_size WAJIB dibatasi {ws_gb} GB")
        print(f"   Gunakan: \"workspace_size\": {ws_gb} << 30  di opsi torch.compile")
        print(f"   (= {ws_gb << 30:,} bytes = {ws_gb} GB)")
        RECOMMENDED_WS = ws_gb << 30
    elif total_vram < 9.0:
        ws_gb = 2
        print(f"ℹ️  VRAM 5–8GB terdeteksi → workspace_size disarankan {ws_gb} GB")
        print(f"   Gunakan: \"workspace_size\": {ws_gb} << 30  di opsi torch.compile")
        print(f"   (= {ws_gb << 30:,} bytes = {ws_gb} GB)")
        RECOMMENDED_WS = ws_gb << 30
    else:
        ws_gb = 4
        print(f"✅ VRAM >= 8GB — workspace_size bebas (disarankan {ws_gb} GB atau tidak perlu dibatasi)")
        RECOMMENDED_WS = ws_gb << 30

    print(f"\n👉 Salin nilai ini ke test_speed_trt.py:")
    print(f"   WORKSPACE_SIZE = {RECOMMENDED_WS}  # {ws_gb} GB")

    # ── Cek dukungan FP16 (Tensor Cores) ─────────────────────
    if props.major >= 7:  # Volta (V100) atau lebih baru
        print(f"\n✅ GPU mendukung FP16 Tensor Cores (Compute Capability {props.major}.{props.minor})")
    else:
        print(f"\n⚠️  GPU Compute Capability {props.major}.{props.minor} — FP16 mungkin tidak optimal")
        print("   Tensor Cores baru tersedia mulai Volta (7.x) ke atas")

else:
    print("❌ CUDA TIDAK TERSEDIA — Eksperimen TRT tidak bisa dijalankan")
    print("   Cek: driver NVIDIA terinstall, GPU CUDA-compatible")
    print("   Pastikan torch versi CUDA (bukan CPU-only) terinstall")

# ── Verifikasi Torch-TensorRT ─────────────────────────────────
print()
try:
    import torch_tensorrt
    trt_version = torch_tensorrt.__version__
    print(f"Torch-TRT   : {trt_version} ✓")
    if trt_version < "2.1.0":
        print("⚠️  Torch-TRT HARUS >= 2.1.0 agar torch.compile backend bekerja!")
        print("   Upgrade: pip install torch-tensorrt>=2.1.0")
    else:
        print("✅ Torch-TRT versi memenuhi syarat (>= 2.1.0)")
except ImportError:
    print("Torch-TRT   : TIDAK TERINSTALL — Fase 2 (TRT benchmark) tidak bisa dijalankan")
    print("   Install dengan: pip install torch-tensorrt")
    print("   Catatan: versi harus kompatibel dengan PyTorch dan CUDA-mu")

# ── Verifikasi torchcfm ────────────────────────────────────────
try:
    import torchcfm
    print(f"torchcfm    : terinstall ✓")
    try:
        print(f"              versi: {torchcfm.__version__}")
    except AttributeError:
        print(f"              (versi tidak tersedia dari __version__)")
except ImportError:
    print("torchcfm    : TIDAK TERINSTALL — Fase 3 (CFM experiment) tidak bisa dijalankan")
    print("   Install dengan: pip install torchcfm")

# ── Verifikasi dependencies inti SBV2 ─────────────────────────
print()
print("── Dependencies inti Style-Bert-VITS2 ──")
deps = {
    "safetensors": "safetensors",
    "onnxruntime": "onnxruntime",
    "numpy": "numpy",
    "scipy": "scipy",
}
for display_name, module_name in deps.items():
    try:
        mod = __import__(module_name)
        ver = getattr(mod, "__version__", "?")
        print(f"  {display_name:<15}: {ver} ✓")
    except ImportError:
        print(f"  {display_name:<15}: TIDAK TERINSTALL ❌")

# ── Verifikasi model Style-Bert-VITS2 tersedia ─────────────────
print()
print("── Cek Model Assets Style-Bert-VITS2 ──")
# Cek dari direktori root proyek (TVJP/) atau dari Style-Bert-VITS2/
possible_roots = [
    os.path.join(os.path.dirname(__file__), "Style-Bert-VITS2", "model_assets"),
    os.path.join(os.path.dirname(__file__), "model_assets"),
]
model_found = False
for model_dir in possible_roots:
    if os.path.isdir(model_dir):
        model_dirs = [d for d in os.listdir(model_dir)
                      if os.path.isdir(os.path.join(model_dir, d))]
        if model_dirs:
            print(f"  Model assets ditemukan di: {model_dir}")
            for d in model_dirs[:5]:  # Tampilkan max 5
                model_path = os.path.join(model_dir, d)
                files = os.listdir(model_path)
                safetensors = [f for f in files if f.endswith(".safetensors")]
                config = "config.json" in files
                style_vec = "style_vectors.npy" in files
                status = "✅" if (safetensors and config and style_vec) else "⚠️ "
                print(f"  {status} {d}")
                if safetensors:
                    print(f"       model: {safetensors[0]}")
            model_found = True
            break
if not model_found:
    print("  ⚠️  Tidak ada model assets ditemukan")
    print("     Letakkan model di Style-Bert-VITS2/model_assets/<model-name>/")

# ── Ringkasan Keputusan ────────────────────────────────────────
print()
print("=" * 60)
print("  RINGKASAN KEPUTUSAN")
print("=" * 60)

cuda_ok = torch.cuda.is_available()
pytorch_ok = torch.__version__ >= "2.1.0"

try:
    import torch_tensorrt
    trt_ok = torch_tensorrt.__version__ >= "2.1.0"
except ImportError:
    trt_ok = False

try:
    import torchcfm
    cfm_ok = True
except ImportError:
    cfm_ok = False

fase2_ready = cuda_ok and pytorch_ok and trt_ok
fase3_ready = cuda_ok and pytorch_ok and cfm_ok

if fase2_ready:
    print("✅ FASE 2 (TensorRT FP16): SIAP — jalankan test_speed_trt.py")
else:
    missing = []
    if not cuda_ok:
        missing.append("CUDA")
    if not pytorch_ok:
        missing.append("PyTorch >= 2.1.0")
    if not trt_ok:
        missing.append("Torch-TensorRT >= 2.1.0")
    print(f"❌ FASE 2 (TensorRT FP16): BELUM SIAP — kurang: {', '.join(missing)}")

if fase3_ready:
    print("✅ FASE 3 (CFM Experiment): SIAP — jalankan test_cfm.py")
else:
    missing = []
    if not cuda_ok:
        missing.append("CUDA")
    if not pytorch_ok:
        missing.append("PyTorch >= 2.1.0")
    if not cfm_ok:
        missing.append("torchcfm (pip install torchcfm)")
    print(f"❌ FASE 3 (CFM Experiment): BELUM SIAP — kurang: {', '.join(missing)}")

print()
print("Setelah verifikasi selesai, jalankan eksperimen yang sesuai.")
print("=" * 60)
