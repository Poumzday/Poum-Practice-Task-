import pandas as pd
import numpy as np
from pathlib import Path

df = pd.read_csv('/Users/poum/Downloads/spell_data_for_snooze_facebook.csv')

df['Date'] = pd.to_datetime(df['Date'])
df['StartTime'] = pd.to_datetime(df['StartTime'])
df['EndTime'] = pd.to_datetime(df['EndTime'])

if 'Snooze' in df.columns:
    df = df.rename(columns={'Snooze': 'HitLimit'})
if 'SnoozeTime' in df.columns:
    df = df.rename(columns={'SnoozeTime': 'HLTime'})
    df['HLTime'] = pd.to_datetime(df['HLTime'], errors='coerce')
if 'incorrect_snooze' in df.columns:
    df = df.drop(columns=['incorrect_snooze'])

numeric_cols = df.select_dtypes(include=[np.number]).columns
for col in numeric_cols:
    df[col] = df[col].round(3)

df = df.sort_values(['AppCode', 'Date', 'StartTime']).reset_index(drop=True)

df = df[(df['UseMinutes'] > 1.0) | (df['HitLimit'] == 1)]

rows_to_keep = []
for (appcode, date), group in df.groupby(['AppCode', 'Date']):
    hitlimit_rows = group[group['HitLimit'] == 1]
    if len(hitlimit_rows) > 0:
        first_hitlimit_idx = hitlimit_rows.index[0]
        rows_to_keep.extend(group[group.index >= first_hitlimit_idx].index.tolist())
    else:
        rows_to_keep.extend(group.index.tolist())

df = df.loc[rows_to_keep].reset_index(drop=True)

df['Snooze'] = 0
for (appcode, date), group in df.groupby(['AppCode', 'Date']):
    if len(group) > 1:
        df.loc[group.index, 'Snooze'] = 1

day_level_data = []
for (appcode, date), group in df.groupby(['AppCode', 'Date']):
    last_row = group.iloc[-1]
    hitlimit_rows = group[group['HitLimit'] == 1]
    hl_time = hitlimit_rows.iloc[0]['HLTime'] if len(hitlimit_rows) > 0 else pd.NaT
    
    day_level_data.append({
        'AppCode': appcode,
        'SnoozeGroup': last_row['SnoozeGroup'],
        'Date': date,
        'CumMins': last_row['CumMins'],
        'LimitMinutes': last_row['LimitMinutes'],
        'Snooze_Acc': group['Snooze'].max(),
        'HLTime': hl_time
    })

day_df = pd.DataFrame(day_level_data)

snooze_order = ['Snooze 0', 'Snooze 2', 'Snooze 5', 'Snooze 20']
day_df['sort_order'] = day_df['SnoozeGroup'].map({val: i for i, val in enumerate(snooze_order)})
day_df = day_df.sort_values(['sort_order', 'AppCode', 'Date']).drop('sort_order', axis=1).reset_index(drop=True)

day_df['CumMins'] = day_df['CumMins'].round(3)
day_df['LimitMinutes'] = day_df['LimitMinutes'].round(3)
day_df['Snooze_Acc'] = day_df['Snooze_Acc'].round(3)

output_dir = Path(__file__).parent.parent / 'output' / 'tables'
output_dir.mkdir(parents=True, exist_ok=True)
day_df.to_csv(output_dir / '2-day_level_data.csv', index=False)
