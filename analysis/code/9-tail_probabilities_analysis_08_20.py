import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def clear_existing_files():
    """Clear all existing 9- files"""
    import os
    import glob
    
    # Clear figures
    figure_files = glob.glob('output/figures/9-*.png')
    for file in figure_files:
        try:
            os.remove(file)
            print(f"Removed: {file}")
        except:
            pass
    
    # Clear tables
    table_files = glob.glob('output/tables/9-*.csv')
    for file in table_files:
        try:
            os.remove(file)
            print(f"Removed: {file}")
        except:
            pass

def main():
    """Calculate tail probabilities P(Spell > x) for consumption and non-consumption spells in 8am-8pm period"""
    print("Clearing all existing 9- files...")
    clear_existing_files()
    
    print("Loading 8am-8pm data and calculating tail probabilities...")
    
    # Load the 8am-8pm data
    df = pd.read_csv('/Users/poum/Downloads/hour_spells_filled_08_20.csv')
    df['seg_start'] = pd.to_datetime(df['seg_start'])
    df['seg_end'] = pd.to_datetime(df['seg_end'])
    df['date'] = pd.to_datetime(df['date'])
    
    # Calculate tail probabilities
    tail_probs = calculate_tail_probabilities_08_20(df)
    
    # Create visualizations
    create_tail_probability_plots_08_20(tail_probs)
    
    # Export to CSV
    export_tail_probabilities_08_20(tail_probs)
    
    print("8am-8pm tail probability analysis complete!")

def calculate_tail_probabilities_08_20(df):
    """Calculate P(Spell > x) for both consumption and non-consumption spells in 8am-8pm period"""
    
    print("Calculating spell lengths for 8am-8pm period...")
    
    # Get all spell lengths for consumption and non-consumption
    consumption_spells = df[df['Consumption'] == 1]['seg_minutes'].values
    non_consumption_spells = df[df['Consumption'] == 0]['seg_minutes'].values
    
    print(f"Found {len(consumption_spells):,} consumption spells in 8am-8pm period")
    print(f"Found {len(non_consumption_spells):,} non-consumption spells in 8am-8pm period")
    
    # Calculate tail probabilities for x = 1 to 720
    x_values = range(1, 721)  # 1 to 720 minutes
    
    tail_probs = []
    
    for x in x_values:
        # P(Spell > x) = (number of spells > x) / (total number of spells)
        consumption_tail = np.sum(consumption_spells > x) / len(consumption_spells)
        non_consumption_tail = np.sum(non_consumption_spells > x) / len(non_consumption_spells)
        
        tail_probs.append({
            'x_minutes': x,
            'consumption_tail_prob': consumption_tail,
            'non_consumption_tail_prob': non_consumption_tail
        })
        
        # Progress indicator
        if x % 100 == 0:
            print(f"Processed x = {x} minutes...")
    
    tail_probs_df = pd.DataFrame(tail_probs)
    
    # Print summary statistics
    print("\n" + "="*60)
    print("8AM-8PM TAIL PROBABILITY SUMMARY")
    print("="*60)
    
    print("\nKey Tail Probabilities:")
    print(f"{'x (minutes)':<12} {'Non-consumption':<15} {'Consumption':<12}")
    print("-" * 40)
    
    key_x_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    for x in key_x_values:
        if x <= 720:
            row = tail_probs_df[tail_probs_df['x_minutes'] == x].iloc[0]
            print(f"{x:<12} {row['non_consumption_tail_prob']:<15.3f} {row['consumption_tail_prob']:<12.3f}")
    
    print(f"\nSpell Length Statistics (8am-8pm):")
    print(f"Consumption spells:")
    print(f"  - Mean: {consumption_spells.mean():.3f} minutes")
    print(f"  - Median: {np.median(consumption_spells):.3f} minutes")
    print(f"  - Max: {consumption_spells.max():.3f} minutes")
    print(f"  - Variance: {consumption_spells.var():.3f}")
    
    print(f"\nNon-consumption spells:")
    print(f"  - Mean: {non_consumption_spells.mean():.3f} minutes")
    print(f"  - Median: {np.median(non_consumption_spells):.3f} minutes")
    print(f"  - Max: {non_consumption_spells.max():.3f} minutes")
    print(f"  - Variance: {non_consumption_spells.var():.3f}")
    
    return tail_probs_df

def create_tail_probability_plots_08_20(tail_probs_df):
    """Create individual plots for consumption and non-consumption spells in 8am-8pm period (NO LOG SCALE)"""
    
    print("Creating individual tail probability plots for 8am-8pm period...")
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create individual plot for non-consumption spells
    plt.figure(figsize=(12, 8))
    
    # Main plot - full range (0 to 720 minutes)
    plt.subplot(2, 1, 1)
    plt.plot(tail_probs_df['x_minutes'], tail_probs_df['non_consumption_tail_prob'], 
             linewidth=2, color='blue', alpha=0.8)
    plt.xlabel('x (minutes)')
    plt.ylabel('P(Spell > x)')
    plt.xlim(0, 720)
    plt.grid(True, alpha=0.3)
    
    # Second plot - first 60 minutes
    plt.subplot(2, 1, 2)
    non_consumption_data = tail_probs_df[tail_probs_df['x_minutes'] <= 60]
    plt.plot(non_consumption_data['x_minutes'], non_consumption_data['non_consumption_tail_prob'], 
             linewidth=2, color='blue', alpha=0.8)
    plt.xlabel('x (minutes)')
    plt.ylabel('P(Spell > x)')
    plt.xlim(0, 60)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/figures/9-non_consumption_tail_probabilities_08_20.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create individual plot for consumption spells
    plt.figure(figsize=(12, 8))
    
    # Main plot - full range (0 to 720 minutes)
    plt.subplot(2, 1, 1)
    plt.plot(tail_probs_df['x_minutes'], tail_probs_df['consumption_tail_prob'], 
             linewidth=2, color='red', alpha=0.8)
    plt.xlabel('x (minutes)')
    plt.ylabel('P(Spell > x)')
    plt.xlim(0, 720)
    plt.grid(True, alpha=0.3)
    
    # Second plot - first 60 minutes
    consumption_data = tail_probs_df[tail_probs_df['x_minutes'] <= 60]
    plt.subplot(2, 1, 2)
    plt.plot(consumption_data['x_minutes'], consumption_data['consumption_tail_prob'], 
             linewidth=2, color='red', alpha=0.8)
    plt.xlabel('x (minutes)')
    plt.ylabel('P(Spell > x)')
    plt.xlim(0, 60)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/figures/9-consumption_tail_probabilities_08_20.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Individual plots saved to output/figures/ directory")

def export_tail_probabilities_08_20(tail_probs_df):
    """Export tail probabilities to CSV file"""
    
    print("Exporting tail probabilities to CSV...")
    
    # Save the full dataset
    tail_probs_df.to_csv('output/tables/9-tail_probabilities_full_08_20.csv', index=False)
    
    # Create a summary table for key values (1-10 minutes)
    key_values = tail_probs_df[tail_probs_df['x_minutes'] <= 10]
    key_values.to_csv('output/tables/9-tail_probabilities_key_values_08_20.csv', index=False)
    
    # Create a summary table for every 10 minutes up to 720
    summary_values = tail_probs_df[tail_probs_df['x_minutes'] % 10 == 0]
    summary_values.to_csv('output/tables/9-tail_probabilities_summary_08_20.csv', index=False)
    
    print("CSV files saved to output/tables/ directory")
    print(f"  - 9-tail_probabilities_full_08_20.csv: All values from x=1 to x=720")
    print(f"  - 9-tail_probabilities_key_values_08_20.csv: Values for x=1 to x=10")
    print(f"  - 9-tail_probabilities_summary_08_20.csv: Values for x=10, 20, 30, ..., 720")

if __name__ == "__main__":
    main()





