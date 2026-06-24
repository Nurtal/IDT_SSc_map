#!/usr/bin/env python3
"""F6 — per-donor module-activation profiles -> candidate endotypes (real AUCell data)."""
import csv, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT="/home/n765/workspace/IDT_SSc_map"
rows=list(csv.DictReader(open(ROOT+"/analysis/overlay/patient_module_scores_aucell.tsv"),delimiter="\t"))
skin=[r for r in rows if r["tissue"] in ("skin","skin_gur")]

DARK="#142C3A"; TEAL="#2E8B9E"; CORAL="#E26D5A"; MUTE="#6B7A82"
M1c="#3A73B8"

fig,axes=plt.subplots(1,2,figsize=(11.6,4.5))
fig.patch.set_facecolor("white")

# --- Panel A: per-donor M1 (IFN) score, SSc vs HC (skin), shows IFN-high tail
ax=axes[0]
ssc=[float(r["M1"]) for r in skin if r["group"]=="SSc"]
hc =[float(r["M1"]) for r in skin if r["group"]=="HC"]
rng=np.random.default_rng(7)
for x0,vals,col,lab in [(0,hc,MUTE,f"HC (n={len(hc)})"),(1,ssc,CORAL,f"SSc (n={len(ssc)})")]:
    jx=x0+(rng.random(len(vals))-0.5)*0.34
    ax.scatter(jx,vals,s=26,color=col,alpha=0.75,edgecolor="white",linewidth=0.4,zorder=3,label=lab)
    ax.hlines(np.median(vals),x0-0.22,x0+0.22,color=DARK,lw=2.2,zorder=4)
thr=np.quantile(hc,0.90)
ax.axhline(thr,color=M1c,ls="--",lw=1.3,zorder=2)
ax.text(1.45,thr,"IFN-high\nthreshold",color=M1c,fontsize=9,va="center",ha="left")
n_high=sum(v>thr for v in ssc)
ax.set_xticks([0,1]); ax.set_xticklabels(["HC","SSc"],fontsize=11)
ax.set_ylabel("M1 / type-I IFN module score\n(AUCell, per donor)",fontsize=10.5,color=DARK)
ax.set_title("A.  Patients differ in interferon activation",fontsize=12,color=DARK,weight="bold",loc="left")
ax.legend(loc="lower right",fontsize=8.5,frameon=False)
ymax=max(ssc+hc)
ax.set_ylim(-ymax*0.05, ymax*1.30)
ax.text(0.5,0.965,f"{n_high}/{len(ssc)} SSc skin donors are IFN-high   ·   Gur p=3.2e-4 · Tabib p=0.011",
        transform=ax.transAxes,fontsize=8.6,color=DARK,ha="center",va="top")
for sp in ("top","right"): ax.spines[sp].set_visible(False)
ax.set_xlim(-0.6,2.2)

# --- Panel B: schematic module-profile endotypes (mean profile per group + concept)
ax=axes[1]
mods=["M1\nIFN","M2\nFibrosis","M3\nVascular","M4\nImmune"]
cols=[M1c,CORAL,"#3F9E8C","#7E5A9E"]
# two illustrative endotype profiles built from real direction of effect
ifn_high=[0.85,0.25,0.15,0.30]
fib_high=[0.30,0.80,0.55,0.45]
x=np.arange(4); w=0.38
ax.bar(x-w/2,ifn_high,w,color=[M1c]+["#c9d6e6"]*3,edgecolor=DARK,linewidth=0.5,label="IFN-dominant")
ax.bar(x+w/2,fib_high,w,color=["#f2cfc7",CORAL,"#bfe0d8","#d6c7e2"],edgecolor=DARK,linewidth=0.5,label="Fibrosis-dominant")
ax.set_xticks(x); ax.set_xticklabels(mods,fontsize=9.5)
ax.set_ylabel("module activation (illustrative)",fontsize=10.5,color=DARK)
ax.set_yticks([])
ax.set_title("B.  Module profiles define candidate endotypes",fontsize=12,color=DARK,weight="bold",loc="left")
ax.legend(loc="upper right",fontsize=9,frameon=False)
for sp in ("top","right","left"): ax.spines[sp].set_visible(False)
ax.text(0.0,-0.30,"Each patient → a 4-module activation vector. Distinct profiles → mechanism-matched endotypes\n(IFN-high → JAK/IFN axis · fibrosis-high → TGF-β/CTGF axis), recapitulating known SSc intrinsic subsets.",
        transform=ax.transAxes,fontsize=8.6,color=MUTE)

plt.tight_layout(rect=[0,0.02,1,1])
out=ROOT+"/figures/F6_endotype_profiles.png"
plt.savefig(out,dpi=200,bbox_inches="tight",facecolor="white")
print("saved",out,"| IFN-high SSc:",n_high,"/",len(ssc))
