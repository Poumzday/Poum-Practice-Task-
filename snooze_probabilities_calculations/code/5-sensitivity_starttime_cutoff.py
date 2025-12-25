import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path
from datetime import time

def clear_existing_files():
    """Clear all existing 5- prefixed files in output directories"""
    print("Clearing existing 5- files...")
    
    script_dir = Path(__file__).parent
    output_dir = script_dir.parent / 'output'
    
    for file in glob.glob(str(output_dir / 'figures' / '5-*')):
        os.remove(file)
    for file in glob.glob(str(output_dir / 'tables' / '5-*')):
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

def process_to_day_level_with_cutoff(starttime_cutoff_hour, starttime_cutoff_minute=0):
    """
    Process data from raw to day level, with additional StartTime cutoff filter.
    
    Parameters:
    - starttime_cutoff_hour: Hour cutoff (e.g., 23 for 23:00)
    - starttime_cutoff_minute: Minute cutoff (default 0)
    
    Returns day-level dataframe
    """
    # Step 1: Load and process raw data
    print(f"\n  Loading and processing raw data...")
    df = pd.read_csv('/Users/poum/Downloads/spell_data_for_snooze_facebook.csv')
    
    # Convert date and time columns
    df['Date'] = pd.to_datetime(df['Date'])
    df['StartTime'] = pd.to_datetime(df['StartTime'])
    df['EndTime'] = pd.to_datetime(df['EndTime'])
    
    # Rename columns
    if 'Snooze' in df.columns:
        df = df.rename(columns={'Snooze': 'HitLimit'})
    
    if 'SnoozeTime' in df.columns:
        df = df.rename(columns={'SnoozeTime': 'HLTime'})
        df['HLTime'] = pd.to_datetime(df['HLTime'], errors='coerce')
    
    # Delete incorrect_snooze column
    if 'incorrect_snooze' in df.columns:
        df = df.drop(columns=['incorrect_snooze'])
    
    # Round all numeric columns to 3 decimal places
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        df[col] = df[col].round(3)
    
    initial_rows = len(df)
    
    # Step 2: Order by AppCode, Date, StartTime
    df = df.sort_values(['AppCode', 'Date', 'StartTime']).reset_index(drop=True)
    
    # Step 3: Filter data (threshold = 1.0)
    rows_before = len(df)
    df = df[(df['UseMinutes'] > 1.0) | (df['HitLimit'] == 1)]
    rows_after = len(df)
    
    # Step 3b: Delete all rows BEFORE the first HitLimit = 1 row for each AppCode-Date
    rows_to_keep = []
    
    for (appcode, date), group in df.groupby(['AppCode', 'Date']):
        # Find first row with HitLimit = 1
        hitlimit_rows = group[group['HitLimit'] == 1]
        
        if len(hitlimit_rows) > 0:
            # Get index of first HitLimit = 1 row
            first_hitlimit_idx = hitlimit_rows.index[0]
            # Keep all rows at or after this index
            rows_to_keep.extend(group[group.index >= first_hitlimit_idx].index.tolist())
        else:
            # No HitLimit = 1 in this group, keep all rows
            rows_to_keep.extend(group.index.tolist())
    
    df = df.loc[rows_to_keep].reset_index(drop=True)
    
    # NEW STEP: Filter out rows where StartTime is after the cutoff
    cutoff_time = time(starttime_cutoff_hour, starttime_cutoff_minute)
    df['StartTime_time'] = df['StartTime'].dt.time
    rows_before_cutoff = len(df)
    df = df[df['StartTime_time'] <= cutoff_time].copy()
    rows_after_cutoff = len(df)
    df = df.drop('StartTime_time', axis=1)
    
    print(f"    Rows removed by StartTime cutoff ({starttime_cutoff_hour:02d}:{starttime_cutoff_minute:02d}): {rows_before_cutoff - rows_after_cutoff:,}")
    print(f"    Rows remaining after cutoff: {rows_after_cutoff:,}")
    
    # Step 4: Add Snooze column
    df['Snooze'] = 0
    
    for (appcode, date), group in df.groupby(['AppCode', 'Date']):
        if len(group) > 1:
            # Multiple rows, set Snooze = 1 for all
            df.loc[group.index, 'Snooze'] = 1
    
    # Step 5: Collapse to day level
    day_level_data = []
    
    for (appcode, date), group in df.groupby(['AppCode', 'Date']):
        # Get last row
        last_row = group.iloc[-1]
        
        # Get values
        cummins = last_row['CumMins']
        limitminutes = last_row['LimitMinutes']
        snoozegroup = last_row['SnoozeGroup']
        max_snooze = group['Snooze'].max()
        
        # Get HLTime from first row where HitLimit = 1
        hitlimit_rows = group[group['HitLimit'] == 1]
        if len(hitlimit_rows) > 0:
            hl_time = hitlimit_rows.iloc[0]['HLTime']
        else:
            hl_time = pd.NaT
        
        day_level_data.append({
            'AppCode': appcode,
            'SnoozeGroup': snoozegroup,
            'Date': date,
            'CumMins': cummins,
            'LimitMinutes': limitminutes,
            'Snooze_Acc': max_snooze,
            'HLTime': hl_time
        })
    
    day_df = pd.DataFrame(day_level_data)
    
    # Order by SnoozeGroup (0, 2, 5, 20), then AppCode, then Date
    snooze_order = ['Snooze 0', 'Snooze 2', 'Snooze 5', 'Snooze 20']
    day_df['sort_order'] = day_df['SnoozeGroup'].map({val: i for i, val in enumerate(snooze_order)})
    day_df = day_df.sort_values(['sort_order', 'AppCode', 'Date']).drop('sort_order', axis=1).reset_index(drop=True)
    
    # Round numeric columns to 3 decimal places
    day_df['CumMins'] = day_df['CumMins'].round(3)
    day_df['LimitMinutes'] = day_df['LimitMinutes'].round(3)
    day_df['Snooze_Acc'] = day_df['Snooze_Acc'].round(3)
    
    return day_df

def calculate_snooze_proportions_8am8pm(df_filtered, cutoff_label, n_bootstrap=10000):
    """Calculate snooze proportions for 8am-8pm HLTime window"""
    # Convert HLTime if needed
    if not pd.api.types.is_datetime64_any_dtype(df_filtered['HLTime']):
        df_filtered['HLTime'] = pd.to_datetime(df_filtered['HLTime'], errors='coerce')
    
    # Filter to 8am-8pm HLTime window
    df_filtered['HLTime_hour'] = df_filtered['HLTime'].dt.hour
    df_8am8pm = df_filtered[(df_filtered['HLTime_hour'] >= 8) & (df_filtered['HLTime_hour'] < 20)].copy()
    df_8am8pm = df_8am8pm.drop('HLTime_hour', axis=1)
    
    # Calculate overall proportion
    total_combinations = len(df_8am8pm)
    snooze_count = (df_8am8pm['Snooze_Acc'] == 1).sum()
    proportion = snooze_count / total_combinations if total_combinations > 0 else 0
    
    # Standard error for overall proportion
    if total_combinations > 0:
        se_overall = np.sqrt(proportion * (1 - proportion) / total_combinations)
        # Bootstrap CI for overall
        overall_data = df_8am8pm['Snooze_Acc'].values
        ci_lower_overall, ci_upper_overall = bootstrap_proportion(overall_data, n_bootstrap)
    else:
        se_overall = 0
        ci_lower_overall, ci_upper_overall = (np.nan, np.nan)
    
    print(f"\nOverall Results (8am-8pm HLTime, StartTime <= {cutoff_label}):")
    print(f"  Total combinations: {total_combinations:,}")
    print(f"  Combinations with Snooze_Acc = 1: {snooze_count:,}")
    print(f"  Proportion: {proportion:.4f} ({proportion*100:.2f}%)")
    print(f"  Standard Error: {se_overall:.4f}")
    print(f"  95% CI (empirical): [{ci_lower_overall:.4f}, {ci_upper_overall:.4f}]")
    
    # By SnoozeGroup
    print(f"\nBy SnoozeGroup (8am-8pm HLTime, StartTime <= {cutoff_label}):")
    snooze_order = ['Snooze 0', 'Snooze 2', 'Snooze 5', 'Snooze 20']
    
    snoozegroup_stats = []
    for group in snooze_order:
        group_data = df_8am8pm[df_8am8pm['SnoozeGroup'] == group]
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
        'snoozegroup_stats': snoozegroup_stats,
        'day_level_data': df_8am8pm
    }

def main():
    """Calculate snooze proportions with different StartTime cutoffs"""
    print("=" * 60)
    print("Script 5: Sensitivity Analysis - StartTime Cutoff")
    print("=" * 60)
    
    clear_existing_files()
    
    # Define StartTime cutoffs: (label, hour, minute)
    cutoffs = [
        ('23:00', 23, 0),   # 8-8 and 11 (11pm = 23:00)
        ('22:00', 22, 0),   # 8-8 and 10 (10pm = 22:00)
        ('21:00', 21, 0),   # 8-8 and 9 (9pm = 21:00)
    ]
    
    output_dir = Path(__file__).parent.parent / 'output' / 'tables'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_summaries = []
    all_snoozegroup_stats = []
    
    for cutoff_label, cutoff_hour, cutoff_minute in cutoffs:
        print("\n" + "=" * 60)
        print(f"StartTime Cutoff: <= {cutoff_label}")
        print("=" * 60)
        
        # Process data with this cutoff
        day_df = process_to_day_level_with_cutoff(cutoff_hour, cutoff_minute)
        
        print(f"\n  Total AppCode-Date combinations: {len(day_df):,}")
        
        # Calculate snooze proportions for 8am-8pm window
        results = calculate_snooze_proportions_8am8pm(day_df, cutoff_label)
        
        # Save day-level data
        safe_label = cutoff_label.replace(':', '_')
        results['day_level_data'].to_csv(output_dir / f'5-day_level_data_cutoff_{safe_label}.csv', index=False)
        
        # Save summary
        summary_data = {
            'starttime_cutoff': [cutoff_label],
            'total_combinations': [results['total_combinations']],
            'snooze_count': [results['snooze_count']],
            'proportion': [results['proportion']],
            'standard_error': [results['standard_error']],
            'ci_lower_2_5': [results['ci_lower_2_5']],
            'ci_upper_97_5': [results['ci_upper_97_5']]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(output_dir / f'5-snooze_proportion_summary_cutoff_{safe_label}.csv', index=False)
        
        # Save by SnoozeGroup
        snoozegroup_df = pd.DataFrame(results['snoozegroup_stats'])
        snoozegroup_df['starttime_cutoff'] = cutoff_label
        snoozegroup_df.to_csv(output_dir / f'5-snooze_proportion_by_snoozegroup_cutoff_{safe_label}.csv', index=False)
        
        # Collect for combined output
        all_summaries.append(summary_data)
        for stat in results['snoozegroup_stats']:
            stat['starttime_cutoff'] = cutoff_label
            all_snoozegroup_stats.append(stat)
        
        print(f"\nSaved results to:")
        print(f"  {output_dir / f'5-day_level_data_cutoff_{safe_label}.csv'}")
        print(f"  {output_dir / f'5-snooze_proportion_summary_cutoff_{safe_label}.csv'}")
        print(f"  {output_dir / f'5-snooze_proportion_by_snoozegroup_cutoff_{safe_label}.csv'}")
    
    # Save combined summary
    combined_summary = pd.concat([pd.DataFrame(s) for s in all_summaries], ignore_index=True)
    combined_summary.to_csv(output_dir / '5-snooze_proportion_summary_all_cutoffs.csv', index=False)
    
    # Save combined by SnoozeGroup
    combined_snoozegroup = pd.DataFrame(all_snoozegroup_stats)
    combined_snoozegroup.to_csv(output_dir / '5-snooze_proportion_by_snoozegroup_all_cutoffs.csv', index=False)
    
    print("\n" + "=" * 60)
    print("All cutoffs analyzed!")
    print("=" * 60)
    print(f"\nCombined results saved to:")
    print(f"  {output_dir / '5-snooze_proportion_summary_all_cutoffs.csv'}")
    print(f"  {output_dir / '5-snooze_proportion_by_snoozegroup_all_cutoffs.csv'}")

if __name__ == "__main__":
    main()

