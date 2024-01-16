import matplotlib.pyplot as plt
import numpy as np
import pickle

with open('../../data-explorer/helmcharts-data-paper/metadatarq1.pickle', 'rb') as f:
    total_meta = pickle.load(f)

import scipy.stats as stats


def test_skewness(data):
    # Calculate skewness coefficient
    skewness = stats.skew(data)
    print("Skewness coefficient:", skewness)

    # Perform hypothesis test for skewness
    _, p_value = stats.skewtest(data)
    print("P-value:", p_value)


def test_normality(data):
    # Shapiro-Wilk Test
    shapiro_stat, shapiro_pvalue = stats.shapiro(data)
    print("Shapiro-Wilk Test:")
    print(f"Test Statistic: {shapiro_stat}")
    print(f"P-value: {shapiro_pvalue}")

    # Anderson-Darling Test
    anderson_stat, anderson_crit_values, anderson_sig_levels = stats.anderson(data)
    print("\nAnderson-Darling Test:")
    print(f"Test Statistic: {anderson_stat}")
    print(f"Critical Values: {anderson_crit_values}")
    print(f"Significance Levels: {anderson_sig_levels}")


# Sample data (replace with your actual data)
def draw(data, use_log=True, x_label='Number of Charts'):
    # Create a histogram
    fig, ax = plt.subplots(figsize=(8, 6))

    # Set logarithmic scale on x-axis
    if use_log:
        ax.set_xscale('log')

    # Plot the histogram with logarithmic bins
    bins = np.logspace(np.log10(min(data)), np.log10(max(data)), 50)
    ax.hist(data, bins=bins, edgecolor='black')

    # Set the y-axis to show counts (frequency)
    ax.set_ylabel('Number of Charts', fontsize=16)
    ax.set_xlabel(x_label, fontsize=16)

    # Add legend
    # ax.legend(['Data'])

    # Display the plot
    plt.show()


if __name__ == '__main__':
    # Helm chart with most cve
    involved_cves, involved_fixable_cves, involved_pkgs, involved_images = total_meta

    data = involved_fixable_cves.values()
    data = [x for x in data if x > 0]
    print(f'count of data points for involved_fixable_cves: {len(data)}')
    test_normality(data)
    test_skewness(data)

    draw(data, x_label='Number of Fixable CVEs Per Chart (Log Scale)')

    data = involved_pkgs.values()
    data = [x for x in data if x > 0]
    print(f'count of data points for involved_pkgs: {len(data)}')
    test_normality(data)
    test_skewness(data)

    draw(data, x_label='Number of Packages Per Chart (Log Scale)')

    data = involved_images.values()
    data = [x for x in data if x > 0]
    print(f'count of data points for involved_images: {len(data)}')
    test_normality(data)
    test_skewness(data)

    draw(data, use_log=True, x_label='Number of Images Per Chart (Log Scale)')

    import scipy.stats as stats

    # Example data
    # print(involved_cves.items())
    # print(involved_fixable_cves.items())
    # involved_cves, involved_fixable_cves, involved_pkgs, involved_images = total_meta
    sorted_cves = sorted(involved_fixable_cves.items(), key=lambda x: x[1], reverse=True)
    sorted_pkgs = sorted(involved_pkgs.items(), key=lambda x: x[1], reverse=True)
    sorted_images = sorted(involved_images.items(), key=lambda x: x[1], reverse=True)

    # print(sorted_cves)
    cves = [x[1] for x in sorted_cves]
    packages = [x[1] for x in sorted_pkgs]
    images = [x[1] for x in sorted_images]
    import pandas as pd
    import pingouin as pg

    # Example data
    data = pd.DataFrame({
        'independent_var1': images,  # Replace with your actual data for the first independent variable
        'independent_var2': packages,  # Replace with your actual data for the second independent variable
        'dependent_var': cves  # Replace with your actual data for the dependent variable
    })

    # Calculate partial correlation coefficient
    partial_corr = pg.partial_corr(data=data, x='independent_var2', y='dependent_var', covar=['independent_var1'])

    # Print partial correlation coefficient
    print("Partial correlation coefficient:", partial_corr['r'].values[0])
    print("P-value:", partial_corr['p-val'].values[0])
