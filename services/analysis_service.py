from pathlib import Path
import pandas as pd

UPLOAD_DIR = Path("uploads")

def analyze_dataset(path):
    """Analyze a CSV file given a filename or Path"""
    # ensure path is a Path object
    path = Path(path)
    df = pd.read_csv(path)
    numeric_cols = df.select_dtypes(include=['int', 'float']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    return {
        "filename": path.name,
        "rows": len(df),
        "columns": list(df.columns),
        "numeric": numeric_cols,
        "categorical": cat_cols
    }

def get_analysis_results():
    """Analyze all uploaded files and return a list of results."""
    results = []
    for file_path in UPLOAD_DIR.glob("*.csv"):
        try:
            results.append(analyze_dataset(file_path))
        except Exception as e:
            print(f"Error analyzing {file_path.name}: {e}")
    return results