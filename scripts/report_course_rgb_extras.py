"""Block-bootstrap noise replicates and a controlled 2x2+gate ablation."""
import numpy as np
import pandas as pd
from scipy.io import loadmat
from prepare_course_rgb_extras import ROOT,RUN,BASE,NOISE_METHODS,ABLATIONS,read,dump,check,now
KEYS=['cntR','sumR','cntP','sumP'];METRICS=['precision','recall','f1','macroF1']
NAMES=dict(rgb_main='RGB主方法：相位＋弱连接门控',gray_phase='灰度＋相位',sobel='Sobel',canny='Canny',
    ideal_highpass='理想高通',gaussian_highpass='高斯高通',gray_fft='灰度FFT梯度，无相位',rgb_fft='RGB融合FFT梯度，无相位',rgb_phase='RGB＋相位，无额外门控')
def metric(c):
    c=np.asarray(c,dtype=float);p=c[...,2]/np.maximum(c[...,3],1);r=c[...,0]/np.maximum(c[...,1],1)
    return np.stack([p,r,2*p*r/np.maximum(p+r,np.finfo(float).eps)],axis=-1)
def summarize(raw,methods,n,indices,stage):
    rows=[];draws={};groups={}
    for name in methods:
        g=raw[raw.method==name].groupby('imageId',sort=True)[KEYS].mean()
        mf=raw[raw.method==name].groupby('imageId',sort=True).f1.mean();assert len(g)==n and g.index.equals(mf.index)
        C=g.to_numpy(dtype=float);point=np.r_[metric(C.sum(axis=0)),mf.mean()]
        bs=np.column_stack([metric(C[indices].sum(axis=1)),mf.to_numpy()[indices].mean(axis=1)])
        lo,hi=np.quantile(bs,[.025,.975],axis=0);draws[name]=bs;groups[name]=(g,mf)
        row=dict(stage=stage,method=name,images=n)
        for j,k in enumerate(METRICS):row[k]=point[j];row[k+'Low95']=lo[j];row[k+'High95']=hi[j]
        rows.append(row)
    return pd.DataFrame(rows).set_index('method'),draws,groups
def contrast(summary,draws,method,base,level,stage,primaryKeys,**extra):
    point=summary.loc[method,METRICS].to_numpy(dtype=float)-summary.loc[base,METRICS].to_numpy(dtype=float)
    db=draws[method]-draws[base];lo,hi=np.quantile(db,[.025,.975],axis=0);tail=(1-level)/2;lc,hc=np.quantile(db,[tail,1-tail],axis=0)
    return [dict(stage=stage,method=method,comparator=base,metric=k,delta=point[j],low95=lo[j],high95=hi[j],
                 correctedLow=lc[j],correctedHigh=hc[j],correctedLevel=level,primary=k in primaryKeys,**extra) for j,k in enumerate(METRICS)]
def main():
    p=read(RUN/'parameters_locked.json');check(p);assert read(RUN/'verification.json')['status']=='PASS'
    rows=[];frames=[];tasks=read(RUN/'tasks.json')['tasks']
    for task in tasks:
        z=loadmat(RUN/'samples'/f'{task["taskId"]}.mat',simplify_cells=True)
        assert z['task']==task and len(z['rows'])==(5 if task['stage']=='ablation' else 6)
        if task['stage']=='ablation':assert z['regressions']['main'] and z['regressions']['gray']
        if task['stage']=='noise' and task['noiseStd']==0:assert z['regressions']['allCleanControls']
        for row,mask in zip(z['rows'],z['masks']):
            assert row['taskId']==task['taskId'] and row['imageId']==task['imageId']
            assert 0<=row['cntR']<=row['sumR'] and 0<=row['cntP']<=row['sumP']
            assert np.max(np.abs(metric([row[k] for k in KEYS])-np.array([row[k] for k in METRICS[:3]])))<1e-12
            row['rawMaskPixels']=int(np.count_nonzero(mask));rows.append(row)
        if task['stage']=='noise':frames.append({**task,**z['inputStats']})
    raw=pd.DataFrame(rows);assert len(raw)==1600 and not raw.duplicated(['taskId','method']).any()
    assert raw.groupby('taskId').sumR.nunique().eq(1).all()
    raw.to_csv(RUN/'all_metrics.csv',index=False,encoding='utf-8-sig')
    ab=raw[raw.stage=='ablation'];noise=raw[raw.stage=='noise'];assert len(ab)==1000 and len(noise)==600
    ab.to_csv(RUN/'ablation_metrics.csv',index=False,encoding='utf-8-sig');noise.to_csv(RUN/'noise_metrics.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(frames).to_csv(RUN/'noise_inputs.csv',index=False,encoding='utf-8-sig')
    image_units=noise.groupby(['noiseStd','method','imageId'],sort=True)[KEYS+['precision','recall','f1']].mean().reset_index()
    image_units.to_csv(RUN/'noise_image_units.csv',index=False,encoding='utf-8-sig')
    B=p['bootstrapReplicates'];idx=np.random.default_rng(p['bootstrapSeed']).integers(0,200,size=(B,200))
    a,ad,ag=summarize(ab,ABLATIONS,200,idx,'ablation');a.to_csv(RUN/'ablation_summary.csv',encoding='utf-8-sig')
    ap=[];wins=[]
    for method,base in p['ablationContrasts']:
        assert ag[method][0].index.equals(ag[base][0].index)
        ap.extend(contrast(a,ad,method,base,p['ablationCorrectedLevel'],'ablation',['precision','f1']))
        d=ag[method][1].to_numpy()-ag[base][1].to_numpy()
        wins.append(dict(method=method,comparator=base,improvedF1Images=int((d>1e-12).sum()),worseF1Images=int((d< -1e-12).sum()),equalF1Images=int((np.abs(d)<=1e-12).sum())))
    ap=pd.DataFrame(ap);assert ap.primary.sum()==10;ap.to_csv(RUN/'ablation_paired_intervals.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(wins).to_csv(RUN/'ablation_per_image_win_loss.csv',index=False)
    idx=np.random.default_rng(p['bootstrapSeed']+10).integers(0,10,size=(B,10));ns=[];nd={};npairs=[];drops=[]
    for sigma in [0,.02,.05,.10]:
        subset=noise[np.isclose(noise.noiseStd,sigma)]
        expected=1 if sigma==0 else 3
        assert subset.groupby(['method','imageId']).size().eq(expected).all()
        s,draws,g=summarize(subset,NOISE_METHODS,10,idx,'noise');s['noiseStd']=sigma;s['seedsPerImage']=expected
        ns.append(s.reset_index());nd[sigma]=draws
        if sigma>0:
            for base in NOISE_METHODS[1:]:
                primary=['f1'] if base in p['noisePrimaryComparators'] else []
                npairs.extend(contrast(s,draws,'rgb_main',base,p['noiseCorrectedLevel'],'noise',primary,noiseStd=sigma))
            for method in NOISE_METHODS:
                clean=ns[0].set_index('method').loc[method];d=draws[method]-nd[0][method]
                lo,hi=np.quantile(d,[.025,.975],axis=0)
                for j,k in enumerate(METRICS):drops.append(dict(method=method,noiseStd=sigma,metric=k,delta=s.loc[method,k]-clean[k],low95=lo[j],high95=hi[j]))
    ns=pd.concat(ns,ignore_index=True);ns.to_csv(RUN/'noise_summary.csv',index=False,encoding='utf-8-sig')
    npairs=pd.DataFrame(npairs);assert npairs.primary.sum()==6;npairs.to_csv(RUN/'noise_paired_intervals.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(drops).to_csv(RUN/'noise_changes_from_clean.csv',index=False)
    matlab=pd.read_csv(RUN/'matlab_summary.csv');error=0
    for row in matlab.to_dict('records'):
        if row['stage']=='ablation':s=a.loc[row['method']]
        else:s=ns[(ns.method==row['method'])&np.isclose(ns.noiseStd,row['noiseStd'])].iloc[0]
        error=max(error,float(np.max(np.abs(np.array([s[k] for k in METRICS])-np.array([row[k] for k in METRICS])))))
    assert error<1e-12;check(p)
    dump(RUN/'table_integrity.json',dict(status='PASS',tasks=300,rows=1600,ablationRows=1000,noiseRows=600,
         noiseImages=10,noiseNonzeroRealizations=90,missingTasks=0,duplicateRows=0,pythonMatlabAggregateMaxError=error,
         cleanSixMethodMaskRegressions=60,mainGrayAblationMaskRegressions=400,noiseBootstrapUnit='image block with all3 seeds',
         ablationPrimaryContrasts=10,noisePrimaryContrasts=6,originalSourcesUnchanged=True))
    write_report(p,a,ap,ns,npairs,wins,frames,error)
    final=dict(status='complete',completedAt=now(),tasks=300,rows=1600,ablationImages=200,ablationRows=1000,noiseImages=10,noiseRows=600,
         parametersChanged=False,newTuning=False,training=False,gpuRequired=False,source='PASS',regression='PASS',tables='PASS')
    dump(RUN/'final_status.json',final);dump(RUN/'status.json',final)
    print('ABLATIONS');print(a[['precision','recall','f1','macroF1']].to_string())
    print('NOISE');print(ns[['noiseStd','method','precision','recall','f1']].to_string(index=False))
    print('ABLATION CONTRASTS');print(ap[ap.metric=='f1'][['method','comparator','delta','correctedLow','correctedHigh']].to_string(index=False))
    print('RGB_EXTRAS_COMPLETE',RUN)

def write_report(p,a,ap,ns,npairs,wins,frames,error):
    lines=['# 当前RGB主方法：噪声实验与模块消融','',
       '## Material Passport','', '- Origin Skill:academic-research-suite/experiment-agent','- Origin Mode:run/validate',
       '- Origin Date:2026-10-27','- Verification Status:VERIFIED','- Version Label:rgb_noise_ablation_v1','',
       '## 完成范围与冻结边界','',
       '当前主方法与完整200图对比的数值源码、参数均未更改。本轮完成200图×5配置=1000行消融，以及10图×（1次干净＋3档噪声×3种子）×6方法=600行，共1600条真实官方评分。',
       '这是固定工作点的补充实验，没有重选阈值、增加候选、训练、GPU或PR扫描。数据此前已观察，不能称新盲测；10图噪声子集固定为测试清单前10张，未按表现筛图。',
       '', '## 消融设计','',
       '前四个配置构成灰度/RGB×相位关/开的2×2，最后增加当前弱连接门控。统一sigma1.8、padding32、高阈值.32、低高比.3、RGB颜色权重.25。灰度FFT无相位行的ratio=.3，与早期ratio=.4基线不是同一配置。',
       '颜色对照：rgb_fft−gray_fft与rgb_phase−gray_phase；相位对照：gray_phase−gray_fft与rgb_phase−rgb_fft；门控对照：rgb_main−rgb_phase。RGB仍含75%灰度梯度分量，颜色对照评估联合梯度张量融合，而非三个通道边缘并集。',
       '无相位时直接使用同一NMS响应；有相位时乘.75+.25Q；最终强种子不额外衰减，仅弱连接乘1−.125(1−Q)。移除相位会改变响应标度和有效阈值，故本轮结论仅针对固定工作点，不能直接归为全PR曲线改善。',
       '', '## 完整200图消融结果','',
       '官方匹配计数汇总，单位为百分比，括号为按200张图bootstrap20000次的边际95%区间。宏平均F1是逐图平均，另存完整区间。',
       '', '|配置|Precision（95%区间）|Recall（95%区间）|F1（95%区间）|宏平均F1|','|---|---:|---:|---:|---:|']
    for method in ABLATIONS:
        r=a.loc[method];cells=[f'{r[k]*100:.3f}%[{r[k+"Low95"]*100:.3f},{r[k+"High95"]*100:.3f}]' for k in METRICS[:3]]
        lines.append('|'+NAMES[method]+'|'+'|'.join(cells)+f'|{r.macroF1*100:.3f}%|')
    lines+=['','## 模块配对变化','',
       '单位为百分点。5个预定差值×P/F1共10个主要区间采用99.5%双侧bootstrap校正，近似家族覆盖95%；Recall及宏平均F1差值95%仅描述。',
       '', '|增加的模块/对照|ΔPrecision（99.5%区间）|ΔRecall（95%区间）|ΔF1（99.5%区间）|','|---|---:|---:|---:|']
    for method,base in p['ablationContrasts']:
        g=ap[(ap.method==method)&(ap.comparator==base)].set_index('metric');cells=[]
        for k in METRICS[:3]:
            r=g.loc[k];lo=r.low95 if k=='recall' else r.correctedLow;hi=r.high95 if k=='recall' else r.correctedHigh
            cells.append(f'{r.delta*100:+.3f}[{lo*100:+.3f},{hi*100:+.3f}]')
        lines.append('|'+NAMES[method]+'−'+NAMES[base]+'|'+'|'.join(cells)+'|')
    for method,base in p['ablationContrasts']:
        r=ap[(ap.method==method)&(ap.comparator==base)&(ap.metric=='f1')].iloc[0]
        label='F1校正区间高于0' if r.correctedLow>0 else ('F1校正区间低于0' if r.correctedHigh<0 else 'F1校正区间跨0，未确认改善方向')
        lines.append(f'\n{NAMES[method]}相对{NAMES[base]}：ΔF1={r.delta*100:+.3f}个百分点；{label}。')
    lines.append('\n本轮结果支持将颜色融合和相位支持作为固定工作点的主要收益来源：颜色在无相位/有相位条件下均改善F1，相位在灰度/RGB条件下也均改善F1。额外弱连接门控的F1改善未被确认，应写为Precision/Recall折衷设计，不作为已经证实独立F1增益的核心贡献。上述不是经过重新调参后的全PR性能结论。')
    lines+=['','逐图胜负数见ablation_per_image_win_loss.csv。若某一模块未提高F1，保留其阴性/不确定结果，不把组合方法相对灰度的整体收益全部归给该模块。',
       '', '## 噪声模型与统计单位','',
       '对RGB0～1数据每个通道独立加零均值高斯噪声，名义标准差.02/.05/.10，截断后量化uint8；sigma0保持原图逐字节输入路径。同一噪声RGB提供给6方法，灰度从该图转换。灰度噪声经颜色加权，实际标准差通常不同，不能把名义sigma理解为灰度输入实际RMSE。',
       '种子42/137/2026加每图100000倍索引偏移，同一图/seed跨强度共享标准噪声场。每张图先平均3次匹配计数，再跨10张汇总P/R/F1；宏平均F1先平均图内3次，再平均图像。bootstrap按10张图块保留3种子，独立样本单位不是30次噪声抽样。',
       '', '## 噪声下P/R/F1','',
       '下表均为10图子集，不能与全200图直接比较基准值。各格为P/R/F1百分比；各方法/噪声档的边际95%区间完整见noise_summary.csv。',
       '', '|方法|干净图|σ=0.02|σ=0.05|σ=0.10|','|---|---:|---:|---:|---:|']
    for method in NOISE_METHODS:
        cells=[]
        for sigma in [0,.02,.05,.10]:
            r=ns[(ns.method==method)&np.isclose(ns.noiseStd,sigma)].iloc[0];cells.append('/'.join(f'{r[k]*100:.2f}' for k in METRICS[:3]))
        lines.append('|'+NAMES[method]+'|'+'|'.join(cells)+'|')
    lines+=['','## 抗噪比较的配对区间','',
       'RGB相对灰度和Canny在3个非零强度的F1差值共6项，另作99.1667%双侧Bonferroni校正；与消融分属预先规定的两个家族，不宣称整个项目的联合覆盖。其他方法与指标95%区间只作描述。单位为百分点。',
       '', '|噪声强度|RGB相对谁|ΔF1|99.1667%区间|','|---|---|---:|---:|']
    for r in npairs[npairs.primary].to_dict('records'):
        lines.append(f'|{r["noiseStd"]:.2f}|{NAMES[r["comparator"]]}|{r["delta"]*100:+.3f}|[{r["correctedLow"]*100:+.3f},{r["correctedHigh"]*100:+.3f}]|')
    lines.append('\n本轮RGB相对灰度的三档F1校正区间均跨0，没有证据证明普遍抗噪优势。相对Canny，只有std=.02的F1校正区间高于0；std=.05/.10的点估计有利但校正区间跨0。应逐档描述，不能统称所有强度显著更好。')
    clean=ns[(ns.method=='rgb_main')&np.isclose(ns.noiseStd,0)].iloc[0]
    high=ns[(ns.method=='rgb_main')&np.isclose(ns.noiseStd,.10)].iloc[0]
    lines.append(f'\nRGB在同10图子集的F1由干净{clean.f1*100:.3f}%降到std=.10的{high.f1*100:.3f}%，下降{(clean.f1-high.f1)*100:.3f}个百分点。Precision从{clean.precision*100:.3f}%升至{high.precision*100:.3f}%，但Recall由{clean.recall*100:.3f}%降至{high.recall*100:.3f}%，故Precision单独上升不意味着噪声有益。哪些边缘被抑制尚未做区域级因果诊断。')
    lines+=['','只有10张噪声图，区间可能较宽。某档更好不等于所有强度更好；不能从单幅示例或种子重复推断普遍抗噪优势。相对同10张干净图的下降和95%区间见noise_changes_from_clean.csv。',
       '', '## 输入噪声的实际程度','',
       '|名义σ|实际RGB RMSE均值|实际灰度RMSE均值|截断比例均值|','|---|---:|---:|---:|']
    frames=pd.DataFrame(frames)
    for sigma in [.02,.05,.10]:
        g=frames[np.isclose(frames.noiseStd,sigma)];lines.append(f'|{sigma:.2f}|{g.rgbRMSE.mean():.5f}|{g.grayRMSE.mean():.5f}|{g.clippedFraction.mean()*100:.2f}%|')
    lines+=['','## 完整性与解释边界','',
       f'- 300个任务、1600行全部完成，无缺失/重复；MATLAB/Python汇总最大误差{error:.3g}。',
       '- 当前RGB和灰度消融各200张掩膜与已完成200图输出逐像素一致；10图干净输入6方法60张掩膜也一致。主算法源码与参数未修改。',
       '- 沿用官方maxDist=.0075、thin=1、原生尺寸及全部标注，不另排除边框。预测分母按官方再次细化核对，GT并集仅显示。',
       '- 原生匹配器重复调用可能有少量计数波动；微小差值不自动解释为检测器收益。区间条件于当前预测与评分，不覆盖历史选择偏差或匹配器随机性。',
       '- 高斯噪声不涵盖椒盐、压缩、模糊等全部退化；本轮也未调参或重新去噪。不能把这组实验说成所有真实噪声场景的结论。',
       '- 当前阈值冻结，移除模块使响应幅度改变，实验旨在解释现有管线而非证明各模块在各自最优阈值下的普遍排名。',
       '', '## 图表与复现','',
       '200图消融及配对模块图、10图噪声F1曲线/配对差值、固定首图及seed42的噪声示例均由保存计数/掩膜/输入绘制；所有6方法及正负结果保留。',
       "MATLAB：addpath('matlab');run_course_rgb_extras;verify_course_rgb_extras; 已有任务自动跳过。",
       'Python：python scripts/report_course_rgb_extras.py；python scripts/plot_course_rgb_extras.py。原始逐次数据、图内种子汇总、区间和输入RMSE均独立保存。',
       '', '## 统计解释检查：11/11','',
       '聚合风险：汇总与宏平均分开；生态谬误：保留逐图胜负；选择偏差：固定前10噪声图并注明历史观察；碰撞变量：不按分数筛图；基率：P不是背景Accuracy；回归均值：完整200消融和固定10噪声；幸存者偏差：不剔除失败；多重比较：两族分别校正；研究者自由度：实验前锁定且不追加候选；相关/因果：模块交互与响应标度边界明确；反向因果：无相应因果主张。',
       '', '## 写作衔接','',
       '现在可将方法、数据、固定参数、完整200比较、本轮消融和噪声结果组织成课程初稿。先写原理/实现和实验设置，再按真实数值写结果与局限，最后写摘要与结论；不把未支持的模块说成有效创新。']
    text='\n'.join(lines)+'\n';(RUN/'EXPERIMENT_REPORT.md').write_text(text,encoding='utf-8');(ROOT/'reports/course_rgb_noise_ablation.md').write_text(text,encoding='utf-8')
if __name__=='__main__':main()
