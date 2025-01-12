import re
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm 
import seaborn as sns
import statistics 

with open('close_wait_lat_results.txt') as f:
    lines = f.readlines()
    pids = [str(re.findall(r'\[.*?\]', line)) for line in lines]
    values = [int(line.split(' ')[1]) for line in lines]


# Gaussian distr.
# mean = statistics.mean(values)
# sd = statistics.stdev(values)
# # Generate data for the x axis
# x = np.linspace(mean - 3*sd, mean + 3*sd, 100)

# # Generate data for the y axis
# y = norm.pdf(x, mean, sd)
# # Create the plot
# plt.plot(x, y)
# # Show the plot
# plt.show()
# plt.hist(values,density=True)      #use this to draw histogram of your data
# plt.savefig('close_wait4.png')

# Histogram
# matplotlib histogram
# plt.hist(values, color = 'blue', edgecolor = 'black',
#          bins = 271)

# Density Plot and Histogram of all arrival delays, bi-modal distr.
sns.distplot(values, hist=True, kde=True, 
             bins=271, color = 'darkblue', 
             hist_kws={'edgecolor':'black'},
             kde_kws={'linewidth': 2})

# Add labels
plt.title('Histogram of Query Latency')
plt.ylabel('Count')
plt.xlabel('Latency (us)')

plt.savefig('close_wait4_hist.png')