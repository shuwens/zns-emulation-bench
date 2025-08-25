#!/usr/bin/env python3
"""
Create separate PDF files for each IOPS visualization
"""

import matplotlib.pyplot as plt
import numpy as np

# Data
ssd_types = ["SK Hynix", "Samsung", "ZNS"]
append_iops = [169702.00, 173172, 297746.5]
read_iops = [437204, 140949, 349782]

# Set consistent style
plt.style.use("default")
colors = {"append": "#2E86AB", "read": "#A23B72"}

# 1. Grouped Bar Chart
plt.figure(figsize=(10, 6))
x = np.arange(len(ssd_types))
width = 0.35

rects1 = plt.bar(
    x - width / 2, append_iops, width, label="Append", color=colors["append"], alpha=0.8
)
rects2 = plt.bar(
    x + width / 2, read_iops, width, label="Read", color=colors["read"], alpha=0.8
)

# Add value labels
for rect in rects1:
    height = rect.get_height()
    plt.annotate(
        f"{height:,.0f}",
        xy=(rect.get_x() + rect.get_width() / 2, height),
        xytext=(0, 3),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=10,
    )

for rect in rects2:
    height = rect.get_height()
    plt.annotate(
        f"{height:,.0f}",
        xy=(rect.get_x() + rect.get_width() / 2, height),
        xytext=(0, 3),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=10,
    )

plt.xlabel("SSD Type", fontsize=12, fontweight="bold")
plt.ylabel("IOPS", fontsize=12, fontweight="bold")
plt.title(
    "SSD Performance Comparison: Append vs Read Operations",
    fontsize=14,
    fontweight="bold",
)
plt.xticks(x, ssd_types)
plt.legend(fontsize=11)
plt.grid(True, axis="y", alpha=0.3, linestyle="--")
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:,.0f}"))
max_value = max(max(append_iops), max(read_iops))
plt.ylim(0, max_value * 1.15)
plt.tight_layout()
plt.savefig("1_grouped_bar_chart.pdf", bbox_inches="tight")
plt.savefig("1_grouped_bar_chart.png", dpi=300, bbox_inches="tight")
plt.close()

# 2. Stacked Bar Chart
plt.figure(figsize=(10, 6))
total_iops = [a + r for a, r in zip(append_iops, read_iops)]
p1 = plt.bar(ssd_types, append_iops, color=colors["append"], alpha=0.8, label="Append")
p2 = plt.bar(
    ssd_types,
    read_iops,
    bottom=append_iops,
    color=colors["read"],
    alpha=0.8,
    label="Read",
)

# Add total labels on top
for i, (ssd, total) in enumerate(zip(ssd_types, total_iops)):
    plt.text(
        i,
        total + 5000,
        f"Total: {total:,.0f}",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold",
    )

# Add segment labels
for i, (a, r) in enumerate(zip(append_iops, read_iops)):
    plt.text(
        i,
        a / 2,
        f"{a:,.0f}",
        ha="center",
        va="center",
        fontsize=9,
        color="white",
        fontweight="bold",
    )
    plt.text(
        i,
        a + r / 2,
        f"{r:,.0f}",
        ha="center",
        va="center",
        fontsize=9,
        color="white",
        fontweight="bold",
    )

plt.ylabel("IOPS", fontsize=12, fontweight="bold")
plt.title("Total IOPS Performance: Stacked View", fontsize=14, fontweight="bold")
plt.legend(fontsize=11)
plt.grid(True, axis="y", alpha=0.3, linestyle="--")
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:,.0f}"))
plt.tight_layout()
plt.savefig("2_stacked_bar_chart.pdf", bbox_inches="tight")
plt.savefig("2_stacked_bar_chart.png", dpi=300, bbox_inches="tight")
plt.close()

# 3. Horizontal Bar Chart
plt.figure(figsize=(10, 6))
y_pos = np.arange(len(ssd_types))
plt.barh(
    y_pos - 0.2, append_iops, 0.4, label="Append", color=colors["append"], alpha=0.8
)
plt.barh(y_pos + 0.2, read_iops, 0.4, label="Read", color=colors["read"], alpha=0.8)

# Add value labels
for i, (a, r) in enumerate(zip(append_iops, read_iops)):
    plt.text(a + 5000, i - 0.2, f"{a:,.0f}", va="center", fontsize=10)
    plt.text(r + 5000, i + 0.2, f"{r:,.0f}", va="center", fontsize=10)

plt.yticks(y_pos, ssd_types)
plt.xlabel("IOPS", fontsize=12, fontweight="bold")
plt.title("SSD Performance Comparison: Horizontal View", fontsize=14, fontweight="bold")
plt.legend(fontsize=11)
plt.grid(True, axis="x", alpha=0.3, linestyle="--")
plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:,.0f}"))
plt.tight_layout()
plt.savefig("3_horizontal_bar_chart.pdf", bbox_inches="tight")
plt.savefig("3_horizontal_bar_chart.png", dpi=300, bbox_inches="tight")
plt.close()

# 4. Performance Ratio Plot
plt.figure(figsize=(10, 6))
ratios = [r / a for r, a in zip(read_iops, append_iops)]
bar_colors = ["#2E86AB", "#F18F01", "#A23B72"]
bars = plt.bar(
    ssd_types, ratios, color=bar_colors, alpha=0.8, edgecolor="black", linewidth=1
)

# Add ratio values on bars
for bar, ratio in zip(bars, ratios):
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2.0,
        height + 0.05,
        f"{ratio:.2f}x",
        ha="center",
        va="bottom",
        fontsize=12,
        fontweight="bold",
    )

plt.ylabel("Read/Append Ratio", fontsize=12, fontweight="bold")
plt.title("Read vs Append Performance Ratio", fontsize=14, fontweight="bold")
plt.axhline(y=1, color="gray", linestyle="--", alpha=0.5, label="Equal Performance")
plt.ylim(0, max(ratios) * 1.2)
plt.grid(True, axis="y", alpha=0.3, linestyle="--")

# Add annotation
plt.text(
    0.5,
    0.95,
    "Values > 1: Read faster | Values < 1: Append faster",
    transform=plt.gca().transAxes,
    ha="center",
    va="top",
    fontsize=10,
    bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8),
)

plt.legend(fontsize=10)
plt.tight_layout()
plt.savefig("4_ratio_comparison.pdf", bbox_inches="tight")
plt.savefig("4_ratio_comparison.png", dpi=300, bbox_inches="tight")
plt.close()

# 5. Side-by-side comparison
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Append performance
ax1.bar(
    ssd_types,
    append_iops,
    color=colors["append"],
    alpha=0.8,
    edgecolor="black",
    linewidth=1,
)
for i, v in enumerate(append_iops):
    ax1.text(i, v + 3000, f"{v:,.0f}", ha="center", va="bottom", fontsize=10)
ax1.set_ylabel("IOPS", fontsize=12, fontweight="bold")
ax1.set_title("Append Performance", fontsize=13, fontweight="bold")
ax1.grid(True, axis="y", alpha=0.3, linestyle="--")
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:,.0f}"))
ax1.set_ylim(0, max(append_iops) * 1.15)

# Read performance
ax2.bar(
    ssd_types,
    read_iops,
    color=colors["read"],
    alpha=0.8,
    edgecolor="black",
    linewidth=1,
)
for i, v in enumerate(read_iops):
    ax2.text(i, v + 3000, f"{v:,.0f}", ha="center", va="bottom", fontsize=10)
ax2.set_ylabel("IOPS", fontsize=12, fontweight="bold")
ax2.set_title("Read Performance", fontsize=13, fontweight="bold")
ax2.grid(True, axis="y", alpha=0.3, linestyle="--")
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:,.0f}"))
ax2.set_ylim(0, max(read_iops) * 1.15)

fig.suptitle(
    "SSD Performance: Append vs Read (Separate Views)", fontsize=14, fontweight="bold"
)
plt.tight_layout()
plt.savefig("5_side_by_side_comparison.pdf", bbox_inches="tight")
plt.savefig("5_side_by_side_comparison.png", dpi=300, bbox_inches="tight")
plt.close()

# 6. Summary Table
fig, ax = plt.subplots(figsize=(10, 4))
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
plt.savefig("6_summary_table.pdf", bbox_inches="tight")
plt.savefig("6_summary_table.png", dpi=300, bbox_inches="tight")
plt.close()

# Print summary
print("Generated PDF files:")
print("-" * 50)
print("1. 1_grouped_bar_chart.pdf      - Main comparison chart")
print("2. 2_stacked_bar_chart.pdf      - Shows total IOPS")
print("3. 3_horizontal_bar_chart.pdf   - Horizontal layout")
print("4. 4_ratio_comparison.pdf       - Read/Append ratios")
print("5. 5_side_by_side_comparison.pdf - Separate append/read views")
print("6. 6_summary_table.pdf          - Data summary table")
print("-" * 50)
print("\nAll files also saved as PNG format for easy viewing.")

# Generate a combined view for reference (optional)
fig = plt.figure(figsize=(16, 10))

# Plot 1: Grouped bars
ax1 = plt.subplot(2, 3, 1)
x = np.arange(len(ssd_types))
width = 0.35
ax1.bar(
    x - width / 2, append_iops, width, label="Append", color=colors["append"], alpha=0.8
)
ax1.bar(x + width / 2, read_iops, width, label="Read", color=colors["read"], alpha=0.8)
ax1.set_title("Grouped Bars")
ax1.set_xticks(x)
ax1.set_xticklabels(ssd_types, rotation=45)
ax1.legend()
ax1.grid(True, axis="y", alpha=0.3)

# Plot 2: Stacked bars
ax2 = plt.subplot(2, 3, 2)
ax2.bar(ssd_types, append_iops, color=colors["append"], alpha=0.8, label="Append")
ax2.bar(
    ssd_types,
    read_iops,
    bottom=append_iops,
    color=colors["read"],
    alpha=0.8,
    label="Read",
)
ax2.set_title("Stacked Bars")
ax2.legend()
ax2.grid(True, axis="y", alpha=0.3)

# Plot 3: Ratios
ax3 = plt.subplot(2, 3, 3)
ax3.bar(ssd_types, ratios, color=bar_colors, alpha=0.8)
ax3.set_title("Read/Append Ratio")
ax3.axhline(y=1, color="gray", linestyle="--", alpha=0.5)
ax3.grid(True, axis="y", alpha=0.3)

# Plot 4: Append only
ax4 = plt.subplot(2, 3, 4)
ax4.bar(ssd_types, append_iops, color=colors["append"], alpha=0.8)
ax4.set_title("Append Performance")
ax4.grid(True, axis="y", alpha=0.3)

# Plot 5: Read only
ax5 = plt.subplot(2, 3, 5)
ax5.bar(ssd_types, read_iops, color=colors["read"], alpha=0.8)
ax5.set_title("Read Performance")
ax5.grid(True, axis="y", alpha=0.3)

# Plot 6: Horizontal bars
ax6 = plt.subplot(2, 3, 6)
y_pos = np.arange(len(ssd_types))
ax6.barh(
    y_pos - 0.2, append_iops, 0.4, label="Append", color=colors["append"], alpha=0.8
)
ax6.barh(y_pos + 0.2, read_iops, 0.4, label="Read", color=colors["read"], alpha=0.8)
ax6.set_yticks(y_pos)
ax6.set_yticklabels(ssd_types)
ax6.set_title("Horizontal Bars")
ax6.legend()
ax6.grid(True, axis="x", alpha=0.3)

plt.suptitle("All Visualizations - Overview", fontsize=16, fontweight="bold")
plt.tight_layout()
plt.savefig("0_all_charts_overview.pdf", bbox_inches="tight")
plt.savefig("0_all_charts_overview.png", dpi=300, bbox_inches="tight")
plt.close()

print("\nBonus: 0_all_charts_overview.pdf - All charts in one view")
