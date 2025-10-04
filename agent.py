#!/usr/bin/env python3
"""
agent.py — LLM-powered Agent-as-Coder using Groq API
"""

from __future__ import annotations
import argparse, os, sys, glob, importlib.util, traceback, subprocess, logging
from textwrap import dedent
from typing import List, Tuple
import pandas as pd
from dotenv import load_dotenv
from groq import Groq

# ============ CONFIG ============ #
load_dotenv()
API_KEY = os.getenv("grok_api_key")
if not API_KEY:
    print("❌ GROQ_API_KEY missing. Please set it via environment or .env file.")
    sys.exit(1)
client = Groq(api_key=API_KEY)
ROOT = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(
    filename="agent.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

# ============ UTILITIES ============ #
def find_data_paths(target: str) -> Tuple[str, str]:
    folder = os.path.join(ROOT, "data", target)
    pdfs = glob.glob(os.path.join(folder, "*.pdf"))
    csvs = glob.glob(os.path.join(folder, "*.csv"))
    if not pdfs or not csvs:
        raise FileNotFoundError(f"Missing PDF or CSV in data/{target}")
    return pdfs[0], csvs[0]

def ensure_custom_parser():
    pkg = os.path.join(ROOT, "custom_parser")
    os.makedirs(pkg, exist_ok=True)
    init_path = os.path.join(pkg, "__init__.py")
    if not os.path.exists(init_path):
        open(init_path, "w").close()

def import_parser(parser_path: str):
    spec = importlib.util.spec_from_file_location("custom_parser", parser_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_parser(parser_path: str, pdf: str, csv: str) -> Tuple[bool, str]:
    try:
        mod = import_parser(parser_path)
        df_pred = mod.parse(pdf)
        df_true = pd.read_csv(csv)
        if df_pred.equals(df_true):
            return True, "✅ DataFrame.equals -> True"
        else:
            diff = f"❌ Mismatch in DataFrames: expected {df_true.shape}, got {df_pred.shape}"
            return False, diff
    except Exception as e:
        return False, f"Exception while running parse(): {e}\n{traceback.format_exc()}"

def run_pytest():
    try:
        res = subprocess.run([sys.executable, "-m", "pytest", "-q"], check=False)
        return res.returncode
    except FileNotFoundError:
        return 1

# ============ CORE LLM AGENT ============ #
def ask_llm_for_parser(target: str, columns: List[str], pdf_name: str, attempt: int, last_error: str = "") -> str:
    """
    Use Groq LLM to generate a Python parser for given bank PDF.
    """
    system_prompt = dedent(f"""
    You are an expert Python developer that writes parsers for bank statements.
    Generate a Python module that defines:
        def parse(pdf_path: str) -> pandas.DataFrame
    Requirements:
      - Must use pdfplumber to extract tables or text.
      - Return a DataFrame with exactly these columns (in order): {columns}.
      - Output must match the CSV schema (same columns, same number of rows ideally).
      - Use pandas, pdfplumber, regex if needed.
      - Clean strings, trim spaces, cast numeric types as float/int where appropriate.
      - Must not rely on external unknown libs.
      - Must be deterministic and runnable without network.
      - Must contain docstring header describing its purpose.

    Bank name: {target.upper()}.
    Sample PDF: {pdf_name}.
    Attempt #: {attempt}.
    Last error summary: {last_error if last_error else "None"}.
    """)
    logging.info("Sending prompt to Groq model...")
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": "You are a senior Python engineer."},
            {"role": "user", "content": system_prompt},
        ],
        temperature=0.2,
    )
    return completion.choices[0].message.content.strip()

import re

def save_parser(target: str, code: str) -> str:
    """
    Clean up LLM output and save as parser file.
    Removes Markdown code fences like ```python ... ``` if present.
    """
    ensure_custom_parser()
    # Extract only the code block content if any
    match = re.search(r"```(?:python)?\n(.*?)```", code, re.DOTALL)
    clean = match.group(1) if match else code

    path = os.path.join(ROOT, "custom_parser", f"{target}_parser.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(clean.strip() + "\n")
    logging.info(f"Saved cleaned parser to {path}")
    return path


# ============ MAIN LOOP ============ #
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    args = parser.parse_args()
    target = args.target.lower().strip()

    pdf_path, csv_path = find_data_paths(target)
    df = pd.read_csv(csv_path, nrows=0)
    expected_cols = list(df.columns)

    print(f"🧠 Starting LLM agent for target: {target}")
    print(f"Expected columns: {expected_cols}")

    success = False
    error_summary = ""
    for attempt in range(1, 4):
        print(f"\n⚙️ Attempt {attempt}/3")
        code = ask_llm_for_parser(target, expected_cols, os.path.basename(pdf_path), attempt, error_summary)
        parser_path = save_parser(target, code)
        ok, msg = test_parser(parser_path, pdf_path, csv_path)
        print(msg)
        if ok:
            success = True
            break
        else:
            error_summary = msg
            print("🔁 Retry: refining based on last error...")

    if success:
        print(f"\n✅ Success! Parser generated: custom_parser/{target}_parser.py")
        print("Running pytest for verification...")
        run_pytest()
    else:
        print("\n❌ Failed after 3 attempts. Check agent.log for debug info.")

if __name__ == "__main__":
    main()
