# 当前RGB主方法：完整200张统一评分

冻结phase_recall_01及灰度FFT＋相位、Sobel、Canny、理想高通、高斯高通，共6种、200张官方test、1200行固定工作点评分。统一使用官方maxDist=.0075图像对角线、thin=1、全部原始多人标注、原生分辨率，不额外排除边框。四种传统方法沿用历史课程验证参数，不能称同等验证预算重新优化。

没有新参数选择、99阈值扫描、噪声或训练；当前主方法不根据test成绩修改。这200张历史上已观察，本轮是冻结配置回归，不是新的盲测。

首次冻结与运行（已经冻结后不再次准备）：

```powershell
python scripts/prepare_course_rgb_main200.py
./scripts/launch_course_rgb_main200.ps1 -Workers 4
```

无其他活动批次时，按需恢复缺失样本：

```matlab
addpath('matlab');
run_course_rgb_main200; % 完整按图样本会跳过
verify_course_rgb_main200;
```

汇总与出图：

```powershell
python scripts/report_course_rgb_main200.py
python scripts/plot_course_rgb_main200.py
```

结果results/course_rgb_main200/run_20261027_01/；EXPERIMENT_REPORT.md同步为reports/course_rgb_main200_comparison.md。fixed_metrics.csv为原始逐图计数，fixed_summary.csv为P/R/F1及宏平均与95%区间，paired_intervals.csv为RGB对5对照的配对差值，per_image_win_loss.csv为逐图改善数。

20000次按图配对bootstrap，P/F1对5对照共10个主要区间用99.5%Bonferroni校正；Recall和宏平均F1差值95%作描述。图示样例固定为200张清单前三个ID，GT并集只显示，不用来评分。运行完成须有final_status.json及全部1200行，只有启动进程不算完成。
