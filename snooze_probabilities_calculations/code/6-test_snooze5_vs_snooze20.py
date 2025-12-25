import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats

def two_proportion_z_test(n1, x1, n2, x2):
    """
    Perform a two-proportion z-test.
    
    Parameters:
    - n1, n2: sample sizes
    - x1, x2: number of successes
    
    Returns:
    - z_statistic, p_value (two-tailed)
    """
    p1 = x1 / n1 if n1 > 0 else 0
    p2 = x2 / n2 if n2 > 0 else 0
    
    # Pooled proportion
    p_pooled = (x1 + x2) / (n1 + n2) if (n1 + n2) > 0 else 0
    
    # Standard error
    se = np.sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2))
    
    if se == 0:
        return np.nan, np.nan
    
    # Z-statistic
    z_stat = (p1 - p2) / se
    
    # Two-tailed p-value
    p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
    
    return z_stat, p_value

def main():
    """Test whether Snooze 5 and Snooze 20 proportions are significantly different"""
    print("=" * 80)
    print("Statistical Test: Snooze 5 vs Snooze 20")
    print("=" * 80)
    
    output_dir = Path(__file__).parent.parent / 'output' / 'tables'
    results = []
    
    # 1. Overall (Midnight-Midnight)
    print("\n" + "=" * 80)
    print("1. Overall Results (Midnight-Midnight)")
    print("=" * 80)
    
    df_overall = pd.read_csv(output_dir / '3-snooze_proportion_by_snoozegroup.csv')
    snooze5 = df_overall[df_overall['SnoozeGroup'] == 'Snooze 5'].iloc[0]
    snooze20 = df_overall[df_overall['SnoozeGroup'] == 'Snooze 20'].iloc[0]
    
    n5, x5 = snooze5['total_combinations'], snooze5['snooze_count']
    n20, x20 = snooze20['total_combinations'], snooze20['snooze_count']
    p5, p20 = snooze5['proportion'], snooze20['proportion']
    
    z_stat, p_value = two_proportion_z_test(n5, x5, n20, x20)
    diff = p5 - p20
    
    print(f"Snooze 5: {p5:.4f} ({x5:,}/{n5:,})")
    print(f"Snooze 20: {p20:.4f} ({x20:,}/{n20:,})")
    print(f"Difference: {diff:.4f} ({diff*100:.2f} percentage points)")
    print(f"Z-statistic: {z_stat:.4f}")
    print(f"P-value: {p_value:.6f}")
    print(f"Significant at α=0.05: {'Yes' if p_value < 0.05 else 'No'}")
    print(f"Significant at α=0.01: {'Yes' if p_value < 0.01 else 'No'}")
    
    results.append({
        'analysis': 'Midnight-Midnight',
        'snooze5_prop': p5,
        'snooze5_count': f"{x5:,}/{n5:,}",
        'snooze20_prop': p20,
        'snooze20_count': f"{x20:,}/{n20:,}",
        'difference': diff,
        'z_statistic': z_stat,
        'p_value': p_value,
        'significant_05': 'Yes' if p_value < 0.05 else 'No',
        'significant_01': 'Yes' if p_value < 0.01 else 'No'
    })
    
    # 2. Time Window Analyses
    print("\n" + "=" * 80)
    print("2. Time Window Analyses")
    print("=" * 80)
    
    time_windows = [
        ('8:00-20:00', '8_00-20_00'),
        ('7:00-21:00', '7_00-21_00'),
        ('7:30-20:30', '7_30-20_30'),
        ('8:30-19:30', '8_30-19_30'),
        ('9:00-19:00', '9_00-19_00'),
    ]
    
    for window_name, file_suffix in time_windows:
        print(f"\n--- {window_name} ---")
        df_window = pd.read_csv(output_dir / f'4-snooze_proportion_by_snoozegroup_{file_suffix}.csv')
        snooze5 = df_window[df_window['SnoozeGroup'] == 'Snooze 5'].iloc[0]
        snooze20 = df_window[df_window['SnoozeGroup'] == 'Snooze 20'].iloc[0]
        
        n5, x5 = snooze5['total_combinations'], snooze5['snooze_count']
        n20, x20 = snooze20['total_combinations'], snooze20['snooze_count']
        p5, p20 = snooze5['proportion'], snooze20['proportion']
        
        z_stat, p_value = two_proportion_z_test(n5, x5, n20, x20)
        diff = p5 - p20
        
        print(f"Snooze 5: {p5:.4f} ({x5:,}/{n5:,})")
        print(f"Snooze 20: {p20:.4f} ({x20:,}/{n20:,})")
        print(f"Difference: {diff:.4f} ({diff*100:.2f} percentage points)")
        print(f"Z-statistic: {z_stat:.4f}")
        print(f"P-value: {p_value:.6f}")
        print(f"Significant at α=0.05: {'Yes' if p_value < 0.05 else 'No'}")
        print(f"Significant at α=0.01: {'Yes' if p_value < 0.01 else 'No'}")
        
        results.append({
            'analysis': f'Time Window: {window_name}',
            'snooze5_prop': p5,
            'snooze5_count': f"{x5:,}/{n5:,}",
            'snooze20_prop': p20,
            'snooze20_count': f"{x20:,}/{n20:,}",
            'difference': diff,
            'z_statistic': z_stat,
            'p_value': p_value,
            'significant_05': 'Yes' if p_value < 0.05 else 'No',
            'significant_01': 'Yes' if p_value < 0.01 else 'No'
        })
    
    # 3. StartTime Cutoff Analyses
    print("\n" + "=" * 80)
    print("3. StartTime Cutoff Analyses (8am-8pm HLTime Window)")
    print("=" * 80)
    
    cutoffs = [
        ('≤23:00', '23_00'),
        ('≤22:00', '22_00'),
        ('≤21:00', '21_00'),
    ]
    
    for cutoff_name, file_suffix in cutoffs:
        print(f"\n--- StartTime {cutoff_name} ---")
        df_cutoff = pd.read_csv(output_dir / f'5-snooze_proportion_by_snoozegroup_cutoff_{file_suffix}.csv')
        snooze5 = df_cutoff[df_cutoff['SnoozeGroup'] == 'Snooze 5'].iloc[0]
        snooze20 = df_cutoff[df_cutoff['SnoozeGroup'] == 'Snooze 20'].iloc[0]
        
        n5, x5 = snooze5['total_combinations'], snooze5['snooze_count']
        n20, x20 = snooze20['total_combinations'], snooze20['snooze_count']
        p5, p20 = snooze5['proportion'], snooze20['proportion']
        
        z_stat, p_value = two_proportion_z_test(n5, x5, n20, x20)
        diff = p5 - p20
        
        print(f"Snooze 5: {p5:.4f} ({x5:,}/{n5:,})")
        print(f"Snooze 20: {p20:.4f} ({x20:,}/{n20:,})")
        print(f"Difference: {diff:.4f} ({diff*100:.2f} percentage points)")
        print(f"Z-statistic: {z_stat:.4f}")
        print(f"P-value: {p_value:.6f}")
        print(f"Significant at α=0.05: {'Yes' if p_value < 0.05 else 'No'}")
        print(f"Significant at α=0.01: {'Yes' if p_value < 0.01 else 'No'}")
        
        results.append({
            'analysis': f'StartTime Cutoff: {cutoff_name}',
            'snooze5_prop': p5,
            'snooze5_count': f"{x5:,}/{n5:,}",
            'snooze20_prop': p20,
            'snooze20_count': f"{x20:,}/{n20:,}",
            'difference': diff,
            'z_statistic': z_stat,
            'p_value': p_value,
            'significant_05': 'Yes' if p_value < 0.05 else 'No',
            'significant_01': 'Yes' if p_value < 0.01 else 'No'
        })
    
    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_dir / '6-snooze5_vs_snooze20_tests.csv', index=False)
    
    print("\n" + "=" * 80)
    print("Summary Table")
    print("=" * 80)
    print("\n" + results_df.to_string(index=False))
    
    print(f"\n\nResults saved to: {output_dir / '6-snooze5_vs_snooze20_tests.csv'}")
    
    return results_df

if __name__ == "__main__":
    results_df = main()

