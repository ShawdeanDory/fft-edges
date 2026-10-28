# 最终课程论文配图清单

更新日期：2026-10-28。

本清单以实际文件和作者确认的信息为依据。仓库原有13组实验图；其中4组已另行导出中文美化版，是同一内容的替换版本，不额外算作4组不同证据。作者已确认在仓库外另行绘制1张整体流程图。因此，论文配图候选为 **13组实验图＋1张整体流程图**。

论文要求正文含图表4–6页，建议优先采用以下5幅核心图，按最终出现顺序编号。整体流程图目前只有提示词保存在仓库，成图由作者另行提供；不把提示词或未提供的图片链接当作已经上传的成图。

## 建议优先用于正文的5幅图

|建议图号|图名|对应正文|成图与状态|
|---|---|---|---|
|图1|整体算法架构／流程图|方法总览，解释FFT梯度、张量融合、相位支路与连接的关系|作者已另行绘制；图片不在当前仓库。[提示词](../paper/figures_polished_20261028/整体流程图_生图提示词.md)|
|图2|RGB通道频谱及中间响应|频域高斯导数与相位门控|[中文PNG](../paper/figures_polished_20261028/fig01_rgb_spectra_responses_cn.png) · [PDF](../paper/figures_polished_20261028/fig01_rgb_spectra_responses_cn.pdf) · [SVG](../paper/figures_polished_20261028/fig01_rgb_spectra_responses_cn.svg)|
|图3|六方法边缘检测定性比较：bsds_3063飞机|方法对比及单图结果解读|[中文PNG](../paper/figures_polished_20261028/fig02_six_method_comparison_cn.png) · [PDF](../paper/figures_polished_20261028/fig02_six_method_comparison_cn.pdf) · [SVG](../paper/figures_polished_20261028/fig02_six_method_comparison_cn.svg)|
|图4|完整200图的模块配对差值|颜色、相位、额外门控的消融分析|[中文PNG](../paper/figures_polished_20261028/fig03_module_paired_changes_cn.png) · [PDF](../paper/figures_polished_20261028/fig03_module_paired_changes_cn.pdf) · [SVG](../paper/figures_polished_20261028/fig03_module_paired_changes_cn.svg)|
|图5|固定10图的高斯噪声曲线与配对差值|有限噪声实验|[中文PNG](../paper/figures_polished_20261028/fig04_noise_robustness_cn.png) · [PDF](../paper/figures_polished_20261028/fig04_noise_robustness_cn.pdf) · [SVG](../paper/figures_polished_20261028/fig04_noise_robustness_cn.svg)|

新图文件名中的01–04沿用当前四图顺序；加入整体流程图后，论文图号可顺延为图2–5，无需为编号修改图片内容。全部中文美化图宽16 cm、字号10 pt，中文宋体、英文及数字Times New Roman。图注与统计解释作为可编辑正文另行排版，见[图注与使用说明](../paper/figures_polished_20261028/图注与使用说明.md)。

## 其他9组已绘制的可选图

以下图均已存在PNG/PDF/SVG三个版本，链接先指向PNG。它们可按叙事需求替换核心图、用于附录或PPT；目前为原有英文标注版，直接加入中文终稿前宜统一字体与中文标签。

|序号|图名|用途及取舍|现有成图|
|---|---|---|---|
|6|完整200图六方法P/R/F1及区间|展示总体成绩；与论文主结果表信息重复，通常二选一|[test200_fixed_scores](../results/course_rgb_main200/run_20261027_01/figures/test200_fixed_scores.png)|
|7|RGB主方法相对五个对照的配对差值|展示方法间差距及不确定性；区分于模块消融|[test200_paired_changes](../results/course_rgb_main200/run_20261027_01/figures/test200_paired_changes.png)|
|8|完整200图五配置消融P/R/F1及区间|展示消融绝对成绩；与现有消融表重复，通常二选一|[ablation200_scores](../results/course_rgb_extras/run_20261027_01/figures/ablation200_scores.png)|
|9|固定噪声输入及边缘结果示例|解释噪声增加后的视觉表现；固定bsds_2018与seed42，不能替代10图定量曲线|[noise_first_image_seed42](../results/course_rgb_extras/run_20261027_01/figures/noise_first_image_seed42.png)|
|10|六方法定性比较：bsds_2018|自然图／纹理例图，可作为飞机示例的补充或替换|[bsds_2018_six_methods](../results/course_rgb_main200/run_20261027_01/figures/bsds_2018_six_methods.png)|
|11|六方法定性比较：bsds_5096|建筑／拱门例图，可补充结构边界与纹理差异|[bsds_5096_six_methods](../results/course_rgb_main200/run_20261027_01/figures/bsds_5096_six_methods.png)|
|12|五配置消融定性比较：bsds_2018|观察模块变化对同一输入的影响|[bsds_2018_ablation](../results/course_rgb_extras/run_20261027_01/figures/bsds_2018_ablation.png)|
|13|五配置消融定性比较：bsds_3063|观察飞机示例的颜色、相位和门控差异|[bsds_3063_ablation](../results/course_rgb_extras/run_20261027_01/figures/bsds_3063_ablation.png)|
|14|五配置消融定性比较：bsds_5096|观察建筑示例的模块差异|[bsds_5096_ablation](../results/course_rgb_extras/run_20261027_01/figures/bsds_5096_ablation.png)|

## 原有13组图的对应关系

原有4组已由中文美化版替换：

|原图|推荐替换版|
|---|---|
|test200_rgb_spectra_and_responses|fig01_rgb_spectra_responses_cn|
|bsds_3063_six_methods|fig02_six_method_comparison_cn|
|ablation200_module_changes|fig03_module_paired_changes_cn|
|noise10_f1_and_paired_changes|fig04_noise_robustness_cn|

其余9组见上表。课堂演示目录另有频谱、单方法掩膜、六方法拼图等文件，属于同一流程的演示材料；不重复计作最终论文的新增实验图，也不以单图成绩替代数据集结论。

## 文字协调与版面安排

方法部分放流程图与频谱／中间响应图；实验部分放一张固定自然图对比；消融与噪声部分各放一张量化图。每幅图附近用正文解释其展示内容和结论边界，分析不合成进图片。完整200图六方法主表与消融表可保留，避免再同时加入信息重复的绝对成绩图。

当前只新增图件和材料索引，尚未将图片替换到Word或重新检查整篇分页。最终插图后须再次确认正文含图表总页数为4–6页、图注与正文邻近、字号和纵横比正确。
