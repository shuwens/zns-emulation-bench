#!/usr/bin/env python3
"""
Enhanced IOPS performance visualization with multiple plot types
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

# Data
ssd_types = ["SK Hynix", "Samsung", "ZNS"]
append_iops = [169702.00, 173172, 297746.5]
read_iops = [437204, 140949, 43289]

# Create figure with subplots
fig = plt.figure(figsize=(15, 10))

# 1. Grouped Bar Chart
ax1 = plt.subplot(2, 2, 1)
x = np.arange(len(ssd_types))
width = 0.35

rects1 = ax1.bar(
    x - width / 2, append_iops, width, label="Append", color="#2E86AB", alpha=0.8
)
rects2 = ax1.bar(
    x + width / 2, read_iops, width, label="Read", color="#A23B72", alpha=0.8
)

# Add value labels
for rect in rects1:
    height = rect.get_height()
    ax1.annotate(
        f"{height:,.0f}",
        xy=(rect.get_x() + rect.get_width() / 2, height),
        xytext=(0, 3),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=8,
    )

for rect in rects2:
    height = rect.get_height()
    ax1.annotate(
        f"{height:,.0f}",
        xy=(rect.get_x() + rect.get_width() / 2, height),
        xytext=(0, 3),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=8,
    )

ax1.set_xlabel("SSD Type")
ax1.set_ylabel("IOPS")
ax1.set_title("IOPS Comparison: Grouped Bar Chart")
ax1.set_xticks(x)
ax1.set_xticklabels(ssd_types)
ax1.legend()
ax1.grid(True, axis="y", alpha=0.3)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:,.0f}"))

# 2. Stacked Bar Chart (showing total IOPS)
ax2 = plt.subplot(2, 2, 2)
total_iops = [a + r for a, r in zip(append_iops, read_iops)]
p1 = ax2.bar(ssd_types, append_iops, color="#2E86AB", alpha=0.8, label="Append")
p2 = ax2.bar(
    ssd_types, read_iops, bottom=append_iops, color="#A23B72", alpha=0.8, label="Read"
)

# Add total labels on top
for i, (ssd, total) in enumerate(zip(ssd_types, total_iops)):
    ax2.text(
        i, total + 5000, f"Total: {total:,.0f}", ha="center", va="bottom", fontsize=9
    )

ax2.set_ylabel("IOPS")
ax2.set_title("Total IOPS: Stacked Bar Chart")
ax2.legend()
ax2.grid(True, axis="y", alpha=0.3)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:,.0f}"))

# 3. Horizontal Bar Chart (for better label visibility)
ax3 = plt.subplot(2, 2, 3)
y_pos = np.arange(len(ssd_types))
ax3.barh(y_pos - 0.2, append_iops, 0.4, label="Append", color="#2E86AB", alpha=0.8)
ax3.barh(y_pos + 0.2, read_iops, 0.4, label="Read", color="#A23B72", alpha=0.8)

# Add value labels
for i, (a, r) in enumerate(zip(append_iops, read_iops)):
    ax3.text(a + 5000, i - 0.2, f"{a:,.0f}", va="center", fontsize=8)
    ax3.text(r + 5000, i + 0.2, f"{r:,.0f}", va="center", fontsize=8)

ax3.set_yticks(y_pos)
ax3.set_yticklabels(ssd_types)
ax3.set_xlabel("IOPS")
ax3.set_title("IOPS Comparison: Horizontal Bars")
ax3.legend()
ax3.grid(True, axis="x", alpha=0.3)
ax3.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:,.0f}"))

# 4. Performance Ratio Plot
ax4 = plt.subplot(2, 2, 4)
ratios = [r / a for r, a in zip(read_iops, append_iops)]
colors = ["#2E86AB", "#F18F01", "#A23B72"]
bars = ax4.bar(ssd_types, ratios, color=colors, alpha=0.8)

# Add ratio values on bars
for bar, ratio in zip(bars, ratios):
    height = bar.get_height()
    ax4.text(
        bar.get_x() + bar.get_width() / 2.0,
        height + 0.05,
        f"{ratio:.2f}x",
        ha="center",
        va="bottom",
        fontsize=10,
    )

ax4.set_ylabel("Read/Append Ratio")
ax4.set_title("Read vs Append Performance Ratio")
ax4.axhline(y=1, color="gray", linestyle="--", alpha=0.5)
ax4.set_ylim(0, max(ratios) * 1.2)
ax4.grid(True, axis="y", alpha=0.3)

# Add a text annotation
ax4.text(
    0.5,
    0.95,
    "Values > 1 indicate read is faster than append",
    transform=ax4.transAxes,
    ha="center",
    va="top",
    fontsize=9,
    bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
)

# Overall title
fig.suptitle(
    "SSD Performance Analysis: Append vs Read IOPS", fontsize=16, fontweight="bold"
)
plt.tight_layout()

# Save the comprehensive plot
plt.savefig("ssd_iops_analysis_comprehensive.png", dpi=300, bbox_inches="tight")
plt.savefig("ssd_iops_analysis_comprehensive.pdf", bbox_inches="tight")

# Show the plot
plt.show()

# Create a simple comparison table plot
fig2, ax = plt.subplots(figsize=(10, 4))
ax.axis("tight")
ax.axis("off")

# Prepare data for table
table_data = []
table_data.append(
    ["SSD Type", "Append IOPS", "Read IOPS", "Total IOPS", "Read/Append Ratio"]
)
for i, ssd in enumerate(ssd_types):
    total = append_iops[i] + read_iops[i]
    ratio = read_iops[i] / append_iops[i]
    table_data.append(
        [
            ssd,
            f"{append_iops[i]:,.0f}",
            f"{read_iops[i]:,.0f}",
            f"{total:,.0f}",
            f"{ratio:.2f}x",
        ]
    )

# Create table
table = ax.table(cellText=table_data, cellLoc="center", loc="center")
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1.2, 2)

# Style the header row
for i in range(5):
    table[(0, i)].set_facecolor("#4472C4")
    table[(0, i)].set_text_props(weight="bold", color="white")

# Alternate row colors
for i in range(1, len(table_data)):
    for j in range(5):
        if i % 2 == 0:
            table[(i, j)].set_facecolor("#E7E6E6")

plt.title("SSD Performance Summary Table", fontsize=14, fontweight="bold", pad=20)
plt.savefig("ssd_iops_table.png", dpi=300, bbox_inches="tight")
plt.show()

# Print insights
print("\nKey Insights:")
print("=" * 50)
print(f"1. Best Append Performance: ZNS ({append_iops[2]:,.0f} IOPS)")
print(f"2. Best Read Performance: SK Hynix ({read_iops[0]:,.0f} IOPS)")
print(
    f"3. Most Balanced: Samsung (Read/Append ratio: {read_iops[1]/append_iops[1]:.2f}x)"
)
print(f"4. ZNS shows {append_iops[2]/append_iops[0]:.1f}x better append than SK Hynix")
print(f"5. SK Hynix shows {read_iops[0]/read_iops[2]:.1f}x better read than ZNS")
print("=" * 50)
