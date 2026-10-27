# 纯相位门控：保护强种子并减少Recall损失

当前角色更新：用户已指定本轮RGB配置为项目主方法，灰度版本作为对照。统一入口course_fourier_edges，课堂演示run_natural_demo；历史实验结论不随角色变动而更改。

灰度主方法是“原图转灰度→FFT高斯导数→相位支持→NMS→滞后连接”的旧管线。本轮固定其代码、参数和入口作为参照，优化独立RGB分支。

当前RGB入口course_fourier_rgb_phase_gate_edges和包装入口course_fourier_rgb_supported_edges均已按用户要求，默认使用“保留强种子、只对弱连接作相位门控”的phase_recall_01。显式传入'phase_only'仍可运行旧门控。各向异性历史算法文件没有删除，当前入口不调用它们。

本轮所选优化保护原RGB强种子，只对弱连接作相位门控；不改变原FFT滤波核、相位参数、NMS方向或高低阈值。旧门控与本轮优化均可单独运行：

88图结果：本轮候选P/R/F1=54.004%/65.727%/59.292%，Recall损失从旧门控的1.978个百分点降至1.063个百分点。相对原RGB的Precision提高0.697个百分点，但F1基本持平、宏平均F1点估计下降0.138个百分点，原严格验证目标未达。此次设为RGB默认是用户选择，原retention_decision.json的实验结论保留，不能改称已证明F1稳定提高。

```matlab
addpath('matlab');
[BWold,dold]=course_fourier_rgb_phase_gate_edges('image.jpg','phase_only');
[BWnew,dnew]=course_fourier_rgb_phase_gate_edges('image.jpg'); % selected is now default
imshow(BWnew);
% Seed and link responses intentionally differ in the optimized pipeline:
imshow(dnew.seedResponse,[]);
imshow(dnew.linkResponse,[]);
```

补跑和汇总（完整样本自动跳过）：

```matlab
run_course_rgb_phase_recall('confirmation');
verify_course_rgb_phase_recall;
```

实验分数与图表已经生成。本次默认切换未重算分数；原implementation_snapshot保留当时的入口源码，复核历史逐字节源码时应使用冻结快照。默认切换前后的入口文件与本次检查单独保存于results/course_rgb_phase_recall/default_switch_20261027/，不覆盖实验锁文件或采用判断。

只有原12图选择6个固定配置，冻结一个后在另88图验证，不用200张test追分。Recall损失目标是相对原RGB不超过1个百分点；主要置信区间同时检查Precision、汇总F1、宏平均F1和相对旧门控的Recall恢复。历史验证图已经观察，区间不消除历史选参偏差。

结果results/course_rgb_phase_recall/run_20261027_01/，完整解释reports/course_rgb_phase_recall.md。是否满足稳定改善要求以retention_decision.json为准；提供实验入口不等于已经证明新数据泛化。
