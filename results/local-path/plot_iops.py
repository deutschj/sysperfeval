import re
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm 
import seaborn as sns
import statistics 

with open('iops.txt') as f:
    lines = f.readlines()
    # pids = [str(re.findall(r'\[.*?\]', line)) for line in lines]
    values = [int(line.split(':')[1].strip()) for line in lines if line.startswith("Parent")]

val2 = [x for x in values if x != 0]
print(values)

sns.histplot(val2, kde=True, 
             bins=160, color = 'darkblue', 
             line_kws={'linewidth':'2'})

# Add labels
plt.title('Histogram of Query Latency')
plt.ylabel('Count')
plt.xlabel('Latency (us)')

plt.savefig('iops_unequal0.png')