import pickle
import statistics
import random

random.seed(42)

with open('dump_actually_fixable_cve_and_pkg_class.pkl', 'rb') as f:
    actually_fixable, cve_pkg_id_map = pickle.load(f)

print(len(actually_fixable))
print(len([cve for cve in cve_pkg_id_map.keys() if cve_pkg_id_map[cve]['cvss_nvd_vector'] != 'NA']))

big_list = [cve_pkg_id_map[cve]['cvss_nvd_vector'] for cve in actually_fixable]
print(big_list[0:10])
import cvss

big_list_exploit = []

base_score = []
exploit_score = []
impact_score = []
for cve_vector in big_list:
    if cve_vector == 'NA':
        continue
    c = cvss.CVSS3(cve_vector)
    c.compute_esc()
    c.compute_isc()
    c.compute_base_score()
    base_score.append(c.base_score)
    exploit_score.append(c.esc)
    impact_score.append(c.isc)

print(f'how many left after removing NA: {len(base_score)}')
print(statistics.mean(base_score))
print(statistics.mean(exploit_score))
print(statistics.mean(impact_score))
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import decimal
from matplotlib.ticker import MaxNLocator

# Assuming base_score, exploit_score, and impact_score are lists of scores
data = {
    'Base Score': base_score,
    'Exploitability Subscore': exploit_score,
    'Impact Subscore': impact_score
}

df = pd.DataFrame(data)

# Convert decimal.Decimal to float
for column in df.columns:
    df[column] = df[column].apply(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)

# Get median values
medians = df.median()

# Iterate over each column to create individual vertical plots
for i, column in enumerate(df.columns):
    plt.figure(figsize=(6, 8))
    ax = sns.boxplot(y=df[column])
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    # Customize the plot
    plt.ylabel('Score', fontweight='bold', fontsize=20)
    # plt.xlabel(column, fontweight='bold', fontsize=20)
    plt.grid(False)

    # Annotate with the median value
    median_val = medians[column]
    # Adjust text position
    # Set y position to the median value and x position for readability
    text_position_y = median_val + 0.15 if i == 0 or i == 2 else median_val + 0.05
    text_position_x = ax.get_xlim()[0] + (ax.get_xlim()[1] - ax.get_xlim()[0]) / 2  # Middle of the plot
    ax.tick_params(axis='both', which='major', labelsize=14)

    ax.text(text_position_x, text_position_y, f'median={median_val:.1f}',
            horizontalalignment='center', size='xx-large', color='black', weight='normal')

    # Show the plot
    plt.show()


def parse_vector_string(vector):
    if vector == 'NA':
        return None
    metrics = vector.split("/")
    metric_dict = {}
    for metric in metrics:
        key, value = metric.split(":")
        metric_dict[key] = value
    return metric_dict


print(parse_vector_string(big_list[0]))

big_matrix = {
    'CVSS': [],
    'AV': [],
    'AC': [],
    'PR': [],
    'UI': [],
    'S': [],
    'C': [],
    'I': [],
    'A': [],
}

for vector in big_list:

    parsed_vector = parse_vector_string(vector)
    if parsed_vector is None:
        continue
    for key in parsed_vector.keys():
        big_matrix[key].append(parsed_vector[key])

from collections import Counter

data = {}

for key in big_matrix.keys():
    if key == 'CVSS':
        continue
    print(key)
    data[key] = Counter(big_matrix[key])
    print(Counter(big_matrix[key]))
    print('------------------')

import pandas as pd

# Example data
# data = {
#     # 'CVSS': {'3.1': 714172, '3.0': 93686},
#     'AV': {'N': 466723, 'L': 317427, 'P': 12161, 'A': 11547},
#     'AC': {'L': 684269, 'H': 123589},
#     'PR': {'N': 550418, 'L': 222608, 'H': 34832},
#     'UI': {'N': 598984, 'R': 208874},
#     'S': {'U': 783016, 'C': 24842},
#     'C': {'N': 388771, 'H': 366965, 'L': 52122},
#     'I': {'N': 470867, 'H': 293376, 'L': 43615},
#     'A': {'H': 603616, 'N': 161583, 'L': 42659}
# }

# Convert to DataFrames
dfs = {}
for key, value in data.items():
    df = pd.DataFrame(list(value.items()), columns=['Subcategory', 'Count'])
    df['Category'] = key
    dfs[key] = df

# Mappings from codes to full words for each CVSS metric
mapping_full_names = {
    'AV': {'N': 'Network', 'A': 'Adjacent', 'L': 'Local', 'P': 'Physical'},
    'AC': {'L': 'Low', 'H': 'High'},
    'PR': {'N': 'None', 'L': 'Low', 'H': 'High'},
    'UI': {'N': 'None', 'R': 'Required'},
    'S': {'U': 'Unchanged', 'C': 'Changed'},
    'C': {'N': 'None', 'L': 'Low', 'H': 'High'},
    'I': {'N': 'None', 'L': 'Low', 'H': 'High'},
    'A': {'N': 'None', 'L': 'Low', 'H': 'High'}
}

# Apply mappings to the subcategories in each DataFrame
for category, df in dfs.items():
    df['Subcategory'] = df['Subcategory'].map(mapping_full_names[category])

# Custom order with full names for each category
category_order_full_names = {
    'AV': ['Network', 'Adjacent', 'Local', 'Physical'],  # From least to most severe
    'AC': ['Low', 'High'],  # From least to most severe
    'PR': ['None', 'Low', 'High'],  # From least to most severe
    'UI': ['None', 'Required'],  # From least to most severe
    'S': ['Unchanged', 'Changed'],  # From least to most severe
    'C': ['None', 'Low', 'High'],  # From least to most severe
    'I': ['None', 'Low', 'High'],  # From least to most severe
    'A': ['None', 'Low', 'High']  # From least to most severe
}
# Full names for the categories
full_category_names = {
    'AV': 'Attack Vector',
    'AC': 'Attack Complexity',
    'PR': 'Privileges Required',
    'UI': 'User Interaction',
    'S': 'Scope',
    'C': 'Confidentiality Impact',
    'I': 'Integrity Impact',
    'A': 'Availability Impact'
}

import matplotlib.pyplot as plt
import seaborn as sns

# Set the overall figure size
plt.figure(figsize=(20, 5))

# Iterate over each DataFrame and create a subplot with ordered x-axis
for i, (category, df) in enumerate(dfs.items(), 1):
    # if i in (1, 2, 3, 4):
    #     continue
    # i -= 4
    if i > 4:
        break
    ax = plt.subplot(1, 4, i)  # Adjust the grid size accordingly
    barplot = sns.barplot(
        data=df,
        x='Subcategory',
        y='Count',
        order=category_order_full_names[category],  # Apply the custom order for the x-axis
        # palette = 'Greys',
    )
    plt.title(full_category_names[category], fontweight='bold', fontsize=20)
    plt.xlabel('', )
    plt.ylabel('Fixable CVE Count', fontweight='bold', fontsize=20)
    # Calculate the percentage and add it to the bars
    total = df['Count'].sum()
    ax.tick_params(axis='y', which='major', labelsize=18)
    ax.tick_params(axis='x', which='major', labelsize=18, rotation=45)
    for p in barplot.patches:
        percentage = f'{100 * p.get_height() / total:.1f}%'
        x = p.get_x() + p.get_width() / 2
        y = p.get_height() + (total * 0.001)  # Add a small offset from the top of the bar
        ax.text(x, y, percentage, ha='center', va='bottom', color='black', size='medium')

# Adjust layout and show plot
plt.tight_layout()
plt.show()
plt.plot()
plt.savefig('breakdown_exploit.pdf', format='pdf', bbox_inches='tight')

if __name__ == '__main__':
    pass
