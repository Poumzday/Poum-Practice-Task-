import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def clear_existing_files():
    """Clear all existing 3- files"""
    import os
    import glob
    
    # Clear figures
    figure_files = glob.glob('output/figures/3-*.png')
    for file in figure_files:
        try:
            os.remove(file)
            print(f"Removed: {file}")
        except:
            pass
    
    # Clear tables
    table_files = glob.glob('output/tables/3-*.csv')
    for file in table_files:
        try:
            os.remove(file)
            print(f"Removed: {file}")
        except:
            pass

def main():
    """Analyze distribution of consumption and non-consumption spell counts per hour"""
    print("Clearing all existing 3- files...")
    clear_existing_files()
    
    print("Loading data for spell count distribution analysis...")
    
    # Load the same dataset as 2- script
    df = pd.read_csv('/Users/poum/Downloads/hour_spells_filled_all_hours.csv')
    df['seg_start'] = pd.to_datetime(df['seg_start'])
    df['seg_end'] = pd.to_datetime(df['seg_end'])
    df['date'] = pd.to_datetime(df['date'])
    
    print("Analyzing spell count distributions...")
    
    # Get spell counts per hour for each user
    spell_counts = get_spell_counts_per_hour(df)
    
    # Create distribution plots
    create_spell_count_plots(spell_counts)
    
    # Export statistics
    export_spell_count_statistics(spell_counts)
    
    print("Spell count distribution analysis complete!")

def get_spell_counts_per_hour(df):
    """Get the number of consumption and non-consumption spells per hour for each user-date combination"""
    
    print("Calculating spell counts per hour per user per date...")
    
    # Create a list to store spell counts
    spell_count_data = []
    
    # For each user
    for user in df['AppCode'].unique():
        user_data = df[df['AppCode'] == user].copy()
        
        # For each date
        for date in user_data['date'].unique():
            user_date_data = user_data[user_data['date'] == date].copy()
            
            # For each hour (0-23)
            for hour in range(24):
                # Get segments that are in this hour
                hour_data = user_date_data[user_date_data['hour_label'] == f'{hour:02d}:00-{hour+1:02d}:00']
                
                # Count consumption and non-consumption segments
                consumption_count = len(hour_data[hour_data['Consumption'] == 1])
                non_consumption_count = len(hour_data[hour_data['Consumption'] == 0])
                
                spell_count_data.append({
                    'AppCode': user,
                    'date': date,
                    'hour': hour,
                    'consumption_count': consumption_count,
                    'non_consumption_count': non_consumption_count,
                    'total_count': consumption_count + non_consumption_count
                })
    
    return pd.DataFrame(spell_count_data)


def create_spell_count_plots(spell_counts):
    """Create distribution plots for spell counts"""
    
    print("Creating spell count distribution plots...")
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Winsorize data at 10
    consumption_winsorized = np.clip(spell_counts['consumption_count'], 0, 10)
    non_consumption_winsorized = np.clip(spell_counts['non_consumption_count'], 0, 10)
    
    # Plot 1: Consumption spell counts (winsorized at 10)
    consumption_counts = consumption_winsorized.value_counts().sort_index()
    axes[0, 0].bar(consumption_counts.index, consumption_counts.values, alpha=0.7, color='red')
    axes[0, 0].set_xlabel('Number of Consumption Spells')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].set_xlim(-0.5, 10.5)
    axes[0, 0].grid(True, alpha=0.3)
    
    # Add text showing original max
    original_max = spell_counts['consumption_count'].max()
    axes[0, 0].text(0.7, 0.9, f'Original max: {original_max}', 
                    transform=axes[0, 0].transAxes, fontsize=10, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    # Plot 2: Non-consumption spell counts (winsorized at 10)
    non_consumption_counts = non_consumption_winsorized.value_counts().sort_index()
    axes[0, 1].bar(non_consumption_counts.index, non_consumption_counts.values, alpha=0.7, color='blue')
    axes[0, 1].set_xlabel('Number of Non-Consumption Spells')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].set_xlim(-0.5, 10.5)
    axes[0, 1].grid(True, alpha=0.3)
    
    # Add text showing original max
    original_max_nc = spell_counts['non_consumption_count'].max()
    axes[0, 1].text(0.7, 0.9, f'Original max: {original_max_nc}', 
                    transform=axes[0, 1].transAxes, fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    # Plot 3: Total spell counts (winsorized at 10)
    total_winsorized = np.clip(spell_counts['total_count'], 0, 10)
    total_counts = total_winsorized.value_counts().sort_index()
    axes[1, 0].bar(total_counts.index, total_counts.values, alpha=0.7, color='green')
    axes[1, 0].set_xlabel('Total Number of Spells')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].set_xlim(-0.5, 10.5)
    axes[1, 0].grid(True, alpha=0.3)
    
    # Add text showing original max
    original_max_total = spell_counts['total_count'].max()
    axes[1, 0].text(0.7, 0.9, f'Original max: {original_max_total}', 
                    transform=axes[1, 0].transAxes, fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    # Plot 4: Comparison of consumption vs non-consumption (winsorized)
    # Create a combined plot showing both distributions
    x_pos = np.arange(11)  # 0 to 10
    consumption_vals = [consumption_counts.get(i, 0) for i in range(11)]
    non_consumption_vals = [non_consumption_counts.get(i, 0) for i in range(11)]
    
    width = 0.35
    axes[1, 1].bar(x_pos - width/2, consumption_vals, width, alpha=0.7, color='red', label='Consumption')
    axes[1, 1].bar(x_pos + width/2, non_consumption_vals, width, alpha=0.7, color='blue', label='Non-Consumption')
    axes[1, 1].set_xlabel('Number of Spells')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].set_xlim(-0.5, 10.5)
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/figures/3-spell_count_distributions.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create detailed individual plots
    create_detailed_distribution_plots(spell_counts)
    
    print("Plots saved to output/figures/ directory")

def create_detailed_distribution_plots(spell_counts):
    """Create detailed individual distribution plots"""
    
    # Consumption spells detailed plot
    plt.figure(figsize=(12, 8))
    
    consumption_winsorized = np.clip(spell_counts['consumption_count'], 0, 10)
    consumption_counts = consumption_winsorized.value_counts().sort_index()
    
    plt.bar(consumption_counts.index, consumption_counts.values, alpha=0.7, color='red')
    plt.xlabel('Number of Consumption Spells')
    plt.ylabel('Frequency')
    plt.xlim(-0.5, 10.5)
    plt.grid(True, alpha=0.3)
    
    # Add statistics text
    original_max = spell_counts['consumption_count'].max()
    mean_val = spell_counts['consumption_count'].mean()
    median_val = spell_counts['consumption_count'].median()
    
    stats_text = f'Original max: {original_max}\nMean: {mean_val:.2f}\nMedian: {median_val:.2f}'
    plt.text(0.7, 0.9, stats_text, transform=plt.gca().transAxes, fontsize=12,
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('output/figures/3-consumption_spell_count_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Non-consumption spells detailed plot
    plt.figure(figsize=(12, 8))
    
    non_consumption_winsorized = np.clip(spell_counts['non_consumption_count'], 0, 10)
    non_consumption_counts = non_consumption_winsorized.value_counts().sort_index()
    
    plt.bar(non_consumption_counts.index, non_consumption_counts.values, alpha=0.7, color='blue')
    plt.xlabel('Number of Non-Consumption Spells')
    plt.ylabel('Frequency')
    plt.xlim(-0.5, 10.5)
    plt.grid(True, alpha=0.3)
    
    # Add statistics text
    original_max_nc = spell_counts['non_consumption_count'].max()
    mean_val_nc = spell_counts['non_consumption_count'].mean()
    median_val_nc = spell_counts['non_consumption_count'].median()
    
    stats_text_nc = f'Original max: {original_max_nc}\nMean: {mean_val_nc:.2f}\nMedian: {median_val_nc:.2f}'
    plt.text(0.7, 0.9, stats_text_nc, transform=plt.gca().transAxes, fontsize=12,
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('output/figures/3-non_consumption_spell_count_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

def export_spell_count_statistics(spell_counts):
    """Export spell count statistics to CSV files"""
    
    print("Exporting spell count statistics to CSV...")
    
    # Create summary statistics
    summary_stats = {
        'consumption_count': {
            'mean': spell_counts['consumption_count'].mean(),
            'std': spell_counts['consumption_count'].std(),
            'median': spell_counts['consumption_count'].median(),
            'min': spell_counts['consumption_count'].min(),
            'max': spell_counts['consumption_count'].max(),
            'q25': spell_counts['consumption_count'].quantile(0.25),
            'q75': spell_counts['consumption_count'].quantile(0.75)
        },
        'non_consumption_count': {
            'mean': spell_counts['non_consumption_count'].mean(),
            'std': spell_counts['non_consumption_count'].std(),
            'median': spell_counts['non_consumption_count'].median(),
            'min': spell_counts['non_consumption_count'].min(),
            'max': spell_counts['non_consumption_count'].max(),
            'q25': spell_counts['non_consumption_count'].quantile(0.25),
            'q75': spell_counts['non_consumption_count'].quantile(0.75)
        },
        'total_count': {
            'mean': spell_counts['total_count'].mean(),
            'std': spell_counts['total_count'].std(),
            'median': spell_counts['total_count'].median(),
            'min': spell_counts['total_count'].min(),
            'max': spell_counts['total_count'].max(),
            'q25': spell_counts['total_count'].quantile(0.25),
            'q75': spell_counts['total_count'].quantile(0.75)
        }
    }
    
    # Convert to DataFrame
    summary_df = pd.DataFrame(summary_stats).round(4)
    summary_df.to_csv('output/tables/3-spell_count_summary_statistics.csv')
    
    # Create distribution tables (winsorized at 10)
    consumption_winsorized = np.clip(spell_counts['consumption_count'], 0, 10)
    non_consumption_winsorized = np.clip(spell_counts['non_consumption_count'], 0, 10)
    total_winsorized = np.clip(spell_counts['total_count'], 0, 10)
    
    # Consumption distribution
    consumption_dist = consumption_winsorized.value_counts().sort_index()
    consumption_dist_df = pd.DataFrame({
        'spell_count': consumption_dist.index,
        'frequency': consumption_dist.values,
        'percentage': (consumption_dist.values / len(spell_counts) * 100).round(2)
    })
    consumption_dist_df.to_csv('output/tables/3-consumption_spell_count_distribution.csv', index=False)
    
    # Non-consumption distribution
    non_consumption_dist = non_consumption_winsorized.value_counts().sort_index()
    non_consumption_dist_df = pd.DataFrame({
        'spell_count': non_consumption_dist.index,
        'frequency': non_consumption_dist.values,
        'percentage': (non_consumption_dist.values / len(spell_counts) * 100).round(2)
    })
    non_consumption_dist_df.to_csv('output/tables/3-non_consumption_spell_count_distribution.csv', index=False)
    
    # Total distribution
    total_dist = total_winsorized.value_counts().sort_index()
    total_dist_df = pd.DataFrame({
        'spell_count': total_dist.index,
        'frequency': total_dist.values,
        'percentage': (total_dist.values / len(spell_counts) * 100).round(2)
    })
    total_dist_df.to_csv('output/tables/3-total_spell_count_distribution.csv', index=False)
    
    # Save raw data
    spell_counts.to_csv('output/tables/3-raw_spell_count_data.csv', index=False)
    
    print("CSV files saved to output/tables/ directory")
    print(f"  - 3-spell_count_summary_statistics.csv: Summary statistics")
    print(f"  - 3-consumption_spell_count_distribution.csv: Consumption spell count distribution")
    print(f"  - 3-non_consumption_spell_count_distribution.csv: Non-consumption spell count distribution")
    print(f"  - 3-total_spell_count_distribution.csv: Total spell count distribution")
    print(f"  - 3-raw_spell_count_data.csv: Raw spell count data per user per hour")

if __name__ == "__main__":
    main()
