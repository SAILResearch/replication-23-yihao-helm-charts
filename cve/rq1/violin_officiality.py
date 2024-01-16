import pickle
import statistics

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import itertools
import random

random.seed(42)
with open('violin_data_comprehensive.pkl', 'rb') as f:
    data = pickle.load(f)

    violin_data = data[0]
    violin_data_on_pkg = data[1]
    category_counter = data[2]


def draw_violin(violin_data, category_counter, type='official'):
    print(violin_data.keys())
    # Generate sample data
    categories = [1, 2, 3, 4, 5, 6, 7, 8, 'BASELINE']

    print(categories)
    categories_mapping = {
        '1': 'AI/ML',
        '2': 'Database',
        '3': 'Integration',
        '4': 'Monitoring',
        '5': 'Networking',
        '6': 'Security',
        '7': 'Storage',
        '8': 'Streaming',
        'MISC': 'MISC',  # This is an estimation of baseline since category is a mixture of all categories
        'BASELINE': 'Aggregated'
    }
    category_data = [categories_mapping[str(cat)] for cat in categories]
    categories = [1, 2, 3, 4, 5, 6, 7, 8]  # reset categories to without baseline which is an aggregation

    if type == 'official':
        officials = [list(filter(lambda x: (x != 'NA'), violin_data[f'{cat}__official'])) for cat in categories]
        non_officials = [list(filter(lambda x: (x != 'NA'), violin_data[f'{cat}__non_official'])) for cat in categories]
        baseline = list(itertools.chain(*officials))
        baseline_non_official = list(itertools.chain(*non_officials))
        officials.append(baseline)
        non_officials.append(baseline_non_official)
    else:
        # split by pkg type
        officials = [list(filter(lambda x: (x != 'NA'), violin_data_on_pkg[f'{cat}__os_pkgs'])) for cat in categories]
        non_officials = [list(filter(lambda x: (x != 'NA'), violin_data_on_pkg[f'{cat}__lang_pkgs'])) for cat in
                         categories]
        baseline = list(itertools.chain(*officials))
        baseline_non_official = list(itertools.chain(*non_officials))
        officials.append(baseline)
        non_officials.append(baseline_non_official)
    official_scores = officials
    non_official_scores = non_officials

    # Flatten the nested score lists
    official_scores_flat = list(itertools.chain(*official_scores))
    non_official_scores_flat = list(itertools.chain(*non_official_scores))

    # Create a list to hold corresponding categories for each score set
    categories = list(itertools.chain(*[[''] * len(scores) for cat, scores in zip(category_data, official_scores)]))
    categories += list(
        itertools.chain(*[[''] * len(scores) for cat, scores in zip(category_data, non_official_scores)]))

    # Create a list to hold the type for each score set (official or non-official)
    if type == 'official':
        types = ['Official'] * len(official_scores_flat) + ['Non-Official'] * len(non_official_scores_flat)
    else:
        types = ['OS'] * len(official_scores_flat) + ['Language'] * len(non_official_scores_flat)
    # Combine the scores
    all_scores = official_scores_flat + non_official_scores_flat
    print(f'median of official scores: {statistics.median(official_scores_flat)}')
    print(f'median of non-official scores: {statistics.median(non_official_scores_flat)}')
    # Create DataFrame
    data = pd.DataFrame({
        ' ': categories,
        'Type': types,
        'CVSS_Score': all_scores
    })
    plt.figure(figsize=(8, 6))

    # Create split violin plot

    # inner{“box”, “quartile”, “point”, “stick”, None}, optional
    sns.violinplot(x=' ', y='CVSS_Score', hue='Type', data=data, split=True, inner='box', scale='area',
                   scale_hue=True, )
    plt.xticks(rotation=45)
    # Customize the plot
    plt.subplots_adjust(bottom=0.2, top=0.95)

    # plt.xlabel('Chart Category', fontsize=14)
    plt.ylabel('CVSS Score (V3)', fontsize=16)
    plt.legend(title='Type', loc='upper right')
    plt.show()
    from scipy.stats import kruskal

    # Prepare data for Kruskal-Wallis H Test
    official_data = [list(filter(lambda x: x != 'NA', official_scores[i])) for i in range(len(official_scores) - 1)]
    non_official_data = [list(filter(lambda x: x != 'NA', non_official_scores[i])) for i in
                         range(len(non_official_scores) - 1)]

    # Get the scores for the 'MISC' category
    official_misc_scores = official_scores[-1]
    non_official_misc_scores = non_official_scores[-1]

    from scipy.stats import mannwhitneyu

    # Conduct Kruskal-Wallis H Test
    statistic, pvalue = kruskal(official_misc_scores, non_official_misc_scores)
    print(f'Kruskal-Wallis H Test for official vs nonofficial: statistic = {statistic}, p-value = {pvalue}')

    # Run the Mann-Whitney U test
    statistic, p_value = mannwhitneyu(official_misc_scores, non_official_misc_scores)

    print("Mann-Whitney U test results:")
    print(f"U statistic: {statistic}")
    print(f"p-value: {p_value}")


if __name__ == '__main__':
    draw_violin(violin_data, category_counter, type='official')
    # draw_violin(violin_data_on_pkg, category_counter, type='pkg')
