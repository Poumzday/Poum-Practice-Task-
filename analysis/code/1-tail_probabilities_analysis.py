import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def main():
    """Calculate tail probabilities P(Spell > x) for consumption and non-consumption spells"""
    print("Loading data and calculating tail probabilities...")
    
    # Load the data
    df = pd.read_csv('/Users/poum/Downloads/bonus_limit_control_consumption_and_non_cons.csv')
    df['StartTime'] = pd.to_datetime(df['StartTime'])
    df['EndTime'] = pd.to_datetime(df['EndTime'])
    df['date'] = pd.to_datetime(df['date'])
    
    # Calculate tail probabilities
    tail_probs = calculate_tail_probabilities(df)
    
    # Create visualizations
    create_tail_probability_plots(tail_probs)
    
    # Export to CSV
    export_tail_probabilities(tail_probs)
    
    print("Tail probability analysis complete!")

def calculate_tail_probabilities(df):
    """Calculate P(Spell > x) for both consumption and non-consumption spells"""
    
    print("Calculating spell lengths...")
    
    # Get all spell lengths for consumption and non-consumption
    consumption_spells = df[df['Consumption'] == 1]['UseMinutes'].values
    non_consumption_spells = df[df['Consumption'] == 0]['UseMinutes'].values
    
    print(f"Found {len(consumption_spells):,} consumption spells")
    print(f"Found {len(non_consumption_spells):,} non-consumption spells")
    
    # Calculate tail probabilities for x = 1 to 1440
    x_values = range(1, 1441)  # 1 to 1440 minutes
    
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
    
    # Print some key statistics
    print("\n" + "="*60)
    print("TAIL PROBABILITY SUMMARY")
    print("="*60)
    
    # Show results for key x values (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    key_x_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    print("\nKey Tail Probabilities:")
    print("x (minutes)\tNon-consumption\tConsumption")
    print("-" * 45)
    
    for x in key_x_values:
        row = tail_probs_df[tail_probs_df['x_minutes'] == x].iloc[0]
        print(f"{x}\t\t{row['non_consumption_tail_prob']:.3f}\t\t{row['consumption_tail_prob']:.3f}")
    
    # Additional statistics
    print(f"\nSpell Length Statistics:")
    print(f"Consumption spells:")
    print(f"  - Mean: {np.mean(consumption_spells):.3f} minutes")
    print(f"  - Median: {np.median(consumption_spells):.3f} minutes")
    print(f"  - Max: {np.max(consumption_spells):.3f} minutes")
    print(f"  - Variance: {np.var(consumption_spells):.3f}")
    
    print(f"\nNon-consumption spells:")
    print(f"  - Mean: {np.mean(non_consumption_spells):.3f} minutes")
    print(f"  - Median: {np.median(non_consumption_spells):.3f} minutes")
    print(f"  - Max: {np.max(non_consumption_spells):.3f} minutes")
    print(f"  - Variance: {np.var(non_consumption_spells):.3f}")
    
    return tail_probs_df

def create_tail_probability_plots(tail_probs_df):
    """Create individual plots for consumption and non-consumption spells (NO LOG SCALE)"""
    
    print("Creating individual tail probability plots...")
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create individual plot for non-consumption spells
    plt.figure(figsize=(12, 8))
    
    # Main plot - full range
    plt.subplot(2, 1, 1)
    plt.plot(tail_probs_df['x_minutes'], tail_probs_df['non_consumption_tail_prob'], 
             linewidth=2, color='blue', alpha=0.8)
    plt.title('Non-Consumption Spells: P(Spell > x) vs x (Full Range)', fontsize=14, fontweight='bold')
    plt.xlabel('x (minutes)')
    plt.ylabel('P(Spell > x)')
    plt.xlim(0, 1440)
    plt.grid(True, alpha=0.3)
    
    # Second plot - first 60 minutes
    plt.subplot(2, 1, 2)
    plt.plot(tail_probs_df['x_minutes'], tail_probs_df['non_consumption_tail_prob'], 
             linewidth=2, color='blue', alpha=0.8)
    plt.title('Non-Consumption Spells: P(Spell > x) vs x (First 60 minutes)', fontsize=12)
    plt.xlabel('x (minutes)')
    plt.ylabel('P(Spell > x)')
    plt.xlim(0, 60)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/figures/1-non_consumption_tail_probabilities.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create individual plot for consumption spells
    plt.figure(figsize=(12, 8))
    
    # Main plot - full range (0 to 1440 minutes)
    plt.subplot(2, 1, 1)
    plt.plot(tail_probs_df['x_minutes'], tail_probs_df['consumption_tail_prob'], 
             linewidth=2, color='red', alpha=0.8)
    plt.title('Consumption Spells: P(Spell > x) vs x (Full Range)', fontsize=14, fontweight='bold')
    plt.xlabel('x (minutes)')
    plt.ylabel('P(Spell > x)')
    plt.xlim(0, 1440)
    plt.grid(True, alpha=0.3)
    
    # Second plot - first 60 minutes
    consumption_data = tail_probs_df[tail_probs_df['x_minutes'] <= 60]
    plt.subplot(2, 1, 2)
    plt.plot(consumption_data['x_minutes'], consumption_data['consumption_tail_prob'], 
             linewidth=2, color='red', alpha=0.8)
    plt.title('Consumption Spells: P(Spell > x) vs x (First 60 minutes)', fontsize=12)
    plt.xlabel('x (minutes)')
    plt.ylabel('P(Spell > x)')
    plt.xlim(0, 60)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/figures/1-consumption_tail_probabilities.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Individual plots saved to output/figures/ directory")

def export_tail_probabilities(tail_probs_df):
    """Export tail probabilities to CSV file"""
    
    print("Exporting tail probabilities to CSV...")
    
    # Save the full dataset
    tail_probs_df.to_csv('output/tables/1-tail_probabilities_full.csv', index=False)
    
    # Create a summary table for key values (1-10 minutes)
    key_values = tail_probs_df[tail_probs_df['x_minutes'] <= 10].copy()
    key_values = key_values.round(3)
    key_values.to_csv('output/tables/1-tail_probabilities_key_values.csv', index=False)
    
    # Create a summary table for every 10 minutes up to 1440
    summary_values = tail_probs_df[tail_probs_df['x_minutes'] % 10 == 0].copy()
    summary_values = summary_values.round(3)
    summary_values.to_csv('output/tables/1-tail_probabilities_summary.csv', index=False)
    
    print("CSV files saved to output/tables/ directory")
    print(f"  - 1-tail_probabilities_full.csv: All values from x=1 to x=1440")
    print(f"  - 1-tail_probabilities_key_values.csv: Values for x=1 to x=10")
    print(f"  - 1-tail_probabilities_summary.csv: Values for x=10, 20, 30, ..., 1440")

if __name__ == "__main__":
    main()