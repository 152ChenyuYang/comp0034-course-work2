import pandas as pd
from pathlib import Path


base_dir = Path(__file__).parent 
file_path = base_dir / 'data' / 'dclg-affordable-housing-borough.xlsx'


if not file_path.exists():
    raise FileNotFoundError(f"Data file not found: {file_path.resolve()}")


data_df = pd.read_excel(file_path, sheet_name=1)


data_df = data_df.iloc[:, 1:]  


data_df.columns = [col.split('-')[0].strip() if '-' in str(col) else col for col in data_df.columns]


cleaned_data_df = data_df.dropna(how='any').reset_index(drop=True)


cleaned_file_path = base_dir / 'output' / 'cleaned_data_second_sheet_updated_years.xlsx'
cleaned_file_path.parent.mkdir(exist_ok=True)  
cleaned_data_df.to_excel(cleaned_file_path, index=False)

print(f"Cleaned file saved to: {cleaned_file_path.resolve()}")
