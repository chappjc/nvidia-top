import subprocess as sp
import xml.etree.ElementTree as ET
import time
import curses as crs

def display_info(root, scr):

    gpunum = 0
    n = int(root.find('attached_gpus').text)

    for gpu in root.findall('gpu'):
        
        # Name
        name = gpu.find('product_name').text
        
        # Memory Use
        mem = gpu.find('memory_usage')
        if (mem == None):
            mem = gpu.find('fb_memory_usage')

        memu = mem.find('used').text
        nmemu = memu.split()
        memt = mem.find('total').text
        nmemt = memt.split()
        memuse = memu + '/' + memt
        usage = float(nmemu[0])*100/float(nmemt[0])

        # GPU Utilization
        util = gpu.find('utilization')
        gpu_util = util.find('gpu_util').text.split()
        ngpu_util = float(gpu_util[0])
        memory_util = util.find('memory_util').text.split()
        
        # Power Use
        pow = gpu.find('power_readings')
        upow = pow.find('power_draw').text
        tpow = pow.find('power_limit').text
        powuse = upow + '/' + tpow
        
        # Temp
        temp = gpu.find('temperature')
        temp = temp.find('gpu_temp').text
        
        line = '%3d' % gpunum + '%23s' % name + '%13s' % memu + '%8.2f %%' % usage + '%11.2f %%' % ngpu_util + '%12s' % upow + '%9s' % temp
        scr.addstr(gpunum+9+n, 0, line)

        gpunum = gpunum+1

# ---Main Section---

# scr = crs.initscr()

def main(scr):    
    
    #scr.nodelay(1)
    scr.keypad(1)

    try:

        width = 90

        data = sp.check_output(['nvidia-smi', '-q', '-x'])
        root = ET.fromstring(data)
        
        timestamp = root.find('timestamp').text
        driver = root.find('driver_version').text
        n = int(root.find('attached_gpus').text)
        
        scr.addstr(0, 0, 'nvidia-top' + '%*s' % (width-10, 'ESC to quit'))
        scr.addstr(1, 0, 'Timestamp:\t' + timestamp)
        scr.addstr(2, 0, 'Driver Version:\t' + driver)
        scr.addstr(3, 0, 'Number of GPUs:\t' + repr(n))

        gpus = root.findall('gpu')
        for ind in range(len(gpus)):
            memt = gpus[ind].find('fb_memory_usage').find('total').text
            scr.addstr(3+ind*2, 0, 'GPU %d Memory:  ' % ind + memt)
            powt = gpus[ind].find('power_readings').find('power_limit').text
            scr.addstr(4+ind*2, 0, 'GPU %d Power Limit:  ' % ind + powt)

        n*=2
        # Drawing header
        scr.addstr(5+n, 0, '-' * width)
        scr.addstr(6+n, 0, '%3s' % '#' + '%23s' % 'Name' + '%13s' % 'Mem. Use' + '%10s' % '% Mem.' + '%13s' % 'GPU Util.' +'%12s' % 'Power Use' + '%9s' % 'Temp.')
        scr.addstr(7+n, 0, '-' * width)
        
        # 10 tenths = 1 sec <- this is the polling frequency
        crs.halfdelay(8)
        #t0 = 0
        while (1):
            #if (time.clock() - t0) > 1.0:
            data = sp.check_output(['nvidia-smi', '-q', '-x'])
            root = ET.fromstring(data)
            
            timestamp = root.find('timestamp').text
            scr.addstr(1, 0, 'Timestamp:\t' + timestamp)
            
            display_info(root, scr)
            #t0 = time.clock()
            scr.refresh()
                
            
            if scr.getch() == 27:
                break

    except:

        print 'Something went wrong! Exception handling is pretty basic right now.'

if __name__=='__main__':
    crs.wrapper(main)

crs.endwin()
