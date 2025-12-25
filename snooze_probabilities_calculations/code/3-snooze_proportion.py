import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path

def clear_existing_files():
    """Clear all existing 3- prefixed files in output directories"""
    print("Clearing existing 3- files...")
    
    script_dir = Path(__file__).parent
    output_dir = script_dir.parent / 'output'
    
    for file in glob.glob(str(output_dir / 'figures' / '3-*')):
        os.remove(file)
    for file in glob.glob(str(output_dir / 'tables' / '3-*')):
        os.remove(file)

def bootstrap_proportion(data, n_bootstrap=10000):
    """
    Bootstrap the proportion to get empirical confidence interval.
    
    Parameters:
    - data: array-like of binary outcomes (0 or 1)
    - n_bootstrap: number of bootstrap samples
    
    Returns:
    - tuple: (2.5th percentile, 97.5th percentile)
    """
    if len(data) == 0:
        return (np.nan, np.nan)
    
    bootstrap_props = []
    for _ in range(n_bootstrap):
        # Resample with replacement
        bootstrap_sample = np.random.choice(data, size=len(data), replace=True)
        bootstrap_prop = np.mean(bootstrap_sample)
        bootstrap_props.append(bootstrap_prop)
    
    ci_lower = np.percentile(bootstrap_props, 2.5)
    ci_upper = np.percentile(bootstrap_props, 97.5)
    
    return (ci_lower, ci_upper)

def main():
    """Calculate proportion of snoozes from day-level data"""
    print("=" * 60)
    print("Script 3: Snooze Proportion (Midnight-Midnight)")
    print("=" * 60)
    
    clear_existing_files()
    
    # Load day-level data from script 2
    print("\nLoading day-level data...")
    input_file = Path(__file__).parent.parent / 'output' / 'tables' / '2-day_level_data.csv'
    df = pd.read_csv(input_file)
    
    # Convert date column
    df['Date'] = pd.to_datetime(df['Date'])
    
    print(f"  Total AppCode-Date combinations: {len(df):,}")
    
    # Calculate overall proportion
    total_combinations = len(df)
    snooze_count = (df['Snooze_Acc'] == 1).sum()
    proportion = snooze_count / total_combinations
    
    # Standard error and CI for overall
    se_overall = np.sqrt(proportion * (1 - proportion) / total_combinations)
    overall_data = df['Snooze_Acc'].values
    ci_lower_overall, ci_upper_overall = bootstrap_proportion(overall_data)
    
    print(f"\nOverall Results (Midnight-Midnight):")
    print(f"  Total combinations: {total_combinations:,}")
    print(f"  Combinations with Snooze_Acc = 1: {snooze_count:,}")
    print(f"  Proportion: {proportion:.4f} ({proportion*100:.2f}%)")
    print(f"  Standard Error: {se_overall:.4f}")
    print(f"  95% CI (empirical): [{ci_lower_overall:.4f}, {ci_upper_overall:.4f}]")
    
    # By SnoozeGroup
    print("\nBy SnoozeGroup (Midnight-Midnight):")
    snooze_order = ['Snooze 0', 'Snooze 2', 'Snooze 5', 'Snooze 20']
    
    snoozegroup_stats = []
    for group in snooze_order:
        group_data = df[df['SnoozeGroup'] == group]
        if len(group_data) > 0:
            group_total = len(group_data)
            group_snooze = (group_data['Snooze_Acc'] == 1).sum()
            group_prop = group_snooze / group_total
            
            # Standard error and CI
            se = np.sqrt(group_prop * (1 - group_prop) / group_total)
            group_binary = group_data['Snooze_Acc'].values
            ci_lower, ci_upper = bootstrap_proportion(group_binary)
            
            print(f"  {group}: {group_prop:.4f} ({group_prop*100:.2f}%) - {group_snooze:,} / {group_total:,}")
            print(f"    SE: {se:.4f}, 95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")
            
            snoozegroup_stats.append({
                'SnoozeGroup': group,
                'total_combinations': group_total,
                'snooze_count': group_snooze,
                'proportion': group_prop,
                'standard_error': se,
                'ci_lower_2_5': ci_lower,
                'ci_upper_97_5': ci_upper
            })
    
    # Save results
    output_dir = Path(__file__).parent.parent / 'output' / 'tables'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save summary
    summary_data = {
        'total_combinations': [total_combinations],
        'snooze_count': [snooze_count],
        'proportion': [proportion],
        'standard_error': [se_overall],
        'ci_lower_2_5': [ci_lower_overall],
        'ci_upper_97_5': [ci_upper_overall]
    }
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(output_dir / '3-snooze_proportion_summary.csv', index=False)
    
    # Save by SnoozeGroup
    snoozegroup_df = pd.DataFrame(snoozegroup_stats)
    snoozegroup_df.to_csv(output_dir / '3-snooze_proportion_by_snoozegroup.csv', index=False)
    
    print(f"\nSaved results to:")
    print(f"  {output_dir / '3-snooze_proportion_summary.csv'}")
    print(f"  {output_dir / '3-snooze_proportion_by_snoozegroup.csv'}")
    
    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)
    
    return df

if __name__ == "__main__":
    df = main()


