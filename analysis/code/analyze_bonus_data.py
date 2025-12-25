import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def main():
    """Main function to load data and generate comprehensive descriptive statistics"""
    print("Loading bonus limit control consumption data...")
    df = load_data()
    
    print("Generating comprehensive descriptive statistics...")
    generate_descriptive_statistics(df)
    
    print("Creating visualizations...")
    create_visualizations(df)
    
    print("Analysis complete! Check the output files.")

def load_data():
    """Load the bonus limit control consumption data"""
    df = pd.read_csv('/Users/poum/Downloads/bonus_limit_control_consumption_and_non_cons.csv')
    
    # Convert datetime columns
    df['StartTime'] = pd.to_datetime(df['StartTime'])
    df['EndTime'] = pd.to_datetime(df['EndTime'])
    df['date'] = pd.to_datetime(df['date'])
    
    # Create additional time-based variables
    df['hour'] = df['StartTime'].dt.hour
    df['day_of_week'] = df['StartTime'].dt.day_name()
    df['month'] = df['StartTime'].dt.month
    df['session_duration'] = (df['EndTime'] - df['StartTime']).dt.total_seconds() / 60  # in minutes
    
    return df

def generate_descriptive_statistics(df):
    """Generate comprehensive descriptive statistics"""
    
    # Basic data overview
    print("\n" + "="*80)
    print("COMPREHENSIVE DESCRIPTIVE STATISTICS")
    print("="*80)
    
    print(f"\nDataset Overview:")
    print(f"- Total observations: {len(df):,}")
    print(f"- Number of unique users (AppCode): {df['AppCode'].nunique():,}")
    print(f"- Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
    print(f"- Number of days: {df['date'].nunique()}")
    
    # Numerical variables summary
    print(f"\n{'='*50}")
    print("NUMERICAL VARIABLES SUMMARY")
    print(f"{'='*50}")
    
    numerical_vars = ['UseMinutes', 'Bonus', 'Consumption', 'session_duration']
    desc_stats = df[numerical_vars].describe()
    print(desc_stats.round(4))
    
    # Additional statistics for numerical variables
    print(f"\nAdditional Statistics:")
    for var in numerical_vars:
        print(f"\n{var.upper()}:")
        print(f"  - Median: {df[var].median():.4f}")
        print(f"  - Mode: {df[var].mode().iloc[0] if not df[var].mode().empty else 'N/A'}")
        print(f"  - Skewness: {df[var].skew():.4f}")
        print(f"  - Kurtosis: {df[var].kurtosis():.4f}")
        print(f"  - Range: {df[var].min():.4f} to {df[var].max():.4f}")
        print(f"  - IQR: {df[var].quantile(0.75) - df[var].quantile(0.25):.4f}")
        print(f"  - Coefficient of Variation: {(df[var].std() / df[var].mean() * 100):.2f}%")
    
    # Categorical variables summary
    print(f"\n{'='*50}")
    print("CATEGORICAL VARIABLES SUMMARY")
    print(f"{'='*50}")
    
    categorical_vars = ['AppCode', 'ForegroundApp', 'SnoozeGroup', 'day_of_week']
    for var in categorical_vars:
        print(f"\n{var.upper()}:")
        value_counts = df[var].value_counts()
        print(f"  - Unique values: {df[var].nunique()}")
        print(f"  - Most frequent: {value_counts.index[0]} ({value_counts.iloc[0]:,} occurrences, {value_counts.iloc[0]/len(df)*100:.2f}%)")
        if df[var].nunique() <= 20:
            print("  - All values:")
            for val, count in value_counts.head(10).items():
                print(f"    {val}: {count:,} ({count/len(df)*100:.2f}%)")
            if len(value_counts) > 10:
                print(f"    ... and {len(value_counts) - 10} more values")
    
    # Consumption analysis
    print(f"\n{'='*50}")
    print("CONSUMPTION ANALYSIS")
    print(f"{'='*50}")
    
    consumption_summary = df.groupby('Consumption').agg({
        'UseMinutes': ['count', 'mean', 'std', 'median'],
        'session_duration': ['mean', 'std', 'median'],
        'AppCode': 'nunique'
    }).round(4)
    
    print("Summary by Consumption Status:")
    print(consumption_summary)
    
    # Bonus analysis
    print(f"\n{'='*50}")
    print("BONUS ANALYSIS")
    print(f"{'='*50}")
    
    bonus_summary = df.groupby('Bonus').agg({
        'UseMinutes': ['count', 'mean', 'std', 'median'],
        'Consumption': ['mean', 'sum'],
        'AppCode': 'nunique'
    }).round(4)
    
    print("Summary by Bonus Status:")
    print(bonus_summary)
    
    # Time-based analysis
    print(f"\n{'='*50}")
    print("TIME-BASED ANALYSIS")
    print(f"{'='*50}")
    
    # Hourly patterns
    hourly_stats = df.groupby('hour').agg({
        'UseMinutes': ['count', 'mean', 'sum'],
        'Consumption': 'mean',
        'AppCode': 'nunique'
    }).round(4)
    
    print("Hourly Usage Patterns:")
    print(hourly_stats.head(10))
    
    # Daily patterns
    daily_stats = df.groupby('day_of_week').agg({
        'UseMinutes': ['count', 'mean', 'sum'],
        'Consumption': 'mean',
        'AppCode': 'nunique'
    }).round(4)
    
    print("\nDaily Usage Patterns:")
    print(daily_stats)
    
    # User-level analysis
    print(f"\n{'='*50}")
    print("USER-LEVEL ANALYSIS")
    print(f"{'='*50}")
    
    user_stats = df.groupby('AppCode').agg({
        'UseMinutes': ['count', 'sum', 'mean', 'std'],
        'Consumption': ['sum', 'mean'],
        'Bonus': ['sum', 'mean'],
        'session_duration': ['mean', 'std']
    }).round(4)
    
    print("User-level Statistics (Top 10 most active users):")
    top_users = user_stats.sort_values(('UseMinutes', 'sum'), ascending=False).head(10)
    print(top_users)
    
    # Correlation analysis
    print(f"\n{'='*50}")
    print("CORRELATION ANALYSIS")
    print(f"{'='*50}")
    
    corr_vars = ['UseMinutes', 'Bonus', 'Consumption', 'session_duration']
    correlation_matrix = df[corr_vars].corr()
    print("Correlation Matrix:")
    print(correlation_matrix.round(4))
    
    # Save detailed statistics to file
    save_detailed_stats(df)

def save_detailed_stats(df):
    """Save detailed statistics to CSV files"""
    
    # User-level statistics
    user_stats = df.groupby('AppCode').agg({
        'UseMinutes': ['count', 'sum', 'mean', 'std', 'min', 'max'],
        'Consumption': ['sum', 'mean', 'count'],
        'Bonus': ['sum', 'mean', 'count'],
        'session_duration': ['mean', 'std', 'min', 'max'],
        'date': ['min', 'max', 'nunique']
    }).round(4)
    
    user_stats.columns = ['_'.join(col).strip() for col in user_stats.columns]
    user_stats.to_csv('output/user_level_statistics.csv')
    
    # Daily statistics
    daily_stats = df.groupby('date').agg({
        'UseMinutes': ['count', 'sum', 'mean', 'std'],
        'Consumption': ['sum', 'mean'],
        'Bonus': ['sum', 'mean'],
        'AppCode': 'nunique',
        'session_duration': ['mean', 'std']
    }).round(4)
    
    daily_stats.columns = ['_'.join(col).strip() for col in daily_stats.columns]
    daily_stats.to_csv('output/daily_statistics.csv')
    
    # Hourly statistics
    hourly_stats = df.groupby('hour').agg({
        'UseMinutes': ['count', 'sum', 'mean', 'std'],
        'Consumption': ['sum', 'mean'],
        'Bonus': ['sum', 'mean'],
        'AppCode': 'nunique',
        'session_duration': ['mean', 'std']
    }).round(4)
    
    hourly_stats.columns = ['_'.join(col).strip() for col in hourly_stats.columns]
    hourly_stats.to_csv('output/hourly_statistics.csv')

def create_visualizations(df):
    """Create comprehensive visualizations"""
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig, axes = plt.subplots(3, 3, figsize=(20, 15))
    fig.suptitle('Comprehensive Analysis of Bonus Limit Control Consumption Data', fontsize=16, fontweight='bold')
    
    # 1. Distribution of UseMinutes
    axes[0, 0].hist(df['UseMinutes'], bins=50, alpha=0.7, edgecolor='black')
    axes[0, 0].set_title('Distribution of Use Minutes')
    axes[0, 0].set_xlabel('Use Minutes')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].set_yscale('log')
    
    # 2. Consumption vs Non-consumption
    consumption_counts = df['Consumption'].value_counts()
    axes[0, 1].pie(consumption_counts.values, labels=['Non-Consumption', 'Consumption'], 
                   autopct='%1.1f%%', startangle=90)
    axes[0, 1].set_title('Consumption vs Non-Consumption')
    
    # 3. Bonus distribution
    bonus_counts = df['Bonus'].value_counts()
    axes[0, 2].bar(bonus_counts.index, bonus_counts.values, alpha=0.7)
    axes[0, 2].set_title('Bonus Distribution')
    axes[0, 2].set_xlabel('Bonus')
    axes[0, 2].set_ylabel('Count')
    
    # 4. Hourly usage patterns
    hourly_usage = df.groupby('hour')['UseMinutes'].sum()
    axes[1, 0].plot(hourly_usage.index, hourly_usage.values, marker='o')
    axes[1, 0].set_title('Total Usage by Hour of Day')
    axes[1, 0].set_xlabel('Hour')
    axes[1, 0].set_ylabel('Total Use Minutes')
    axes[1, 0].grid(True, alpha=0.3)
    
    # 5. Daily usage patterns
    daily_usage = df.groupby('day_of_week')['UseMinutes'].sum()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_usage = daily_usage.reindex(day_order)
    axes[1, 1].bar(range(len(daily_usage)), daily_usage.values, alpha=0.7)
    axes[1, 1].set_title('Total Usage by Day of Week')
    axes[1, 1].set_xlabel('Day of Week')
    axes[1, 1].set_ylabel('Total Use Minutes')
    axes[1, 1].set_xticks(range(len(daily_usage)))
    axes[1, 1].set_xticklabels(daily_usage.index, rotation=45)
    
    # 6. UseMinutes vs Consumption
    consumption_means = df.groupby('Consumption')['UseMinutes'].mean()
    axes[1, 2].bar(['Non-Consumption', 'Consumption'], consumption_means.values, alpha=0.7)
    axes[1, 2].set_title('Average Use Minutes by Consumption Status')
    axes[1, 2].set_ylabel('Average Use Minutes')
    
    # 7. Session duration distribution
    axes[2, 0].hist(df['session_duration'], bins=50, alpha=0.7, edgecolor='black')
    axes[2, 0].set_title('Distribution of Session Duration')
    axes[2, 0].set_xlabel('Session Duration (minutes)')
    axes[2, 0].set_ylabel('Frequency')
    axes[2, 0].set_yscale('log')
    
    # 8. Top 20 users by total usage
    top_users = df.groupby('AppCode')['UseMinutes'].sum().sort_values(ascending=False).head(20)
    axes[2, 1].barh(range(len(top_users)), top_users.values, alpha=0.7)
    axes[2, 1].set_title('Top 20 Users by Total Usage')
    axes[2, 1].set_xlabel('Total Use Minutes')
    axes[2, 1].set_yticks(range(len(top_users)))
    axes[2, 1].set_yticklabels([f"User {i+1}" for i in range(len(top_users))])
    
    # 9. Usage over time
    daily_total = df.groupby('date')['UseMinutes'].sum()
    axes[2, 2].plot(daily_total.index, daily_total.values, marker='o', markersize=3)
    axes[2, 2].set_title('Total Usage Over Time')
    axes[2, 2].set_xlabel('Date')
    axes[2, 2].set_ylabel('Total Use Minutes')
    axes[2, 2].tick_params(axis='x', rotation=45)
    axes[2, 2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/comprehensive_analysis_plots.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create correlation heatmap
    plt.figure(figsize=(10, 8))
    corr_vars = ['UseMinutes', 'Bonus', 'Consumption', 'session_duration']
    correlation_matrix = df[corr_vars].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                square=True, fmt='.3f')
    plt.title('Correlation Matrix of Key Variables')
    plt.tight_layout()
    plt.savefig('output/correlation_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Visualizations saved to output/ directory")

if __name__ == "__main__":
    main()





