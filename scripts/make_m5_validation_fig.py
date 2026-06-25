#!/usr/bin/env python3
"""F7 — validation of module M5 (B-cell / autoreactivity).
Panel A: B/plasma-restricted AUCell, SSc vs HC (real, from committed scores).
Panel B: GSE45536 whole-blood M5 sub-signatures (values from M5_validation.md,
reproducible via scripts/validate_m5_gse45536.py)."""
import csv, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT="/home/n765/workspace/IDT_SSc_map"
DARK="#142C3A"; CORAL="#E26D5A"; MUTE="#6B7A82"; M4c="#7E5A9E"; GREEN="#3F9E8C"; BLUE="#3A73B8"

# Panel A data (real)
rows=[r for r in csv.DictReader(open(ROOT+"/analysis/overlay/patient_module_scores_bplasma_aucell.tsv"),delimiter="\t")
      if r["dataset"]=="gse195452"]
ssc=[float(r["M5"]) for r in rows if r["group"]=="SSc"]
hc =[float(r["M5"]) for r in rows if r["group"]=="HC"]

fig,(axA,axB)=plt.subplots(1,2,figsize=(11.8,4.6)); fig.patch.set_facecolor("white")

rng=np.random.default_rng(3)
for x0,vals,col,lab in [(0,hc,MUTE,f"HC (n={len(hc)})"),(1,ssc,CORAL,f"SSc (n={len(ssc)})")]:
    jx=x0+(rng.random(len(vals))-0.5)*0.34
    axA.scatter(jx,vals,s=30,color=col,alpha=0.8,edgecolor="white",linewidth=0.4,zorder=3,label=lab)
    axA.hlines(np.median(vals),x0-0.22,x0+0.22,color=DARK,lw=2.4,zorder=4)
axA.set_xticks([0,1]); axA.set_xticklabels(["HC","SSc"],fontsize=11)
axA.set_ylabel("M5 AUCell (B/plasma compartment)",fontsize=11,color=DARK)
axA.set_title("A.  Skin scRNA-seq — B/plasma compartment",fontsize=12,color=DARK,weight="bold",loc="left")
axA.legend(loc="upper right",fontsize=9,frameon=False)
ymax=max(ssc+hc); axA.set_ylim(-ymax*0.05,ymax*1.28)
axA.text(0.02,0.97,"M5 SSc>HC, p=0.046\n(only significant module)",transform=axA.transAxes,
         ha="left",va="top",fontsize=9,color=DARK)
for s in ("top","right"): axA.spines[s].set_visible(False)
axA.set_xlim(-0.6,1.6)

# Panel B data (GSE45536, from M5_validation.md)
labels=["Autoantigens\n(TOP1,CENPB)","Plasma-cell core\n(PRDM1/XBP1/BCMA…)","B-surface\n(CD19/20/79/22)","M1 / IFN\n(control)"]
delta=[+1.07,-0.43,-0.34,+0.42]; pv=["1.7e-10","2e-6","1.8e-3","3.8e-5"]
cols=[CORAL,M4c,BLUE,GREEN]
y=np.arange(len(labels))[::-1]
axB.barh(y,delta,color=cols,edgecolor=DARK,linewidth=0.5)
axB.axvline(0,color=DARK,lw=0.8)
for yi,d,p in zip(y,delta,pv):
    axB.text(d+(0.04 if d>0 else -0.04),yi,f"p={p}",va="center",ha="left" if d>0 else "right",fontsize=8.5,color=DARK)
axB.set_yticks(y); axB.set_yticklabels(labels,fontsize=9)
axB.set_xlabel("Δ mean z-score (SSc − HC)",fontsize=11,color=DARK)
axB.set_title("B.  External bulk cohort GSE45536 (99 SSc / 24 HC, blood)",fontsize=12,color=DARK,weight="bold",loc="left")
axB.set_xlim(-0.9,1.4)
for s in ("top","right"): axB.spines[s].set_visible(False)
axB.text(0.0,-0.22,"Autoantibody targets ↑ in SSc; circulating B/plasma abundance ↓ (lymphopenia). IFN control ↑, as expected.",
         transform=axB.transAxes,fontsize=8.3,color=MUTE)

plt.tight_layout(rect=[0,0.03,1,1])
out=ROOT+"/figures/F7_M5_validation.png"
plt.savefig(out,dpi=200,bbox_inches="tight",facecolor="white")
print("saved",out)
