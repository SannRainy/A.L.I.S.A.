import os
import httpx
import asyncio
from pathlib import Path

READING_TEXTS = {
    "read_1": "私はクリスです。学生です。日本語の文化が好きです。毎日日本語を練習します。すみません、あなたも学生ですか。",
    "read_2": "私と一緒に お昼ご飯を 食べませんか。いいですね。駅の 近くの レストランで 食べましょう。私は 魚が 好きですが、肉も 好きです。じゃあ、駅で 会いましょうね。お茶か コーヒーも 飲みましょう。",
    "read_3": "私は ケーキを 作るのが 好きです。あなたは ケーキの 作り方を 知っていますか。とても 簡単ですよ。でも、私は おはしの 使い方が 下手です。おはしの 使い方が 上手になりたいです。教えてください。",
    "read_4": "日曜日は 買い物したり、映画を 見たりしました。自転車が こわれたから、新しい 自転車を 買いに 行きました。日本語を もっと 勉強したいですから、日本語の 本も 買いました。将来は 日本の 会社で 働きたいです。",
    "read_5": "今日の お昼ご飯は 食堂が とても 混んでいます。でも、私の 家には 料理が 作ってありますから、家で 食べます。お母さんは 「肉だけじゃなくて、野菜も 食べたほうが いいですよ」と言いました。寝る前には スマホを 見ては いけません。早く 寝たほうが いいです。"
}

async def generate():
    url = "http://127.0.0.1:5050/voice"
    output_dir = Path("c:/Users/satya/OneDrive/Desktop/TVJP/frontend/static/audio/reading")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        for passage_id, text in READING_TEXTS.items():
            print(f"Generating audio for {passage_id}...")
            params = {
                "text": text,
                "model_id": 0,
                "speaker_id": 0,
                "sdp_ratio": 0.4,
                "noise": 0.6,
                "noisew": 0.9,
                "length": 1.1,
                "language": "JP",
                "auto_split": "true",
                "split_interval": 0.5,
                "style": "Neutral",
                "style_weight": 0.5
            }
            try:
                response = await client.post(url, params=params)
                if response.status_code == 200:
                    dest = output_dir / f"{passage_id}.wav"
                    dest.write_bytes(response.content)
                    print(f"Successfully saved to {dest}")
                else:
                    print(f"Failed for {passage_id}: Status {response.status_code}")
            except Exception as e:
                print(f"Error for {passage_id}: {e}")

if __name__ == "__main__":
    asyncio.run(generate())
