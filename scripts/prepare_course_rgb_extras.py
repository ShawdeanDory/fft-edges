"""Freeze Gaussian-noise robustness and controlled module ablations."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'results/course_rgb_main200/run_20261027_01'
RUN=ROOT/'results/course_rgb_extras/run_20261027_01'
NOISE_METHODS=['rgb_main','gray_phase','sobel','canny','ideal_highpass','gaussian_highpass']
ABLATIONS=['gray_fft','gray_phase','rgb_fft','rgb_phase','rgb_main']
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.now(timezone(timedelta(hours=8))).isoformat()
def check(lock):
    for f in lock['numericalSources']+lock['parameterFiles']:assert sha(ROOT/f['source'])==f['sha256'],f['source']
    assert sha(BASE/'parameters_locked.json')==lock['baseLockSHA256']
def main():
    RUN.mkdir(parents=True,exist_ok=True);assert not (RUN/'parameters_locked.json').exists()
    base=read(BASE/'parameters_locked.json');assert read(BASE/'final_status.json')['status']=='complete'
    sources=base['numericalSources'].copy()
    for f in sources+base['parameterFiles']:assert sha(ROOT/f['source'])==f['sha256']
    for name in ['matlab/run_course_rgb_extras.m','matlab/verify_course_rgb_extras.m']:
        sources.append(dict(source=name,sha256=sha(ROOT/name)))
    records=read(BASE/'manifest.json')['records'];assert len(records)==200
    tasks=[]
    for i,r in enumerate(records):
        tasks.append(dict(taskId='ablation_'+r['id'],stage='ablation',imageIndex=i+1,imageId=r['id'],noiseStd=0,seed=0,rngSeed=0))
    for i,r in enumerate(records[:10]):
        tasks.append(dict(taskId='noise_'+r['id']+'_clean',stage='noise',imageIndex=i+1,imageId=r['id'],noiseStd=0,seed=0,rngSeed=0))
        for sigma in [.02,.05,.10]:
            for seed in [42,137,2026]:
                tasks.append(dict(taskId=f'noise_{r["id"]}_s{round(sigma*100):02}_seed{seed}',stage='noise',imageIndex=i+1,
                    imageId=r['id'],noiseStd=sigma,seed=seed,rngSeed=seed+100000*i))
    assert len(tasks)==len({r['taskId'] for r in tasks})==300
    lock=dict(lockedAt=now(),authorization='User asked to supplement noise and clear ablations before drafting.',
        numericalSources=sources,parameterFiles=base['parameterFiles'],baseLockSHA256=sha(BASE/'parameters_locked.json'),
        main=base['main'],selected=base['selected'],grayChoice=base['grayChoice'],controls=base['controls'],
        noiseMethods=NOISE_METHODS,ablationMethods=ABLATIONS,maxDist=.0075,thin=1,padding=32,high=.32,ratio=.3,beta=.25,
        noiseImages=[r['id'] for r in records[:10]],noiseStandardDeviations=[.02,.05,.10],seeds=[42,137,2026],
        noiseModel='Independent RGB-channel additive zero-mean Gaussian noise on double0..1, clipping0..1, then im2uint8.',
        noiseSharing='One noisy uint8 RGB per image/std/seed shared by all methods; gray derived by rgb2gray of that same input.',
        rngRule='MATLAB twister, base seed +100000*(noise image index-1). Same normalized realization across std for a given image/seed.',
        quantization='Uint8 preserves exact sigma0 clean pipeline; record pre/post clipping RGB RMSE, gray RMSE and clipping fraction.',
        seedUnit='Average matching counts over three seeds inside each image; bootstrap10 image blocks, never treat30 draws as independent images.',
        ablationRule='2x2 gray/RGB and phase off/on, fixed beta=.25, sigma1.8, padding32, high.32, ratio.3; final gate differs only seed/link rule.',
        ablationContrasts=[['rgb_fft','gray_fft'],['rgb_phase','gray_phase'],['gray_phase','gray_fft'],['rgb_phase','rgb_fft'],['rgb_main','rgb_phase']],
        bootstrapReplicates=20000,bootstrapSeed=20261027,ablationCorrectedLevel=.995,
        ablationPrimary='Five predefined contrasts x Precision/F1 =10; Bonferroni approximate family coverage95%.',
        noisePrimaryComparators=['gray_phase','canny'],noiseCorrectedLevel=1-.05/6,
        noisePrimary='RGB F1 vs gray/Canny at three nonzero std =6; separate Bonferroni family coverage95%. Other contrasts descriptive95%.',
        multiplicityScope='Ablation and noise are separately predeclared families; no whole-project family guarantee.',
        cleanRegression='Recompute six clean masks on10 images and gray/main ablation masks on200; compare completed main200 frozen masks.',
        expectedTasks=300,expectedAblationRows=1000,expectedNoiseRows=600,expectedRows=1600,
        parameterSearch=False,thresholdScan=False,training=False,gpuRequired=False,changeMainAlgorithm=False,
        history='Previously observed official test200; no new blind data. Noise subset fixed first10 IDs, not selected by performance.',
        exampleIds=[r['id'] for r in records[:3]],noiseExampleId=records[0]['id'],noiseExampleSeed=42)
    check(lock);dump(RUN/'parameters_locked.json',lock);dump(RUN/'manifest.json',dict(count=200,records=records))
    dump(RUN/'tasks.json',dict(count=300,tasks=tasks))
    for f in sources+base['parameterFiles']:
        p=RUN/'implementation_snapshot'/f['source'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f['source'],p)
    protocol=['# 当前RGB：固定噪声与模块消融协议','',
        '在完成200图统一对比后锁定，主方法、灰度和传统对照源码/参数不变，不根据本轮结果调参。',
        '消融：完整200张，gray_fft、gray_phase、rgb_fft、rgb_phase、rgb_main五种。统一sigma=1.8、padding32、high=.32、ratio=.3；RGB beta=.25。前四项形成灰度/RGB×相位关/开的2×2，最后只增加当前强种子保护/弱连接门控。',
        'gray_fft与早期ratio=.4的FFT基线不是同一个配置，须用本轮标签。模块移除会改变响应标度/有效阈值，本轮只评价固定工作点差异，不宣称等预算PR最优。',
        '噪声：预先固定test清单前10张，sigma=.02/.05/.10，base seed42/137/2026，加每图唯一偏移。RGB各通道独立加高斯噪声，截断到0..1后量化uint8；所有方法共享同一张噪声RGB，灰度从中转换。',
        '同一图/seed跨sigma共享标准噪声场。保存实际RGB/gray RMSE、截断比例和可视化输入，sigma0精确还原原输入。灰度实际噪声经颜色加权，不能声称其标准差与单色RGB通道相同。',
        '噪声每个图内先平均3次匹配计数，主指标按图汇总比率；20k次bootstrap以10张图为块，不把种子当独立样本。消融bootstrap以200张图为块。',
        '消融5个预定差值×P/F1采用99.5%校正区间；噪声RGB与gray/Canny各3档F1采用99.1667%校正区间，两族分别校正，其余指标95%描述。10张噪声图的范围及精度有限，不能推广为全200图抗噪结论。',
        '全部使用官方maxDist=.0075、thin=1、原生尺寸与全部多人标注，不额外排除边框；图像/标注沿用已逐字节校验的原始200数据。',
        '200个消融任务×5=1000行，100个噪声任务（10clean+90noisy）×6=600行，总1600行。保存按任务原子检查点；旧输出均保留。',
        '固定历史已观察数据，属于补充实验。没有PR/ODS/OIS/AP扫描、新训练、GPU或扩网格。无论正负都报告，不以结果改主方法。','']
    (RUN/'PROTOCOL.md').write_text('\n'.join(protocol),encoding='utf-8');dump(RUN/'status.json',dict(status='locked_not_scored',expectedRows=1600,expectedTasks=300))
    print('FROZEN: ablation200x5=1000, noise10x(1+3x3)x6=600; total1600 rows.')
if __name__=='__main__':main()
