'''
D.Melgar 10-2013
Tools to batch compute the qc metrics for the GM data
'''

#--------------           Global variables and statements      -----------------
home='/home/sopac/GM/'
gpsgain=1e6 #Because at SCEDC it is stored in micrometers (I know right?)
accgain=1
varlen=120 #Moving varaince widnow length in s
varover=varlen/2 #Moving variance overlap between windows
#-------------------------------------------------------------------------------


#---------------             Batch Processing Rotuines       -------------------
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
       qc(day[k],month[k],year[k],dovar=False,dopsd=True,doppsd=True,reset=False)
       qcplots(day[k],month[k],year[k],
            reset=False,
            dataplot=False,
            varplot=False,
            specplot=True)
            
#-------------------------------------------------------------------------------



#---------------------      QC Computations            -------------------------
def qc(day,month,year,dovar=True,dopsd=True,doppsd=True,reset=True):
    '''
    Compute QC metrics for all files in one days worth of data
    All variables EXCEPT the PPSD are save in a individual .npz files that sgould be 
    stored under a daily folder. The PPSD gets updated  every day so there is only
    a single file.
    '''
    import datetime,qcgm,os,cPickle
    from glob import glob
    from obspy.core import read
    from shutil import rmtree
    from numpy import savez,vstack
    
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
            if dovar or dopsd or doppsd:
                imdone=False
            else:
                print procdir+' Nothing to do, exiting...'
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
                psdtr=st[0].copy()  #Used for psd computations
            elif st[0].stats.channel[1]=='Y':#GPS
                print ' -- Channel is GPS'
                st=qcgm.applygain(st,gpsgain)
                NFFT=256
                noverlap=NFFT/2
                Fs=1/st[0].stats.delta
                #Differentiate to acceleration for psd
                psdtr=st[0].copy()
                agps=gps2accel(psdtr.data,psdtr.stats.delta)
                psdtr.data=agps
            #Now do all the metrics
            if dovar:
                #Compute moving variance
                print '        Computing moving variance'
                Nt=1/st[0].stats.delta
                v=qcgm.var(st[0],varlen*Nt,varover*Nt)
                #save to pickle
                fid=open(procdir+st[0].stats.station+'.'+st[0].stats.channel+
                                                            '.var.pkl','wb')
                st[0].data=v
                if st[0].stats.channel[1]=='N':#Accel decimate
                    st[0].decimate(100,no_filter=True)
                cPickle.dump(st,fid)
                fid.close()
            if dopsd:
                #compute usual psd
                print '        Computing PSD'
                T,P=qcgm.psd(psdtr,NF=NFFT,nover=noverlap,Fsample=Fs)
                #save to npz file
                fid=open(procdir+st[0].stats.station+'.'+st[0].stats.channel+
                                                            '.psd.npz','wb')
                savez(fid,T=T,P=P)
                fid.close()
            #Compute PPSD
            if doppsd:
                print '        computing PPSD'
                qcgm.getppsd(psdtr)
                
#-------------------------------------------------------------------------------

                    
#--------------------           QC Plots         ------------------------------- 
                                    
def qcplots(day,month,year,
    dataplot=True,
    varplot=True,
    specplot=True,
    reset=False):
    '''
    Make the QC plots and save to daily directory
    '''
    
    import os,datetime,cPickle,glob,qcgm
    import matplotlib.pyplot as pl
    from shutil import rmtree
    from numpy import load,log10
    from obspy.core import read
    
    pl.close("all")
    doy=datetime.date(year,month,day).strftime('%j')
    #Define directories
    datadir=home+'data/'+str(year)+doy+'/'
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
            if dataplot or varplot or specplot:
                imdone=False
            else:
                print 'Folder '+plotdir+' nothing to plot, exiting...'
                imdone=True
    if not imdone: #Make the plots
        if dataplot:
            #Which files?
            iolist=glob.glob(datadir+'*.sac')
            for k in range(len(iolist)):
                print  '..P.. plotting time series for '+iolist[k]
                savefile=plotdir+iolist[k][-12:-4]+'.dataplot.png'
                #Get data
                st=read(iolist[k])
                #Correct gain
                if iolist[k][-6]=='N':
                    st=qcgm.applygain(st,accgain)
                    yunits='(m/s^2)'
                else:
                    st=qcgm.applygain(st,gpsgain)
                    yunits='(m)'
                #plot
                pl.close("all")
                F=pl.figure(figsize=(12, 4))
                st.plot(fig=F)
                pl.ylabel(yunits)
                pl.grid()
                pl.savefig(savefile, bbox_inches=0)
        if varplot: #Make variances plot
            iolist=glob.glob(procdir+'*.var.pkl')
            for k in range(len(iolist)):
                print  '..P.. plotting variance for '+iolist[k]
                savefile=plotdir+iolist[k][-16:-8]+'.varplot.png'
                #Get varaince
                stv=cPickle.load(open(iolist[k],'rb'))
                pl.close("all")
                Fv=pl.figure(figsize=(12, 4))
                stv.plot(fig=Fv)
                pl.ylabel('Variance')
                pl.grid(which='both')
                yl=pl.ylim()
                pl.ylim((0,yl[1]))
                pl.savefig(savefile, bbox_inches=0)
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
                pl.close("all")
                savefile=plotdir+ppsd.station+'.'+ppsd.channel+'.psdplot.png'
                #Make ppsd
                ppsd.plot(show=False,show_percentiles=True,show_noise_models=False)
                ax=pl.figure(1).axes[0]
                pl.sca(ax)
                #Add days PSD
                pl.semilogx(T,10*log10(P),color='black',linewidth=2,alpha=0.8)
                #Change percentiles
                pl.setp(ax.lines[0:5],linestyle='--',linewidth=2.5,color='black',alpha=0.7)
                #Set limits
                if pfile[0][-11]=='Y': #GPS limits
                    pl.xlim((2,200))
                    pl.ylim((-150,0))
                elif pfile[0][-11]=='N': #Accel limits
                    pl.xlim((0.02,300))
                    pl.ylim((-150,0))
                #Add legend
                pl.legend([ax.lines[0],ax.lines[5]],['Percentiles','Today''s PSD'],loc=4,ncol=2)
                pl.savefig(savefile, bbox_inches=0)
                pl.close("all")
        pass
    pass

#-------------------------------------------------------------------------------


#------------               Web Page Management               ------------------

def serve1day(day,month,year):
    '''
    Update site with data from one particular day
    '''
    #Update index
    addday2index(day,month,year)   
    #Make site pages and link to index
    linkdaypages(day,month,year)
    


def addday2index(day,month,year):
    '''
    Add one line of stations tot eh index
    '''
    
    import datetime
    
    doy=datetime.date(year,month,day).strftime('%j')
    indexpage='/var/www/index.html'
    #Read in template web page and replace patterns
    s = open(indexpage).read()
    #add dummy line
    s = s.replace('<p>Available data:</p></br>','''<p>Available data:</p></br>YYYY-MM-DD 
<a href="daypages/YYYYDDD/DESC.html">DESC</a>
<a href="daypages/YYYYDDD/GLRS.html">GLRS</a>
<a href="daypages/YYYYDDD/HNPS.html">HNPS</a>
<a href="daypages/YYYYDDD/P482.html">P482</a>
<a href="daypages/YYYYDDD/P483.html">P483</a>
<a href="daypages/YYYYDDD/P484.html">P484</a>
<a href="daypages/YYYYDDD/P486.html">P486</a>
<a href="daypages/YYYYDDD/P491.html">P491</a>
<a href="daypages/YYYYDDD/P494.html">P494</a>
<a href="daypages/YYYYDDD/P505.html">P505</a>
<a href="daypages/YYYYDDD/P506.html">P506</a>
<a href="daypages/YYYYDDD/P797.html">P797</a>
<a href="daypages/YYYYDDD/PIN2.html">PIN2</a>
<a href="daypages/YYYYDDD/PMOB.html">PMOB</a>
<a href="daypages/YYYYDDD/POTR.html">POTR</a>
<a href="daypages/YYYYDDD/RAAP.html">RAAP</a>
<a href="daypages/YYYYDDD/SIO5.html">SIO5</a>
<a href="daypages/YYYYDDD/SLMS.html">SLMS</a>
<a href="daypages/YYYYDDD/USGC.html">USGC</a></br>''')
    #Now add day and month and year
    s=s.replace('YYYY-MM-DD',str(year)+'-'+str(month)+'-'+str(day))
    s=s.replace('YYYYDDD',str(year)+doy)
    #save as new page
    f = open(indexpage, 'w')
    f.write(s)
    f.close()
    
def linkdaypages(day,month,year):
    '''
    Make day pages for each station and copy plots
    '''
    
    from numpy import genfromtxt
    
    stationlist=home+'info/'+'stalist.txt'
    stas=genfromtxt(stationlist,dtype='str')
    for k in range(len(stas)):
        makedaypage(day,month,year,stas[k])
        
            
def makedaypage(day,month,year,station):
    '''
    Make daily page for one station and copy plots to desired directory
    '''
    import datetime,os,glob,shutil
    
    doy=datetime.date(year,month,day).strftime('%j')
    daypage='/var/www/daypages/mainday.html'
    daydir='/var/www/daypages/'+str(year)+doy+'/'
    stationpage=daydir+station+'.html'
    plotdir='/home/sopac/GM/plots/'+str(year)+doy+'/'
    #Make directory for webpage
    try:
        os.mkdir(daydir)
    except:
        pass
    #Read in template web page and replace patterns
    s = open(daypage).read()
    #station name
    s = s.replace('Station ####', 'Station '+station)
    #date
    s = s.replace('YYYY/MM/DD', str(year)+'/'+str(month)+'/'+str(day))
    #name of plot files
    s = s.replace('SSSS.', station+'.')
    #save as new page
    f = open(stationpage, 'w')
    f.write(s)
    f.close()
    #Now station plots to this dir
    plotlist=glob.glob(plotdir+station+'*')
    for k in range(len(plotlist)):
        shutil.copy(plotlist[k], daydir)
        

    

            
            
            
#----------               MINOR NUMERICAL  TOOLS                   -------------
    
def gps2accel(d,dt):
    '''
    Differentiate gps to acceleration
    '''
    from numpy import gradient
    v=gradient(d,dt)
    a=gradient(v,dt)
    return a