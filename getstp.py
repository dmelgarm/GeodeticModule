'''
Diego Melgar 09/2013

Some tools to download geodetic module data from the caltech archive and do some
batch processing
'''

def download:
    import os, datetime, subprocess
    from numpy import genfromtxt

    #Day to download

    #Specific date
    day=13
    month=10
    year=2013

    #Today's date
    #now=datetime.date.today()-datetime.timedelta(days=2)
    #day=now.day
    #year=now.year
    #month=now.month

    #Generate file structure
    dir='/home/sopac/GM/'
    stas=genfromtxt(dir+'info/stalist.txt',dtype='str')
    #What day of year are we working on
    doy=datetime.date(year,month,day).strftime('%j')
    #Make the directory
    dir=dir+'data/'+str(year)+doy
    try:
        os.mkdir(dir)
        os.chdir(dir)
    except:
        pass
        os.chdir(dir)
        os.remove('stp_accel.log')
        os.remove('stp_gps.log')

    #get data through STP
    for k in range(stas.size):
        #Get accelerometer data
        stp= 'win GD '+stas[k]+' HN_ '+str(year)+'/'+str(month)+'/'+str(day)+',00:00:00 +1d'
        print 'STP '+stp
        pdata=subprocess.Popen('AIST2stp',stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        s='''v
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
    