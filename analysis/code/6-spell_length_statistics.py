import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def clear_existing_files():
    """Clear all existing 6- files"""
    import os
    import glob
    
    # Clear figures
    figure_files = glob.glob('output/figures/6-*.png')
    for file in figure_files:
        try:
            os.remove(file)
            print(f"Removed: {file}")
        except:
            pass
    
    # Clear tables
    table_files = glob.glob('output/tables/6-*.csv')
    for file in table_files:
        try:
            os.remove(file)
            print(f"Removed: {file}")
        except:
            pass

def main():
    """Calculate mean minutes and variance for both consumption and non-consumption spells"""
    print("Clearing all existing 6- files...")
    clear_existing_files()
    
    print("Loading data for spell length statistics analysis...")
    
    # Load the same dataset as other scripts
    df = pd.read_csv('/Users/poum/Downloads/hour_spells_filled_all_hours.csv')
    df['seg_start'] = pd.to_datetime(df['seg_start'])
    df['seg_end'] = pd.to_datetime(df['seg_end'])
    df['date'] = pd.to_datetime(df['date'])
    
    print("Calculating spell length statistics...")
    
    # Calculate statistics for both consumption types
    statistics = calculate_spell_length_statistics(df)
    
    # Export to CSV
    export_statistics(statistics)
    
    # Print the results
    print_results(statistics)
    
    print("Spell length statistics analysis complete!")

def calculate_spell_length_statistics(df):
    """Calculate mean minutes and variance for both consumption and non-consumption spells PER HOUR"""
    
    print("Calculating mean and variance for consumption and non-consumption spells per hour...")
    
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
            consumption_data = hour_data[hour_data['Consumption'] == consumption_type]['seg_minutes']
            
            if len(consumption_data) > 0:
                stats = {
                    'hour_starting': hour,
                    'consumption': consumption_type,
                    'mean_minutes': consumption_data.mean(),
                    'variance_minutes': consumption_data.var(),
                    'count': len(consumption_data)
                }
            else:
                # No data for this hour and consumption type
                stats = {
                    'hour_starting': hour,
                    'consumption': consumption_type,
                    'mean_minutes': np.nan,
                    'variance_minutes': np.nan,
                    'count': 0
                }
            
            all_results.append(stats)
    
    return all_results

def export_statistics(statistics):
    """Export statistics to CSV"""
    
    print("Exporting statistics to CSV...")
    
    # Create DataFrame
    df_results = pd.DataFrame(statistics)
    
    # Save to CSV
    df_results.to_csv('output/tables/6-spell_length_statistics.csv', index=False)
    
    print("CSV files saved to output/tables/ directory")
    print(f"  - 6-spell_length_statistics.csv: Mean and variance for both consumption types")

def print_results(statistics):
    """Print the results to console"""
    
    print("\n" + "="*80)
    print("SPELL LENGTH STATISTICS BY HOUR")
    print("="*80)
    
    # Print summary table
    print(f"{'Hour':<6} {'Type':<12} {'Count':<8} {'Mean':<8} {'Variance':<12}")
    print("-" * 60)
    
    for stats in statistics:
        consumption_type = "Consumption" if stats['consumption'] == 1 else "Non-Consumption"
        hour = stats['hour_starting']
        count = stats['count']
        mean = stats['mean_minutes']
        variance = stats['variance_minutes']
        
        if not np.isnan(mean):
            print(f"{hour:<6} {consumption_type:<12} {count:<8,} {mean:<8.3f} {variance:<12.3f}")
        else:
            print(f"{hour:<6} {consumption_type:<12} {count:<8,} {'N/A':<8} {'N/A':<12}")
    
    print("\n" + "="*80)
    print("KEY INSIGHTS")
    print("="*80)
    
    # Calculate overall averages
    consumption_means = [s['mean_minutes'] for s in statistics if s['consumption'] == 1 and not np.isnan(s['mean_minutes'])]
    non_consumption_means = [s['mean_minutes'] for s in statistics if s['consumption'] == 0 and not np.isnan(s['mean_minutes'])]
    
    consumption_vars = [s['variance_minutes'] for s in statistics if s['consumption'] == 1 and not np.isnan(s['variance_minutes'])]
    non_consumption_vars = [s['variance_minutes'] for s in statistics if s['consumption'] == 0 and not np.isnan(s['variance_minutes'])]
    
    if consumption_means and non_consumption_means:
        print(f"Average mean across all hours:")
        print(f"  Consumption: {np.mean(consumption_means):.3f} minutes")
        print(f"  Non-Consumption: {np.mean(non_consumption_means):.3f} minutes")
        print(f"  Ratio (consumption/non-consumption): {np.mean(consumption_means)/np.mean(non_consumption_means):.3f}")
        
        print(f"\nAverage variance across all hours:")
        print(f"  Consumption: {np.mean(consumption_vars):.3f}")
        print(f"  Non-Consumption: {np.mean(non_consumption_vars):.3f}")
        print(f"  Ratio (consumption/non-consumption): {np.mean(consumption_vars)/np.mean(non_consumption_vars):.3f}")

if __name__ == "__main__":
    main()
