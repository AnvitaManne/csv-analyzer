from langchain_core.tools import tool
import pandas as pd

@tool
def generate_csv_summary(file_path: str) -> str:
    """Generate summary of a CSV file."""
    df = pd.read_csv(file_path)
    return df.describe(include='all').to_string()
