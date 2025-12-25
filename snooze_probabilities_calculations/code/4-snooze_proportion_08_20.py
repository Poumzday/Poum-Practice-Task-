import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path
from datetime import time

def clear_existing_files():
    """Clear all existing 4- prefixed files in output directories"""
    print("Clearing existing 4- files...")
    
    script_dir = Path(__file__).parent
    output_dir = script_dir.parent / 'output'
    
    for file in glob.glob(str(output_dir / 'figures' / '4-*')):
        os.remove(file)
    for file in glob.glob(str(output_dir / 'tables' / '4-*')):
        os.remove(file)

def filter_by_time_window(df, start_hour, start_minute, end_hour, end_minute):
    """
    Filter dataframe to rows where HLTime falls within the specified time window.
    
    Parameters:
    - start_hour, start_minute: Start time (e.g., 7, 0 for 7:00)
    - end_hour, end_minute: End time (e.g., 21, 0 for 21:00)
    
    Returns filtered dataframe
    """
    # Create time objects for comparison
    start_time = time(start_hour, start_minute)
    end_time = time(end_hour, end_minute)
    
    # Extract time component from HLTime
    df['HLTime_time'] = df['HLTime'].dt.time
    
    # Handle case where end time is before start time (e.g., 8:30am-7:30pm spans midnight)
    if end_time < start_time:
        # Time window spans midnight (e.g., 8:30am to 7:30pm next day)
        mask = (df['HLTime_time'] >= start_time) | (df['HLTime_time'] < end_time)
    else:
        # Normal time window (e.g., 7:00am to 21:00pm)
        mask = (df['HLTime_time'] >= start_time) & (df['HLTime_time'] < end_time)
    
    df_filtered = df[mask].copy()
    df_filtered = df_filtered.drop('HLTime_time', axis=1)
    
    return df_filtered

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

def calculate_snooze_proportions(df_filtered, time_window_name, n_bootstrap=10000):
    """Calculate snooze proportions with standard errors and confidence intervals"""
    # Calculate overall proportion
    total_combinations = len(df_filtered)
    snooze_count = (df_filtered['Snooze_Acc'] == 1).sum()
    proportion = snooze_count / total_combinations if total_combinations > 0 else 0
    
    # Standard error for overall proportion
    if total_combinations > 0:
        se_overall = np.sqrt(proportion * (1 - proportion) / total_combinations)
        # Bootstrap CI for overall
        overall_data = df_filtered['Snooze_Acc'].values
        ci_lower_overall, ci_upper_overall = bootstrap_proportion(overall_data, n_bootstrap)
    else:
        se_overall = 0
        ci_lower_overall, ci_upper_overall = (np.nan, np.nan)
    
    print(f"\nOverall Results ({time_window_name}):")
    print(f"  Total combinations: {total_combinations:,}")
    print(f"  Combinations with Snooze_Acc = 1: {snooze_count:,}")
    print(f"  Proportion: {proportion:.4f} ({proportion*100:.2f}%)")
    print(f"  Standard Error: {se_overall:.4f}")
    print(f"  95% CI (empirical): [{ci_lower_overall:.4f}, {ci_upper_overall:.4f}]")
    
    # By SnoozeGroup
    print(f"\nBy SnoozeGroup ({time_window_name}):")
    snooze_order = ['Snooze 0', 'Snooze 2', 'Snooze 5', 'Snooze 20']
    
    snoozegroup_stats = []
    for group in snooze_order:
        group_data = df_filtered[df_filtered['SnoozeGroup'] == group]
        if len(group_data) > 0:
            group_total = len(group_data)
            group_snooze = (group_data['Snooze_Acc'] == 1).sum()
            group_prop = group_snooze / group_total if group_total > 0 else 0
            
            # Standard error
            if group_total > 0:
                se = np.sqrt(group_prop * (1 - group_prop) / group_total)
                # Bootstrap CI
                group_binary = group_data['Snooze_Acc'].values
                ci_lower, ci_upper = bootstrap_proportion(group_binary, n_bootstrap)
            else:
                se = 0
                ci_lower, ci_upper = (np.nan, np.nan)
            
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
    
    return {
        'total_combinations': total_combinations,
        'snooze_count': snooze_count,
        'proportion': proportion,
        'standard_error': se_overall,
        'ci_lower_2_5': ci_lower_overall,
        'ci_upper_97_5': ci_upper_overall,
        'snoozegroup_stats': snoozegroup_stats
    }

def main():
    """Calculate proportion of snoozes for multiple HLTime windows"""
    print("=" * 60)
    print("Script 4: Snooze Proportion (Multiple Time Windows)")
    print("=" * 60)
    
    clear_existing_files()
    
    # Load day-level data from script 2
    print("\nLoading day-level data...")
    input_file = Path(__file__).parent.parent / 'output' / 'tables' / '2-day_level_data.csv'
    df = pd.read_csv(input_file)
    
    # Convert date columns
    df['Date'] = pd.to_datetime(df['Date'])
    df['HLTime'] = pd.to_datetime(df['HLTime'], errors='coerce')
    
    print(f"  Total AppCode-Date combinations: {len(df):,}")
    
    # Define time windows: (name, start_hour, start_minute, end_hour, end_minute)
    time_windows = [
        ('7:00-21:00', 7, 0, 21, 0),      # 7am-9pm
        ('7:30-20:30', 7, 30, 20, 30),    # 7:30am-8:30pm
        ('8:30-19:30', 8, 30, 19, 30),    # 8:30am-7:30pm
        ('9:00-19:00', 9, 0, 19, 0),      # 9am-7pm
        ('8:00-20:00', 8, 0, 20, 0),      # 8am-8pm (original)
    ]
    
    output_dir = Path(__file__).parent.parent / 'output' / 'tables'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_summaries = []
    all_snoozegroup_stats = []
    
    for window_name, start_h, start_m, end_h, end_m in time_windows:
        print("\n" + "=" * 60)
        print(f"Time Window: {window_name}")
        print("=" * 60)
        
        # Filter data
        rows_before = len(df)
        df_filtered = filter_by_time_window(df, start_h, start_m, end_h, end_m)
        rows_after = len(df_filtered)
        rows_removed = rows_before - rows_after
        
        print(f"\nFiltering to HLTime between {window_name}...")
        print(f"  Rows before filtering: {rows_before:,}")
        print(f"  Rows removed: {rows_removed:,}")
        print(f"  Rows remaining: {rows_after:,}")
        
        # Calculate proportions
        results = calculate_snooze_proportions(df_filtered, window_name)
        
        # Save filtered day-level data
        safe_name = window_name.replace(':', '_')
        df_filtered.to_csv(output_dir / f'4-day_level_data_{safe_name}.csv', index=False)
        
        # Save summary
        summary_data = {
            'time_window': [window_name],
            'total_combinations': [results['total_combinations']],
            'snooze_count': [results['snooze_count']],
            'proportion': [results['proportion']],
            'standard_error': [results['standard_error']],
            'ci_lower_2_5': [results['ci_lower_2_5']],
            'ci_upper_97_5': [results['ci_upper_97_5']]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(output_dir / f'4-snooze_proportion_summary_{safe_name}.csv', index=False)
        
        # Save by SnoozeGroup
        snoozegroup_df = pd.DataFrame(results['snoozegroup_stats'])
        snoozegroup_df['time_window'] = window_name
        snoozegroup_df.to_csv(output_dir / f'4-snooze_proportion_by_snoozegroup_{safe_name}.csv', index=False)
        
        # Collect for combined output
        all_summaries.append(summary_data)
        for stat in results['snoozegroup_stats']:
            stat['time_window'] = window_name
            all_snoozegroup_stats.append(stat)
        
        print(f"\nSaved results to:")
        print(f"  {output_dir / f'4-day_level_data_{safe_name}.csv'}")
        print(f"  {output_dir / f'4-snooze_proportion_summary_{safe_name}.csv'}")
        print(f"  {output_dir / f'4-snooze_proportion_by_snoozegroup_{safe_name}.csv'}")
    
    # Save combined summary
    combined_summary = pd.concat([pd.DataFrame(s) for s in all_summaries], ignore_index=True)
    combined_summary.to_csv(output_dir / '4-snooze_proportion_summary_all_windows.csv', index=False)
    
    # Save combined by SnoozeGroup
    combined_snoozegroup = pd.DataFrame(all_snoozegroup_stats)
    combined_snoozegroup.to_csv(output_dir / '4-snooze_proportion_by_snoozegroup_all_windows.csv', index=False)
    
    print("\n" + "=" * 60)
    print("All time windows analyzed!")
    print("=" * 60)
    print(f"\nCombined results saved to:")
    print(f"  {output_dir / '4-snooze_proportion_summary_all_windows.csv'}")
    print(f"  {output_dir / '4-snooze_proportion_by_snoozegroup_all_windows.csv'}")
    
    return df

if __name__ == "__main__":
    df = main()
