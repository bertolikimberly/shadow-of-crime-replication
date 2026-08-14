import matplotlib.pyplot as plt

#ESS Round to Year Mapping
ROUND_YEARS = {
    1: 2002, 2: 2004, 3: 2006, 4: 2008, 5: 2010,
    6: 2012, 7: 2014, 8: 2016, 9: 2018, 10: 2020, 11: 2023
}

#Colors
COL = {
    'navy':   '#003366',
    'red':    '#C8102E',
    'teal':   '#0077B6',
    'gold':   '#D4A843',
    'grey':   '#6C757D',
    'green':  '#2A9D8F',
    'orange': '#E76F51',
    'purple': '#7B2D8E',
}

#Variables for regressions
INDIVIDUAL_VARS = ['victim', 'female', 'age_clean', 'eduyrs_clean', 'domicil_clean']

#Style
def apply_style():
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        'font.size': 11,
        'axes.titlesize': 13,
        'axes.titleweight': 'bold',
        'axes.labelsize': 11,
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
        'axes.grid': True,
        'grid.alpha': 0.3,
        'grid.linewidth': 0.5,
    })