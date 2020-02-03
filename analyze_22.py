"""
Analiza zależności od szumu
"""
import numpy as np
from tabulate import tabulate
import matplotlib.pyplot as plt
from scipy.signal import medfilt
import pandas as pd
from math import pi
from scipy.ndimage.filters import gaussian_filter1d

from matplotlib import rcParams

# Set plot params
rcParams["font.family"] = "monospace"
colors = [(0, 0, 0), (0, 0, 0.9), (0.9, 0, 0), (0, 0, 0), (0, 0, 0.9), (0.9, 0, 0)]
ls = ["--", "--", "--", "-", "-", "-"]
lw = [1, 1, 1, 1, 1, 1]

methods = ["NON-KNORAU2", "RUS-KNORAU2", "CNN-KNORAU2", "NON-KNORAE2", "RUS-KNORAE2", "CNN-KNORAE2"]
label_noises = [
    "0.01",
    "0.03",
    "0.05"
]
ln = [a.replace('.','-') for a in label_noises]
distributions = ["0.05", "0.10"]
dist = [a.replace('.','-') for a in distributions]
drifts = ["gradual", "incremental", "sudden"]
metrics = ["Balanced accuracy", "G-mean", "f1 score", "precision", "recall", "specificity"]
clfs = ["GNB", "HT"]

scores = np.load("scores_22.npy")

# print(scores.shape)

def plot_runs(
    clfs, metrics, selected_scores, methods, mean_scores, dependency, what
):
    fig = plt.figure(figsize=(4, 4))
    ax = plt.axes()
    for z, (value, label, mean) in enumerate(
        zip(selected_scores, methods, mean_scores)
    ):
        label += "\n{0:.3f}".format(mean)
        val = gaussian_filter1d(value, sigma=3, mode="nearest")

        # plt.plot(value, label=label, c=colors[z], ls=ls[z])

        plt.plot(val, label=label, c=colors[z], ls=ls[z], lw=lw[z])

    # box = ax.get_position()
    # ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
    ax.legend(
        loc=8,
        # bbox_to_anchor=(0.5, -0.1),
        fancybox=False,
        shadow=True,
        ncol=3,
        fontsize=6,
        frameon=False,
    )

    plt.grid(ls=":", c=(0.7, 0.7, 0.7))
    plt.xlim(0, 200)
    axx = plt.gca()
    axx.spines["right"].set_visible(False)
    axx.spines["top"].set_visible(False)

    plt.title(
        "%s %s\n%s" % (clfs[j], dependency[k][:], metrics[i]),
        fontfamily="serif",
        y=1.04,
        fontsize=8,
    )
    plt.ylim(0.0, 1.0)
    plt.xticks(fontfamily="serif")
    plt.yticks(fontfamily="serif")
    plt.ylabel("score", fontfamily="serif", fontsize=8)
    plt.xlabel("chunks", fontfamily="serif", fontsize=8)
    plt.tight_layout()
    plt.savefig("plots/experiment22/runs/%s/22_%s_%s_%s.eps" % (what, clfs[j], metrics[i], dependency[k]), bbox_inches='tight', dpi=250)
    plt.close()

def plot_radars(
    methods, metrics, table, classifier_name, parameter_name, what
):
    """
    Strach.
    """
    columns = ["group"] + methods
    df = pd.DataFrame(columns=columns)
    for i in range(len(table)):
        df.loc[i] = table[i]
    df = pd.DataFrame()
    df["group"] = methods
    for i in range(len(metrics)):
        df[table[i][0]] = table[i][1:]
    groups = list(df)[1:]
    N = len(groups)

    # nie ma nic wspolnego z plotem, zapisywanie do txt texa
    # print(df.to_latex(index=False), file=open("tables/%s.tex" % (filename), "w"))

    # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    # Initialise the spider plot
    ax = plt.subplot(111, polar=True)

    # If you want the first axis to be on top:
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)

    # No shitty border
    ax.spines["polar"].set_visible(False)

    # Draw one axe per variable + add labels labels yet
    plt.xticks(angles, metrics)

    # Adding plots
    for i in range(len(methods)):
        values = df.loc[i].drop("group").values.flatten().tolist()
        values += values[:1]
        values = [float(i) for i in values]
        ax.plot(
            angles, values, label=df.iloc[i, 0], c=colors[i], ls=ls[i], lw=lw[i],
        )

    # Add legend
    plt.legend(
        loc="lower center",
        ncol=3,
        columnspacing=1,
        frameon=False,
        bbox_to_anchor=(0.5, -0.3),
        fontsize=6,
    )

    # Add a grid
    plt.grid(ls=":", c=(0.7, 0.7, 0.7))

    # Add a title
    plt.title("%s %s" % (clfs[j], parameter_name), size=8, y=1.08, fontfamily="serif")
    plt.tight_layout()

    # Draw labels
    a = np.linspace(0, 1, 6)
    plt.yticks(a[1:], ["%.1f" % f for f in a[1:]], fontsize=6, rotation=90)
    plt.ylim(0.0, 1.0)
    plt.gcf().set_size_inches(4, 4)
    plt.gcf().canvas.draw()
    angles = np.rad2deg(angles)

    ax.set_rlabel_position((angles[0] + angles[1]) / 2)

    har = [(a >= 90) * (a <= 270) for a in angles]

    for z, (label, angle) in enumerate(zip(ax.get_xticklabels(), angles)):
        x, y = label.get_position()
        print(label, angle)
        lab = ax.text(
            x, y, label.get_text(), transform=label.get_transform(), fontsize=6,
        )
        lab.set_rotation(angle)

        if har[z]:
            lab.set_rotation(180 - angle)
        else:
            lab.set_rotation(-angle)
        lab.set_verticalalignment("center")
        lab.set_horizontalalignment("center")
        lab.set_rotation_mode("anchor")

    for z, (label, angle) in enumerate(zip(ax.get_yticklabels(), a)):
        x, y = label.get_position()
        print(label, angle)
        lab = ax.text(
            x,
            y,
            label.get_text(),
            transform=label.get_transform(),
            fontsize=4,
            c=(0.7, 0.7, 0.7),
        )
        lab.set_rotation(-(angles[0] + angles[1]) / 2)

        lab.set_verticalalignment("bottom")
        lab.set_horizontalalignment("center")
        lab.set_rotation_mode("anchor")

    ax.set_xticklabels([])
    ax.set_yticklabels([])

    plt.savefig("plots/experiment22/radars/%s/22_%s_%s.eps" % (what, classifier_name, parameter_name), bbox_inches='tight', dpi=250)
    plt.close()

for j, clf in enumerate(clfs):
    print("\n###\n### %s\n###\n" % (clf))
    for i, metric in enumerate(metrics):
        print("\n---\n--- %s\n---\n" % (metric))
        # KLASYFIKATOR, CHUJ, DIST, LABELNOISE, METHOD, CHUNK, METRYKA
        sub_scores = scores[j, :, :, :, :, :, i]
        # print(sub_scores.shape)

        # LABNO
        # CHUJ, DIST, LABELNOISE, METHOD, CHUNK
        reduced_scores = np.mean(sub_scores, axis=0)
        reduced_scores = np.mean(reduced_scores, axis=0)
        table = []
        header = ["LN"] + methods
        for k, label_noise in enumerate(ln):
            # LABELNOISE, METHOD, CHUNK
            selected_scores = reduced_scores[k]
            mean_scores = np.mean(selected_scores, axis=1)
            table.append([label_noise] + ["%.3f" % score for score in mean_scores])

            plot_runs(clfs, metrics, selected_scores, methods, mean_scores, ln, "label_noise")

        print(tabulate(table, headers=header))
        print("")

        # DISTRIBUTION
        # CHUJ, DIST, LABELNOISE, METHOD, CHUNK
        reduced_scores = np.mean(sub_scores, axis=0)
        reduced_scores = np.mean(reduced_scores, axis=1)
        table = []
        header = ["Dist"] + methods
        for k, distribution in enumerate(dist):
            # LABELNOISE, METHOD, CHUNK
            selected_scores = reduced_scores[k]
            mean_scores = np.mean(selected_scores, axis=1)
            table.append([distribution] + ["%.3f" % score for score in mean_scores])

            plot_runs(clfs, metrics, selected_scores, methods, mean_scores, dist, "distributions")

        # print(table)
        print(tabulate(table, headers=header))
        print("")

        # Drift
        # CHUJ, DIST, LABELNOISE, METHOD, CHUNK
        reduced_scores = np.mean(sub_scores, axis=1)
        reduced_scores = np.mean(reduced_scores, axis=1)
        table = []
        header = ["Drift"] + methods
        for k, drift in enumerate(drifts):
            # LABELNOISE, METHOD, CHUNK
            selected_scores = reduced_scores[k]
            mean_scores = np.mean(selected_scores, axis=1)
            table.append([drift] + ["%.3f" % score for score in mean_scores])

            plot_runs(clfs, metrics, selected_scores, methods, mean_scores, drifts, "drift_type")

        # print(table)
        print(tabulate(table, headers=header))
        print("")

# RADAR DIAGRAMS

for j, clf in enumerate(clfs):
    print("\n###\n### %s\n###\n" % (clf))
    for i, drift in enumerate(drifts):
        print("\n---\n--- %s\n---\n" % (drift))
        # KLASYFIKATOR, CHUJ, DIST, LABELNOISE, METHOD, CHUNK, METRYKA
        sub_scores = scores[j, i, :, :, :, :, :]

        # Metryka
        # DIST, LABELNOISE, METHOD, CHUNK, METRYKA
        reduced_scores = np.mean(sub_scores, axis=0)
        reduced_scores = np.mean(reduced_scores, axis=0)
        table = []
        header = ["Metric"] + methods
        for k, metric in enumerate(metrics):
            # METHOD, CHUNK, Metryka
            selected_scores = reduced_scores[:,:,k]
            mean_scores = np.mean(selected_scores, axis=1)
            table.append([metric] + ["%.3f" % score for score in mean_scores])

        # print(table)
        print(tabulate(table, headers=header))
        print("")

        plot_radars(methods, metrics, table, clf, drift, "drift_type")

    for i, distribution in enumerate(dist):
        print("\n---\n--- %s\n---\n" % (distribution))
        # KLASYFIKATOR, CHUJ, DIST, LABELNOISE, METHOD, CHUNK, METRYKA
        sub_scores = scores[j, :, i, :, :, :, :]

        # Metryka
        # CHUJ, LABELNOISE, METHOD, CHUNK, METRYKA
        reduced_scores = np.mean(sub_scores, axis=0)
        reduced_scores = np.mean(reduced_scores, axis=0)
        table = []
        header = ["Metric"] + methods
        for k, metric in enumerate(metrics):
            # METHOD, CHUNK, Metryka
            selected_scores = reduced_scores[:,:,k]
            mean_scores = np.mean(selected_scores, axis=1)
            table.append([metric] + ["%.3f" % score for score in mean_scores])

        # print(table)
        print(tabulate(table, headers=header))
        print("")

        plot_radars(methods, metrics, table, clf, distribution, "distributions")

    for i, label_noise in enumerate(ln):
        print("\n---\n--- %s\n---\n" % (label_noise))
        # KLASYFIKATOR, CHUJ, DIST, LABELNOISE, METHOD, CHUNK, METRYKA
        sub_scores = scores[j, :, :, i, :, :, :]

        # Metryka
        # CHUJ, LABELNOISE, METHOD, CHUNK, METRYKA
        reduced_scores = np.mean(sub_scores, axis=0)
        reduced_scores = np.mean(reduced_scores, axis=0)
        table = []
        header = ["Metric"] + methods
        for k, metric in enumerate(metrics):
            # METHOD, CHUNK, Metryka
            selected_scores = reduced_scores[:,:,k]
            mean_scores = np.mean(selected_scores, axis=1)
            table.append([metric] + ["%.3f" % score for score in mean_scores])

        # print(table)
        print(tabulate(table, headers=header))
        print("")

        plot_radars(methods, metrics, table, clf, label_noise, "label_noise")