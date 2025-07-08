import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from collections import Counter

# Load the dataset
try:
    df = pd.read_csv('tasindex_import.csv')
except FileNotFoundError:
    print("Error: 'tasindex_import.csv' not found. Please make sure the file is in the correct directory.")
    exit()

# Define the software families
software_families = {
    'Thermal Desktop, SINDA family': ['Thermal Desktop', 'SINDA', 'RADCAD', 'FloCAD', 'Veritrek'],
    'ESATAN family': ['ESATAN', 'ESARAD', 'ThermXL', 'ESABASE', 'MINITAN'],
    'Systema family': ['Systema', 'Thermica', 'Thermisol'],
    'NX TMG family': ['NX', 'TMG', 'I-DEAS'],
    'Legacy Radiation Analyzers': ['TRASYS', 'NEVADA', 'TSS', 'LOHARP', 'MTRAP', 'Chrysler Shape Factor'],
    'Legacy Network Analyzers': ['CINDA', 'MITAS', 'THERM', 'TAL'],
    'FE analysis family': ['ANSYS', 'Abaqus', 'Nastran', 'Patran', 'COMSOL', 'COSMOS'],
    'Self-developed tools': ['Scilab', 'MATLAB', 'In-house', 'Fortran', 'Excel', 'MathCAD']
}

# Function to assign a software to a family
def get_software_family(software_name):
    if pd.isna(software_name):
        return None
    for family, names in software_families.items():
        for name in names:
            if name.lower() in software_name.lower():
                return family
    print(f"Software '{software_name}' does not match any known family.")
    return 'Others'

# --- Create 5 subplots for different decades ---
# Define the decades
decades = [
    (1970, 1989),
    (1990, 1999),
    (2000, 2009),
    (2010, 2019),
    (2020, 2029)
]

# Prepare data for all decades
df['launch_date'] = pd.to_datetime(df['launch_date'], errors='coerce')
df['launch_year'] = df['launch_date'].dt.year

# Create subplots: 3 rows, 2 columns
fig, axes = plt.subplots(3, 2, figsize=(190/25.4*2, 140/25.4*2))
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 12

# Flatten axes array for easier indexing
axes = axes.flatten()

software_columns = ['software_1', 'software_2', 'software_3', 'software_4', 'software_5']

for i, (year_min, year_max) in enumerate(decades):
    # Filter data for current decade
    df_filtered = df[(df['launch_year'] >= year_min) & (df['launch_year'] <= year_max)]
    
    # Initialize counter with all software families set to 0
    family_counter = Counter()
    for family in software_families.keys():
        family_counter[family] = 0
    
    # Iterate over each project (row) in filtered data
    for index, row in df_filtered.iterrows():
        project_families = set()
        # Find all unique families used in this project
        for col in software_columns:
            software_name = row[col]
            if pd.notna(software_name):
                family = get_software_family(software_name)
                if family:
                    project_families.add(family)
        
        # Add the unique families to the total count
        family_counter.update(project_families)
    
    # Convert the counter to a pandas Series for plotting
    family_counts = pd.Series(family_counter).sort_values(ascending=True)
    
    # Plot on current subplot
    ax = axes[i]
    ax.barh(family_counts.index, family_counts.values)
    ax.set_xlabel('Number of Projects', fontsize=12)
    ax.set_title(f'Launch in {year_min}–{year_max}', fontsize=12)
    ax.set_xlim(0, 30)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    ax.grid(True, axis='x', which='major', linestyle='-', linewidth=0.5)
    ax.grid(True, axis='x', which='minor', linestyle='--', linewidth=0.5)

# Remove the 6th subplot (empty)
axes[5].remove()

plt.tight_layout()
plt.savefig('software_count.pdf', format='pdf')
plt.close()


