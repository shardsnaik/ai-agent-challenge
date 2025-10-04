import os
import pandas as pd
import importlib.util
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT, "data", "icici")
PARSER_PATH = os.path.join(ROOT, "custom_parsers", "icici_parser.py")

def import_parser(path):
    spec = importlib.util.spec_from_file_location("icici_parser", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_icici_parse_equals_csv():
    assert os.path.exists(PARSER_PATH), f"Parser file not found: {PARSER_PATH}"
    mod = import_parser(PARSER_PATH)
    assert hasattr(mod, "parse"), "Parser module must define parse(pdf_path) function"
    pdfs = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(".pdf")]
    csvs = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(".csv")]
    assert pdfs, "No pdf found in data/icici"
    assert csvs, "No csv found in data/icici"
    pdf_path = os.path.join(DATA_DIR, pdfs[0])
    csv_path = os.path.join(DATA_DIR, csvs[0])
    df_out = mod.parse(pdf_path)
    df_exp = pd.read_csv(csv_path)
    # Must be exact equals per assignment
    assert df_out.equals(df_exp)
