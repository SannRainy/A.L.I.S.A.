import os
import sys
from pathlib import Path

# Force UTF-8 stdout to prevent Windows CP1252 encoding crashes
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add backend directory to path
sys.path.append(str(Path(__file__).resolve().parent))

from core.config import settings
from llama_cpp import Llama

def test_model():
    model_path = os.path.join(os.path.dirname(__file__), settings.UNSLOTH_MODEL_PATH)
    print(f"Menguji model dari path: {model_path}")
    print(f"File exists: {os.path.exists(model_path)}")
    
    if not os.path.exists(model_path):
        print("ERROR: File model tidak ditemukan!")
        sys.exit(1)
        
    print("Memuat model Llama (Qwen3-Swallow-8B-RL-v0.2-Q4_K_M.gguf) ke VRAM...")
    try:
        # Load the model with standard settings
        model = Llama(
            model_path=model_path,
            n_gpu_layers=32,
            n_ctx=512,  # Short context for quick connection test
            verbose=False
        )
        print("Model berhasil dimuat!")
        
        prompt = "<|im_start|>system\nKamu adalah Teman Ngobrol Native Bahasa Jepang. Respon FULL dalam Bahasa Jepang, santai, dan kasual (Maksimal 1-2 kalimat pendek). DILARANG KERAS menggunakan format markdown atau penjelasan.<|im_end|>\n<|im_start|>user\nこんにちは！元気？<|im_end|>\n<|im_start|>assistant\n"
        print(f"Mengirim prompt test: 'こんにちは！元気？'")
        
        response = model(
            prompt,
            max_tokens=50,
            temperature=0.7,
            stop=["<|im_end|>", "<|eot_id|>"]
        )
        
        text = response["choices"][0]["text"].strip()
        print("\n=== RESPONS DARI MODEL ===")
        print(text)
        print("==========================")
        print("Tes koneksi model berhasil!")
    except Exception as e:
        print(f"Terjadi kesalahan saat memuat atau menjalankan model: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_model()
