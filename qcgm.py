'''
Diego Melgar 10/2013
Some tools to quality control the accelerometer, displacement and kalman filter 
outputs of the geodetic module stations.

Things in this toolbox:
    psd - computes PSD with the multitaper method
    ppsd - calcualtes probabilistic PSD
    drops - calculates number of dropouts in the time series
    var - calculates moving variance for data
'''



def psd(fname,*args):
    '''
    Read data from SAC files and get multitaper PSD estimate.
    
    Usage:
        f,P=psd(fname,K)
    
    Parameters:
        fname - Fielname to SAC file with absolute path included
        K - Time-bandwidth product, if none provided default to K=3
        f - Frequency vector at which PSD was estimated
        P - PSD values
    
    Comments:
    This requires PySpectrum to run
    http://thomas-cokelaer.info/software/spectrum/html/contents.html
    '''
    import spectools as spt
    from obspy import read as rsac
    #Did user supply time-bandiwdth?
    if len(args)==0:
        K=2.5  
    else:
        K=args[0]  
    #Read stream data and extract trace
    st=rsac(fname)
    tr=st[0]
    #Get data from the stream object
    data=tr.data
    #Get sampling rate
    dt=tr.stats.delta
    #Get time vector
    time=tr.times()
    #Compute spectrum
    f,P=spt.psdmtm(time,data,K)
    #Output and done
    return f,P
    
    
def drops(fname):
    '''
    Calcualte # of dropouts in a sac file
    
    Usage:
        d=drops(fname)
        
    parameters:
        fname - input fielname with absolute path of SAC file
        d - number of dropouts
    '''
    from obspy import read as rsac
    import numpy as np
    #Get data
    st=rsac(fname)
    data=st[0].data
    #Compute dropouts
    d=data.shape[0]-np.count_nonzero(data)
    #Return result and exit
    return d
    
def var(fname,*args):
    '''
    Compute the running variance over a sac file
    
    Usage:
        v=var(fname,tlen)
        
    parameters:
        fname - input filename with absolute path of SAC file
        tlen - length of the moving variance window in seconds, if none provided default to 120s
        v - moving variance time series
    '''
    if len(args)==0:
        tlen=120 
    else:
        tlen=args[0] 
    #Get data
    st=rsac(fname)
    data=st[0].data
    #Determine how many samples in the window
    dt=st[0].stats.delta
    N=int(tlen/dt)
    #Form 2D array for computation
    
    
        
    