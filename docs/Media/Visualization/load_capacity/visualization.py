import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import scienceplots

plt.style.use(["science", "ieee"])
plt.rcParams["text.usetex"] = False

CSV_FILE = "gripper_break_results_summary.csv"

METHOD_ORDER = ["xy", "z", "yaw", "roll_pitch"]
SURFACE_ORDER = ["metal", "wood", "plexi"]

SURFACE_COLORS = {
    "metal": "#7f7f7f",
    "wood": "#c68642",
    "plexi": "#5dade2",
}

FIGSIZE_IN = (3.25, 1.8)

ylabel_map = {
    "xy": r"Force [N]",
    "z": r"Force [N]",
    "yaw": r"Torque [Nm]",
    "roll_pitch": r"Torque [Nm]",
}

# read csv
df = pd.read_csv(CSV_FILE)
df.columns = [c.strip() for c in df.columns]

# numeric conversion
numeric_cols = ["angle", "n", "mean", "std", "median", "q1", "q3", "min", "max", "iqr"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# only peak_signal
df = df[df["variable"] == "peak_signal"].copy()

# drop rows with missing key values
df = df.dropna(subset=["method", "surface", "angle", "median", "q1", "q3", "min", "max"])

for method in METHOD_ORDER:
    df_method = df[df["method"] == method].copy()
    if df_method.empty:
        continue

    df_method = df_method.drop_duplicates(subset=["angle", "surface"], keep="first")

    angles_used = sorted(df_method["angle"].dropna().unique())
    surfaces_used = [s for s in SURFACE_ORDER if s in df_method["surface"].unique()]

    if len(angles_used) == 0 or len(surfaces_used) == 0:
        continue

    fig, ax = plt.subplots(figsize=FIGSIZE_IN, constrained_layout=True)

    x_centers = list(range(len(angles_used)))

    n_surfaces = len(surfaces_used)
    group_width = 0.8
    box_width = 0.22

    legend_handles = []

    for s_idx, surface in enumerate(surfaces_used):
        color = SURFACE_COLORS.get(surface, "lightgray")
        stats = []
        positions = []

        offset = (s_idx - (n_surfaces - 1) / 2.0) * (group_width / max(n_surfaces, 1))

        for i, angle in enumerate(angles_used):
            row = df_method[
                (df_method["surface"] == surface) &
                (df_method["angle"] == angle)
            ]

            if row.empty:
                continue

            row = row.iloc[0]
            pos = x_centers[i] + offset

            stats.append({
                "whislo": row["min"],
                "q1": row["q1"],
                "med": row["median"],
                "q3": row["q3"],
                "whishi": row["max"],
                "fliers": [],
            })
            positions.append(pos)

        if not stats:
            continue

        bplot = ax.bxp(
            stats,
            positions=positions,
            widths=box_width,
            showfliers=False,
            patch_artist=True,
            manage_ticks=False
        )

        for patch in bplot["boxes"]:
            patch.set_facecolor(color)
            patch.set_alpha(0.85)
            patch.set_linewidth(0.8)

        for whisker in bplot["whiskers"]:
            whisker.set_linewidth(0.8)

        for cap in bplot["caps"]:
            cap.set_linewidth(0.8)

        for median in bplot["medians"]:
            median.set_color("black")
            median.set_linewidth(1.0)

        legend_handles.append(
            Patch(facecolor=color, edgecolor="black", label=surface, alpha=0.85)
        )

    ax.set_xticks(x_centers)
    ax.set_xticklabels([str(int(a)) if float(a).is_integer() else str(a) for a in angles_used])
    ax.set_xlabel("Angle [°]")
    ax.set_ylabel(ylabel_map.get(method, "Value"))
    ax.set_title(method.replace("_", r"\_"))

    ax.grid(True, axis="y", alpha=0.35, linewidth=0.6)
    ax.grid(True, axis="x", alpha=0.15, linewidth=0.5)

    if legend_handles:
        ax.legend(
            handles=legend_handles,
            title="Surface",
            loc="upper right",
            frameon=True,
            fontsize=6,
            title_fontsize=6
        )

    plt.show()
    plt.close(fig)