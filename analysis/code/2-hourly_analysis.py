import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def clear_existing_files():
    """Clear all existing 2- files"""
    import os
    import glob
    
    # Clear figures
    figure_files = glob.glob('output/figures/2-*.png')
    for file in figure_files:
        try:
            os.remove(file)
            print(f"Removed: {file}")
        except:
            pass
    
    # Clear tables
    table_files = glob.glob('output/tables/2-*.csv')
    for file in table_files:
        try:
            os.remove(file)
            print(f"Removed: {file}")
        except:
            pass

def main():
    """Hour-by-hour analysis using the properly structured hour_spells_filled_all_hours.csv"""
    print("Clearing all existing 2- files...")
    clear_existing_files()
    
    print("Loading properly structured hourly data...")
    
    # Load the properly structured data
    df = pd.read_csv('/Users/poum/Downloads/hour_spells_filled_all_hours.csv')
    
    # Convert datetime columns
    df['seg_start'] = pd.to_datetime(df['seg_start'])
    df['seg_end'] = pd.to_datetime(df['seg_end'])
    df['date'] = pd.to_datetime(df['date'])
    
    print("Processing hour-by-hour analysis with proper data structure...")
    
    # Process each hour (0-23)
    hourly_results = process_hourly_analysis_final(df)
    
    # Generate outputs
    create_hourly_plots(hourly_results)
    export_hourly_statistics(hourly_results)
    
    print("Final hour-by-hour analysis complete!")

def process_hourly_analysis_final(df):
    """Process each hour (0-23) using the properly structured data"""
    
    hourly_results = []
    
    # Map hour labels to hour numbers
    hour_mapping = {
        '00:00-01:00': 0, '01:00-02:00': 1, '02:00-03:00': 2, '03:00-04:00': 3,
        '04:00-05:00': 4, '05:00-06:00': 5, '06:00-07:00': 6, '07:00-08:00': 7,
        '08:00-09:00': 8, '09:00-10:00': 9, '10:00-11:00': 10, '11:00-12:00': 11,
        '12:00-13:00': 12, '13:00-14:00': 13, '14:00-15:00': 14, '15:00-16:00': 15,
        '16:00-17:00': 16, '17:00-18:00': 17, '18:00-19:00': 18, '19:00-20:00': 19,
        '20:00-21:00': 20, '21:00-22:00': 21, '22:00-23:00': 22, '23:00-00:00': 23
    }
    
    for hour_label, hour_num in hour_mapping.items():
        print(f"Processing {hour_label} (Hour {hour_num})...")
        
        # Get all segments for this hour
        hour_data = df[df['hour_label'] == hour_label].copy()
        
        if len(hour_data) == 0:
            print(f"  No data found for {hour_label}")
            continue
        
        # Separate consumption and non-consumption segments
        consumption_segments = hour_data[hour_data['Consumption'] == 1]['seg_minutes'].values
        non_consumption_segments = hour_data[hour_data['Consumption'] == 0]['seg_minutes'].values
        
        # Calculate basic statistics
        consumption_stats = {
            'count': len(consumption_segments),
            'mean': np.mean(consumption_segments) if len(consumption_segments) > 0 else 0,
            'std': np.std(consumption_segments) if len(consumption_segments) > 0 else 0,
            'variance': np.var(consumption_segments) if len(consumption_segments) > 0 else 0,
            'median': np.median(consumption_segments) if len(consumption_segments) > 0 else 0
        }
        
        non_consumption_stats = {
            'count': len(non_consumption_segments),
            'mean': np.mean(non_consumption_segments) if len(non_consumption_segments) > 0 else 0,
            'std': np.std(non_consumption_segments) if len(non_consumption_segments) > 0 else 0,
            'variance': np.var(non_consumption_segments) if len(non_consumption_segments) > 0 else 0,
            'median': np.median(non_consumption_segments) if len(non_consumption_segments) > 0 else 0
        }
        
        # Calculate tail probabilities for x = 1 to 60 minutes
        tail_probs_consumption = []
        tail_probs_non_consumption = []
        
        for x in range(1, 61):  # 1 to 60 minutes
            if len(consumption_segments) > 0:
                consumption_tail = np.sum(consumption_segments > x) / len(consumption_segments)
            else:
                consumption_tail = 0
            tail_probs_consumption.append(consumption_tail)
            
            if len(non_consumption_segments) > 0:
                non_consumption_tail = np.sum(non_consumption_segments > x) / len(non_consumption_segments)
            else:
                non_consumption_tail = 0
            tail_probs_non_consumption.append(non_consumption_tail)
        
        # Store results
        hourly_results.append({
            'hour': hour_num,
            'hour_label': hour_label,
            'consumption_stats': consumption_stats,
            'non_consumption_stats': non_consumption_stats,
            'tail_probs_consumption': tail_probs_consumption,
            'tail_probs_non_consumption': tail_probs_non_consumption,
            'consumption_segments': consumption_segments,
            'non_consumption_segments': non_consumption_segments
        })
        
        print(f"  {hour_label}: {consumption_stats['count']:4d} consumption, {non_consumption_stats['count']:4d} non-consumption segments")
    
    return hourly_results

def create_hourly_plots(hourly_results):
    """Create plots for hourly analysis"""
    
    print("Creating hourly analysis plots...")
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create figure for consumption segments (24 subplots)
    fig, axes = plt.subplots(6, 4, figsize=(20, 24))
    
    for i, result in enumerate(hourly_results):
        row = i // 4
        col = i % 4
        
        if result['consumption_stats']['count'] > 0:
            x_values = range(1, 61)
            axes[row, col].plot(x_values, result['tail_probs_consumption'], 
                               linewidth=2, color='red', alpha=0.8)
            axes[row, col].set_xlabel('x (minutes)')
            axes[row, col].set_ylabel('P(Segment > x)')
            axes[row, col].set_xlim(0, 60)
            axes[row, col].grid(True, alpha=0.3)
            axes[row, col].text(0.5, 0.95, f'Hour {result["hour"]}', 
                               ha='center', va='top', transform=axes[row, col].transAxes, 
                               fontsize=10, fontweight='bold')
        else:
            axes[row, col].text(0.5, 0.5, f'{result["hour_label"]}\nNo Data', 
                               ha='center', va='center', transform=axes[row, col].transAxes)
            axes[row, col].text(0.5, 0.95, f'Hour {result["hour"]}', 
                               ha='center', va='top', transform=axes[row, col].transAxes, 
                               fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('output/figures/2-hourly_consumption_plots.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create figure for non-consumption segments (24 subplots)
    fig, axes = plt.subplots(6, 4, figsize=(20, 24))
    
    for i, result in enumerate(hourly_results):
        row = i // 4
        col = i % 4
        
        if result['non_consumption_stats']['count'] > 0:
            x_values = range(1, 61)
            axes[row, col].plot(x_values, result['tail_probs_non_consumption'], 
                               linewidth=2, color='blue', alpha=0.8)
            axes[row, col].set_xlabel('x (minutes)')
            axes[row, col].set_ylabel('P(Segment > x)')
            axes[row, col].set_xlim(0, 60)
            axes[row, col].grid(True, alpha=0.3)
            axes[row, col].text(0.5, 0.95, f'Hour {result["hour"]}', 
                               ha='center', va='top', transform=axes[row, col].transAxes, 
                               fontsize=10, fontweight='bold')
        else:
            axes[row, col].text(0.5, 0.5, f'{result["hour_label"]}\nNo Data', 
                               ha='center', va='center', transform=axes[row, col].transAxes)
            axes[row, col].text(0.5, 0.95, f'Hour {result["hour"]}', 
                               ha='center', va='top', transform=axes[row, col].transAxes, 
                               fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('output/figures/2-hourly_non_consumption_plots.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create summary plots showing patterns across hours
    create_hourly_summary_plots(hourly_results)
    
    print("Plots saved to output/figures/ directory")

def create_hourly_summary_plots(hourly_results):
    """Create summary plots showing patterns across hours"""
    
    # Extract summary statistics
    hours = [r['hour'] for r in hourly_results]
    hour_labels = [r['hour_label'] for r in hourly_results]
    consumption_means = [r['consumption_stats']['mean'] for r in hourly_results]
    consumption_counts = [r['consumption_stats']['count'] for r in hourly_results]
    non_consumption_means = [r['non_consumption_stats']['mean'] for r in hourly_results]
    non_consumption_counts = [r['non_consumption_stats']['count'] for r in hourly_results]
    
    # Create summary figure
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Plot 1: Mean segment lengths by hour
    axes[0, 0].plot(hours, consumption_means, 'o-', linewidth=2, color='red', alpha=0.8, label='Consumption')
    axes[0, 0].plot(hours, non_consumption_means, 'o-', linewidth=2, color='blue', alpha=0.8, label='Non-Consumption')
    axes[0, 0].set_xlabel('Hour of Day')
    axes[0, 0].set_ylabel('Mean Segment Length (minutes)')
    axes[0, 0].set_xlim(-0.5, 23.5)
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].legend()
    
    # Plot 2: Segment counts by hour
    axes[0, 1].bar(hours, consumption_counts, alpha=0.7, color='red', label='Consumption')
    axes[0, 1].bar(hours, non_consumption_counts, alpha=0.7, color='blue', label='Non-Consumption')
    axes[0, 1].set_xlabel('Hour of Day')
    axes[0, 1].set_ylabel('Number of Segments')
    axes[0, 1].set_xlim(-0.5, 23.5)
    axes[0, 1].legend()
    
    # Plot 3: Consumption rate by hour
    consumption_rates = [c / (c + nc) if (c + nc) > 0 else 0 for c, nc in zip(consumption_counts, non_consumption_counts)]
    axes[1, 0].plot(hours, consumption_rates, 'o-', linewidth=2, color='green', alpha=0.8)
    axes[1, 0].set_xlabel('Hour of Day')
    axes[1, 0].set_ylabel('Consumption Rate')
    axes[1, 0].set_xlim(-0.5, 23.5)
    axes[1, 0].set_ylim(0, 1)
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 4: Total activity by hour
    total_counts = [c + nc for c, nc in zip(consumption_counts, non_consumption_counts)]
    axes[1, 1].bar(hours, total_counts, alpha=0.7, color='purple')
    axes[1, 1].set_xlabel('Hour of Day')
    axes[1, 1].set_ylabel('Total Number of Segments')
    axes[1, 1].set_xlim(-0.5, 23.5)
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/figures/2-hourly_summary_plots.png', dpi=300, bbox_inches='tight')
    plt.close()

def export_hourly_statistics(hourly_results):
    """Export hourly statistics to CSV files"""
    
    print("Exporting hourly statistics to CSV...")
    
    # Create summary statistics table
    summary_data = []
    for result in hourly_results:
        summary_data.append({
            'hour': result['hour'],
            'hour_label': result['hour_label'],
            'consumption_count': result['consumption_stats']['count'],
            'consumption_mean': result['consumption_stats']['mean'],
            'consumption_std': result['consumption_stats']['std'],
            'consumption_variance': result['consumption_stats']['variance'],
            'consumption_median': result['consumption_stats']['median'],
            'non_consumption_count': result['non_consumption_stats']['count'],
            'non_consumption_mean': result['non_consumption_stats']['mean'],
            'non_consumption_std': result['non_consumption_stats']['std'],
            'non_consumption_variance': result['non_consumption_stats']['variance'],
            'non_consumption_median': result['non_consumption_stats']['median']
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv('output/tables/2-hourly_summary_statistics.csv', index=False)
    
    # Create tail probabilities tables
    # Consumption tail probabilities
    consumption_tail_data = []
    for result in hourly_results:
        for x in range(1, 61):
            consumption_tail_data.append({
                'hour': result['hour'],
                'hour_label': result['hour_label'],
                'x_minutes': x,
                'tail_probability': result['tail_probs_consumption'][x-1]
            })
    
    consumption_tail_df = pd.DataFrame(consumption_tail_data)
    consumption_tail_df.to_csv('output/tables/2-hourly_tail_probabilities_consumption.csv', index=False)
    
    # Non-consumption tail probabilities
    non_consumption_tail_data = []
    for result in hourly_results:
        for x in range(1, 61):
            non_consumption_tail_data.append({
                'hour': result['hour'],
                'hour_label': result['hour_label'],
                'x_minutes': x,
                'tail_probability': result['tail_probs_non_consumption'][x-1]
            })
    
    non_consumption_tail_df = pd.DataFrame(non_consumption_tail_data)
    non_consumption_tail_df.to_csv('output/tables/2-hourly_tail_probabilities_non_consumption.csv', index=False)
    
    print("CSV files saved to output/tables/ directory")
    print(f"  - 2-hourly_summary_statistics.csv: Summary statistics for all 24 hours")
    print(f"  - 2-hourly_tail_probabilities_consumption.csv: Tail probabilities for consumption segments")
    print(f"  - 2-hourly_tail_probabilities_non_consumption.csv: Tail probabilities for non-consumption segments")

if __name__ == "__main__":
    main()
