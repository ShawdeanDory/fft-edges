"""Freeze the current RGB main and five controls before official test200."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,shutil,tarfile
ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'results/course_rgb_main200/run_20261027_01'
METHODS=['rgb_main','gray_phase','sobel','canny','ideal_highpass','gaussian_highpass']
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.now(timezone(timedelta(hours=8))).isoformat()
def check_sources(lock):
    for item in lock['numericalSources']:assert sha(ROOT/item['source'])==item['sha256'],item['source']
    for item in lock['parameterFiles']:assert sha(ROOT/item['source'])==item['sha256'],item['source']

def main():
    RUN.mkdir(parents=True,exist_ok=True);assert not (RUN/'parameters_locked.json').exists(),'Refuse to overwrite frozen run.'
    m=read(ROOT/'data/course_full200/manifest.json');assert m['count']==len(m['records'])==200
    records=m['records'];assert len({r['id'] for r in records})==200
    assert [int(r['id'].split('_')[1]) for r in records]==sorted(int(r['id'].split('_')[1]) for r in records)
    # Verify every raw image/annotation against the original official archive.
    with tarfile.open(ROOT/'data/BSR_bsds500.tgz') as a:
        members={x.name:x for x in a.getmembers()};image_members={Path(n).stem:n for n in members if '/images/test/' in n and n.endswith('.jpg')}
        assert len(image_members)==200 and {r['id'][5:] for r in records}==set(image_members)
        hashes=[]
        for r in records:
            name=image_members[r['id'][5:]];ref=name.replace('/images/test/','/groundTruth/test/').replace('.jpg','.mat')
            for key,member in [('image',name),('reference',ref)]:
                content=a.extractfile(member).read();assert Path(r[key]).read_bytes()==content
            hashes.append(dict(imageId=r['id'],imageSHA256=sha(Path(r['image'])),referenceSHA256=sha(Path(r['reference']))))
    val={r['id'] for r in read(ROOT/'results/course_rgb_phase_recall/run_20261027_01/manifest.json')['records']}
    assert val.isdisjoint(r['id'] for r in records)
    main=read(ROOT/'matlab/course_main_method.json')
    selected=read(ROOT/'results/course_rgb_phase_recall/run_20261027_01/parameters_locked.json')['selected']
    assert main['mainMethod']=='rgb_phase_gate' and selected['candidateId']=='phase_recall_01'
    assert selected['seedEta']==0 and selected['linkEta']==.125 and not main['anisotropicSupport']
    previous=read(ROOT/'results/course_natural/run_20261026_231522_733/parameters_locked.json')
    controls=[c for c in previous['choices'] if c['method'] not in ['fft_gaussian']]
    assert [c['method'] for c in controls]==METHODS[2:]
    numeric=['matlab/course_fourier_edges.m','matlab/course_fourier_rgb_phase_gate_edges.m',
             'matlab/course_rgb_phase_features.m','matlab/course_rgb_phase_map.m','matlab/course_rgb_phase_gate_features.m',
             'matlab/course_rgb_phase_gate_hysteresis.m','matlab/course_fourier_phase_edges.m','matlab/course_phase_features.m',
             'matlab/course_phase_edges.m','matlab/course_fourier_scale_bank.m','matlab/course_directional_hysteresis.m',
             'matlab/gradient_nonmax_suppression.m','matlab/course_detect_edges.m','matlab/fourier_edge_responses.m',
             'matlab/thin_hysteresis_edges.m','external/kovesi/phasecong3.m','external/kovesi/lowpassfilter.m',
             'external/kovesi/filtergrid.m','external/kovesi/rayleighmode.m','external/structured_edges/edgesEvalImg.m',
             'external/structured_edges/private/correspondPixels.mexw64','external/pdollar_toolbox/matlab/getPrmDflt.m',
             'matlab/run_course_rgb_main200.m','matlab/verify_course_rgb_main200.m']
    params=['matlab/course_main_method.json','results/course_rgb_phase_recall/run_20261027_01/parameters_locked.json',
            'results/course_phase/run_20261027_100711_491/parameters_locked.json',
            'results/course_phase/run_20261027_100711_491/parameters_locked.mat',
            'results/course_natural/run_20261026_231522_733/parameters_locked.json',
            'results/course_natural/run_20261026_231522_733/parameters_locked.mat']
    sources=[dict(source=n,sha256=sha(ROOT/n)) for n in numeric];parameters=[dict(source=n,sha256=sha(ROOT/n)) for n in params]
    lock=dict(lockedAt=now(),authorization='User: freeze current algorithm and complete unified comparison on200 images.',
              main=main,selected=selected,methods=METHODS,controls=controls,grayChoice=next(c for c in read(ROOT/params[2])['choices'] if c['branch']=='fft_phase'),
              numericalSources=sources,parameterFiles=parameters,maxDist=.0075,thin=1,padding=32,
              primaryStatistic='pooled official counts; macro P/R/F1 reported separately',bootstrapReplicates=20000,bootstrapSeed=20261027,
              primaryEndpoints=['precision','f1'],primaryComparators=METHODS[1:],correctedPrimaryIntervalLevel=.995,
              marginalIntervalLevel=.95,multiplicity='Ten P/F1 differences vs five controls; Bonferroni approximate family coverage95%.',
              comparisonScope='Six frozen pipelines; controls retain their historical validation parameters. Not equal-budget official-metric retuning.',
              testUsedForTuning=False,parameterSearch=False,thresholdScan=False,newNoise=False,training=False,gpuRequired=False,
              history='All200 test images previously observed in earlier project runs. Current configuration fixed before this regression. Not a new blind test.',
              timing='Detection/score wall times measured in parallel batch jobs; descriptive, not a controlled speed benchmark.',
              figures=dict(exampleIds=[r['id'] for r in records[:3]],selection='First three numeric test IDs fixed before scoring; no favorable selection.'),
              mainRoleChanged=False,automaticParameterOrRoleChanges=False)
    check_sources(lock);dump(RUN/'parameters_locked.json',lock);dump(RUN/'manifest.json',m)
    dump(RUN/'data_integrity.json',dict(status='PASS',images=200,allArchiveBytesIdentical=True,validationDisjoint=True,hashes=hashes))
    for item in sources+parameters:
        dest=RUN/'implementation_snapshot'/item['source'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/item['source'],dest)
    protocol=['# 当前RGB主方法完整200张统一对比协议','',
        '固定RGB主方法phase_recall_01及灰度FFT＋相位、Sobel、Canny、理想高通、高斯高通，共6种。',
        'RGB保留强种子，只门控弱连接。高阈值.32、低高比.3、seedEta=0、linkEta=.125，其余既有滤波/颜色/相位参数不变。',
        '全部原始200张官方test、原生分辨率、全部多人标注；maxDist=.0075图像对角线，thin=1，不另排除边框。图像及标注逐字节核对原始官方压缩包。',
        '四个传统对照沿用历史课程验证参数，与新RGB选择预算和原选参指标存在差异；统一评价协议不等于所有预处理/选参预算完全相同。',
        '主要报告匹配计数汇总P/R/F1，同时保存逐图与宏平均。20000次按图配对bootstrap；各方法分数边际95%区间，RGB对5对照的P/F1共10项用99.5%双侧区间作Bonferroni校正，Recall及宏平均差值95%作描述。',
        '不设自动换主方法或调整参数规则；如实报告全部结果。旧200图历史上已观察，本轮是固定配置回归，不称新盲测。',
        '不执行阈值扫描、ODS/OIS/AP、噪声或训练；这些留作独立任务。批处理耗时记录仅描述运行，不作严格速度排名。',
        '图示固定前三个数值ID，GT并集仅显示。主RGB与灰度逐图对照公开旧入口/旧掩膜验证，逐图原子保存可恢复。','']
    (RUN/'PROTOCOL.md').write_text('\n'.join(protocol),encoding='utf-8')
    dump(RUN/'status.json',dict(status='locked_not_scored',images=200,methods=6,expectedRows=1200))
    print('FROZEN: official200 x6,1200 fixed-point rows; all raw data match archive; no tuning.')
if __name__=='__main__':main()
