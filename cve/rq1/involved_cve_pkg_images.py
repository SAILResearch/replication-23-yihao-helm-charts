import pickle

with open('../../data-explorer/helmcharts-data-paper/total_meta.pkl', 'rb') as f:
    total_meta = pickle.load(f)

# Helm chart with most cve
involved_cves, involved_pkgs, involved_images = total_meta

print(f'involved_cves: {(involved_cves)}')
print(f'Involved CVEs: {len(involved_cves)}')
key_with_highest_value = max(involved_cves, key=involved_cves.get)
print(f'key with highest value: {key_with_highest_value}, value: {involved_cves[key_with_highest_value]}')

key_with_lowest_value = min(involved_cves, key=involved_cves.get)
print(f'key with lowest value: {key_with_lowest_value}, value: {involved_cves[key_with_lowest_value]}')

median = sorted(involved_cves.values())[len(involved_cves) // 2]
mean = sum(involved_cves.values()) / len(involved_cves)
print(f'median: {median}, mean: {mean}')

# print(f'involved_pkgs: {(involved_pkgs)}')
print(f'Involved packages: {len(involved_pkgs)}')
key_with_highest_value = max(involved_pkgs, key=involved_pkgs.get)
print(f'key with highest value: {key_with_highest_value}, value: {involved_pkgs[key_with_highest_value]}')

key_with_lowest_value = min(involved_pkgs, key=involved_pkgs.get)
print(f'key with lowest value: {key_with_lowest_value}, value: {involved_pkgs[key_with_lowest_value]}')

median = sorted(involved_pkgs.values())[len(involved_pkgs) // 2]
mean = sum(involved_pkgs.values()) / len(involved_pkgs)
print(f'median: {median}, mean: {mean}')

# print(f'involved_images: {(involved_images)}')
# sort the dicsts by value


print(f'Involved images: {len(involved_images)}')
key_with_highest_value = max(involved_images, key=involved_images.get)
print(f'key with highest value: {key_with_highest_value}, value: {involved_images[key_with_highest_value]}')

key_with_lowest_value = min(involved_images, key=involved_images.get)
print(f'key with lowest value: {key_with_lowest_value}, value: {involved_images[key_with_lowest_value]}')

median = sorted(involved_images.values())[len(involved_images) // 2]
mean = sum(involved_images.values()) / len(involved_images)
print(f'median: {median}, mean: {mean}')

######

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt

# Sample data (replace with your actual data)
cves_data = list(involved_cves.values())
images_data = list(involved_images.values())
packages_data = list(involved_pkgs.values())

cves_data = sorted(cves_data, reverse=True)[:]
images_data = sorted(images_data, reverse=True)[:]
packages_data = sorted(packages_data, reverse=True)[:]

# Create violin plots using Seaborn
sns.set(style='whitegrid')
print(cves_data)
# CVEs per chart
fig, ax = plt.subplots(figsize=(6, 6))
sns.violinplot(data=cves_data, ax=ax, inner='quartile', saturation=0.8, )
sns.stripplot(data=cves_data, color='black', size=3, alpha=0.3)
ax.set_ylabel('CVEs per Chart')
ax.set_title('Distribution of CVEs per Chart')
ax.set_ylim(0, 1000)
ax.set_yscale('log')
plt.show()
# Images per chart (similar modifications for other plots)
fig, ax = plt.subplots(figsize=(6, 6))
sns.violinplot(data=images_data, ax=ax, inner='quartile', saturation=0.8, bw='silverman')
sns.stripplot(data=images_data, color='black', size=3, alpha=0.3)
ax.set_ylabel('Images per Chart')
ax.set_title('Distribution of Images per Chart')
# ax.set_yscale('log')
ax.set_ylim(0, 1000)

# Packages per chart (similar modifications for other plots)
fig, ax = plt.subplots(figsize=(6, 6))
sns.violinplot(data=packages_data, ax=ax, inner='quartile', saturation=0.8, bw='silverman')
sns.stripplot(data=packages_data, color='black', size=3, alpha=0.3)
ax.set_ylabel('Packages per Chart')
ax.set_title('Distribution of Packages per Chart')
# ax.set_yscale('log')
# Show the plots
ax.set_ylim(0, 1000)

plt.show()
