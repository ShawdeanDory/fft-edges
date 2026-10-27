# 第三方来源与保留声明

本项目是课程实现与实验分析，不能将已有算法、数据或代码归为全部原创。未对整个仓库统一赋予MIT等新许可证。

- `external/kovesi/`：Peter Kovesi的相位一致性与频率辅助函数，来自[作者代码库](https://codeberg.org/peterkovesi/matlabfns)。各文件内的版权与许可声明保留。理论参考为Kovesi2003的Phase Congruency Detects Corners and Edges。
- `external/structured_edges/`：Piotr Dollár的[Structured Edge Detection Toolbox](https://github.com/pdollar/edges)，使用`edgesEvalImg.m`与官方边界匹配器；保留`license.txt`中的MSR-LA条款和原源码声明。原记录版本为94260b5d0fc068202598312e01a37604972dcc9e。匹配器原始来源可追溯至BSDS基准代码，包含作者提供的不同平台MEX。
- `external/pdollar_toolbox/`：取自[Piotr Dollár工具箱](https://github.com/pdollar/toolbox)的参数辅助函数等必要文件。原记录版本为e87332637bbe8e8b92dd487c87567d9628404523，各源码版权声明保留；完整工具箱条款见其作者文档。
- `data/`中的自然图、人工标注及实验图中出现的原图来自[BSDS500](https://www2.eecs.berkeley.edu/Research/Projects/CS/vision/grouping/resources.html)。应引用Arbeláez等2011年的Contour Detection and Hierarchical Image Segmentation。原数据权利归相应权利人，本仓库用于课程研究与复核，不为原图另行授权。
- 多通道梯度参考DiZenzo1986；Canny对照参考Canny1986；完整书目信息位于`docs/references/`。

本仓库保留实际调用的第三方代码，不包含作者模型权重，也不宣称完成这些工具箱所有算法的复现。
