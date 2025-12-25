import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def clear_existing_files():
    """Clear all existing 8- files"""
    import os
    import glob
    
    # Clear figures
    figure_files = glob.glob('output/figures/8-*.png')
    for file in figure_files:
        try:
            os.remove(file)
            print(f"Removed: {file}")
        except:
            pass
    
    # Clear tables
    table_files = glob.glob('output/tables/8-*.csv')
    for file in table_files:
        try:
            os.remove(file)
            print(f"Removed: {file}")
        except:
            pass

def main():
    """Calculate mean minutes and variance for both consumption and non-consumption spells in 8am-8pm period"""
    print("Clearing all existing 8- files...")
    clear_existing_files()
    
    print("Loading 8am-8pm data for spell length statistics analysis...")
    
    # Load the 8am-8pm dataset
    df = pd.read_csv('/Users/poum/Downloads/hour_spells_filled_08_20.csv')
    df['seg_start'] = pd.to_datetime(df['seg_start'])
    df['seg_end'] = pd.to_datetime(df['seg_end'])
    df['date'] = pd.to_datetime(df['date'])
    
    print("Calculating spell length statistics for 8am-8pm...")
    
    # Calculate statistics for both consumption types
    statistics = calculate_spell_length_statistics_08_20(df)
    
    # Export to CSV
    export_statistics(statistics)
    
    # Print the results
    print_results(statistics)
    
    print("8am-8pm spell length statistics analysis complete!")

def calculate_spell_length_statistics_08_20(df):
    """Calculate mean minutes and variance for both consumption and non-consumption spells in 8am-8pm period"""
    
    print("Calculating mean and variance for consumption and non-consumption spells in 8am-8pm period...")
    
    # Separate consumption and non-consumption data
    consumption_data = df[df['Consumption'] == 1]['seg_minutes']
    non_consumption_data = df[df['Consumption'] == 0]['seg_minutes']
    
    # Calculate statistics
    consumption_stats = {
        'consumption': 1,
        'mean_minutes': consumption_data.mean(),
        'variance_minutes': consumption_data.var(),
        'count': len(consumption_data)
    }
    
    non_consumption_stats = {
        'consumption': 0,
        'mean_minutes': non_consumption_data.mean(),
        'variance_minutes': non_consumption_data.var(),
        'count': len(non_consumption_data)
    }
    
    return [consumption_stats, non_consumption_stats]

def export_statistics(statistics):
    """Export statistics to CSV"""
    
    print("Exporting statistics to CSV...")
    
    # Create DataFrame
    df_results = pd.DataFrame(statistics)
    
    # Save to CSV
    df_results.to_csv('output/tables/8-spell_length_statistics_08_20.csv', index=False)
    
    print("CSV files saved to output/tables/ directory")
    print(f"  - 8-spell_length_statistics_08_20.csv: Mean and variance for both consumption types in 8am-8pm period")

def print_results(statistics):
    """Print the results to console"""
    
    print("\n" + "="*60)
    print("SPELL LENGTH STATISTICS FOR 8AM-8PM PERIOD")
    print("="*60)
    
    for stats in statistics:
        consumption_type = "Consumption" if stats['consumption'] == 1 else "Non-Consumption"
        
        print(f"\n{consumption_type} Spells (8am-8pm):")
        print(f"  Count: {stats['count']:,}")
        print(f"  Mean minutes: {stats['mean_minutes']:.3f}")
        print(f"  Variance minutes: {stats['variance_minutes']:.3f}")
    
    print("\n" + "="*60)
    print("SUMMARY COMPARISON (8AM-8PM)")
    print("="*60)
    
    consumption = statistics[0]
    non_consumption = statistics[1]
    
    print(f"Consumption vs Non-Consumption (8am-8pm):")
    print(f"  Mean ratio (consumption/non-consumption): {consumption['mean_minutes']/non_consumption['mean_minutes']:.3f}")
    print(f"  Variance ratio (consumption/non-consumption): {consumption['variance_minutes']/non_consumption['variance_minutes']:.3f}")
    print(f"  Count ratio (consumption/non-consumption): {consumption['count']/non_consumption['count']:.3f}")

if __name__ == "__main__":
    main()





