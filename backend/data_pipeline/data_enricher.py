import json
import csv
import re
import os
import httpx
import asyncio
from typing import List, Dict

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOC_DIR = os.path.join(BASE_DIR, "document")
KANJI_JSON = os.path.join(DOC_DIR, "jlpt-kanji.json")
GRAMMAR_TXT = os.path.join(DOC_DIR, "560045363-JLPT-N5-Grammar-Master-Ebok-by-JLPTsensei-com.txt")

NODES_VOCAB = os.path.join(BASE_DIR, "nodes_vocabulary.csv")
NODES_KANJI = os.path.join(BASE_DIR, "nodes_kanji.csv")
NODES_GRAMMAR = os.path.join(BASE_DIR, "nodes_grammar.csv")
NODES_SENTENCE = os.path.join(BASE_DIR, "nodes_sentence.csv")
EDGES_SENTENCE_GRAMMAR = os.path.join(BASE_DIR, "edges_sentence_grammar.csv")
EDGES_SENTENCE_VOCAB = os.path.join(BASE_DIR, "edges_sentence_vocab.csv")

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings
from services.llm_agent import get_unsloth_model

class DataEnricher:
    def __init__(self):
        self.vocab = []
        self.kanji = {}
        self.grammar = {}
        self.sentences = []
        self.edges_gs = []
        self.edges_sv = []

    def load_existing_data(self):
        print("Loading existing CSV data...")
        # Load Vocab for cross-linking
        if os.path.exists(NODES_VOCAB):
            with open(NODES_VOCAB, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.vocab = list(reader)

        # Load Kanji to update
        if os.path.exists(NODES_KANJI):
            with open(NODES_KANJI, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.kanji[row["kanji_id"]] = row

        # Load Grammar to merge
        if os.path.exists(NODES_GRAMMAR):
            with open(NODES_GRAMMAR, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.grammar[row["grammar_id"]] = row

    def enrich_kanji(self):
        print("Enriching Kanji from JSON...")
        if not os.path.exists(KANJI_JSON):
            print(f"Warning: {KANJI_JSON} not found.")
            return

        with open(KANJI_JSON, "r", encoding="utf-8") as f:
            kanji_data = json.load(f)

        for item in kanji_data:
            char = item.get("kanji")
            if char in self.kanji:
                # Update existing
                self.kanji[char]["strokes"] = item.get("strokes") or ""
                self.kanji[char]["frequency"] = item.get("frequency") or ""
                self.kanji[char]["description"] = item.get("description") or ""
            elif item.get("jlpt") == "N5":
                # Add new N5 kanji if missing
                self.kanji[char] = {
                    "kanji_id": char,
                    "onyomi": "", # Should be filled later or skipped if we don't have it
                    "kunyomi": "",
                    "arti": "",
                    "level": "N5",
                    "strokes": item.get("strokes") or "",
                    "frequency": item.get("frequency") or "",
                    "description": item.get("description") or ""
                }

    def parse_grammar_txt(self):
        print("Parsing Grammar TXT...")
        if not os.path.exists(GRAMMAR_TXT):
            print(f"Warning: {GRAMMAR_TXT} not found.")
            return

        with open(GRAMMAR_TXT, "r", encoding="utf-8") as f:
            content = f.read()

        # Split by Table of Contents or Pages - actually better to look for numbered sections
        # Pattern for grammar sections: \n\s*(\d+)\s+([^\n]+)\n
        # But titles are often followed by "Meaning" and "How To Use"
        
        # Strategy: Find all "Example Sentences" blocks and work backwards to find the title
        sections = re.split(r"", content) # Split by Form Feed character if present
        
        grammar_count = 0
        sentence_id_counter = 1
        
        for section in sections:
            # Try to find a grammar title at the top
            lines = [l.strip() for l in section.split("\n") if l.strip()]
            if not lines: continue
            
            # Look for grammar title like "2    だ・です" or just the title "だ・です"
            # Some sections start with "Example Sentences" but belong to previous titles.
            # This is tricky because the PDF-to-txt conversion might be messy.
            
            # Let's search for "Learn Japanese grammar: [Name]"
            learn_match = re.search(r"Learn Japanese grammar:\s*([^\.]+)\.", section)
            if learn_match:
                grammar_raw = learn_match.group(1).split("(")[0].strip()
                grammar_id = grammar_raw.split("/")[0].strip() # Use first one as ID
                
                if grammar_id not in self.grammar:
                    self.grammar[grammar_id] = {
                        "grammar_id": grammar_id,
                        "name": grammar_raw,
                        "level": "N5"
                    }
                
                # Find Example Sentences
                ex_block = re.search(r"Example Sentences\s+(.+?)(\n\s*\d+\s+|$)", section, re.DOTALL)
                if ex_block:
                    ex_text = ex_block.group(1)
                    # Pattern for numbered sentences: 1. [JP]\n [Romaji]\n [EN]
                    sentences = re.findall(r"(\d+)\.\s+([^\n]+)\n\s+([^\n]+)\n\s+([^\n]+)", ex_text)
                    for num, jp, romaji, en in sentences:
                        sid = f"S{sentence_id_counter:03d}"
                        self.sentences.append({
                            "sentence_id": sid,
                            "japanese_text": jp.strip(),
                            "romaji": romaji.strip(),
                            "english_text": en.strip(), # Intermediate
                            "indonesian_translation": "", # Target
                            "level": "N5"
                        })
                        self.edges_gs.append({"grammar_id": grammar_id, "sentence_id": sid})
                        sentence_id_counter += 1
                        
        print(f"Extracted {len(self.grammar)} grammar points and {len(self.sentences)} sentences.")

    async def translate_sentences(self):
        print("Translating sentences to Indonesian via Unsloth...")
        model, tokenizer = await asyncio.to_thread(get_unsloth_model)
        
        for i, row in enumerate(self.sentences):
            en_text = row["english_text"]
            prompt = f"Translate this Japanese-English sentence translation into a natural Indonesian translation (very concise and friendly, use 'saya' or 'aku' as appropriate for a tutor): '{en_text}'. Output ONLY the translation text."
            
            try:
                messages = [{"role": "user", "content": prompt}]
                inputs = tokenizer.apply_chat_template(
                    messages,
                    tokenize = True,
                    add_generation_prompt = True,
                    return_tensors = "pt",
                ).to("cuda")
                
                def generate_sync():
                    outputs = model.generate(
                        inputs, 
                        max_new_tokens=256, 
                        temperature=0.3, 
                        do_sample=True
                    )
                    return tokenizer.batch_decode(outputs[:, inputs.shape[1]:], skip_special_tokens=True)[0]
                
                translation = await asyncio.get_running_loop().run_in_executor(None, generate_sync)
                translation = translation.replace('"', '').replace("'", "").strip()
                row["indonesian_translation"] = translation
            except Exception as e:
                print(f"Error translating: {e}")
                row["indonesian_translation"] = en_text
            
            if (i+1) % 10 == 0:
                print(f"Translated {i+1}/{len(self.sentences)} sentences...")

    def link_sentences_to_vocab(self):
        print("Linking sentences to vocabulary...")
        for sent in self.sentences:
            jp_text = sent["japanese_text"]
            for v in self.vocab:
                v_id = v["vocab_id"]
                # Basic check: is the kanji/vocab in the sentence?
                if v_id in jp_text:
                    self.edges_sv.append({"sentence_id": sent["sentence_id"], "vocab_id": v_id})

    def save_csvs(self):
        print("Saving updated CSV files...")
        
        # Kanji
        fieldnames_kanji = ["kanji_id", "onyomi", "kunyomi", "arti", "level", "strokes", "frequency", "description"]
        with open(NODES_KANJI, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames_kanji)
            writer.writeheader()
            for k in self.kanji.values():
                # Filter out unwanted keys if any
                writer.writerow({fn: k.get(fn, "") for fn in fieldnames_kanji})

        # Grammar
        fieldnames_grammar = ["grammar_id", "name", "level"]
        with open(NODES_GRAMMAR, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames_grammar)
            writer.writeheader()
            for g in self.grammar.values():
                writer.writerow({fn: g.get(fn, "") for fn in fieldnames_grammar})

        # Sentences
        fieldnames_sentence = ["sentence_id", "japanese_text", "romaji", "indonesian_translation", "level"]
        with open(NODES_SENTENCE, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames_sentence)
            writer.writeheader()
            for s in self.sentences:
                writer.writerow({fn: s.get(fn, "") for fn in fieldnames_sentence})

        # Edges
        with open(EDGES_SENTENCE_GRAMMAR, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["grammar_id", "sentence_id"])
            writer.writeheader()
            writer.writerows(self.edges_gs)

        with open(EDGES_SENTENCE_VOCAB, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["sentence_id", "vocab_id"])
            writer.writeheader()
            writer.writerows(self.edges_sv)

async def main():
    enricher = DataEnricher()
    enricher.load_existing_data()
    enricher.enrich_kanji()
    enricher.parse_grammar_txt()
    await enricher.translate_sentences()
    enricher.link_sentences_to_vocab()
    enricher.save_csvs()
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
