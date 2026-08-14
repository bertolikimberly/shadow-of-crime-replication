#Runs all OLS models, gender interactions, and temporal analysis.
#Saves regression coefficients to CSV files for the graph script.

#Input:  data_clean.csv
#Output: temporal_coefs.csv, pooled_coefs.csv (+ printed tables)

import pandas as pd
import numpy as np
from scipy.stats import norm
from config import ROUND_YEARS, INDIVIDUAL_VARS

print("=" * 70)
print("02  REGRESSION ANALYSIS")
print("=" * 70)

#Load cleaned data
df_reg = pd.read_csv('data_clean.csv')
print(f"Loaded: {len(df_reg):,} observations")

#OLS function with HC1 robust SE
def ols_with_inference(X, y, feature_names, weights=None):
    n, k = X.shape
    if weights is not None:
        sw = np.sqrt(weights)
        Xw = X * sw[:, None]
        yw = y * sw
    else:
        Xw, yw = X, y

    ones = np.ones((n, 1))
    if weights is not None:
        ones = ones * sw[:, None]
    Xw_full = np.hstack([ones, Xw])

    XtX_inv = np.linalg.inv(Xw_full.T @ Xw_full)
    beta = XtX_inv @ (Xw_full.T @ yw)
    resid = yw - Xw_full @ beta

    ss_res = np.sum(resid**2)
    ss_tot = np.sum((yw - np.mean(yw))**2)
    r2 = 1 - ss_res / ss_tot
    adj_r2 = 1 - (1 - r2) * (n - 1) / (n - k - 1)

    meat = np.zeros((k + 1, k + 1))
    for i in range(n):
        xi = Xw_full[i:i+1, :]
        meat += (resid[i]**2) * (xi.T @ xi)
    hc1_factor = n / (n - k - 1)
    V_robust = hc1_factor * XtX_inv @ meat @ XtX_inv
    se_robust = np.sqrt(np.diag(V_robust))

    t_stats = beta / se_robust
    p_values = 2 * (1 - norm.cdf(np.abs(t_stats)))

    names = ['Intercept'] + list(feature_names)
    return {
        'names': names, 'coef': beta, 'se': se_robust,
        't': t_stats, 'p': p_values, 'r2': r2, 'adj_r2': adj_r2, 'n': n
    }

def print_regression(result, title):
    print(f"\n{'─'*70}")
    print(f"  {title}")
    print(f"  N = {result['n']:,}   R² = {result['r2']:.4f}   Adj R² = {result['adj_r2']:.4f}")
    print(f"{'─'*70}")
    print(f"  {'Variable':25s} {'Coeff':>10s} {'Robust SE':>10s} {'t-stat':>10s} {'p-value':>10s}")
    print(f"  {'─'*65}")
    for i, name in enumerate(result['names']):
        if name.startswith('c_') or name.startswith('r_'):
            continue
        sig = '***' if result['p'][i] < 0.001 else '**' if result['p'][i] < 0.01 else '*' if result['p'][i] < 0.05 else ''
        print(f"  {name:25s} {result['coef'][i]:10.4f} {result['se'][i]:10.4f} "
              f"{result['t'][i]:10.2f} {result['p'][i]:10.4f} {sig}")
    n_cfe = sum(1 for n in result['names'] if n.startswith('c_'))
    n_rfe = sum(1 for n in result['names'] if n.startswith('r_'))
    if n_cfe > 0:
        print(f"  {'Country FE':25s} {'Yes':>10s} ({n_cfe} dummies)")
    if n_rfe > 0:
        print(f"  {'Round FE':25s} {'Yes':>10s} ({n_rfe} dummies)")


# POOLED MODELS
country_dummies = pd.get_dummies(df_reg['cntry'], prefix='c', drop_first=True)
round_dummies = pd.get_dummies(df_reg['essround'], prefix='r', drop_first=True)

X_full = np.hstack([
    df_reg[INDIVIDUAL_VARS].values,
    country_dummies.values,
    round_dummies.values
])
feature_names = INDIVIDUAL_VARS + list(country_dummies.columns) + list(round_dummies.columns)
weights = df_reg['w'].values

print("\n" + "=" * 70)
print("POOLED REGRESSION MODELS")
print("=" * 70)

res_safety = ols_with_inference(X_full, df_reg['safety'].values, feature_names, weights)
print_regression(res_safety, "MODEL 1: Safety Perception (1-4, higher=safer)")

res_happy = ols_with_inference(X_full, df_reg['happiness'].values, feature_names, weights)
print_regression(res_happy, "MODEL 2: Happiness (0-10)")

res_life = ols_with_inference(X_full, df_reg['life_sat'].values, feature_names, weights)
print_regression(res_life, "MODEL 3: Life Satisfaction (0-10)")

# Save pooled coefficients for graph script
pooled_rows = []
for var_key, res in [('safety', res_safety), ('happiness', res_happy), ('life_sat', res_life)]:
    for j, vname in enumerate(INDIVIDUAL_VARS):
        pooled_rows.append({
            'outcome': var_key,
            'variable': vname,
            'coef': float(res['coef'][j + 1]),
            'se': float(res['se'][j + 1]),
            'p': float(res['p'][j + 1]),
        })
pd.DataFrame(pooled_rows).to_csv('pooled_coefs.csv', index=False)


# GENDER INTERACTION MODELS
print("\n" + "=" * 70)
print("GENDER INTERACTION MODELS")
print("=" * 70)

df_reg['victim_x_female'] = df_reg['victim'] * df_reg['female']
interact_vars = ['victim', 'female', 'victim_x_female', 'age_clean', 'eduyrs_clean', 'domicil_clean']
X_interact = np.hstack([df_reg[interact_vars].values, country_dummies.values, round_dummies.values])
feat_interact = interact_vars + list(country_dummies.columns) + list(round_dummies.columns)

for y_var, y_label in [('safety', 'Safety Perception'), ('happiness', 'Happiness'), ('life_sat', 'Life Satisfaction')]:
    res = ols_with_inference(X_interact, df_reg[y_var].values, feat_interact, weights)
    print_regression(res, f"INTERACTION: {y_label}")


# TEMPORAL ANALYSIS: ROUND-BY-ROUND REGRESSIONS
print("\n" + "=" * 70)
print("VICTIMIZATION COEFFICIENT BY ROUND (with controls)")
print("=" * 70)

rounds_available = sorted(df_reg['essround'].unique())
temporal_rows = []

for rnd in rounds_available:
    sub = df_reg[df_reg['essround'] == rnd].copy()
    c_dum = pd.get_dummies(sub['cntry'], prefix='c', drop_first=True)
    X_r = np.hstack([sub[INDIVIDUAL_VARS].values, c_dum.values])
    fn_r = INDIVIDUAL_VARS + list(c_dum.columns)
    w_r = sub['w'].values

    for var in ['safety', 'happiness', 'life_sat']:
        res_r = ols_with_inference(X_r, sub[var].values, fn_r, w_r)
        temporal_rows.append({
            'round': int(rnd),
            'year': ROUND_YEARS[int(rnd)],
            'outcome': var,
            'coef': float(res_r['coef'][1]),
            'se': float(res_r['se'][1]),
        })

    row_s = [r for r in temporal_rows if r['round'] == rnd and r['outcome'] == 'safety'][0]
    row_h = [r for r in temporal_rows if r['round'] == rnd and r['outcome'] == 'happiness'][0]
    row_l = [r for r in temporal_rows if r['round'] == rnd and r['outcome'] == 'life_sat'][0]
    print(f"  Round {rnd:2d} ({ROUND_YEARS[int(rnd)]}): "
          f"Safety={row_s['coef']:+.4f}, Happy={row_h['coef']:+.4f}, LifeSat={row_l['coef']:+.4f}")

pd.DataFrame(temporal_rows).to_csv('temporal_coefs.csv', index=False)
print(f"\nSaved temporal_coefs.csv and pooled_coefs.csv")


# ESTIMATED EQUATIONS
print("\n" + "=" * 70)
print("ESTIMATED EQUATIONS (for thesis)")
print("=" * 70)

for res, name, varname in [
    (res_safety, 'Safety Perception', 'safety'),
    (res_happy, 'Happiness', 'happiness'),
    (res_life, 'Life Satisfaction', 'life_sat')
]:
    b = res['coef']
    print(f"\n{name}:")
    print(f"  {varname}_hat = {b[0]:.4f} "
          f"{'+ ' if b[1] >= 0 else ''}{b[1]:.4f}*victim "
          f"{'+ ' if b[2] >= 0 else ''}{b[2]:.4f}*female "
          f"{'+ ' if b[3] >= 0 else ''}{b[3]:.4f}*age "
          f"{'+ ' if b[4] >= 0 else ''}{b[4]:.4f}*eduyrs "
          f"{'+ ' if b[5] >= 0 else ''}{b[5]:.4f}*domicil "
          f"+ country_FE + round_FE")

# Country FE
print("\n\nCountry Fixed Effects (relative to BE):")
for res, name in [(res_safety, 'Safety'), (res_happy, 'Happiness'), (res_life, 'Life Sat')]:
    print(f"\n  {name}:")
    for i, n in enumerate(res['names']):
        if n.startswith('c_'):
            cname = n.replace('c_', '')
            sig = '***' if res['p'][i] < 0.001 else '**' if res['p'][i] < 0.01 else '*' if res['p'][i] < 0.05 else ''
            print(f"    {cname}: {res['coef'][i]:+.4f} {sig}")

# Round FE
print("\n\nRound Fixed Effects (relative to Round 1):")
for res, name in [(res_safety, 'Safety'), (res_happy, 'Happiness'), (res_life, 'Life Sat')]:
    print(f"\n  {name}:")
    for i, n in enumerate(res['names']):
        if n.startswith('r_'):
            rname = n.replace('r_', '')
            sig = '***' if res['p'][i] < 0.001 else '**' if res['p'][i] < 0.01 else '*' if res['p'][i] < 0.05 else ''
            print(f"    Round {rname}: {res['coef'][i]:+.4f} {sig}")

print("\n" + "=" * 70)
print("REGRESSION ANALYSIS COMPLETE")
print("=" * 70)