# 不用四元数的彩色边缘检测与普通二维FFT：文献核对

检索日期：2026-10-27。范围：普通实数/复数二维傅里叶、RGB及保留颜色的多通道方法；排除四元数、Clifford、量子变换及深度网络。本轮只检索与分析，不运行新算法，不改变灰度FFT＋相位支持主方法。

## 结论与匹配程度

普通二维FFT可以分别处理RGB三个通道，不需要四元数。但“作者明确采用二维FFT”“作者采用可用FFT实现的普通卷积”“原文是灰度方法，可扩展到RGB”是不同证据。

本轮核实到：一篇论文明确描述RGB＋二维FFT＋Log-Gabor边缘特征，最终任务是图像检索；两篇不使用四元数的完整彩色边缘检测方法采用普通高斯/Gabor卷积，可由我们使用卷积定理实现成二维FFT；另有一篇明确使用FFT2/IFFT2的边缘检测方法，可作为逐通道RGB扩展的依据，但本轮没有核实它原本进行了RGB联合检测。不能把这四篇一概写成作者已完成“RGB联合二维FFT边缘基准”的论文。

检索沿用nature-academic-search的多源流程。没有专用academic-search数据库连接，采用出版方正文、作者原稿和Crossref。部分出版方直连返回403/429或机器人检查；正文可用出版方搜索索引及作者公开稿核对，取得范围逐项标注。只使用论文原始内容判断方法，不以第三方自动摘要替代技术证据。不是穷尽性检索。

## 1. RGB＋普通二维FFT的直接文字证据

Gupta,S.;Modem,S.;Thakre,V.V.(2020).**Phase congruency and ODBTC based image retrieval**.IET Image Processing14(10):2195–2203.DOI：[10.1049/iet-ipr.2019.1023](https://doi.org/10.1049/iet-ipr.2019.1023)。

- [出版方正文](https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/iet-ipr.2019.1023)第3节明确描述：RGB图像经2D FFT转到频域，Log-Gabor滤波，2D逆FFT，矩分析得到边缘与角点特征；没有使用四元数。
- 最终任务是CBIR图像检索，数据为Corel与CALTECH。文中的Precision/Recall用于检索相关图像，不是BSDS边缘像素Precision/Recall，不能拿其约88%的检索Precision与本项目比较。
- 对现方法的价值：可以引用为“普通二维FFT获取彩色图像相位边缘特征”的先例。我们已有Log-Gabor相位一致性最大矩支持，因此主要是补充方法依据，不能再把相同模块说成新的优化。
- 证据限制：正文描述不等于已核实三通道融合的可运行完整代码；本轮未复现其通道处理细节或整套检索系统，不需要把ODBTC与码本训练加入课程边缘检测。

## 2. 最贴近现有高斯导数流程的彩色方法

Wang,Dongyun;Yin,Jiawei;Tang,Chu;Cheng,Xiaojun;Ge,Binzhao.(2020).**Color Edge Detection Using the Normalization Anisotropic Gaussian Kernel and Multichannel Fusion**.IEEE Access8:228277–228288.DOI：[10.1109/ACCESS.2020.3044341](https://doi.org/10.1109/ACCESS.2020.3044341)。

- 原方法MF-NAGK：RGB/HSV多通道、CLAHE、归一化各向异性高斯方向导数、多通道梯度矩阵及SVD融合；不依赖四元数。
- 原始证据：[IEEE条目](https://ieeexplore.ieee.org/document/9292969)，以及[作者论文公开全文](https://www.researchgate.net/publication/347631178_Color_Edge_Detection_Using_the_Normalization_Anisotropic_Gaussian_Kernel_and_Multichannel_Fusion)的摘要、II.A、II.B及III节。公开稿带接受稿模板页眉，正式年份/卷页依据出版记录为2020年，不按模板中的2017年引用。
- 原文计算式是普通卷积，并未在本轮读到的算法段明确采用FFT作为实现。改用普通二维FFT是我们根据卷积定理作出的实现选择，不能归于作者原有实现。
- 可借鉴：优先单独研究各向异性高斯导数与核响应归一化，保持现有相位支持和后处理。与当前各向同性sigma=1.8相比，这是明确的滤波器变化，不需要分数阶或高维代数。
- 避免重复：对三通道二维梯度矩阵G，主奇异值与结构张量G转置乘G的最大特征值平方根对应。我们已有结构张量联合梯度，不能把简单换成SVD称为独立新贡献。论文的多方向/多空间构造也不等同于现有三通道2×2张量。
- 若只抽取归一化或各向异性模块，须写“借鉴模块”，不冒充完整MF-NAGK复现，也不承诺Precision提高。

## 3. 更突出傅里叶滤波器组的彩色方法

Li,Yunhong;Bi,Yuandong;Zhang,Weichuan;Ren,Jie;Chen,Jinni.(2023).**M²GF:Multi-Scale and Multi-Directional Gabor Filters for Image Edge Detection**.Applied Sciences13(16):9409.DOI：[10.3390/app13169409](https://doi.org/10.3390/app13169409)。

- [出版方原文](https://www.mdpi.com/2076-3417/13/16/9409)，[作者机构库全文](https://research-repository.griffith.edu.au/server/api/core/bitstreams/4ccaae4a-18b9-4a99-b87f-b2d38c8144b0/content)。第二、三节及式(5)—(8)描述RGB转换到保留颜色的Lab空间，各通道多方向、多尺度Gabor卷积，边缘强度融合与局部处理。
- 不使用四元数；转换Lab不等于转灰度。不过它不是直接保持原始RGB三个数值通道的方案，原文卷积式也不能直接说成作者已采用FFT2实现。
- 可借鉴：把有限采样Gabor核的普通卷积用FFT2/IFFT2实现；单独研究跨尺度几何平均/乘积，以及亮度和色度边缘响应融合，再与现有相位支持连接。需要正确补边与核对齐，才能对应线性卷积，而非误用循环卷积。
- 项目已有简化FFT＋Gabor支持实验，在旧20图口径下未超过只调阈值的对照；这不是完整M²GF的多通道流程。已有负结果应保留，不把同一简化模块重新包装为新优化。本轮未确认可直接复现的完整作者工程。
- 适合课程解释：卷积定理、频率与方向选择、多尺度与抗噪折中。RGB转换Lab和后处理需说明，不能把整个流程说成只进行一次FFT。

## 4. 普通FFT相位滤波的额外对照

Asghari,Mohammad H.;Jalali,Bahram.(2015).**Edge Detection in Digital Images Using Dispersive Phase Stretch Transform**.International Journal of Biomedical Imaging2015:687819.DOI：[10.1155/2015/687819](https://doi.org/10.1155/2015/687819)。

- [开放原文](https://pmc.ncbi.nlm.nih.gov/articles/PMC4386678/)第二节式(1)明确给出FFT2、频域定位核与相位核、IFFT2，再取复数相位进行边缘检测，即PST。
- 不使用四元数，但本轮未核实原论文提供RGB三通道联合检测流程，因此不列作“原作者已完成完整RGB联合FFT”的直接证据。
- 可借鉴：将其作为普通FFT相位方法的独立对照；若逐通道应用于RGB并联合，则属于本项目扩展，需要新验证。PST输出相位与Kovesi相位一致性不是同一个量，不应直接把参数或阈值混用。
- 课程贴合度高；目前只确认原理与来源，未运行该方法，不填入本项目实测表。

## 5. 标题很匹配、但还不宜据此实施的候选

Prakash,M.C.;Jagannadan,V.;Raghunath Sharma,R.;Prabhakara Rao,G.V.(2005).**Edge and corner detection in grayscale and color images using first Fourier basis**.Proc.SPIE6006:60060R.DOI：[10.1117/12.629860](https://doi.org/10.1117/12.629860)。

Crossref已核实题名、作者、日期与卷号；[出版方页](https://www.spiedigitallibrary.org/conference-proceedings-of-spie/6006/60060R/Edge-and-corner-detection-in-grayscale-and-color-images-using/10.1117/12.629860.full)受到访问检查，当前未取得可读原文，Crossref也未提供摘要。不能根据题名就断言它等同于对整幅RGB图像执行普通二维FFT，也不能把第三方自动摘要中的细节当作已核实方法。暂作待全文复核候选，不据此声称完成复现。

## 与课程实现的对应

对三个颜色通道分别用普通二维FFT即可计算滤波响应：

\[
R_{c,s,\theta}=\operatorname{IFFT2}\!\left[\operatorname{FFT2}(I_c)\,H_{s,\theta}\right],
\qquad c\in\{R,G,B\}.
\]

其中H可以是现有高斯导数核，也可以是普通各向异性高斯导数/Gabor核的频域表示。对离散有限核复现空间卷积时，必须使用相同的采样核、边界条件、补边与中心对齐；解析连续高斯频谱与截断空间核不应无条件声称逐像素等价。

随后如何归一化、融合颜色/方向/尺度，以及如何用相位支持、NMS和双阈值连接，仍需额外设计与验证。数学上的频域实现可行不等于效果必然提高。

建议阅读顺序：先MF-NAGK的归一化各向异性导数，再M²GF的多通道/跨尺度融合；用2020年PCF论文支撑现有普通FFT相位路线，PST作为独立方法对照。当前主方法和RGB保留决定维持不变。本轮没有新的性能实验或新增Precision成绩；既有200图、12图与88图也不会因本次检索而重新用于调参。
