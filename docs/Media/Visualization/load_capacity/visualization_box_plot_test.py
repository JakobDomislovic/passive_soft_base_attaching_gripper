import pandas as pd
import matplotlib.pyplot as plt
import scienceplots

plt.style.use(["science", "ieee"])
plt.rcParams["text.usetex"] = False

CSV_FILE = "test.csv"
ANGLE_TO_PLOT = 0

METHOD_ORDER = ["xy", "z", "yaw", "roll_pitch"]
SURFACE_ORDER = ["metal", "wood", "plexi"]

SURFACE_COLORS = {
    "metal": "#7f7f7f",
    "wood": "#c68642",
    "plexi": "#5dade2",
}

FIGSIZE_IN = (3.25, 2.0)

ylabel_map = {
    "xy": "Force [N]",
    "z": "Force [N]",
    "yaw": "Torque [Nm]",
    "roll_pitch": "Torque [Nm]",
}

# read csv
df = pd.read_csv(CSV_FILE)
df.columns = [c.strip() for c in df.columns]

# numeric conversion
numeric_cols = ["angle", "n", "mean", "std", "median", "q1", "q3", "min", "max", "iqr"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ONLY peak_signal
df = df[(df["angle"] == ANGLE_TO_PLOT) & (df["variable"] == "peak_signal")].copy()

for method in METHOD_ORDER:
    df_method = df[df["method"] == method].copy()
    if df_method.empty:
        continue

    # if duplicates exist for same surface, keep first
    df_method = df_method.drop_duplicates(subset=["surface"], keep="first")

    surfaces_used = [s for s in SURFACE_ORDER if s in df_method["surface"].unique()]

    fig, ax = plt.subplots(figsize=FIGSIZE_IN, constrained_layout=True)

    positions = []
    stats = []
    colors = []

    for j, surface in enumerate(surfaces_used):
        row = df_method[df_method["surface"] == surface]
        if row.empty:
            continue

        row = row.iloc[0]

        positions.append(j)
        stats.append({
            "whislo": row["min"],
            "q1": row["q1"],
            "med": row["median"],
            "q3": row["q3"],
            "whishi": row["max"],
            "fliers": []
        })
        colors.append(SURFACE_COLORS.get(surface, "lightgray"))

    bplot = ax.bxp(
        stats,
        positions=positions,
        widths=0.5,
        showfliers=False,
        patch_artist=True,
        manage_ticks=False
    )

    for patch, color in zip(bplot["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.9)
        patch.set_linewidth(0.8)

    for whisker in bplot["whiskers"]:
        whisker.set_linewidth(0.8)

    for cap in bplot["caps"]:
        cap.set_linewidth(0.8)

    for median in bplot["medians"]:
        median.set_color("black")
        median.set_linewidth(1.0)

    ax.set_xticks(range(len(surfaces_used)))
    ax.set_xticklabels(surfaces_used)
    ax.set_xlabel("Surface")
    ax.set_ylabel(ylabel_map[method])
    ax.set_title(method.replace("_", r"\_"))
    ax.grid(True, axis="y", alpha=0.3)

    plt.show()
    plt.close(fig)