'''
D.Melgar 10-2013
Tools to batch compute the qc metrics for the GM data
'''

#Global variables and statements
home='/home/sopac/GM/'
gpsgain=1e6 #Because at SCEDC it is stored in micrometers (I know right?)
accgain=1




def qc(day,month,year,dopsd=True,doppsd=True,reset=True):
    '''
    Compute QC metrics for all files in one days worth of data
    All variables EXCEPT the PPSD are save in a individual .npz files that sgould be 
    stored under a daily folder. The PPSD gets updated  every day so there is only
    a single file.
    '''
    import datetime,qcgm,os
    from glob import glob
    from obspy.core import read
    from shutil import rmtree
    from numpy import savez
    
    doy=datetime.date(year,month,day).strftime('%j')
    #Data directory
    datadir=home+'data/'+str(year)+doy+'/'
    procdir=home+'proc/'+str(year)+doy+'/'
    #Try to make the daily proc directory
    try:
        print 'procdir not found, creating it...'
        os.mkdir(procdir)
        imdone=False #Doesn't exist, continue procing
    except: #Folder exists already, delete or keep?
        if reset==True: #Hard reset, delete and remake directory
            print 'procdir exists but you requested a hard reset, deleting...'
            rmtree(procdir)
            os.mkdir(procdir)
            imdone=False
        else:
            print procdir+' exists and you requested a soft reset, exiting...'
            imdone=True
    if not imdone: #Get going
        #get list of files to be processed
        files=glob(datadir+'*.sac')
        
        for k in range(len(files)):
            print 'Working on file '+files[k]
            st=read(files[k])
            
            #Which type of instruemnt is it? apply gain and define some numbers
            if st[0].stats.channel[1]=='N':#Accel
                print ' -- Channel is strong motion'
                st=qcgm.applygain(st,accgain)
                NFFT=2**18
                noverlap=NFFT/2
                Fs=1/st[0].stats.delta
            elif st[0].stats.channel[1]=='Y':#GPS
                print ' -- Channel is GPS'
                st=qcgm.applygain(st,gpsgain)
                NFFT=256
                noverlap=NFFT/2
                Fs=1/st[0].stats.delta
                
            #Now do all the metrics
            #compute usual psd
            if dopsd:
                print '        Computing PSD'
                T,P=qcgm.psd(st[0],NF=NFFT,nover=noverlap,Fsample=Fs)
                #save to npz file
                fid=open(procdir+st[0].stats.station+'.'+st[0].stats.channel+
                                                            '.psd.npz','wb')
                savez(fid,T=T,P=P)
                fid.close()
            #Compute PPSD
            if doppsd:
                print '        computing PPSD'
                qcgm.getppsd(st[0])
                
    
            
                    
                                    
def qcplots(day,month,year,specplot=True,reset=False):
    '''
    Make the QC plots and save to daily directory
    '''
    
    import os,datetime,cPickle,glob
    from shutil import rmtree
    from numpy import load,log10
    import matplotlib.pyplot as pl
    
    pl.close("all")
    doy=datetime.date(year,month,day).strftime('%j')
    #Define directories
    plotdir=home+'plots/'+str(year)+doy+'/'
    procdir=home+'proc/'+str(year)+doy+'/'
    ppsddir=home+'proc/ppsd/'
    #Try to make directory
    try:
        os.mkdir(plotdir)
        imdone=False #Doesn't exist, make the plots
    except: #Folder exists already, delete or keep?
        if reset==True: #Hard reset, delete and remake directory
            rmtree(plotdir)
            os.mkdir(plotdir)
            imdone=False
        else:
            print 'Folder '+plotdir+' exists and you requested a soft reset, exiting...'
            imdone=True
    if not imdone: #Make the plots
        if specplot:
            #Read in file list
            iolist=glob.glob(procdir+'*.psd.npz')
            for k in range(len(iolist)):
                print  '..P.. plotting spectra for '+iolist[k]
                #Load psd
                iobuff=load(iolist[k])
                T=iobuff['T']
                P=iobuff['P']
                #load ppsd (get station and channel from psd file)
                pfile=glob.glob(ppsddir+iolist[k][-16:-8]+'*')
                ppsd=cPickle.load(open(pfile[0],'rb'))
                #Make plot and save
                savefile=plotdir+pfile[0][-17:-9]+'.psdplot.png'
                #Make ppsd
                ppsd.plot(show=False,show_percentiles=True,show_noise_models=False)
                ax=pl.figure(1).axes[0]
                pl.sca(ax)
                #Add days PSD
                pl.semilogx(T,10*log10(P),color='black',linewidth=3,alpha=0.6)
                #Change percentiles
                pl.setp(ax.lines[0:5],linestyle='--',linewidth=4,color='#708090',alpha=0.6)
                #Set limits
                if pfile[0][-11]=='Y': #GPS limits
                    pl.xlim((2,200))
                    pl.ylim((-100,20))
                elif pfile[0][-11]=='N': #GPS limits
                    pl.xlim((0.02,300))
                    pl.ylim((-150,-20))
                #Add legend
                pl.legend([ax.lines[0],ax.lines[5]],['Percentiles','Today''s PSD'],loc=4,ncol=2)
                pl.savefig(savefile, bbox_inches=0)
                pl.close("all")
        pass
    pass

                

                
                
            
            
            
def batchqc():
    import numpy as np
    day=np.arange(1,25,1)
    month=10*np.ones(day.shape)
    year=2013*np.ones(day.shape)
    #Make integers
    day=day.astype(int)
    month=month.astype(int)
    year=year.astype(int)
    for k in range(len(day)):
       qc(day[k],month[k],year[k],dopsd=True,doppsd=True,reset=True)
       qcplots(day[k],month[k],year[k],reset=True)



        
    
