"""All-data ablation/noise plots, plus predeclared unmodified examples."""
import numpy as np
import pandas as pd
from PIL import Image
from scipy.io import loadmat
from scipy.sparse import issparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from prepare_course_rgb_extras import RUN,NOISE_METHODS,ABLATIONS,read,dump
AB_LABELS=['Gray FFT','Gray FFT + phase','RGB FFT','RGB FFT + phase','RGB + phase + weak gate']
NO_LABELS=['RGB main','Gray + phase','Sobel','Canny','Ideal high-pass','Gaussian high-pass']
COLORS=['#369271','#65717a','#9b94a8','#407da1','#bd7646','#bc9a71']
AB_COLORS=['#9ca2a7','#65717a','#79a4b8','#407da1','#369271']
def save(fig,path):
    for ext in ['png','pdf','svg']:fig.savefig(path.with_suffix('.'+ext),dpi=300,bbox_inches='tight',facecolor='white')
    plt.close(fig)
def ground_truth(path):
    gt=loadmat(path,simplify_cells=True)['groundTruth'];gt=[gt] if isinstance(gt,dict) else gt
    return np.logical_or.reduce([x['Boundaries'].toarray() if issparse(x['Boundaries']) else x['Boundaries'] for x in gt])
def panel(ax,array,title,binary=True):
    ax.imshow(array,**(dict(cmap='gray_r',vmin=0,vmax=1) if binary else {}),interpolation='nearest')
    ax.set_xticks([]);ax.set_yticks([]);ax.set_title(title,fontsize=9)
    for spine in ax.spines.values():spine.set_visible(False)
def main():
    assert read(RUN/'final_status.json')['status']=='complete';p=read(RUN/'parameters_locked.json')
    out=RUN/'figures';out.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],'font.size':10,
        'svg.fonttype':'none','pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'legend.frameon':False})
    ab=pd.read_csv(RUN/'ablation_summary.csv').set_index('method');ap=pd.read_csv(RUN/'ablation_paired_intervals.csv');metrics=['precision','recall','f1']
    fig,axes=plt.subplots(1,3,figsize=(11.5,4.4),sharey=True)
    for j,k in enumerate(metrics):
        ax=axes[j]
        for y,(m,c) in enumerate(zip(ABLATIONS,AB_COLORS)):
            r=ab.loc[m];ax.plot([r[k+'Low95']*100,r[k+'High95']*100],[y,y],color=c,lw=1.6);ax.plot(r[k]*100,y,'o',color=c,ms=5)
        ax.set(yticks=range(5),yticklabels=AB_LABELS,ylim=(4.5,-.5),xlabel='Score (%)');ax.grid(axis='x',alpha=.15)
        ax.set_title(f'{chr(97+j)}  '+['Precision','Recall','Pooled F1'][j],loc='left',fontweight='bold',fontsize=11)
    fig.suptitle('Controlled ablation on all 200 test images: fixed thresholds and color weight',fontsize=12,y=1.01)
    fig.text(.5,-.025,'Pooled official counts; 95% image-bootstrap CI; 20,000 paired resamples. Phase removal changes response scale at this fixed working point.',ha='center',fontsize=8)
    fig.tight_layout(w_pad=2);save(fig,out/'ablation200_scores')
    pair_labels=['Color without phase','Color with phase','Phase on gray','Phase on RGB','Extra weak-link gate']
    fig,axes=plt.subplots(1,3,figsize=(11.5,4.4),sharey=True)
    for j,k in enumerate(metrics):
        ax=axes[j];ax.axvline(0,color='#999999',ls='--',lw=.9)
        for y,(m,b) in enumerate(p['ablationContrasts']):
            r=ap[(ap.method==m)&(ap.comparator==b)&(ap.metric==k)].iloc[0]
            lo=r.low95 if k=='recall' else r.correctedLow;hi=r.high95 if k=='recall' else r.correctedHigh
            ax.plot([lo*100,hi*100],[y,y],color='#407da1',lw=1.6);ax.plot(r.delta*100,y,'o',color='#407da1',ms=5)
        ax.set(yticks=range(5),yticklabels=pair_labels,ylim=(4.5,-.5),xlabel='Difference (percentage points)');ax.grid(axis='x',alpha=.15)
        ax.set_title(f'{chr(97+j)}  '+['Precision','Recall','Pooled F1'][j],loc='left',fontweight='bold',fontsize=11)
    fig.suptitle('Predeclared module contrasts: color, phase and weak-link gating',fontsize=12,y=1.01)
    fig.text(.5,-.025,'Precision/F1: 99.5% CI for10 primary contrasts. Recall: descriptive95% CI. No threshold retuning.',ha='center',fontsize=8)
    fig.tight_layout(w_pad=2);save(fig,out/'ablation200_module_changes')
    ns=pd.read_csv(RUN/'noise_summary.csv');npairs=pd.read_csv(RUN/'noise_paired_intervals.csv')
    fig,axes=plt.subplots(1,2,figsize=(11.0,4.8),gridspec_kw={'width_ratios':[1.15,1]})
    for method,label,color in zip(NOISE_METHODS,NO_LABELS,COLORS):
        g=ns[ns.method==method].sort_values('noiseStd');x=g.noiseStd.to_numpy();y=g.f1.to_numpy()*100
        axes[0].plot(x,y,'o-',ms=4,color=color,lw=2 if method=='rgb_main' else 1.3,label=label)
        if method=='rgb_main':axes[0].fill_between(x,g.f1Low95.to_numpy()*100,g.f1High95.to_numpy()*100,color=color,alpha=.13,lw=0)
    axes[0].set(xlabel='Nominal RGB Gaussian noise std',ylabel='Pooled F1 (%)',xticks=[0,.02,.05,.10])
    axes[0].set_title('a  Six frozen methods on10 fixed images',loc='left',fontweight='bold',fontsize=11);axes[0].grid(alpha=.15);axes[0].legend(fontsize=8,ncol=2,loc='lower left')
    axes[1].axvline(0,color='#999999',ls='--',lw=.9)
    for base,label,color,offset in [('gray_phase','vs gray','#65717a',-.1),('canny','vs Canny','#407da1',.1)]:
        point=[]
        for y,sigma in enumerate([.02,.05,.10]):
            r=npairs[(npairs.comparator==base)&(npairs.metric=='f1')&np.isclose(npairs.noiseStd,sigma)].iloc[0]
            axes[1].plot([r.correctedLow*100,r.correctedHigh*100],[y+offset,y+offset],color=color,lw=1.6);point.append(r.delta*100)
        axes[1].plot(point,np.arange(3)+offset,'o',color=color,ms=5,label=label)
    axes[1].set(yticks=range(3),yticklabels=['std0.02','std0.05','std0.10'],ylim=(2.5,-.5),xlabel='RGB F1 difference (percentage points)')
    axes[1].set_title('b  Noise F1 paired differences',loc='left',fontweight='bold',fontsize=11);axes[1].grid(axis='x',alpha=.15);axes[1].legend(fontsize=8)
    fig.text(.5,-.025,'Three noise seeds averaged inside each image; bootstrap n=10 image blocks. Left shading: RGB95% CI. Right:99.1667% CI for6 contrasts.',ha='center',fontsize=8)
    fig.tight_layout(w_pad=2.5);save(fig,out/'noise10_f1_and_paired_changes')
    records={r['id']:r for r in read(RUN/'manifest.json')['records']};examples=[]
    for image_id in p['exampleIds']:
        r=records[image_id];z=loadmat(RUN/'samples'/f'ablation_{image_id}.mat',simplify_cells=True)
        image=np.asarray(Image.open(r['image']));gt=ground_truth(r['reference']);fig,axes=plt.subplots(2,4,figsize=(13,7.0))
        arrays=[image,gt,*list(z['masks'])];titles=['Original RGB','GT union (display only)',*AB_LABELS]
        for j,(ax,array,title) in enumerate(zip(axes.flat,arrays,titles)):
            panel(ax,array,title,j!=0)
            if j>=2:
                row=z['rows'][j-2];ax.set_xlabel(f'P {row["precision"]*100:.1f}% | R {row["recall"]*100:.1f}% | F1 {row["f1"]*100:.1f}%',fontsize=8)
        axes.flat[-1].axis('off');fig.suptitle(image_id+' | Controlled module ablation',fontsize=12,y=.995)
        fig.text(.5,.005,'GT union is display-only. All scores use individual original annotations and the official matcher.',ha='center',fontsize=8)
        fig.tight_layout(rect=[0,.025,1,.97],w_pad=.7,h_pad=1.5);save(fig,out/(image_id+'_ablation'))
        examples.append(dict(imageId=image_id,stage='ablation',crop=False,photometricChanges=False))
    image_id=p['noiseExampleId'];fig,axes=plt.subplots(4,4,figsize=(11.5,13))
    for i,sigma in enumerate([0,.02,.05,.10]):
        task_id='noise_'+image_id+('_clean' if sigma==0 else f'_s{round(sigma*100):02}_seed{p["noiseExampleSeed"]}')
        z=loadmat(RUN/'samples'/f'{task_id}.mat',simplify_cells=True);assert z['inputExample'].size>0
        arrays=[z['inputExample'],z['masks'][0],z['masks'][1],z['masks'][3]]
        for j,(ax,array) in enumerate(zip(axes[i],arrays)):
            title=['Shared RGB input','RGB main','Gray + phase','Canny'][j] if i==0 else ''
            panel(ax,array,title,j!=0)
            if j==0:ax.set_ylabel('Clean' if sigma==0 else f'std={sigma:.2f}',fontsize=10)
            if j>0:
                row=z['rows'][[0,1,3][j-1]];ax.set_xlabel(f'P {row["precision"]*100:.1f}% | R {row["recall"]*100:.1f}% | F1 {row["f1"]*100:.1f}%',fontsize=7.5)
    fig.suptitle(image_id+' | Fixed seed42, same RGB noise input for all methods',fontsize=12,y=.995)
    fig.text(.5,.005,'No cropping or contrast changes. Display is one predeclared realization; quantitative curves use10 images x3 seeds.',ha='center',fontsize=8)
    fig.tight_layout(rect=[0,.02,1,.97],w_pad=.7,h_pad=1.2);save(fig,out/'noise_first_image_seed42')
    dump(out/'figure_contract_and_qa.json',dict(status='rendered_pending_visual_check',backend='python',
        conclusion='Separate fixed-working-point color/phase/gate contributions and limited10-image Gaussian-noise robustness.',
        archetypes=['quantitative grid','image plate + quant'],ablationImages=200,noiseImages=10,noiseSeeds=3,
        excludedImages=0,expectedFigures=7,examples=examples,noiseExample=dict(imageId=image_id,seed=42,crop=False,contrastChange=False),
        sourceData=['ablation_summary.csv','ablation_paired_intervals.csv','noise_summary.csv','noise_paired_intervals.csv'],
        statistics='Ablation image bootstrap200; noise bootstrap10 image blocks with3 seeds. Separate corrected families10 and6.',
        exports=['PNG300dpi','PDF editable text','SVG editable text'],imageIntegrity='Native photo/mask arrays; binary edges black-on-white for display only.'))
    print('RGB_EXTRAS_FIGURES_SAVED',out)
if __name__=='__main__':main()
