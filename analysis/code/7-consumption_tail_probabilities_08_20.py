import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def clear_existing_files():
    """Clear all existing 7- files"""
    import os
    import glob
    
    # Clear figures
    figure_files = glob.glob('output/figures/7-*.png')
    for file in figure_files:
        try:
            os.remove(file)
            print(f"Removed: {file}")
        except:
            pass
    
    # Clear tables
    table_files = glob.glob('output/tables/7-*.csv')
    for file in table_files:
        try:
            os.remove(file)
            print(f"Removed: {file}")
        except:
            pass

def main():
    """Calculate tail probabilities for consumption spells in 8am-8pm period"""
    print("Clearing all existing 7- files...")
    clear_existing_files()
    
    print("Loading 8am-8pm data for consumption spell tail probability analysis...")
    
    # Load the 8am-8pm dataset
    df = pd.read_csv('/Users/poum/Downloads/hour_spells_filled_08_20.csv')
    df['seg_start'] = pd.to_datetime(df['seg_start'])
    df['seg_end'] = pd.to_datetime(df['seg_end'])
    df['date'] = pd.to_datetime(df['date'])
    
    print("Calculating consumption spell tail probabilities for 8am-8pm...")
    
    # Calculate tail probabilities for both consumption types
    tail_probabilities = calculate_tail_probabilities_08_20(df)
    
    # Export to CSV
    export_tail_probabilities(tail_probabilities)
    
    print("8am-8pm consumption spell tail probability analysis complete!")

def calculate_tail_probabilities_08_20(df):
    """Calculate P(Spell > x) for both consumption = 0 and consumption = 1 for x from 0 to 720"""
    
    print("Calculating tail probabilities for 8am-8pm period for both consumption types...")
    
    # Create a list to store all results
    all_results = []
    
    # For each consumption type (0 and 1)
    for consumption_type in [0, 1]:
        consumption_data = df[df['Consumption'] == consumption_type]['seg_minutes']
        
        if len(consumption_data) > 0:
            # For each x value from 0 to 720
            for x in range(721):  # 0 to 720 inclusive
                # Calculate P(Spell > x)
                tail_prob = np.mean(consumption_data > x)
                
                all_results.append({
                    'consumption': consumption_type,
                    'x_minutes': x,
                    'tail_probability': tail_prob,
                    'count': len(consumption_data)
                })
        else:
            # No data for this consumption type
            for x in range(721):  # 0 to 720 inclusive
                all_results.append({
                    'consumption': consumption_type,
                    'x_minutes': x,
                    'tail_probability': np.nan,
                    'count': 0
                })
    
    return all_results

def export_tail_probabilities(tail_probabilities):
    """Export tail probabilities to CSV"""
    
    print("Exporting tail probabilities to CSV...")
    
    # Create DataFrame
    df_results = pd.DataFrame(tail_probabilities)
    
    # Save to CSV
    df_results.to_csv('output/tables/7-consumption_spell_tail_probabilities_08_20.csv', index=False)
    
    print("CSV files saved to output/tables/ directory")
    print(f"  - 7-consumption_spell_tail_probabilities_08_20.csv: Full table with {len(df_results)} rows")
    print(f"  - Columns: consumption, x_minutes, tail_probability, count")
    print(f"  - Covers both consumption = 0 and consumption = 1 for 8am-8pm period")
    print(f"  - X values range from 0 to 720 minutes")

if __name__ == "__main__":
    main()





