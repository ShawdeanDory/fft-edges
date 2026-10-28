# fft-edges

基于普通二维傅里叶变换与相位支持的彩色自然图边缘检测课程项目。主方法融合灰度/RGB梯度张量与相位一致性支持，使用NMS、强种子保护和弱连接门控形成细边缘。MATLAB实现，不需要训练或GPU。

## 当前论文

[基于二维傅里叶变换与相位支持的彩色图像边缘检测及实验分析](paper/基于二维傅里叶变换与相位支持的彩色图像边缘检测及实验分析.docx)

Word稿保留课程模板原封面，供小组填写成员信息；当前仍为待审阅稿。[初版论文 Markdown](paper/初版论文.md)便于讨论正文和 LaTeX 公式，图像与排版以 Word 及独立图件为准。

## 中文论文图件

四幅论文用图已按课程模板重绘为中文宋体、英文及数字 Times New Roman，图内字号10 pt，宽度16 cm，提供600 dpi PNG、PDF及可编辑文字SVG。原始图像、检测掩膜、统计点估计和区间沿用冻结实验；图内只保留标签、图例和数值。

- [四幅美化图与独立重绘材料](paper/figures_polished_20261028/)
- [图注、尺寸与使用说明](paper/figures_polished_20261028/图注与使用说明.md)
- [绘图脚本](scripts/plot_paper_figures_cn.py)
- [最终论文配图清单](reports/FINAL_PAPER_FIGURES.md)，包含13组已绘实验图的用途与备选关系，以及作者另行绘制的整体流程图。
- [整体流程图生图提示词](paper/figures_polished_20261028/整体流程图_生图提示词.md)。作者已确认另行绘制流程图，成图未保存在本仓库中。

四幅图可直接用于替换原稿对应图件；Word内的替换与全文重新分页尚未执行。后续加入整体流程图时，应按最终正文顺序重新编号。

## 最终结果

200张BSDS500官方测试图的冻结工作点结果，单位为%。P/R/F1按官方匹配计数汇总。

|方法|Precision|Recall|F1|
|---|---:|---:|---:|
|RGB主方法|55.381|65.816|60.149|
|灰度FFT＋相位|54.503|66.069|59.731|
|Sobel|40.154|74.211|52.112|
|Canny|46.840|78.097|58.558|
|理想高通|37.137|70.161|48.567|
|高斯高通|35.833|71.140|47.660|

颜色融合和相位支持在固定工作点分别有F1收益；额外门控的独立F1收益尚未确认。10图高斯噪声实验中RGB与灰度接近，不宣称普遍抗噪优势。测试数据历史已观察，本轮属于冻结配置回归；各对照的历史选参预算不同。当前主方法尚无完整PR/ODS/OIS/AP结果。

## 文件入口

|内容|位置|
|---|---|
|主方法及配置|`matlab/course_fourier_edges.m`、`matlab/course_main_method.json`|
|200图六方法对比|`results/course_rgb_main200/run_20261027_01/`|
|200图消融与10图噪声|`results/course_rgb_extras/run_20261027_01/`|
|历史验证与配置选择|`results/course_rgb_phase_recall/run_20261027_01/`|
|原始自然图及多人标注|`data/course_full200/`及所需验证样例目录|
|课程演示结果|`results/natural_demo/rgb_main_20261027_195146_106/`|
|最终论文|`paper/`|
|参考文献|`docs/references/`|
|实验解释与提纲|`reports/`|

200图对比1200行、消融1000行、噪声600行，共2800行最终评分，另保留历史验证记录。逐图原始匹配计数、预测MAT、参数、协议、校验记录与13组PNG/PDF/SVG图件可追溯。`figures/`里的PDF是既有实验图矢量版，并非论文PDF。

## 队友写作顺序

1.先读`reports/COURSE_CURRENT_METHOD.md`与论文Word稿，统一方法和数据范围。
2.主表使用`fixed_summary.csv`；消融及噪声分别使用`ablation_summary.csv`、`noise_summary.csv`，不要混合不同范围的分数。
3.方法差值引用各目录的`paired_intervals.csv`或`*_paired_intervals.csv`，置信区间水平见协议。
4.论文优先使用`paper/figures_polished_20261028/`中的频谱/响应、固定飞机对比、模块差值及噪声曲线；其他完整图件位于两组最终实验的`figures/`。图件取舍见`reports/FINAL_PAPER_FIGURES.md`。

10图干净F1=65.153%与完整200图F1=60.149%来自不同图像范围。消融和主对比中相同掩膜的末位差异来自原生匹配器微小波动，不解释为算法改进。不要将Precision写成Accuracy或“成功率”。

## 本地使用

MATLAB R2026b与Image Processing Toolbox是已使用环境。Python统计和绘图依赖见`requirements.txt`。

```powershell
python -m pip install -r requirements.txt
python scripts/configure_local_paths.py
```

冻结记录中保留了原机器的绝对数据路径。配置脚本只将清单里的图像/标注路径替换为当前仓库路径，不改算法、阈值、标签或评分；会在`tmp/`备份原清单。阅读CSV与论文无需执行它。

在仓库根目录运行MATLAB：

```matlab
addpath('matlab');
[BW,details] = course_fourier_edges('data/course_full200/images/bsds_2018.jpg');
demoDir = run_natural_demo;
```

统计与图件脚本：

```powershell
python scripts/report_course_rgb_main200.py
python scripts/plot_course_rgb_main200.py
python scripts/report_course_rgb_extras.py
python scripts/plot_course_rgb_extras.py
python scripts/plot_paper_figures_cn.py
```

这些命令会重写相应派生CSV/图件；原始结果已提交，可用Git查看变化。已有实验参数已冻结，不应再次执行`prepare_*`覆盖锁。本次上传核对了已有数据与文件完整性，没有重新运行检测或在干净克隆中完成全量MATLAB验证。

## 数据和第三方代码

BSDS数据来自[Berkeley官方资源](https://www2.eecs.berkeley.edu/Research/Projects/CS/vision/grouping/resources.html)，保留来源与原始标注；本仓库不为原图、数据集或第三方程序授予额外权利。未上传重复的原始数据压缩包、模型权重和历史CAMUS工程。第三方源码与匹配器的原版权声明及适用条款见[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
