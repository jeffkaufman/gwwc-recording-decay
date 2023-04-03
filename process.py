#!/usr/bin/env python3

import json
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# cohort year -> pledge year -> fraction
reporting = {}
with open("gwwc-reporting-fraction-by-cohort-and-year.tsv") as inf:
    for line in inf:
        if line.startswith("Cohort"): continue
        
        cols = line.replace("\n", "").split("\t")
        cohort_year, *pledge_years = cols
        reporting[cohort_year] = [float(x) for x in pledge_years if x]

# cohort year -> size
cohort_sizes = Counter()
with open("membership-dates.json") as inf:
    for month_year, count in json.load(inf).items():
        month_year = {
            "June 1990": "December 2021",
            "December 2008": "May 2022",
            "December 2004": "Aug 2022",
            "January 1983": "Jan 2023",
        }.get(month_year, month_year)
        
        if not month_year: continue
        
        month, year = month_year.split()
        cohort_sizes[year] += count

biggest_cohort_size = max(cohort_sizes.values())

cmap = plt.colormaps["Blues"]

fig, ax = plt.subplots(constrained_layout=True)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
for cohort in reporting:
    ys = [y*100 for y in reporting[cohort]]
    xs = list(range(len(ys)))

    ax.plot(xs, ys, label=cohort,
            color=cmap(cohort_sizes[cohort] / biggest_cohort_size))
ax.legend()
ax.set_ylabel("fraction of people in cohort reporting any donations")
ax.set_xlabel("years since pledging")
ax.set_title("GWWC Reporting Fraction By Cohort Over Time")
fig.savefig("gwwc-recording-by-cohort-big.png", dpi=180)
plt.clf()


# cohort year -> pledge year -> y/y decay
full_decay = {}
for cohort in reporting:
    if len(reporting[cohort]) < 2: continue

    full_decay[cohort] = [
        1-y2/y1
        for (y1, y2)
        in zip(reporting[cohort], reporting[cohort][1:])]

fig, ax = plt.subplots(constrained_layout=True)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
for cohort in full_decay:
    ys = [y*100 for y in full_decay[cohort]]
    xs = list(range(len(ys)))

    ax.plot(xs, ys, label=cohort,
            color=cmap(cohort_sizes[cohort] / biggest_cohort_size))

ys = [0] * len(full_decay["2009"])
xs = list(range(len(ys)))
weights = [0] * len(ys)
xs = list(range(len(ys)))
for cohort in full_decay:
    for pledge_year, decay in enumerate(full_decay[cohort]):
        ys[pledge_year] += decay * cohort_sizes[cohort]
        weights[pledge_year] += cohort_sizes[cohort]

for pledge_year, decay in enumerate(ys):
    ys[pledge_year] = decay / weights[pledge_year] * 100
ax.plot(xs, ys, label="weighted\naverage", color="red")
for i in range(len(xs)-1):
    xs_segment = [xs[i], xs[i+1]]
    ys_segment = [ys[i], ys[i+1]]
    weight = weights[i]
    ax.plot(xs_segment, ys_segment,
            color=plt.colormaps["Reds"](weight / max(weights)))
    
ax.legend()
ax.set_ylim(ymax=30, ymin=0)
ax.set_ylabel("year over year decrease in donation reporting")
ax.set_xlabel("years since pledging")
ax.set_title("GWWC Reporting Fraction Decrease By Cohort Over Time")
fig.savefig("gwwc-recording-decay-by-cohort-big.png", dpi=180)
plt.clf()

weight = 0
weighted_decay_after_5y = 0
for cohort in full_decay:
    for pledge_year, decay in enumerate(full_decay[cohort]):
        if pledge_year < 5: continue
        weighted_decay_after_5y += decay * cohort_sizes[cohort]
        weight +=cohort_sizes[cohort]

print ("%.1f%%" % (weighted_decay_after_5y/weight * 100))
