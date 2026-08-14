import subprocess
import sys

scripts = [
    ('data_prep.py',           'Data Preparation'),
    ('02_regression_analysis.py', 'Regression Analysis'),
    ('graphs.py',     'Graph Generation'),
]

for script, label in scripts:
    print(f"\n{'#' * 70}")
    print(f"#  RUNNING: {label} ({script})")
    print(f"{'#' * 70}\n")
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        print(f"\nERROR: {script} failed. Stopping.")
        sys.exit(1)

print(f"\n{'#' * 70}")
print("#  ALL SCRIPTS COMPLETED SUCCESSFULLY")
print(f"{'#' * 70}")