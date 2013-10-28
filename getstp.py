'''
Diego Melgar 09/2013

Some tools to download geodetic module data from the caltech archive and do some
batch processing
'''

def download(day,month,year,reset=False):
    '''
    Use AISTstp and AIST2stp to access SCEDC nad fetch geodetic module data
    day - day to download
    month - month to download
    year - year to download
    reset - True to download data again fi it already exists, False to leave it 
            alone if it already exists
    '''
    import os, datetime, subprocess
    from numpy import genfromtxt
    from shutil import rmtree


    #Today's date
    #now=datetime.date.today()-datetime.timedelta(days=1)
    #day=now.day
    #year=now.year
    #month=now.month

    #Get working directory and station list
    dir='/home/sopac/GM/'
    stas=genfromtxt(dir+'info/stalist.txt',dtype='str')
    #What day of year are we working on
    doy=datetime.date(year,month,day).strftime('%j')
    #Data directory
    dir=dir+'data/'+str(year)+doy
    try:
        os.mkdir(dir)
        imdone=False #Doesn't exist, download the data
    except: #Folder exists already, delete or keep?
        if reset==True: #Hard reset, delete and remake directory
            rmtree(dir)
            os.mkdir(dir)
            imdone=False
        else:
            print 'Folder '+dir+' exists and you requested a soft reset, exiting...'
            imdone=True
    if not imdone: #Go get the data
        os.chdir(dir)
        #get data through STP
        for k in range(stas.size):
            #Get accelerometer data
            stp= 'win GD '+stas[k]+' HN_ '+str(year)+'/'+str(month)+'/'+str(day)+',00:00:00 +1d'
            print 'STP '+stp
            pdata=subprocess.Popen('AIST2stp',stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            s='''v
gain on
%s
quit''' % stp
            out,err=pdata.communicate(s)
            #Write log
            f=open('stp_accel.log','a')
            f.write(out)
            f.write(err)
            f.close()
            #Get GPS data
            stp= 'win GD '+stas[k]+' LY_ '+str(year)+'/'+str(month)+'/'+str(day)+',00:00:00 +1d'
            print 'STP '+stp
            pdata=subprocess.Popen('AISTstp',stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            s='''v
%s
quit''' % stp
            out,err=pdata.communicate(s)
            #Write log
            f=open('stp_gps.log','a')
            f.write(out)
            f.write(err)
            f.close()
            
def getmany():
    '''
    Batch download a bunch of data
    '''
    import numpy as np
    day=np.arange(1,25,1)
    month=10*np.ones(day.shape)
    year=2013*np.ones(day.shape)
    #Make integers
    day=day.astype(int)
    month=month.astype(int)
    year=year.astype(int)
    for k in range(len(day)):
        download(day[k],month[k],year[k],reset=True)