# 冻结RGB主方法的噪声与消融实验

完整200张做灰度/RGB×相位关/开的2×2以及最终门控，共5配置、1000行。所有阈值、颜色权重、核参数保持固定。灰度无相位消融的ratio=.3，不混称早期ratio=.4基线。

噪声取test清单前10张，3档RGB独立通道加性高斯噪声（σ=.02/.05/.10）、3种子，截断后量化uint8；各方法共享同一输入，灰度从该噪声图转换。加上10张干净对照，6方法共600行。本轮总1600行，无新调参和训练。

噪声种子42/137/2026加每图唯一索引偏移，同图/seed跨强度共享标准噪声场。统计以10张图为块，3个种子先在图内平均，不把它们当作30张独立图。报告实际RGB/gray RMSE和截断比例。

首次准备和运行：

```powershell
python scripts/prepare_course_rgb_extras.py
./scripts/launch_course_rgb_extras.ps1 -Workers 4
```

已有锁不再次准备。有缺失任务、且无其他活动批次时恢复：

```matlab
addpath('matlab');
run_course_rgb_extras; % 已完整任务会跳过
verify_course_rgb_extras;
```

```powershell
python scripts/report_course_rgb_extras.py
python scripts/plot_course_rgb_extras.py
```

结果results/course_rgb_extras/run_20261027_01/，完整解读reports/course_rgb_noise_ablation.md。消融10个P/F1主要差值用99.5%区间；噪声RGB对灰度/Canny的6个F1差值另用99.1667%区间。两个分析家族分别校正，不声称整个项目联合覆盖。其他指标95%描述。

本实验只解释当前冻结工作点与固定10图高斯噪声，不证明各模块在重调阈值后仍有同样差距，也不概括所有噪声或全200图抗噪表现。历史数据已观察，非新盲测；正负结果均保留，不按test扩网格。
