# bert_cache.py — BERT Embedding Cache for TTS Optimization
# Caches BERT inference results to avoid redundant ~150-400ms calls
# Safe to delete - this is an experimental optimization module

import hashlib
import pickle
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Cache directory in project root
_BERT_CACHE_DIR = Path(__file__).parent.parent.parent / "bert_cache"
_BERT_CACHE_DIR.mkdir(exist_ok=True)

def get_text_cached(text: str, language_str, hps, device, **kwargs):
    """
    Wrapper for get_text() with disk cache based on text hash.
    Cache is stored in bert_cache/ as .pkl files.

    Args:
        text: Input text for TTS
        language_str: Language string (e.g., "JP", "EN")
        hps: Hyperparameters object
        device: Target device (cuda/cpu)
        **kwargs: Additional arguments passed to get_text()

    Returns:
        Tuple of tensors (same as get_text())
    """
    # Cache key: hash of all parameters affecting output
    cache_key = hashlib.md5(
        f"{text}|{language_str}|{hps.version}".encode('utf-8')
    ).hexdigest()
    cache_path = _BERT_CACHE_DIR / f"{cache_key}.pkl"

    # Cache hit - load from disk
    if cache_path.exists():
        try:
            with open(cache_path, "rb") as f:
                tensors = pickle.load(f)
            # Move tensors to requested device
            result = tuple(t.to(device) for t in tensors)
            logger.debug(f"[BERT Cache] HIT for text: {text[:30]}...")
            return result
        except Exception as e:
            logger.warning(f"[BERT Cache] Failed to load cache {cache_key}: {e}")
            # Fall through to cache miss

    # Cache miss - call original get_text()
    from style_bert_vits2.models.infer import get_text
    result = get_text(text, language_str, hps, device, **kwargs)

    # Save to disk (CPU version for portability across devices)
    try:
        tensors_cpu = tuple(t.cpu() for t in result)
        with open(cache_path, "wb") as f:
            pickle.dump(tensors_cpu, f)
        logger.debug(f"[BERT Cache] MISS - cached for text: {text[:30]}...")
    except Exception as e:
        logger.warning(f"[BERT Cache] Failed to save cache {cache_key}: {e}")

    return result
