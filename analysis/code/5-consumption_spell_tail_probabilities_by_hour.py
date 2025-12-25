import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def clear_existing_files():
    """Clear all existing 5- files"""
    import os
    import glob
    
    # Clear figures
    figure_files = glob.glob('output/figures/5-*.png')
    for file in figure_files:
        try:
            os.remove(file)
            print(f"Removed: {file}")
        except:
            pass
    
    # Clear tables
    table_files = glob.glob('output/tables/5-*.csv')
    for file in table_files:
        try:
            os.remove(file)
            print(f"Removed: {file}")
        except:
            pass

def main():
    """Calculate tail probabilities for consumption spells by hour"""
    print("Clearing all existing 5- files...")
    clear_existing_files()
    
    print("Loading data for consumption spell tail probability analysis...")
    
    # Load the same dataset as other scripts
    df = pd.read_csv('/Users/poum/Downloads/hour_spells_filled_all_hours.csv')
    df['seg_start'] = pd.to_datetime(df['seg_start'])
    df['seg_end'] = pd.to_datetime(df['seg_end'])
    df['date'] = pd.to_datetime(df['date'])
    
    print("Calculating consumption spell tail probabilities by hour...")
    
    # Calculate tail probabilities for each hour
    tail_probabilities = calculate_consumption_tail_probabilities_by_hour(df)
    
    # Export to CSV
    export_tail_probabilities(tail_probabilities)
    
    print("Consumption spell tail probability analysis complete!")

def calculate_consumption_tail_probabilities_by_hour(df):
    """Calculate P(Spell > x) for both consumption = 0 and consumption = 1 for each hour and x from 0 to 60"""
    
    print("Calculating tail probabilities for each hour for both consumption types...")
    
    # Create a list to store all results
    all_results = []
    
    # For each hour (0-23)
    for hour in range(24):
        if hour == 23:
            hour_label = '23:00-00:00'  # Special case for the last hour
        else:
            hour_label = f'{hour:02d}:00-{hour+1:02d}:00'
        hour_data = df[df['hour_label'] == hour_label]
        
        # For each consumption type (0 and 1)
        for consumption_type in [0, 1]:
            consumption_data = hour_data[hour_data['Consumption'] == consumption_type]
            
            if len(consumption_data) > 0:
                # Get all spell lengths for this hour and consumption type
                spell_lengths = consumption_data['seg_minutes'].values
                
                # For each x value from 0 to 60
                for x in range(61):  # 0 to 60 inclusive
                    # Calculate P(Spell > x)
                    if len(spell_lengths) > 0:
                        tail_prob = np.mean(spell_lengths > x)
                    else:
                        tail_prob = np.nan
                    
                    all_results.append({
                        'hour_starting': hour,
                        'consumption': consumption_type,
                        'x_minutes': x,
                        'tail_probability': tail_prob,
                        'count': len(spell_lengths)
                    })
            else:
                # No data for this hour and consumption type
                for x in range(61):  # 0 to 60 inclusive
                    all_results.append({
                        'hour_starting': hour,
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
    df_results.to_csv('output/tables/5-consumption_spell_tail_probabilities_by_hour.csv', index=False)
    
    print("CSV files saved to output/tables/ directory")
    print(f"  - 5-consumption_spell_tail_probabilities_by_hour.csv: Full table with {len(df_results)} rows")
    print(f"  - Columns: hour_starting, consumption, x_minutes, tail_probability, count")
    print(f"  - Covers both consumption = 0 and consumption = 1 for all 24 hours")

if __name__ == "__main__":
    main()
