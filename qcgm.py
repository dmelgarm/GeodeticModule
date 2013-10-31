'''
Diego Melgar 10/2013
Some tools to quality control the accelerometer, displacement and kalman filter 
outputs of the geodetic module stations.

Things in this toolbox:
    psd - computes PSD with the multitaper method
    ppsd - calcualtes probabilistic PSD
    gpsdrops - counts the number of dropouts in the gps time series
    accdrops - counts the number of dropouts in the acc. tiem series 
    var - calculates moving variance for data
    applygain - apply a simple gain correction to an ObsPy stream object
'''

#Global variables and statements
import getqc
home=getqc.home
#-------------------------------------------------------------------------------


def psd(tr,NF=256,nover=128,Fsample=1):
    '''
    Read ObsPy trace and get PSD estimate.
    
    Usage:
        f,P=psd(tr,NF,noverlap,Fs,detrend,window)
    
        tr - Input ObsPy trace
        NFFT - Will break up the time series into multipl NF segments
        nover - segments will voerlap by noverlap samples
        Fsample - No of samples epr second
        
        Returns:
        f - Frequency vector at which PSD was estimated
        P - PSD values
    '''
    from obspy.signal.spectral_estimation import fft_taper
    from matplotlib.mlab import psd as mpsd
    from matplotlib.pylab import detrend_linear
    P,f=mpsd(tr.data,NFFT=NF,Fs=Fsample,detrend=detrend_linear,window=fft_taper,noverlap=nover,
            pad_to=None,sides='onesided',scale_by_freq=True)
    # leave out first entry (offset)
    P = P[1:]
    f=f[1:]
    # working with the periods not frequencies later so reverse spectrum
    P = P[::-1]
    T=1/f[::-1]
    #Output and dones
    return T,P
    

def getppsd(tr):
    '''
    Compute proabilsitic power spectrum,it is assumed that the input data are 
    gain corrected so the instrument response is unitary and flat 
    
    Usage:
    getppsd(tr)
    
    st - ObsPy trace containing teh data
    '''
    
    import cPickle
    from obspy.signal import PPSD as ppsd
    
    #Where are the ppsd's saved?
    pdir='proc/ppsd/'
    #Get some metadata
    station=tr.stats.station
    channel=tr.stats.channel
    #What's the ppsd called
    pname=home+pdir+station+'.'+channel+'.ppsd.pkl'
    #Attempt to load ppsd
    try:
        fid=open(pname,'rb')
        P=cPickle.load(fid)
        fid.close()
    except: #ppsd doesn't exist so initalize
        print '        PPSD object doesn''t exist, instantiating...'
        paz={'sensitivity':1} #This defines the freq. response
        P=ppsd(tr.stats,paz,is_rotational_data=True,db_bins=[-150, 50, 0.5])
    #Now add day's segments
    P.add(tr)
    #Pickle
    fid=open(pname,'wb')
    cPickle.dump(P,fid)
    fid.close()
    
    
def gpsdrops(tr):
    '''
    Calcualte # of dropouts in a sac file
    
    Usage:
        d=drops(fname)
        
    parameters:
        st - ObsPy stream object with data
        d - number of dropouts
    '''
    import numpy as np
    #Get data
    data=tr.data
    #Compute dropouts
    d=data.shape[0]-np.count_nonzero(np.diff(data))
    #Return result and exit
    return d
    
    
def accdrops(tr):
    '''
    Calcualte # of dropouts in a sac file
    
    Usage:
        d=drops(fname)
        
    parameters:
        st - ObsPy trace
        object with data
        d - number of dropoutscount
    '''
    import numpy as np
    #Get data
    data=tr.data
    #Compute dropouts
    d=data.shape[0]-np.count_nonzero(data)
    #Return result and exit
    return d
    
    
def var(tr,nlen,noverlap):
    '''
    Compute the running variance over a sac file
    
    Usage:
        v=var(fname,nlen,noverlap)
        
    parameters:
        st - ObsPy trace with data
        nlen - length of the moving variance window in samples
        noverlap - how many samples overlap from window to window
        v - moving variance time series
    '''
    from numpy import var,zeros
    
    #Get data
    data=tr.data
    #Initialize
    v=zeros(data.shape)
    #Get variance
    k=0
    while True:
        v[k:k+nlen]=var(data[k:k+nlen])
        if k>=v.size-nlen: #Window has gone over time series elngth
            break
        k=k+nlen-noverlap
    #Now pad the end variances
    #v[-N+1:]=v[-N]
    return v
    
def applygain(stin,gain=1):
    '''
    Apply a simpleg ain correction to a stream object
    
    Usage:
    stout=applygain(stin,gain)
        stin - input stream object
        gain - number data will be DIVIDED by (default is 1, duh)
        stout - output stream object
    '''
    stout=stin.copy()
    tr0=stin[0]
    tr1=tr0.copy()
    tr1.data=tr1.data/gain
    stout[0]=tr1
    return stout
        

        
        