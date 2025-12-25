import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def clear_existing_files():
    """Clear all existing 4- files"""
    import os
    import glob
    
    # Clear figures
    figure_files = glob.glob('output/figures/4-*.png')
    for file in figure_files:
        try:
            os.remove(file)
            print(f"Removed: {file}")
        except:
            pass
    
    # Clear tables
    table_files = glob.glob('output/tables/4-*.csv')
    for file in table_files:
        try:
            os.remove(file)
            print(f"Removed: {file}")
        except:
            pass

def main():
    """Analyze average length of consumption spells by hour"""
    print("Clearing all existing 4- files...")
    clear_existing_files()
    
    print("Loading data for consumption spell length analysis...")
    
    # Load the same dataset as 2- and 3- scripts
    df = pd.read_csv('/Users/poum/Downloads/hour_spells_filled_all_hours.csv')
    df['seg_start'] = pd.to_datetime(df['seg_start'])
    df['seg_end'] = pd.to_datetime(df['seg_end'])
    df['date'] = pd.to_datetime(df['date'])
    
    print("Analyzing consumption spell lengths by hour...")
    
    # Calculate average consumption spell lengths by hour
    consumption_lengths = calculate_consumption_lengths_by_hour(df)
    
    # Create plots
    create_consumption_length_plots(consumption_lengths, df)
    
    # Export statistics
    export_consumption_length_statistics(consumption_lengths)
    
    print("Consumption spell length analysis complete!")

def calculate_consumption_lengths_by_hour(df):
    """Calculate average consumption spell lengths by hour"""
    
    print("Calculating consumption spell lengths by hour...")
    
    # Filter for consumption segments only
    consumption_df = df[df['Consumption'] == 1].copy()
    
    # Create a list to store results
    hourly_results = []
    
    # For each hour (0-23)
    for hour in range(24):
        hour_label = f'{hour:02d}:00-{hour+1:02d}:00'
        hour_data = consumption_df[consumption_df['hour_label'] == hour_label]
        
        if len(hour_data) > 0:
            # Calculate statistics for this hour
            lengths = hour_data['seg_minutes']
            
            hourly_results.append({
                'hour': hour,
                'hour_label': hour_label,
                'count': len(lengths),
                'mean_length': lengths.mean(),
                'median_length': lengths.median(),
                'std_length': lengths.std(),
                'min_length': lengths.min(),
                'max_length': lengths.max(),
                'q25_length': lengths.quantile(0.25),
                'q75_length': lengths.quantile(0.75)
            })
        else:
            # No consumption data for this hour
            hourly_results.append({
                'hour': hour,
                'hour_label': hour_label,
                'count': 0,
                'mean_length': np.nan,
                'median_length': np.nan,
                'std_length': np.nan,
                'min_length': np.nan,
                'max_length': np.nan,
                'q25_length': np.nan,
                'q75_length': np.nan
            })
    
    return hourly_results

def create_consumption_length_plots(hourly_results, df):
    """Create plots for consumption spell lengths by hour"""
    
    print("Creating consumption spell length plots...")
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create single figure
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Extract data for plotting
    hours = [r['hour'] for r in hourly_results]
    mean_lengths = [r['mean_length'] for r in hourly_results]
    
    # Calculate overall mean from ALL consumption spell lengths in the entire dataset
    all_consumption_lengths = df[df['Consumption'] == 1]['seg_minutes']
    overall_mean = all_consumption_lengths.mean()
    
    # Plot hourly means
    ax.plot(hours, mean_lengths, 'o-', linewidth=2, color='red', alpha=0.8, label='Mean')
    
    ax.set_xlabel('Hour of day')
    ax.set_ylabel('Consumption spell length (minutes)')
    ax.set_xlim(-0.5, 23.5)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig('output/figures/4-consumption_spell_length_summary.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Plots saved to output/figures/ directory")


def export_consumption_length_statistics(hourly_results):
    """Export consumption spell length statistics to CSV files"""
    
    print("Exporting consumption spell length statistics to CSV...")
    
    # Create summary statistics table
    summary_data = []
    for result in hourly_results:
        summary_data.append({
            'hour': result['hour'],
            'hour_label': result['hour_label'],
            'count': result['count'],
            'mean_length': result['mean_length'],
            'median_length': result['median_length'],
            'std_length': result['std_length'],
            'min_length': result['min_length'],
            'max_length': result['max_length'],
            'q25_length': result['q25_length'],
            'q75_length': result['q75_length']
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv('output/tables/4-consumption_spell_length_summary.csv', index=False)
    
    # Create a simplified table with just mean lengths
    mean_data = []
    for result in hourly_results:
        mean_data.append({
            'hour': result['hour'],
            'hour_label': result['hour_label'],
            'mean_consumption_spell_length': result['mean_length'],
            'count': result['count']
        })
    
    mean_df = pd.DataFrame(mean_data)
    mean_df.to_csv('output/tables/4-mean_consumption_spell_length_by_hour.csv', index=False)
    
    print("CSV files saved to output/tables/ directory")
    print(f"  - 4-consumption_spell_length_summary.csv: Detailed statistics for all hours")
    print(f"  - 4-mean_consumption_spell_length_by_hour.csv: Mean lengths by hour")

if __name__ == "__main__":
    main()
