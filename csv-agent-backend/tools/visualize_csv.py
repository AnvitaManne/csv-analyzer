# visualize_csv.py
from langchain_core.tools import tool
import pandas as pd
import matplotlib.pyplot as plt
import os

@tool
def visualize_csv(file_path: str) -> str:
    """Generate a visualization from a CSV file.
    Attempts to generate histograms for numerical columns.
    If no numerical columns are found after cleaning, it will return a message.
    """
    df = pd.read_csv(file_path)
    plot_path = os.path.join("uploads", "plot.png")

    # --- Data Cleaning Step ---
    # Attempt to convert all object/string columns to numeric
    # This handles commas, currency symbols, etc., by converting them to actual numbers.
    # 'errors="coerce"' will turn anything that can't be converted into NaN (Not a Number)
    for col in df.columns:
        if df[col].dtype == 'object':
            # Try to convert to numeric, handles commas by default
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[$,%]', '', regex=True), errors='coerce')
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            # If it's already datetime, keep it.
            pass
        elif not pd.api.types.is_numeric_dtype(df[col]):
            # Attempt to convert other non-numeric types to numeric
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- End Data Cleaning Step ---

    try:
        # Check if there are any numerical columns to plot AFTER cleaning
        numerical_cols = df.select_dtypes(include=['number', 'datetime']).columns
        if numerical_cols.empty:
            return "No numerical or datetime columns found for histogram generation after cleaning."

        if not os.path.exists("uploads"):
            os.makedirs("uploads")

        # Create a single figure with subplots for all numerical columns
        fig, axes = plt.subplots(nrows=len(numerical_cols), ncols=1, figsize=(10, 5 * len(numerical_cols)))
        if len(numerical_cols) == 1: # Handle case with only one subplot
            axes = [axes] # Make it iterable

        for i, col in enumerate(numerical_cols):
            # Drop NaNs for plotting, as hist can't plot NaNs
            df[col].dropna().hist(ax=axes[i])
            axes[i].set_title(f'Distribution of {col}')
            axes[i].set_xlabel(col)
            axes[i].set_ylabel('Frequency')

        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close()
        return plot_path # Return the actual path if successful

    except ValueError as e:
        return f"Error generating plot: {e}. Double-check your CSV data types and column names."
    except Exception as e:
        return f"An unexpected error occurred during plot generation: {e}"