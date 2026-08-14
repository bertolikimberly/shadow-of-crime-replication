
#Loads raw ESS data, cleans all variables, and saves a clean CSV that the other scripts can read directly.

#Input:  ess_merged.csv
#Output: data_clean.csv

import pandas as pd
import numpy as np
from config import ROUND_YEARS

print("=" * 70)
print("01  DATA PREPARATION")
print("=" * 70)

#Load
df = pd.read_csv('ess_merged.csv', low_memory=False)
print(f"Raw: {len(df):,} obs, {df['cntry'].nunique()} countries, "
      f"rounds {df['essround'].min()}-{df['essround'].max()}")

#Recode variables

#Victimization: 1=Yes, 2=No -> binary
df['victim'] = df['crmvct'].map({1: 1, 2: 0})

#Safety: reverse so higher = safer (4=very safe, 1=very unsafe)
df['safety'] = df['aesfdrk'].replace({7: np.nan, 8: np.nan, 9: np.nan})
df['safety'] = 5 - df['safety']

#Happiness: 0-10
df['happiness'] = df['happy'].replace({77: np.nan, 88: np.nan, 99: np.nan})
df.loc[df['happiness'] > 10, 'happiness'] = np.nan

#Life satisfaction: 0-10 (handle both possible column names)
if 'stflife' in df.columns:
    df['life_sat'] = df['stflife'].replace({77: np.nan, 88: np.nan, 99: np.nan})
elif 'stflfsf' in df.columns:
    df['life_sat'] = df['stflfsf'].replace({77: np.nan, 88: np.nan, 99: np.nan})
    print("Note: using stflfsf as life satisfaction variable")
else:
    raise KeyError("No life satisfaction column found (stflife or stflfsf)")
df.loc[df['life_sat'] > 10, 'life_sat'] = np.nan

#Gender: 1=Male, 2=Female -> female dummy
df['female'] = df['gndr'].map({1: 0, 2: 1, 9: np.nan})

#Age
df['age_clean'] = pd.to_numeric(df['agea'], errors='coerce')
df.loc[df['age_clean'] > 120, 'age_clean'] = np.nan
df.loc[df['age_clean'] < 15, 'age_clean'] = np.nan

#Education years
df['eduyrs_clean'] = pd.to_numeric(df['eduyrs'], errors='coerce')
df.loc[df['eduyrs_clean'] > 50, 'eduyrs_clean'] = np.nan
df.loc[df['eduyrs_clean'].isin([77, 88, 99]), 'eduyrs_clean'] = np.nan

#Domicile: 1=Big city ... 5=Countryside
df['domicil_clean'] = df['domicil'].replace({7: np.nan, 8: np.nan, 9: np.nan})

#Year and weight
df['year'] = df['essround'].map(ROUND_YEARS)
df['w'] = df['pspwght'].fillna(1)

#Drop rows with missing key variables
key_vars = ['victim', 'safety', 'happiness', 'life_sat', 'female',
            'age_clean', 'eduyrs_clean', 'domicil_clean']
df_clean = df.dropna(subset=key_vars).copy()

print(f"Clean sample: {len(df_clean):,} obs")
print(f"Countries: {sorted(df_clean['cntry'].unique())}")

#Summary
print(f"\n{'Variable':25s} {'Mean':>8s} {'SD':>8s} {'Min':>6s} {'Max':>6s} {'N':>10s}")
print("-" * 65)
for v, lab in [('victim', 'Victimization'), ('safety', 'Safety (1-4)'),
               ('happiness', 'Happiness (0-10)'), ('life_sat', 'Life Sat (0-10)'),
               ('female', 'Female'), ('age_clean', 'Age'),
               ('eduyrs_clean', 'Educ years'), ('domicil_clean', 'Domicile (1-5)')]:
    s = df_clean[v]
    print(f"  {lab:22s} {s.mean():8.3f} {s.std():8.3f} {s.min():6.0f} "
          f"{s.max():6.0f} {s.notna().sum():10,}")

#Save
cols_to_keep = ['essround', 'cntry', 'victim', 'safety', 'happiness', 'life_sat',
                'female', 'age_clean', 'eduyrs_clean', 'domicil_clean', 'year', 'w']
df_clean[cols_to_keep].to_csv('data_clean.csv', index=False)
print(f"\nSaved data_clean.csv ({len(df_clean):,} rows, {len(cols_to_keep)} columns)")