from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Optional, Union
from collections import OrderedDict

import numpy as np
import onnxruntime
from numpy.typing import NDArray

from style_bert_vits2.constants import Languages
from style_bert_vits2.nlp import bert_models, onnx_bert_models
from style_bert_vits2.nlp.japanese.g2p import text_to_sep_kata
from style_bert_vits2.utils import get_onnx_device_options

if TYPE_CHECKING:
    import torch

# LRU Cache settings for BERT features
_bert_feature_cache: OrderedDict[tuple, torch.Tensor] = OrderedDict()
_bert_feature_onnx_cache: OrderedDict[tuple, NDArray[Any]] = OrderedDict()
_MAX_CACHE_SIZE = 500


def extract_bert_feature(
    text: str,
    word2ph: list[int],
    device: str,
    assist_text: Optional[str] = None,
    assist_text_weight: float = 0.7,
) -> torch.Tensor:
    """
    日本語のテキストから BERT の特徴量を抽出する (PyTorch 推論)

    Args:
        text (str): 日本語のテキスト
        word2ph (list[int]): 元のテキストの各文字に音素が何個割り当てられるかを表すリスト
        device (str): 推論に利用するデバイス
        assist_text (Optional[str], optional): 補助テキスト (デフォルト: None)
        assist_text_weight (float, optional): 補助テキストの重み (デフォルト: 0.7)

    Returns:
        torch.Tensor: BERT の特徴量
    """

    import torch

    # 各単語が何文字かを作る `word2ph` を使う必要があるので、読めない文字は必ず無視する
    # でないと `word2ph` の結果とテキストの文字数結果が整合性が取れない
    text_clean = "".join(text_to_sep_kata(text, raise_yomi_error=False)[0])
    assist_text_clean = "".join(text_to_sep_kata(assist_text, raise_yomi_error=False)[0]) if assist_text else None

    if device == "cuda" and not torch.cuda.is_available():
        device = "cpu"

    # Check memory cache (Fase 3 Optimization)
    cache_key = (text_clean, tuple(word2ph), device, assist_text_clean, assist_text_weight)
    global _bert_feature_cache
    if cache_key in _bert_feature_cache:
        val = _bert_feature_cache.pop(cache_key)
        _bert_feature_cache[cache_key] = val
        return val.clone()

    model = bert_models.load_model(Languages.JP, device_map=device)
    bert_models.transfer_model(Languages.JP, device)

    style_res_mean = None
    with torch.no_grad():
        tokenizer = bert_models.load_tokenizer(Languages.JP)
        inputs = tokenizer(text_clean, return_tensors="pt")
        for i in inputs:
            inputs[i] = inputs[i].to(device)  # type: ignore
        res = model(**inputs, output_hidden_states=True)
        res = torch.cat(res["hidden_states"][-3:-2], -1)[0].cpu()
        if assist_text_clean:
            style_inputs = tokenizer(assist_text_clean, return_tensors="pt")
            for i in style_inputs:
                style_inputs[i] = style_inputs[i].to(device)  # type: ignore
            style_res = model(**style_inputs, output_hidden_states=True)
            style_res = torch.cat(style_res["hidden_states"][-3:-2], -1)[0].cpu()
            style_res_mean = style_res.mean(0)

    assert len(word2ph) == len(text_clean) + 2, text_clean
    word2phone = word2ph
    phone_level_feature = []
    for i in range(len(word2phone)):
        if assist_text_clean:
            assert style_res_mean is not None
            repeat_feature = (
                res[i].repeat(word2phone[i], 1) * (1 - assist_text_weight)
                + style_res_mean.repeat(word2phone[i], 1) * assist_text_weight
            )
        else:
            repeat_feature = res[i].repeat(word2phone[i], 1)
        phone_level_feature.append(repeat_feature)

    phone_level_feature = torch.cat(phone_level_feature, dim=0)
    res_tensor = phone_level_feature.T

    # Store in cache
    if len(_bert_feature_cache) >= _MAX_CACHE_SIZE:
        _bert_feature_cache.popitem(last=False)
    _bert_feature_cache[cache_key] = res_tensor

    return res_tensor.clone()


def extract_bert_feature_onnx(
    text: str,
    word2ph: list[int],
    onnx_providers: Sequence[Union[str, tuple[str, dict[str, Any]]]],
    assist_text: Optional[str] = None,
    assist_text_weight: float = 0.7,
) -> NDArray[Any]:
    """
    日本語のテキストから BERT の特徴量を抽出する (ONNX 推論)

    Args:
        text (str): 日本語のテキスト
        word2ph (list[int]): 元のテキストの各文字に音素が何個割り当てられるかを表すリスト
        onnx_providers (list[str]): ONNX 推論で利用する ExecutionProvider (CPUExecutionProvider, CUDAExecutionProvider など)
        assist_text (Optional[str], optional): 補助テキスト (デフォルト: None)
        assist_text_weight (float, optional): 補助テキスト of the weight (デフォルト: 0.7)

    Returns:
        NDArray[Any]: BERT の特徴量
    """

    # 各単語が何文字かを作る `word2ph` を使う必要があるので、読めない文字は必ず無視する
    # でないと `word2ph` の結果とテキストの文字数結果が整合性が取れない
    text_clean = "".join(text_to_sep_kata(text, raise_yomi_error=False)[0])
    assist_text_clean = "".join(text_to_sep_kata(assist_text, raise_yomi_error=False)[0]) if assist_text else None

    # Check memory cache (Fase 3 Optimization)
    prov_key = tuple((p if isinstance(p, str) else (p[0], tuple(sorted(p[1].items())))) for p in onnx_providers)
    cache_key = (text_clean, tuple(word2ph), prov_key, assist_text_clean, assist_text_weight)
    global _bert_feature_onnx_cache
    if cache_key in _bert_feature_onnx_cache:
        val = _bert_feature_onnx_cache.pop(cache_key)
        _bert_feature_onnx_cache[cache_key] = val
        return val.copy()

    # トークナイザーとモデルの読み込み
    tokenizer = onnx_bert_models.load_tokenizer(Languages.JP)
    session = onnx_bert_models.load_model(
        language=Languages.JP,
        onnx_providers=onnx_providers,
    )
    input_names = [input.name for input in session.get_inputs()]
    output_name = session.get_outputs()[0].name

    # 入力テンソルの転送に使用するデバイス種別, デバイス ID, 実行オプションを取得
    device_type, device_id, run_options = get_onnx_device_options(session, onnx_providers)  # fmt: skip

    # 入力をテンソルに変換
    inputs = tokenizer(text_clean, return_tensors="np")
    input_tensor = [
        inputs["input_ids"].astype(np.int64),  # type: ignore
        inputs["attention_mask"].astype(np.int64),  # type: ignore
    ]
    # 推論デバイスに入力テンソルを割り当て
    ## GPU 推論の場合、device_type + device_id に対応する GPU デバイスに入力テンソルが割り当てられる
    io_binding = session.io_binding()
    for name, value in zip(input_names, input_tensor):
        gpu_tensor = onnxruntime.OrtValue.ortvalue_from_numpy(
            value, device_type, device_id
        )
        io_binding.bind_ortvalue_input(name, gpu_tensor)
    # text から BERT 特徴量を抽出
    io_binding.bind_output(output_name, device_type)
    session.run_with_iobinding(io_binding, run_options=run_options)
    res = io_binding.get_outputs()[0].numpy()

    style_res_mean = None
    if assist_text_clean:
        # 入力をテンソルに変換
        style_inputs = tokenizer(assist_text_clean, return_tensors="np")
        style_input_tensor = [
            style_inputs["input_ids"].astype(np.int64),  # type: ignore
            style_inputs["attention_mask"].astype(np.int64),  # type: ignore
        ]
        # 推論デバイスに入力テンソルを割り当て
        ## GPU 推論の場合、device_type + device_id に対応する GPU デバイスに入力テンソルが割り当てられる
        io_binding = session.io_binding()  # IOBinding は作り直す必要がある
        for name, value in zip(input_names, style_input_tensor):
            gpu_tensor = onnxruntime.OrtValue.ortvalue_from_numpy(
                value, device_type, device_id
            )
            io_binding.bind_ortvalue_input(name, gpu_tensor)
        # assist_text から BERT 特徴量を抽出
        io_binding.bind_output(output_name, device_type)
        session.run_with_iobinding(io_binding, run_options=run_options)
        style_res = io_binding.get_outputs()[0].numpy()
        style_res_mean = np.mean(style_res, axis=0)

    assert len(word2ph) == len(text_clean) + 2, text_clean
    word2phone = word2ph
    phone_level_feature = []
    for i in range(len(word2phone)):
        if assist_text_clean:
            assert style_res_mean is not None
            repeat_feature = (
                np.tile(res[i], (word2phone[i], 1)) * (1 - assist_text_weight)
                + np.tile(style_res_mean, (word2phone[i], 1)) * assist_text_weight
            )
        else:
            repeat_feature = np.tile(res[i], (word2phone[i], 1))
        phone_level_feature.append(repeat_feature)

    phone_level_feature = np.concatenate(phone_level_feature, axis=0)
    res_np = phone_level_feature.T

    # Store in cache
    if len(_bert_feature_onnx_cache) >= _MAX_CACHE_SIZE:
        _bert_feature_onnx_cache.popitem(last=False)
    _bert_feature_onnx_cache[cache_key] = res_np

    return res_np.copy()
