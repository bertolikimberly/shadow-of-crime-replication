
#Input:  data_clean.csv, temporal_coefs.csv, pooled_coefs.csv
#Output: g1_victimization_rates.png through g8_descriptive_bars.png

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from config import ROUND_YEARS, COL, apply_style

apply_style()

#Load data
df_reg = pd.read_csv('data_clean.csv')
temporal = pd.read_csv('temporal_coefs.csv')
pooled = pd.read_csv('pooled_coefs.csv')

rounds_list = sorted(df_reg['essround'].unique())
years_list = [ROUND_YEARS[r] for r in rounds_list]
countries = sorted(df_reg['cntry'].unique())

def wmean(vals, wts):
    mask = np.isfinite(vals) & np.isfinite(wts)
    if mask.sum() == 0:
        return np.nan
    return np.average(vals[mask], weights=wts[mask])

print("Generating graphs...")


#G1 Descriptive Bars by Round
print("  G1: Descriptive bars by round...")
fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))

vr = [df_reg[df_reg['essround'] == r]['victim'].mean() * 100 for r in rounds_list]
axes[0].bar(years_list, vr, color=COL['navy'], alpha=0.8, width=1.5, edgecolor='white')
for yv, vv in zip(years_list, vr):
    axes[0].text(yv, vv + 0.3, f'{vv:.1f}%', ha='center', va='bottom', fontsize=8, color=COL['navy'])
axes[0].set_ylabel('Victimization Rate (%)')
axes[0].set_title('Victimization Rate', fontweight='bold')
axes[0].set_xticks(years_list)
axes[0].set_xticklabels([str(y) for y in years_list], rotation=45, fontsize=9)
axes[0].spines['top'].set_visible(False)
axes[0].spines['right'].set_visible(False)
axes[0].set_ylim(0, max(vr) * 1.15)

safety_gaps = []
for r in rounds_list:
    sub = df_reg[df_reg['essround'] == r]
    safety_gaps.append(sub[sub['victim'] == 1]['safety'].mean() - sub[sub['victim'] == 0]['safety'].mean())
bar_colors = [COL['red'] if g < -0.17 else COL['orange'] for g in safety_gaps]
axes[1].bar(years_list, safety_gaps, color=bar_colors, alpha=0.8, width=1.5, edgecolor='white')
for yv, gv in zip(years_list, safety_gaps):
    axes[1].text(yv, gv - 0.005, f'{gv:.3f}', ha='center', va='top', fontsize=7.5, color='black')
axes[1].set_ylabel('Gap (Victim - Non-Victim)')
axes[1].set_title('Safety Perception Gap', fontweight='bold')
axes[1].set_xticks(years_list)
axes[1].set_xticklabels([str(y) for y in years_list], rotation=45, fontsize=9)
axes[1].axhline(y=0, color='black', linewidth=0.6)
axes[1].spines['top'].set_visible(False)
axes[1].spines['right'].set_visible(False)

happy_gaps, life_gaps = [], []
for r in rounds_list:
    sub = df_reg[df_reg['essround'] == r]
    happy_gaps.append(sub[sub['victim'] == 1]['happiness'].mean() - sub[sub['victim'] == 0]['happiness'].mean())
    life_gaps.append(sub[sub['victim'] == 1]['life_sat'].mean() - sub[sub['victim'] == 0]['life_sat'].mean())
xb = np.arange(len(years_list))
axes[2].bar(xb - 0.18, happy_gaps, 0.35, label='Happiness', color=COL['teal'], alpha=0.8, edgecolor='white')
axes[2].bar(xb + 0.18, life_gaps, 0.35, label='Life Satisfaction', color=COL['gold'], alpha=0.8, edgecolor='white')
axes[2].set_ylabel('Gap (Victim - Non-Victim)')
axes[2].set_title('Wellbeing Gaps', fontweight='bold')
axes[2].set_xticks(xb)
axes[2].set_xticklabels([str(y) for y in years_list], rotation=45, fontsize=9)
axes[2].axhline(y=0, color='black', linewidth=0.6)
axes[2].legend(fontsize=9, frameon=True)
axes[2].spines['top'].set_visible(False)
axes[2].spines['right'].set_visible(False)
fig.suptitle('Victimization Rates and Gaps by ESS Round', fontweight='bold', y=1.03)
plt.tight_layout()
plt.savefig('g1_descriptive_bars.png', dpi=300, bbox_inches='tight')
plt.close()

#G2 Safety Perception Gap Over Time
print("  G2: Safety perception gap...")
fig, ax = plt.subplots(figsize=(10, 6))
nv_safety, v_safety = [], []
for r in rounds_list:
    sub = df_reg[df_reg['essround'] == r]
    nv_safety.append(wmean(sub[sub['victim'] == 0]['safety'].values, sub[sub['victim'] == 0]['w'].values))
    v_safety.append(wmean(sub[sub['victim'] == 1]['safety'].values, sub[sub['victim'] == 1]['w'].values))

ax.plot(years_list, nv_safety, marker='s', markersize=7, linewidth=2.5, color=COL['navy'], label='Non-victims', zorder=3)
ax.plot(years_list, v_safety, marker='^', markersize=7, linewidth=2.5, color=COL['red'], label='Victims', zorder=3)
ax.fill_between(years_list, v_safety, nv_safety, alpha=0.12, color=COL['red'])
ax.set_xlabel('Year')
ax.set_ylabel('Mean Safety Perception (1-4, higher = safer)')
ax.set_title('Safety Perception: Victims vs Non-Victims Over Time')
ax.legend(fontsize=11, frameon=True)
ax.set_xticks(years_list)
ax.set_xticklabels([str(y) for y in years_list], rotation=45)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig('g2_safety_gap.png', dpi=300, bbox_inches='tight')
plt.close()


#G3 Happiness & Life Satisfaction Gap
print("  G3: Wellbeing gaps...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
for ax_cur, var, title in [(ax1, 'happiness', 'Happiness'), (ax2, 'life_sat', 'Life Satisfaction')]:
    nv_m, v_m = [], []
    for r in rounds_list:
        sub = df_reg[df_reg['essround'] == r]
        nv_m.append(wmean(sub[sub['victim'] == 0][var].values, sub[sub['victim'] == 0]['w'].values))
        v_m.append(wmean(sub[sub['victim'] == 1][var].values, sub[sub['victim'] == 1]['w'].values))
    ax_cur.plot(years_list, nv_m, marker='s', markersize=6, linewidth=2.5, color=COL['navy'], label='Non-victims')
    ax_cur.plot(years_list, v_m, marker='^', markersize=6, linewidth=2.5, color=COL['red'], label='Victims')
    ax_cur.fill_between(years_list, v_m, nv_m, alpha=0.12, color=COL['red'])
    ax_cur.set_xlabel('Year')
    ax_cur.set_ylabel(f'Mean {title} (0-10)')
    ax_cur.set_title(title, fontweight='bold')
    ax_cur.legend(fontsize=10, frameon=True)
    ax_cur.set_xticks(years_list)
    ax_cur.set_xticklabels([str(y) for y in years_list], rotation=45, fontsize=9)
    ax_cur.spines['top'].set_visible(False)
    ax_cur.spines['right'].set_visible(False)
fig.suptitle('Subjective Wellbeing: Victims vs Non-Victims (ESS Rounds 1-11)', fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('g3_wellbeing_gap.png', dpi=300, bbox_inches='tight')
plt.close()


#G4 Regression Coefficients Over Time
print("  G4: Regression coefficients over time...")
fig, ax = plt.subplots(figsize=(11, 6))
for var, label, color, marker in [
    ('safety', 'Safety Perception', COL['red'], 's'),
    ('happiness', 'Happiness', COL['teal'], '^'),
    ('life_sat', 'Life Satisfaction', COL['gold'], 'o')
]:
    t = temporal[temporal['outcome'] == var].sort_values('year')
    coefs = t['coef'].values
    ses = t['se'].values
    yrs = t['year'].values
    ax.plot(yrs, coefs, marker=marker, markersize=7, linewidth=2.5, color=color, label=label, zorder=3)
    ax.fill_between(yrs, coefs - 1.96 * ses, coefs + 1.96 * ses, alpha=0.15, color=color)

ax.axhline(y=0, color='black', linewidth=0.8, linestyle='--', alpha=0.5)
ax.set_xlabel('Year')
ax.set_ylabel('Victimization Coefficient (OLS with controls + country FE)')
ax.set_title('Controlled Victimization Effect Over Time\n(with 95% confidence intervals)', fontweight='bold')
ax.legend(fontsize=10, frameon=True, loc='lower left')
ax.set_xticks(years_list)
ax.set_xticklabels([str(y) for y in years_list], rotation=45)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig('g4_coefficients_over_time.png', dpi=300, bbox_inches='tight')
plt.close()


#G5 Gender x Victimization Interaction
print("  G5: Gender x victimization...")
fig, axes = plt.subplots(1, 3, figsize=(15, 6))
for ax_idx, (var, title) in enumerate([('safety', 'Safety Perception'), ('happiness', 'Happiness'), ('life_sat', 'Life Satisfaction')]):
    labels_map = {
        (0, 0): ('Male, Non-victim', COL['navy'], '-', 's'),
        (0, 1): ('Female, Non-victim', COL['teal'], '-', 'o'),
        (1, 0): ('Male, Victim', COL['orange'], '--', '^'),
        (1, 1): ('Female, Victim', COL['red'], '--', 'D')
    }
    for (v_val, f_val), (lab, col, ls, mk) in labels_map.items():
        x_plot, y_plot = [], []
        for r in rounds_list:
            sub = df_reg[(df_reg['essround'] == r) & (df_reg['victim'] == v_val) & (df_reg['female'] == f_val)]
            if len(sub) > 0:
                x_plot.append(ROUND_YEARS[r])
                y_plot.append(wmean(sub[var].values, sub['w'].values))
        axes[ax_idx].plot(x_plot, y_plot, marker=mk, markersize=5, linewidth=1.8,
                          color=col, linestyle=ls, label=lab, alpha=0.9)
    axes[ax_idx].set_xlabel('Year')
    axes[ax_idx].set_title(title, fontweight='bold')
    axes[ax_idx].set_xticks(years_list)
    axes[ax_idx].set_xticklabels([str(y) for y in years_list], rotation=45, fontsize=8)
    axes[ax_idx].spines['top'].set_visible(False)
    axes[ax_idx].spines['right'].set_visible(False)
    if ax_idx == 1:
        axes[ax_idx].set_ylabel('Mean Score')
        axes[ax_idx].legend(fontsize=8, frameon=True, loc='lower right')
fig.suptitle('Gender and Victimization Interaction Over Time', fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('g5_gender_interaction.png', dpi=300, bbox_inches='tight')
plt.close()

#G6 Country Heatmap
print("  G6: Country heatmap...")
fig, ax = plt.subplots(figsize=(10, 8))
outcomes = ['safety', 'happiness', 'life_sat']
olabels = ['Safety\nPerception', 'Happiness', 'Life\nSatisfaction']
gap_mat = np.zeros((len(countries), 3))
for i, c in enumerate(countries):
    sub = df_reg[df_reg['cntry'] == c]
    for j, var in enumerate(outcomes):
        v_vals = sub[sub['victim'] == 1][var]
        nv_vals = sub[sub['victim'] == 0][var]
        if len(v_vals) > 10:
            gap_mat[i, j] = v_vals.mean() - nv_vals.mean()
sort_idx = np.argsort(gap_mat[:, 0])
gap_mat = gap_mat[sort_idx]
countries_s = [countries[ii] for ii in sort_idx]
im = ax.imshow(gap_mat, cmap='RdBu_r', aspect='auto', vmin=-0.8, vmax=0.1)
ax.set_xticks(range(3))
ax.set_xticklabels(olabels, fontsize=11)
ax.set_yticks(range(len(countries_s)))
ax.set_yticklabels(countries_s, fontsize=10)
for i in range(len(countries_s)):
    for j in range(3):
        color = 'black'
        ax.text(j, i, f'{gap_mat[i, j]:.2f}', ha='center', va='center', fontsize=9, color=color)
plt.colorbar(im, ax=ax, shrink=0.8, label='Victim minus Non-Victim Gap')
ax.set_title('Victimization Effect by Country\n(negative = victims score lower)', fontweight='bold')
plt.tight_layout()
plt.savefig('g6_country_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()

#G7 Regression Coefficient Summary
print("  G7: Coefficient bar chart...")
fig, ax = plt.subplots(figsize=(10, 6))
var_labels = ['Victimization', 'Female', 'Age', 'Education\n(years)', 'Urban\n(domicile)']
x = np.arange(len(var_labels))
width = 0.25
var_order = ['victim', 'female', 'age_clean', 'eduyrs_clean', 'domicil_clean']

for i, (outcome, label, color) in enumerate([
    ('safety', 'Safety', COL['red']),
    ('happiness', 'Happiness', COL['teal']),
    ('life_sat', 'Life Satisfaction', COL['gold'])
]):
    sub = pooled[pooled['outcome'] == outcome].set_index('variable')
    coefs = [float(sub.loc[v, 'coef']) for v in var_order]
    sigs = []
    for v in var_order:
        p = float(sub.loc[v, 'p'])
        sigs.append('***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else '')
    bars = ax.bar(x + i * width, coefs, width, label=label, color=color, alpha=0.85, edgecolor='white')
    for bar, sig in zip(bars, sigs):
        if sig:
            ypos = bar.get_height()
            offset = 0.01 if ypos >= 0 else -0.02
            ax.text(bar.get_x() + bar.get_width() / 2, ypos + offset, sig,
                    ha='center', va='bottom' if ypos >= 0 else 'top', fontsize=8, fontweight='bold')

ax.set_xticks(x + width)
ax.set_xticklabels(var_labels, fontsize=10)
ax.axhline(y=0, color='black', linewidth=0.8)
ax.set_ylabel('OLS Coefficient (with country + round FE)')
ax.set_title('Regression Coefficients Across Three Outcome Models', fontweight='bold')
ax.legend(fontsize=10, frameon=True)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig('g7_coefficient_summary.png', dpi=300, bbox_inches='tight')
plt.close()

#G8 Victimization Rates by Country Over Time
print("  G8: Victimization rates by country...")
fig, ax = plt.subplots(figsize=(12, 7))
cpal = plt.cm.tab20(np.linspace(0, 1, len(countries)))
country_means = {}
for c in countries:
    country_means[c] = df_reg[df_reg['cntry'] == c]['victim'].mean()
countries_sorted = sorted(countries, key=lambda c: country_means[c], reverse=True)

for i, c in enumerate(countries_sorted):
    x_vals, y_vals = [], []
    for r in rounds_list:
        sub = df_reg[(df_reg['cntry'] == c) & (df_reg['essround'] == r)]
        if len(sub) > 0:
            x_vals.append(ROUND_YEARS[r])
            y_vals.append(sub['victim'].mean() * 100)
    ax.plot(x_vals, y_vals, marker='o', markersize=4, linewidth=1.5,
            label=c, color=cpal[i], alpha=0.85)

ax.set_xlabel('Year')
ax.set_ylabel('Victimization Rate (%)')
ax.set_title('Crime Victimization Rates Across European Countries (ESS Rounds 1-11)')
ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9, frameon=True)
ax.set_xticks(years_list)
ax.set_xticklabels([str(y) for y in years_list], rotation=45)
ax.set_ylim(0, None)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig('g8_victimization_rates.png', dpi=300, bbox_inches='tight')
plt.close()

#G9: Distribution Violin Plots
print("  Graph 9: Violin distributions...")

fig, axes = plt.subplots(1, 3, figsize=(15, 6))

for ax_i, (var, title, ylab) in enumerate([
    ('safety', 'Safety Perception', 'Score (1-4)'),
    ('happiness', 'Happiness', 'Score (0-10)'),
    ('life_sat', 'Life Satisfaction', 'Score (0-10)')
]):
    
    ax = axes[ax_i]

    # Data
    data_v = [
        df_reg[df_reg['victim'] == 0][var].values,
        df_reg[df_reg['victim'] == 1][var].values
    ]

    parts = ax.violinplot(
        data_v,
        positions=[0, 1],
        showmeans=True,
        showmedians=True
    )

    # Colors
    for pc, col in zip(parts['bodies'], [COL['navy'], COL['red']]):
        pc.set_facecolor(col)
        pc.set_alpha(0.6)

    # Style
    for key in ['cmeans', 'cmedians', 'cmins', 'cmaxes', 'cbars']:
        if key in parts:
            parts[key].set_color('black' if key == 'cmeans' else COL['grey'])

    # Axis formatting
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Non-victim', 'Victim'], fontsize=11)
    ax.set_ylabel(ylab)
    ax.set_title(title, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    #Mean Placement
    ymin, ymax = ax.get_ylim()
    offset = (ymax - ymin) * 0.08

    for v, xp, col in [(0, 0, COL['navy']), (1, 1, COL['red'])]:
        m = df_reg[df_reg['victim'] == v][var].mean()
        ax.text(
            xp,
            ymax + offset,
            f'μ={m:.2f}',
            ha='center',
            va='bottom',
            fontsize=9,
            color=col,
            fontweight='bold'
        )

    ax.set_ylim(ymin, ymax + offset * 2)

fig.suptitle(
    'Distribution of Outcomes by Victimization Status (Pooled ESS 1-11)',
    fontweight='bold',
    y=1.03
)

plt.tight_layout()
plt.savefig('g9_distributions.png', dpi=300, bbox_inches='tight')
plt.close()

print("\n" + "=" * 60)
print("ALL GRAPHS SAVED:")
print("  g1_descriptive_bars.png")
print("  g2_safety_gap.png")
print("  g3_wellbeing_gap.png")
print("  g4_country_heatmap.png")
print("  g5_coefficients_over_time.png")
print("  g6_gender_interaction.png")
print("  g7_coefficient_summary.png")
print("  g8_victimization_rates.png")
print("=" * 60)