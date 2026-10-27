"""Data-grounded full200 score/interval figures and predeclared examples."""
import numpy as np
import pandas as pd
from scipy.io import loadmat
from scipy.sparse import issparse
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from prepare_course_rgb_main200 import RUN,METHODS,read,dump
LABELS=['RGB FFT + phase gate','Gray FFT + phase','Sobel','Canny','Ideal high-pass','Gaussian high-pass']
COLORS=['#369271','#65717a','#9b94a8','#407da1','#bd7646','#bc9a71']

def save(fig,path):
    for ext in ['png','pdf','svg']:fig.savefig(path.with_suffix('.'+ext),dpi=300,bbox_inches='tight',facecolor='white')
    plt.close(fig)

def main():
    assert read(RUN/'final_status.json')['status']=='complete'
    out=RUN/'figures';out.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],'font.size':10,
        'svg.fonttype':'none','pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'legend.frameon':False})
    s=pd.read_csv(RUN/'fixed_summary.csv').set_index('method');pairs=pd.read_csv(RUN/'paired_intervals.csv')
    lock=read(RUN/'parameters_locked.json');metrics=['precision','recall','f1']
    fig,axes=plt.subplots(1,3,figsize=(11.6,4.5),sharey=True)
    for j,k in enumerate(metrics):
        ax=axes[j]
        for y,(m,color) in enumerate(zip(METHODS,COLORS)):
            r=s.loc[m];ax.plot([r[k+'Low95']*100,r[k+'High95']*100],[y,y],color=color,lw=1.7)
            ax.plot(r[k]*100,y,'o',color=color,ms=6 if m=='rgb_main' else 5)
        ax.set(yticks=range(6),yticklabels=LABELS,ylim=(5.6,-.6),xlabel='Score (%)')
        ax.set_title(f'{chr(97+j)}  '+['Precision','Recall','Pooled F1'][j],loc='left',fontweight='bold',fontsize=11)
        ax.grid(axis='x',alpha=.15)
    fig.suptitle('Complete BSDS500 test split: 200 images, six frozen pipelines',fontsize=12,y=1.01)
    fig.text(.5,-.025,'Pooled official matching counts; 95% image-bootstrap intervals; 20,000 paired resamples. Historical test images.',ha='center',fontsize=8)
    fig.tight_layout(w_pad=2);save(fig,out/'test200_fixed_scores')
    fig,axes=plt.subplots(1,3,figsize=(11.6,4.5),sharey=True)
    for j,k in enumerate(metrics):
        ax=axes[j];ax.axvline(0,color='#999999',ls='--',lw=.9)
        for y,(base,color) in enumerate(zip(METHODS[1:],COLORS[1:])):
            r=pairs[(pairs.comparator==base)&(pairs.metric==k)].iloc[0]
            lo=r.low95 if k=='recall' else r.low995;hi=r.high95 if k=='recall' else r.high995
            ax.plot([lo*100,hi*100],[y,y],color=color,lw=1.7);ax.plot(r.delta*100,y,'o',color=color,ms=5)
        ax.set(yticks=range(5),yticklabels=['vs '+x for x in LABELS[1:]],ylim=(4.6,-.6),xlabel='Difference (percentage points)')
        ax.set_title(f'{chr(97+j)}  '+['Precision','Recall','Pooled F1'][j],loc='left',fontweight='bold',fontsize=11);ax.grid(axis='x',alpha=.15)
    fig.suptitle('RGB main minus each frozen comparison: paired changes on all 200 images',fontsize=12,y=1.01)
    fig.text(.5,-.025,'Precision/F1: 99.5% CI (10 primary contrasts, Bonferroni). Recall: descriptive 95% CI. 20,000 paired image resamples.',ha='center',fontsize=8)
    fig.tight_layout(w_pad=2);save(fig,out/'test200_paired_changes')
    records={r['id']:r for r in read(RUN/'manifest.json')['records']};examples=[]
    for image_id in lock['figures']['exampleIds']:
        r=records[image_id];z=loadmat(RUN/'samples'/f'{image_id}.mat',simplify_cells=True)
        image=np.asarray(Image.open(r['image']));gt=loadmat(r['reference'],simplify_cells=True)['groundTruth']
        if isinstance(gt,dict):gt=[gt]
        union=np.logical_or.reduce([g['Boundaries'].toarray() if issparse(g['Boundaries']) else g['Boundaries'] for g in gt])
        panels=[image,union,*list(z['masks'])];titles=['Original RGB','GT union (display only)',*LABELS]
        fig,axes=plt.subplots(2,4,figsize=(13.0,7.0))
        for j,(ax,array,title) in enumerate(zip(axes.flat,panels,titles)):
            ax.imshow(array,**({} if j==0 else dict(cmap='gray_r',vmin=0,vmax=1)),interpolation='nearest')
            ax.set_xticks([]);ax.set_yticks([]);ax.set_title(title,fontsize=9.5,pad=7)
            for spine in ax.spines.values():spine.set_visible(False)
            if j>=2:
                score=z['rows'][j-2];ax.set_xlabel(f'P {score["precision"]*100:.1f}% | R {score["recall"]*100:.1f}% | F1 {score["f1"]*100:.1f}%',fontsize=8)
        fig.suptitle(image_id+' | Fixed example, native resolution',fontsize=12,y=.995)
        fig.text(.5,.005,'GT union is for display; all scores use the official matcher against each original annotation.',ha='center',fontsize=8)
        fig.tight_layout(rect=[0,.025,1,.97],w_pad=.7,h_pad=1.6);save(fig,out/(image_id+'_six_methods'))
        examples.append(dict(imageId=image_id,crop=False,photometricChanges=False,groundTruth='Union display only; original individual labels for scoring.',
                             source=r['image'],reference=r['reference'],sample=str(RUN/'samples'/f'{image_id}.mat')))
    # RGB frequency/response mechanism plate for the first predeclared image.
    image_id=lock['figures']['exampleIds'][0];z=loadmat(RUN/'samples'/f'{image_id}.mat',simplify_cells=True);e=z['example']
    fig,axes=plt.subplots(2,3,figsize=(11.5,7.1))
    arrays=[e['logSpectra'][:,:,c] for c in range(3)]+[e['seedResponse'],e['linkResponse'],z['masks'][0]]
    titles=['R: log FFT magnitude','G: log FFT magnitude','B: log FFT magnitude','Strong-seed response','Phase-gated weak-link response','Final RGB main edges']
    for j,(ax,array,title) in enumerate(zip(axes.flat,arrays,titles)):
        if j==5:ax.imshow(array,cmap='gray_r',vmin=0,vmax=1,interpolation='nearest')
        else:ax.imshow(array,cmap='gray',vmin=0,vmax=float(np.max(array)) if np.max(array)>0 else 1,interpolation='nearest')
        ax.set_title(title,fontsize=10);ax.set_xticks([]);ax.set_yticks([])
        for spine in ax.spines.values():spine.set_visible(False)
    fig.suptitle(image_id+' | RGB ordinary 2D FFT and phase gating',fontsize=12,y=.995)
    fig.tight_layout(rect=[0,0,1,.965],w_pad=1,h_pad=2);save(fig,out/'test200_rgb_spectra_and_responses')
    dump(out/'figure_contract_and_qa.json',dict(status='rendered_pending_visual_check',backend='python',
        conclusion='Quantify all200 fixed-parameter pipelines and paired differences; examples explain outputs, not dataset superiority.',
        archetypes=['quantitative grid','image plate + quant'],images=200,methods=6,excludedImages=0,expectedFigures=6,
        sourceData=['fixed_metrics.csv','fixed_summary.csv','paired_intervals.csv'],examples=examples,
        exports=['PNG300dpi','PDF editable text','SVG editable text'],
        imageIntegrity='Native arrays; no cropping or photo contrast change; edge display black-on-white; each spectrum individually scaled for display only.',
        statistics='Pooled counts; paired image bootstrap20000; marginal95%; ten P/F1 differences corrected99.5%; Recall95% descriptive.'))
    print('RGB200_FIGURES_SAVED',out)
if __name__=='__main__':main()
