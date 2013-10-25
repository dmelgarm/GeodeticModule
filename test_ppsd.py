import obspy
import obspy.signal
import qcgm
from matplotlib import pyplot as plt
from numpy import log10
from matplotlib.mlab import psd as shittypsd

#data='/Users/dmelgarm/scripts/Python/GM/data/2013294/20131021000000.GD.DESC.HNE.sac'
data='/Users/dmelgarm/scripts/Python/GM/data/2013293/20131020000000.GD.P494.LYZ.sac'
st=obspy.read(data)
st.detrend('demean')
tr0=st[0]
tstart=tr0.stats.starttime
tr1=tr0.copy()
#tr1.trim(tstart+(6*3600),tstart+(7*3600))
tr1.data=tr1.data/1e6
st[0]=tr1
#f,P=qcgm.psd(tr1,15)
#dB=10*log10(P)

plt.close("all")
#plt.figure()
#plt.semilogx(f,dB)

shittyP,shittyf=shittypsd(st[0].data,Fs=100)
shittydB=10*log10(shittyP)
plt.figure()
plt.semilogx(shittyf,shittydB)

paz={'sensitivity':1}
ppsd=obspy.signal.PPSD(tr1.stats,paz,is_rotational_data=True,db_bins=[-80, 20, 0.5])
ppsd.add(st)

ppsd.plot()

