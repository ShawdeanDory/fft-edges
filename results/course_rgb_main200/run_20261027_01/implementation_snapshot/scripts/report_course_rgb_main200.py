"""Complete six-method frozen test200 comparison; paired image uncertainty."""
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.io import loadmat
from prepare_course_rgb_main200 import ROOT,RUN,METHODS,read,dump,sha,now,check_sources
KEYS=['cntR','sumR','cntP','sumP'];METRICS=['precision','recall','f1','macroF1']
NAMES=dict(rgb_main='RGB主方法：FFT＋相位门控',gray_phase='灰度FFT＋相位支持',sobel='Sobel',canny='Canny',
           ideal_highpass='理想高通',gaussian_highpass='高斯高通')

def metric(c):
    c=np.asarray(c,dtype=float);p=c[...,2]/np.maximum(c[...,3],1);r=c[...,0]/np.maximum(c[...,1],1)
    return np.stack([p,r,2*p*r/np.maximum(p+r,np.finfo(float).eps)],axis=-1)

def main():
    lock=read(RUN/'parameters_locked.json');check_sources(lock)
    assert read(RUN/'verification.json')['status']=='PASS'
    records=read(RUN/'manifest.json')['records'];rows=[];gray_count_changes=[]
    data_hashes={r['imageId']:r for r in read(RUN/'data_integrity.json')['hashes']}
    for record in records:
        assert sha(Path(record['image']))==data_hashes[record['id']]['imageSHA256']
        assert sha(Path(record['reference']))==data_hashes[record['id']]['referenceSHA256']
        z=loadmat(RUN/'samples'/f'{record["id"]}.mat',simplify_cells=True)
        assert len(z['rows'])==6 and len(z['masks'])==6 and z['grayAgreement']
        assert z['selected']==lock['selected']
        original=loadmat(ROOT/'results/course_full200/run_20261027_01/samples/fft_phase'/f'{record["id"]}.mat',variable_names=['fixedRow','fixed'],simplify_cells=True)
        assert np.array_equal(z['masks'][1],original['fixed'])
        for j,(row,mask,scored) in enumerate(zip(z['rows'],z['masks'],z['scoredPixelCounts'])):
            assert row['method']==METHODS[j] and row['imageId']==record['id'] and row['sumP']==int(scored)
            assert 0<=row['cntR']<=row['sumR'] and 0<=row['cntP']<=row['sumP']
            assert np.max(np.abs(metric([row[k] for k in KEYS])-np.array([row[k] for k in METRICS[:3]])))<1e-12
            row['rawMaskPixels']=int(np.count_nonzero(mask));rows.append(row)
            if j==1:gray_count_changes.append(dict(imageId=record['id'],**{k:int(row[k]-original['fixedRow'][k]) for k in KEYS}))
    raw=pd.DataFrame(rows);assert len(raw)==1200 and not raw.duplicated(['imageId','method']).any()
    assert raw.groupby('imageId').sumR.nunique().eq(1).all()
    raw.to_csv(RUN/'fixed_metrics.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(gray_count_changes).to_csv(RUN/'gray_rescore_differences.csv',index=False)
    n=200;B=lock['bootstrapReplicates'];indices=np.random.default_rng(lock['bootstrapSeed']).integers(0,n,size=(B,n))
    summary=[];draws={};groups={};absolute=[]
    for method in METHODS:
        g=raw[raw.method==method].set_index('imageId').sort_index();assert len(g)==n;groups[method]=g
        C=g[KEYS].to_numpy(dtype=float);point=np.r_[metric(C.sum(axis=0)),g.f1.mean()]
        bs=np.column_stack([metric(C[indices].sum(axis=1)),g.f1.to_numpy()[indices].mean(axis=1)]);draws[method]=bs
        lo,hi=np.quantile(bs,[.025,.975],axis=0);row=dict(method=method,images=200)
        for j,k in enumerate(METRICS):
            row[k]=point[j];row[k+'Low95']=lo[j];row[k+'High95']=hi[j]
            absolute.append(dict(method=method,metric=k,value=point[j],low95=lo[j],high95=hi[j],images=n,replicates=B))
        row.update(macroPrecision=g.precision.mean(),macroRecall=g.recall.mean(),
                   detectionSecondsMean=g.detectionSeconds.mean(),detectionSecondsMedian=g.detectionSeconds.median(),
                   scoringSecondsTotal=g.scoringSeconds.sum(),rawPredictedPixels=int(g.rawMaskPixels.sum()),
                   officialPredictedPixels=int(g.sumP.sum()),matchedPredictedPixels=int(g.cntP.sum()))
        summary.append(row)
    s=pd.DataFrame(summary).set_index('method');s.to_csv(RUN/'fixed_summary.csv',encoding='utf-8-sig')
    pd.DataFrame(absolute).to_csv(RUN/'absolute_intervals.csv',index=False)
    ms=pd.read_csv(RUN/'matlab_summary.csv').set_index('method')
    cols=['precision','recall','f1','macroPrecision','macroRecall','macroF1']
    error=float(np.max(np.abs(s.loc[METHODS,cols].to_numpy()-ms.loc[METHODS,cols].to_numpy())));assert error<1e-12
    pairs=[];per_image=[];wins=[];tail=(1-lock['correctedPrimaryIntervalLevel'])/2
    for base in METHODS[1:]:
        assert groups['rgb_main'].index.equals(groups[base].index)
        point=s.loc['rgb_main',METRICS].to_numpy(dtype=float)-s.loc[base,METRICS].to_numpy(dtype=float)
        db=draws['rgb_main']-draws[base];lo,hi=np.quantile(db,[.025,.975],axis=0);lc,hc=np.quantile(db,[tail,1-tail],axis=0)
        for j,k in enumerate(METRICS):
            pairs.append(dict(comparator=base,method='rgb_main',metric=k,delta=point[j],low95=lo[j],high95=hi[j],
                              low995=lc[j],high995=hc[j],primary=k in lock['primaryEndpoints'],images=200))
        d=groups['rgb_main'].f1.to_numpy()-groups[base].f1.to_numpy()
        wins.append(dict(comparator=base,improvedF1Images=int((d>1e-12).sum()),worseF1Images=int((d< -1e-12).sum()),equalF1Images=int((np.abs(d)<=1e-12).sum())))
        for image_id in groups[base].index:
            per_image.append(dict(imageId=image_id,comparator=base,**{'delta'+k.title():groups['rgb_main'].loc[image_id,k]-groups[base].loc[image_id,k] for k in METRICS[:3]}))
    pairs=pd.DataFrame(pairs);assert pairs.primary.sum()==10
    pairs.to_csv(RUN/'paired_intervals.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(per_image).to_csv(RUN/'paired_per_image.csv',index=False);pd.DataFrame(wins).to_csv(RUN/'per_image_win_loss.csv',index=False)
    maximum_gray_count_change=max(abs(x[k]) for x in gray_count_changes for k in KEYS)
    dump(RUN/'table_integrity.json',dict(status='PASS',images=200,methods=6,rows=1200,missingImages=0,duplicatedRows=0,
         pythonMatlabAggregateMaxError=error,grayMaskRegression=200,parameterSourcesUnchanged=True,
         bootstrapReplicates=B,samePairedImageResamples=True,primaryComparisons=10,
         maximumHistoricalGrayRescoreCountChange=maximum_gray_count_change))
    write_report(lock,s,pairs,wins,error,maximum_gray_count_change)
    final=dict(status='complete',completedAt=now(),images=200,methods=6,rows=1200,
         mainMethod='rgb_main',parametersFrozen=True,newParameterSearch=False,thresholdScan=False,newNoise=False,
         training=False,gpuRequired=False,source='PASS',data='PASS',regression='PASS',tables='PASS',
         interpretation='Previously observed full official test split; frozen-config regression, not a new blind test.')
    dump(RUN/'final_status.json',final);dump(RUN/'status.json',final)
    print(s[['precision','recall','f1','macroF1']].to_string());print(pairs[pairs.comparator.isin(['gray_phase','canny'])].to_string(index=False))
    print('RGB_MAIN200_COMPLETE',RUN)

def write_report(lock,s,pairs,wins,error,gray_change):
    lines=['# 当前RGB主方法：完整200张统一对比','',
      '## Material Passport','', '- Origin Skill:academic-research-suite/experiment-agent','- Origin Mode:run/validate',
      '- Origin Date:2026-10-27','- Verification Status:VERIFIED','- Version Label:rgb_main200_fixed_v1','',
      '## 实际完成范围','',
      '完整官方BSDS500测试集200张，6条冻结管线，共1200行真实MATLAB评分全部完成。当前RGB主方法为phase_recall_01，灰度为对照；Sobel、Canny、理想高通和高斯高通沿用早期课程验证参数。本轮没有新增调参、训练、噪声或阈值扫描。',
      '这200张在项目历史中已观察，本轮是当前固定配置的完整回归，不能称全新盲测；相同评价器不表示颜色输入、预处理、参数选择预算和原选参指标完全一致。',
      '', '## 200张固定工作点结果','',
      '主表为官方匹配计数汇总P/R/F1，括号为按图像bootstrap20000次的边际95%区间。每种方法使用相同抽样图像索引，不把像素或标注员作为独立样本。',
      '', '|方法|Precision（95%区间）|Recall（95%区间）|F1（95%区间）|宏平均F1|','|---|---:|---:|---:|---:|']
    for m in METHODS:
        r=s.loc[m];cells=[f'{r[k]*100:.3f}%[{r[k+"Low95"]*100:.3f},{r[k+"High95"]*100:.3f}]' for k in METRICS[:3]]
        lines.append('|'+NAMES[m]+'|'+'|'.join(cells)+f'|{r.macroF1*100:.3f}%|')
    lines+=['','宏平均是逐图F1算术平均，不等于计数汇总F1，也不等于平均P/R的调和均值。各宏平均95%区间完整保存在fixed_summary.csv。',
      '', '## RGB主方法相对5个对照的配对差值','',
      '单位为百分点。P/F1共10个主要比较采用99.5%双侧bootstrap区间，Bonferroni近似家族覆盖95%；Recall及宏平均F1差值95%区间仅作描述。不根据有利口径更换主指标。',
      '', '|RGB主方法相对谁|ΔPrecision（99.5%区间）|ΔRecall（95%区间）|ΔF1（99.5%区间）|','|---|---:|---:|---:|']
    for base in METHODS[1:]:
        p=pairs[pairs.comparator==base].set_index('metric');cells=[]
        for k in METRICS[:3]:
            row=p.loc[k];lo=row.low95 if k=='recall' else row.low995;hi=row.high95 if k=='recall' else row.high995
            cells.append(f'{row.delta*100:+.3f}[{lo*100:+.3f},{hi*100:+.3f}]')
        lines.append('|'+NAMES[base]+'|'+'|'.join(cells)+'|')
    lines+=['','## 如何解释差距','']
    for base in ['gray_phase','canny']:
        p=pairs[pairs.comparator==base].set_index('metric');f=p.loc['f1'];pr=p.loc['precision']
        label='F1校正区间整体高于0' if f.low995>0 else ('F1校正区间整体低于0' if f.high995<0 else 'F1校正区间跨0，证据不足以确认差异方向')
        lines.append(f'- 相对{NAMES[base]}：Precision变化{pr.delta*100:+.3f}个百分点，F1变化{f.delta*100:+.3f}个百分点；{label}。')
    for w in wins:
        lines.append(f'- 相对{NAMES[w["comparator"]]}：逐图F1提高/下降/相同={w["improvedF1Images"]}/{w["worseF1Images"]}/{w["equalF1Images"]}。总体成绩不能解读为每图改善。')
    best=s.f1.idxmax();lines.append(f'\n本轮固定工作点计数汇总F1最高的是{NAMES[best]}（{s.loc[best,"f1"]*100:.3f}%）。这只是已冻结工作点排名，不是全阈值最优或论文排行榜。主方法角色保持用户选定RGB，不因本轮排序更改参数或历史采用结论。')
    lines.append('\n88张验证中的稳定性目标主要比较当前RGB与原RGB无新增门控版本，并包含宏平均F1及Recall护栏；本轮六方法对比中没有重新评分那个原RGB版本。样本和对照不同，因此当前RGB相对灰度的正向结果不能改写为“88图原验证门槛已经通过”，也不能独立证明新增门控本身有效。原target_not_met判断保留。')
    lines+=['','## 冻结参数与输入差异','',
      'RGB主方法：sigma=1.8、padding=32、灰度/颜色梯度张量权重0.75/0.25、相位权重0.25、高阈值0.32、低高比0.3、seedEta=0、linkEta=0.125。强种子不额外衰减，仅弱连接使用相位门控，无各向异性支持。RGB方法包含灰度分量，不能称纯RGB三通道边缘并集。',
      '灰度对照沿用已完成灰度FFT＋相位的k=4、alpha=.25、high=.32、ratio=.3。Canny sigma=1.8、high=.24、low=.096；Sobel自动阈值乘数.75；理想/高斯高通cutoff=.06、Otsu阈值乘数1.25。所有方法保留自身处理和细化，统一评分。',
      'RGB及灰度相位版本和传统对照历史上采用过不同验证搜索及指标，不能把本轮统一评分说成同等调参预算。未按test重调阈值，参数文件与数值源码先冻结。',
      '', '## 核对与实验边界','',
      '- 原始200张图和全部标注与官方原始压缩包逐字节一致，完整test与当前val名单不相交；不剔除失败或低分图。',
      '- 官方maxDist=.0075图像对角线，thin=1，原生尺寸及全部多人Boundaries；不另排除评分外圈。预测分母核对官方再次细化后像素数。GT并集只用于图示。',
      f'- 200张灰度掩膜与原完整200实验逐像素一致，当前主入口与本轮预测一致。MATLAB/Python独立汇总最大误差{error:.3g}。',
      f'- 同灰度掩膜相对旧官方评分计数最大变化{gray_change}，另存gray_rescore_differences.csv。原生匹配器的小幅重复调用差异不计为检测器收益，主要比较采用本轮同批评分。',
      '- 记录各方法检测及评分耗时，但处于并行批处理，含入口和回归检查开销，不是严格速度基准，不作CPU吞吐排名。',
      '- 区间只反映当前图像抽样，不覆盖历史选参偏差、标注员重抽样或匹配器本身的变异；校正bootstrap覆盖率为近似而非严格有限样本保证。',
      '- 本轮只有固定工作点P/R/F1，没有新PR/ODS/OIS/AP、噪声实验或独立新数据泛化；不得沿用旧配置成绩为当前RGB成绩。',
      '', '## 图表与复现','',
      '统计图覆盖全部200张。样例固定为数值ID最小的前三张：'+','.join(lock['figures']['exampleIds'])+'，展示原图、GT并集和6方法；不能以个别样例代替总体结论。R/G/B频谱和响应图由保存的原始数组绘制。',
      "MATLAB：addpath('matlab');run_course_rgb_main200;verify_course_rgb_main200; 已有完整按图样本自动跳过。",
      'Python：python scripts/report_course_rgb_main200.py；python scripts/plot_course_rgb_main200.py。原始计数fixed_metrics.csv、汇总区间fixed_summary.csv、配对区间paired_intervals.csv、逐图差值paired_per_image.csv。',
      '', '## 统计解释检查：11/11','',
      '聚合/Simpson风险：固定汇总并另报宏平均；生态谬误：逐图差值与胜负数；选择偏差：明确历史test观察和验证预算差异；碰撞变量：不按评分筛图；基率：不以Accuracy代Precision；回归均值：完整200图对照；幸存者偏差：1200行全部纳入；多重比较：10个主要区间校正；研究者自由度：冻结后不调参/换指标；相关与因果：颜色、相位、后处理均保留各自差异，不能把整条管线差距归因于单模块；反向因果：无相应因果主张。']
    text='\n'.join(lines)+'\n';(RUN/'EXPERIMENT_REPORT.md').write_text(text,encoding='utf-8');(ROOT/'reports/course_rgb_main200_comparison.md').write_text(text,encoding='utf-8')
if __name__=='__main__':main()
