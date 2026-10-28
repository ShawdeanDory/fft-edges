"""Reproduce the four paper figures from frozen arrays and CSV tables.

Run from the repository or from the standalone figure bundle. All labels use
the course template's SimSun / Times New Roman font pair. Analysis belongs in
the manuscript; the figures contain only labels, measurements and legends.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.text import Text
from matplotlib.ticker import FixedLocator, FormatStrFormatter
import numpy as np
from PIL import Image
from scipy.io import loadmat
from scipy.sparse import issparse


CM = 1 / 2.54
width_mm = 160.0
WIDTH_CM = width_mm / 10
DPI = 600
FONT_PT = 10.0
PALETTE = {
    "rgb_main": "#235789",
    "gray_phase": "#68747D",
    "sobel": "#8B80A8",
    "canny": "#C67B2B",
    "ideal_highpass": "#3F8D8A",
    "gaussian_highpass": "#A38D68",
}
METHODS = list(PALETTE)
METHOD_LABELS = ["RGB主方法", "灰度＋相位", "Sobel", "Canny", "理想高通", "高斯高通"]
CONTRASTS = [
    ("rgb_fft", "gray_fft", "无相位：加入颜色"),
    ("rgb_phase", "gray_phase", "有相位：加入颜色"),
    ("gray_phase", "gray_fft", "灰度：加入相位"),
    ("rgb_phase", "rgb_fft", "RGB：加入相位"),
    ("rgb_main", "rgb_phase", "增加弱连接门控"),
]
FIGURES = [
    ("fig01_rgb_spectra_responses_cn", 10.2),
    ("fig02_six_method_comparison_cn", 8.8),
    ("fig03_module_paired_changes_cn", 6.6),
    ("fig04_noise_robustness_cn", 8.1),
]


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def unique(rows: list[dict], **fields) -> dict:
    matches = [r for r in rows if all(r[k] == v for k, v in fields.items())]
    if len(matches) != 1:
        raise ValueError(f"Expected one record for {fields}; found {len(matches)}")
    return matches[0]


def setup_fonts(chinese: str | None, latin: str | None) -> dict:
    defaults = [(chinese, "C:/Windows/Fonts/simsun.ttc", "SimSun"),
                (latin, "C:/Windows/Fonts/times.ttf", "Times New Roman")]
    resolved = []
    for explicit, default, family in defaults:
        path = Path(explicit or default)
        if path.exists():
            font_manager.fontManager.addfont(str(path))
            actual = font_manager.FontProperties(fname=str(path)).get_name()
        elif explicit:
            raise FileNotFoundError(path)
        else:
            path = Path(font_manager.findfont(family, fallback_to_default=False))
            actual = family
        resolved.append((actual, path))
    # Per-glyph fallback: Latin and numerals use Times, Chinese uses SimSun.
    plt.rcParams.update({
        "font.family": [resolved[1][0], resolved[0][0]],
        "font.size": 10.0,
        "axes.labelsize": FONT_PT,
        "axes.titlesize": FONT_PT,
        "xtick.labelsize": FONT_PT,
        "ytick.labelsize": FONT_PT,
        "legend.fontsize": FONT_PT,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "axes.unicode_minus": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": "#6B7280",
        "axes.linewidth": 0.65,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        "text.color": "#20252B",
        "axes.labelcolor": "#20252B",
        "xtick.color": "#30363D",
        "ytick.color": "#30363D",
        "legend.frameon": False,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "mathtext.fontset": "stix",
    })
    return {"chinese": resolved[0][0], "latin": resolved[1][0],
            "source": "Course template: Chinese SimSun; Latin/numerals Times New Roman."}


def new_figure(height_cm: float):
    return plt.figure(figsize=(WIDTH_CM * CM, height_cm * CM))


def panel_title(ax, title: str):
    ax.set_title(title, pad=5, fontweight="normal", fontsize=FONT_PT)


def image_panel(ax, array, title: str, binary=False, color=False, vmax=None):
    # Antialiasing preserves the coverage of one-pixel edges when the full
    # image is reduced to the paper panel size; source masks stay unchanged.
    options = {"interpolation": "hanning", "aspect": "equal", "resample": True}
    if binary:
        options.update(cmap="gray_r", vmin=0, vmax=1)
    elif not color:
        options.update(cmap="gray", vmin=0, vmax=vmax)
    ax.imshow(array, **options)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    panel_title(ax, title)


def clean_axes(ax, grid_axis="x"):
    ax.set_axisbelow(True)
    ax.grid(axis=grid_axis, color="#E6E9ED", linewidth=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def finite_vector(values):
    a = np.asarray(values, dtype=float)
    if not np.all(np.isfinite(a)):
        raise ValueError("Nonfinite source values")
    return a


def save(fig, output: Path, stem: str, qa: dict):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    text_bounds = []
    # A fixed canvas preserves the template's 16 cm insertion width. A tight
    # crop would change the physical size (and hence the final text size).
    fw, fh = fig.bbox.width, fig.bbox.height
    for text in fig.findobj(Text):
        if not text.get_visible() or not text.get_text():
            continue
        bbox = text.get_window_extent(renderer)
        if bbox.width <= 0 or bbox.height <= 0:
            continue
        if bbox.x0 < -1 or bbox.y0 < -1 or bbox.x1 > fw + 1 or bbox.y1 > fh + 1:
            raise ValueError(f"Text outside the canvas in {stem}: {text.get_text()}")
        text_bounds.append({"text": text.get_text(), "sizePt": text.get_fontsize()})
    fig.savefig(output / f"{stem}.png", dpi=600, bbox_inches=None)
    fig.savefig(output / f"{stem}.pdf", dpi=600, bbox_inches=None)
    fig.savefig(output / f"{stem}.svg", dpi=600, bbox_inches=None)
    # Internal inspection only; omitted from the deliverable archive.
    preview_dir = output / "_qa"
    preview_dir.mkdir(exist_ok=True)
    fig.savefig(preview_dir / f"{stem}.png", dpi=300, bbox_inches=None)
    qa[stem] = {
        "widthCm": WIDTH_CM,
        "heightCm": round(float(fig.get_figheight()) / CM, 3),
        "dpi": DPI,
        "minimumTextPt": min(t["sizePt"] for t in text_bounds),
        "visibleText": [t["text"] for t in text_bounds],
        "outsideCanvasText": [],
        "exports": ["png", "pdf", "svg"],
    }
    plt.close(fig)


def figure1(inputs: Path, output: Path, qa: dict):
    z = loadmat(inputs / "bsds_2018.mat", simplify_cells=True)
    e = z["example"]
    spectra = np.asarray(e["logSpectra"])
    seed, link = np.asarray(e["seedResponse"]), np.asarray(e["linkResponse"])
    assert seed.shape == link.shape == z["masks"][0].shape
    assert np.all(np.isfinite(spectra)) and spectra.shape[2] == 3
    assert seed.min() >= 0 and link.min() >= 0 and seed.max() == link.max() == 1
    fig = new_figure(FIGURES[0][1])
    axes = fig.subplots(2, 3)
    fig.subplots_adjust(left=.025, right=.985, bottom=.025, top=.93,
                        wspace=.10, hspace=.25)
    titles = ["(a) R通道频谱", "(b) G通道频谱", "(c) B通道频谱",
              "(d) 强种子响应", "(e) 弱连接响应", "(f) 最终边缘"]
    for c in range(3):
        a = spectra[:, :, c]
        # The original figure also scales each channel by its own maximum.
        image_panel(axes[0, c], a, titles[c], vmax=float(a.max()))
    image_panel(axes[1, 0], seed, titles[3], vmax=1)
    image_panel(axes[1, 1], link, titles[4], vmax=1)
    image_panel(axes[1, 2], z["masks"][0], titles[5], binary=True)
    qa["imageIntegrity"] = {
        "imageIds": ["bsds_2018", "bsds_3063"],
        "selection": "Same fixed examples as the existing four manuscript figures.",
        "crop": False, "gammaOrPhotoContrastChange": False,
        "binaryMaskMorphologyChange": False,
        "displayResampling": "Hanning antialiasing only; no change to input pixel arrays.",
        "spectra": "Existing log-magnitude arrays; each channel's original per-panel maximum scaling retained.",
        "responseScale": [0, 1], "imageAspect": "native, equal",
    }
    save(fig, output, FIGURES[0][0], qa)


def figure2(inputs: Path, output: Path, qa: dict):
    z = loadmat(inputs / "bsds_3063.mat", simplify_cells=True)
    image = np.asarray(Image.open(inputs / "bsds_3063.jpg"))
    gt = loadmat(inputs / "bsds_3063_ground_truth.mat", simplify_cells=True)["groundTruth"]
    if isinstance(gt, dict):
        gt = [gt]
    union = np.logical_or.reduce([g["Boundaries"].toarray() if issparse(g["Boundaries"])
                                 else g["Boundaries"] for g in gt])
    assert image.shape[:2] == union.shape
    assert [r["method"] for r in z["rows"]] == METHODS
    fig = new_figure(FIGURES[1][1])
    axes = fig.subplots(2, 4)
    fig.subplots_adjust(left=.018, right=.985, bottom=.16, top=.915,
                        wspace=.10, hspace=1.18)
    arrays = [image, union, *list(z["masks"])]
    titles = ["(a) 原始图像", "(b) 人工边界并集", "(c) RGB主方法", "(d) 灰度＋相位",
              "(e) Sobel", "(f) Canny", "(g) 理想高通", "(h) 高斯高通"]
    measured = []
    for j, (ax, array, title) in enumerate(zip(axes.flat, arrays, titles)):
        image_panel(ax, array, title, binary=j != 0, color=j == 0)
        if j >= 2:
            r = z["rows"][j - 2]
            values = finite_vector([r["precision"], r["recall"], r["f1"]]) * 100
            label = f"P {values[0]:.1f}%  R {values[1]:.1f}%\nF1 {values[2]:.1f}%"
            ax.text(.5, -.12, label, transform=ax.transAxes, ha="center", va="top",
                    fontsize=FONT_PT, linespacing=1.2, color="#30363D")
            measured.append({"method": r["method"], "displayPercent": values.tolist()})
    qa["qualitativeExampleMeasurements"] = measured
    save(fig, output, FIGURES[1][0], qa)


def figure3(inputs: Path, output: Path, qa: dict):
    rows = read_csv(inputs / "ablation_paired_intervals.csv")
    assert len(rows) == 20
    fig = new_figure(FIGURES[2][1])
    axes = fig.subplots(1, 3, sharey=True)
    fig.subplots_adjust(left=.242, right=.982, top=.865, bottom=.245, wspace=.24)
    metrics = ["precision", "recall", "f1"]
    titles = ["(a) 查准率 P", "(b) 查全率 R", "(c) F1值"]
    bounds = [(-.25, 4.7), (-4.9, 1.05), (-.18, 1.4)]
    ticks = [[0, 2, 4], [-4, -2, 0], [0, .5, 1.0]]
    evidence = []
    for j, (ax, metric, title) in enumerate(zip(axes, metrics, titles)):
        ax.axvline(0, color="#8C949C", ls=(0, (3, 3)), lw=.8, zorder=1)
        for y, (method, comparator, label) in enumerate(CONTRASTS):
            r = unique(rows, method=method, comparator=comparator, metric=metric)
            assert float(r["correctedLevel"]) == .995
            lo, hi = ("low95", "high95") if metric == "recall" else ("correctedLow", "correctedHigh")
            delta, low, high = finite_vector([r["delta"], r[lo], r[hi]]) * 100
            assert low <= delta <= high
            ax.hlines(y, low, high, color=PALETTE["rgb_main"], lw=1.45, zorder=3)
            ax.plot(delta, y, "o", ms=4.4, color=PALETTE["rgb_main"], zorder=4)
            evidence.append({"method": method, "comparator": comparator, "metric": metric,
                             "deltaPercentagePoints": float(delta), "interval": [float(low), float(high)]})
        ax.set(yticks=np.arange(5), yticklabels=[c[2] for c in CONTRASTS],
               ylim=(4.45, -.45), xlim=bounds[j], xlabel="变化量 / 百分点")
        ax.xaxis.set_major_locator(FixedLocator(ticks[j]))
        if j == 2:
            ax.xaxis.set_major_formatter(FormatStrFormatter("%.1f"))
        panel_title(ax, title)
        clean_axes(ax)
        if j:
            ax.tick_params(axis="y", left=False)
        else:
            ax.tick_params(axis="y", length=0, pad=7)
        for e in evidence[-5:]:
            assert bounds[j][0] < e["interval"][0] <= e["interval"][1] < bounds[j][1]
    qa["ablationSourceRows"] = len(rows)
    qa["ablationDisplayedRows"] = 15
    qa["ablationMetricScope"] = "P/R/pooled F1, as in the existing manuscript figure; five macro-F1 rows remain in the source CSV."
    qa["ablationPlottedContrasts"] = evidence
    save(fig, output, FIGURES[2][0], qa)


def figure4(inputs: Path, output: Path, qa: dict):
    summaries = read_csv(inputs / "noise_summary.csv")
    pairs = read_csv(inputs / "noise_paired_intervals.csv")
    assert len(summaries) == 24
    fig = new_figure(FIGURES[3][1])
    axes = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.18, 1]})
    fig.subplots_adjust(left=.09, right=.982, top=.875, bottom=.315, wspace=.45)
    ax = axes[0]
    markers = ["o", "s", "D", "^", "v", "P"]
    lines = ["-", (0, (4, 2)), (0, (1, 2)), (0, (5, 2, 1, 2)), (0, (6, 2)), (0, (3, 1, 1, 1))]
    handles = []
    source_curves = []
    for method, label, marker, linestyle in zip(METHODS, METHOD_LABELS, markers, lines):
        selected = sorted([r for r in summaries if r["method"] == method], key=lambda r: float(r["noiseStd"]))
        assert len(selected) == 4 and all(int(r["images"]) == 10 for r in selected)
        x = finite_vector([r["noiseStd"] for r in selected])
        y = finite_vector([r["f1"] for r in selected]) * 100
        assert np.array_equal(x, [0, .02, .05, .10])
        handle, = ax.plot(x, y, marker=marker, linestyle=linestyle,
                          ms=5.0 if method == "rgb_main" else 3.7,
                          linewidth=1.7 if method == "rgb_main" else 1.15,
                          markerfacecolor=PALETTE[method] if method == "rgb_main" else "white",
                          markeredgewidth=.9, color=PALETTE[method], label=label,
                          zorder=6 if method == "gray_phase" else (5 if method == "rgb_main" else 4))
        handles.append(handle)
        if method == "rgb_main":
            low = finite_vector([r["f1Low95"] for r in selected]) * 100
            high = finite_vector([r["f1High95"] for r in selected]) * 100
            ax.fill_between(x, low, high, color=PALETTE[method], alpha=.09, lw=0, zorder=1)
        source_curves.append({"method": method, "noiseStd": x.tolist(), "f1Percent": y.tolist()})
    ax.set(xlabel="噪声标准差 σ", ylabel="F1 / %", xlim=(-.005, .105), ylim=(38.5, 73))
    ax.xaxis.set_major_locator(FixedLocator([0, .02, .05, .10]))
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.2f"))
    ax.yaxis.set_major_locator(FixedLocator([40, 50, 60, 70]))
    panel_title(ax, "(a) 六种方法的噪声曲线")
    clean_axes(ax, "both")
    ax = axes[1]
    ax.axvline(0, color="#8C949C", ls=(0, (3, 3)), lw=.8)
    paired_evidence = []
    for base, label, color, offset, marker in [
        ("gray_phase", "相对灰度", PALETTE["gray_phase"], -.105, "s"),
        ("canny", "相对Canny", PALETTE["canny"], .105, "o"),
    ]:
        for y, sigma in enumerate([.02, .05, .10]):
            found = [r for r in pairs if r["method"] == "rgb_main" and r["comparator"] == base
                     and r["metric"] == "f1" and np.isclose(float(r["noiseStd"]), sigma)]
            assert len(found) == 1
            r = found[0]
            delta, low, high = finite_vector([r["delta"], r["correctedLow"], r["correctedHigh"]]) * 100
            assert low <= delta <= high and np.isclose(float(r["correctedLevel"]), .9916666666666667)
            ax.hlines(y + offset, low, high, color=color, lw=1.4, zorder=3)
            ax.plot(delta, y + offset, marker, color=color, ms=4.2,
                    markerfacecolor="white" if base == "gray_phase" else color,
                    label=label if y == 0 else "_nolegend_", zorder=4)
            paired_evidence.append({"comparator": base, "noiseStd": sigma,
                                    "deltaPercentagePoints": float(delta), "interval": [float(low), float(high)]})
    ax.set(yticks=range(3), yticklabels=["0.02", "0.05", "0.10"],
           ylim=(2.7, -.65), xlim=(-2.3, 4.45), xlabel="F1差值 / 百分点", ylabel="σ")
    ax.xaxis.set_major_locator(FixedLocator([-2, 0, 2, 4]))
    ax.tick_params(axis="y", length=0, pad=5)
    panel_title(ax, "(b) RGB主方法的配对差值")
    clean_axes(ax)
    ax.legend(loc="lower center", bbox_to_anchor=(.5, -.015), ncol=2,
              fontsize=FONT_PT, handletextpad=.3, columnspacing=.6, borderaxespad=0)
    # A shared legend avoids covering any of the close curves.
    fig.legend(handles=handles, labels=METHOD_LABELS, loc="lower center", ncol=3,
               bbox_to_anchor=(.5, .018), handlelength=2.6, columnspacing=1.15,
               handletextpad=.5, labelspacing=.6, fontsize=FONT_PT)
    qa["noiseSourceRows"] = len(summaries)
    qa["noiseCurves"] = source_curves
    qa["noisePairedF1Comparisons"] = paired_evidence
    qa["noiseIntervals"] = {"left": "RGB marginal 95% interval only",
                            "right": "99.1666667% corrected intervals for six F1 comparisons"}
    save(fig, output, FIGURES[3][0], qa)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parent
    default = here if (here / "source_data").exists() else here.parent / "paper/figures_polished_20261028"
    parser.add_argument("--inputs", type=Path, default=default / "source_data")
    parser.add_argument("--output", type=Path, default=default)
    parser.add_argument("--chinese-font", help="Path to the template's SimSun font")
    parser.add_argument("--latin-font", help="Path to Times New Roman")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    fonts = setup_fonts(args.chinese_font, args.latin_font)
    qa = {"backend": "python", "fonts": fonts, "widthCm": WIDTH_CM,
          "analysisTextInsideFigures": False, "statisticsRecomputed": False,
          "sourceObservationsExcluded": 0, "fullTestImages": 200, "noiseIndependentImages": 10,
          "noiseSeedsPerImageAtNonzeroNoise": 3,
          "fontPolicy": "The course-template serif fonts replace generic publication defaults.",
          "canvasPolicy": "Fixed 16 cm canvas replaces tight cropping to preserve final physical text size.",
          "archetypes": {"fig1": "image plate", "fig2": "image plate + quant",
                          "fig3": "quantitative grid", "fig4": "quantitative grid"}}
    figure1(args.inputs, args.output, qa)
    figure2(args.inputs, args.output, qa)
    figure3(args.inputs, args.output, qa)
    figure4(args.inputs, args.output, qa)
    for stem, _ in FIGURES:
        with Image.open(args.output / f"{stem}.png") as im:
            assert abs(im.width / DPI * 2.54 - WIDTH_CM) < .01
            assert im.info["dpi"][0] >= 599
    (args.output / "figure_qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": "rendered_pending_visual_inspection", "figures": len(FIGURES),
                      "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
