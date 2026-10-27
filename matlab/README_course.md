# 基于二维傅里叶变换与相位门控的彩色图像边缘检测

当前项目主方法为RGB二维FFT＋相位门控，采用phase_recall_01：保留强边缘种子，仅对弱连接作相位门控。灰度FFT＋相位支持作为对照保留。此角色由用户指定；原严格验证判断target_not_met保留，不表述为已证明F1稳定优于灰度或原RGB。

程序使用MATLAB与Image Processing Toolbox，CPU即可运行，无深度学习、GPU、四元数或各向异性支持。主算法与相位模块均使用普通二维傅里叶运算。

## 主入口

在项目根目录运行：

```matlab
addpath('matlab');
[BW,details]=course_fourier_edges('C:\images\photo.jpg');
imshow(BW);
% 灰度对照：
[BWgray,grayDetails]=course_fourier_edges('C:\images\photo.jpg','gray');
```

统一入口course_fourier_edges默认读取course_main_method.json中的RGB主方法。旧灰度入口course_fourier_phase_edges继续输出原算法，不重命名、不覆盖历史数据。RGB专用入口course_fourier_rgb_phase_gate_edges和包装入口course_fourier_rgb_supported_edges也使用相同RGB默认配置。

## 课堂快速演示

```matlab
addpath('matlab');
demoDir=run_natural_demo;
imshow(imread(fullfile(demoDir,'six_methods.png')));
imshow(imread(fullfile(demoDir,'frequency_spectra.png')));
```

默认取验证清单固定首图bsds_3096，不按分数选图，自动展示原图、GT显示合并图、RGB主方法、灰度对照及Sobel、Canny、理想高通、高斯高通。输出6方法边缘图、R/G/B对数频谱、强种子/弱连接响应、MAT原始数组和单图指标。旧five_methods.png文件名保留为同一6方法图的兼容别名，当前使用six_methods.png。

自定义图片：

```matlab
demoDir=run_natural_demo('C:\images\photo.jpg');
```

自定义图片没有随附标注时只输出图像，不生成Precision/Recall/F1。默认样例使用官方BSDS匹配，maxDist=.0075图像对角线、thin=1、全部原始多人标注。GT并集仅展示。四个传统对照沿用历史验证参数，没有为新演示重新调参；单图展示不能替代数据集排名。

原5方法灰度课堂演示保留为run_natural_demo_legacy，历史完整参数/噪声实验仍由run_course_natural执行，说明见README_legacy_course.md。这些历史实验和分数没有改成RGB成绩。

## 当前RGB方法如何工作

R/G/B分别通过普通fft2计算高斯平滑导数，再以ifft2恢复各通道梯度。采用sigma=1.8、对称补边32，融合75%的灰度梯度张量与25%的RGB联合梯度张量，取主特征值和方向执行原NMS。这是使用颜色信息的混合方法，仍含灰度分量，不称完全独立的三个颜色通道边缘简单并集。

既有相位一致性同样通过普通二维FFT和频域滤波实现。灰度/颜色相位支持按固定权重融合，原相位权重0.25不变。高阈值0.32作为强种子，低阈值0.096决定弱连接；新主方法仅对弱连接响应乘以1−0.125(1−Q)，强种子不额外衰减，再8连通重建和细化。未使用各向异性核、深度网络或训练标签计算输入响应。

这仍属于基于傅里叶变换的图像边缘检测：FFT负责导数与相位滤波，颜色张量及门控负责融合和边缘连接。报告可按“傅里叶性质→通道梯度→相位支持→连接→对照实验”组织。

## 已有证据与报告口径

本主方法已完成原12张选择与另88张验证。88图固定工作点P/R/F1=54.004%/65.727%/59.292%；相对原RGB，Precision提高0.697个百分点、汇总F1基本持平，宏平均F1下降0.138个百分点。相对旧纯相位门控恢复Recall0.915个百分点，但相对原RGB仍损失1.063个百分点，未通过原严格稳定性目标。

历史100张val已观察，不能称新盲测。当前RGB主方法已完成完整200张固定工作点统一对比（README_rgb_main200.md），P/R/F1=55.381%/65.816%/60.149%，相对灰度的P/F1校正差值区间均高于0；当前配置已补齐10图×3强度×3种子的高斯噪声实验与完整200图消融（README_rgb_extras.md），99阈值PR/ODS/OIS/AP尚未运行；原200图和噪声成绩仍属于当时的灰度/旧RGB等指定配置，不得改标签归到当前RGB主方法。

本次将RGB作为研究与展示主线，不依赖宣称其所有指标均优于灰度。灰度、原RGB、旧相位门控均保留作消融/比较。完整区间与逐图数据见reports/course_rgb_phase_recall.md及results/course_rgb_phase_recall/run_20261027_01/。

## 常用对照入口

```matlab
% 当前RGB主方法：
[BW,d]=course_fourier_edges('image.jpg');
% 原灰度对照：
[BWgray,dgray]=course_fourier_edges('image.jpg','gray');
% 原RGB响应、不附加新门控：
[BWref,dref]=course_fourier_rgb_phase_gate_edges('image.jpg','reference');
% 旧纯相位门控（同时衰减种子和弱连接）：
[BWold,dold]=course_fourier_rgb_phase_gate_edges('image.jpg','phase_only');
```

后续若扩充实验，应沿用冻结参数和相同评价器，分别标明当前主方法的新结果。旧统计锁、历史图表和验证判定保持原记录。
