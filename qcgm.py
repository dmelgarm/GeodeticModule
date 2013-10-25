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
'''

#some global variables

gain=1e6


def psd(tr,*args):
    '''
    Read data from SAC files and get multitaper PSD estimate.
    
    Usage:
        f,P=psd(fname,K)
    
    Parameters:
        st - ObsPy trace with data
        K - Time-bandwidth product, if none provided default to K=3
        f - Frequency vector at which PSD was estimated
        P - PSD values
    
    Comments:
    This requires PySpectrum to run
    http://thomas-cokelaer.info/software/spectrum/html/contents.html
    '''
    import spectools as spt
    from numpy import mean
    #Did user supply time-bandiwdth?
    if len(args)==0:
        K=2.5  
    else:
        K=args[0]  
    #Get data from the trace
    data=tr.data
    #Scale to SI
    data=data
    #Get sampling rate
    dt=tr.stats.delta
    #Get time vector
    time=tr.times()
    time=time
    #Compute spectrum
    f,P=spt.psdmtm(time,data,K)
    #Output and done
    return f,P
    
    
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
    #Scale to SI units
    data=data/gain
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
        

        
        