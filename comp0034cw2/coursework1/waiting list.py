import pandas as pd
from pathlib import Path


base_dir = Path(__file__).parent  
file_path = base_dir / 'data' / 'households-on-local-authority-waiting-list.xlsx'


if not file_path.exists():
    raise FileNotFoundError(f"Data file not found: {file_path.resolve()}")


data_df = pd.read_excel(file_path, sheet_name=1)


data_df = data_df.iloc[:, 1:]  
data_df.iloc[0, 0] = "Current ONS Code" 
data_df.iloc[0, 1] = "Area name"  


data_df.columns = data_df.iloc[0] 
data_df = data_df[1:].reset_index(drop=True) 


cleaned_data_df = data_df.dropna(how='any').reset_index(drop=True)


output_path = base_dir / 'output' / 'cleaned_final_result_waiting_list.xlsx'
output_path.parent.mkdir(exist_ok=True) 
cleaned_data_df.to_excel(output_path, index=False)

print(f"Cleaned data saved to: {output_path.resolve()}")
