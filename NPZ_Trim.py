## Code for the NPZ Trimmer

## Run from the command line as:
## python NPZ_Trim.py filename.npz x_min x_max y_min y_max
## Where x_min is the left boundary,
## x_max is the right boundary
## y_min is the bottom boundary
## and y_max is the top boundary

import numpy
import sys

if __name__ == '__main__':
    try:
        print 'NPZ Trim'
        
        filename = ''
        x_min = 0
        x_max = 0
        y_min = 0
        y_max = 0

        ## Everest
        #filename = 'N27E086_join.npz' # Everest
        #x_min = 487000 # 9km square
        #x_max = 496000
        #y_min = 3091700
        #y_max = 3100700

        if filename == '':
            # Check if the npz filename was passed in argv (e.g. "python NPZ_Trim.py N54W004.npz")
            if len(sys.argv) > 1: filename = sys.argv[1]
            # Check for x_min etc in argv (e.g. "python NPZ_Trim.py N54W004_join.npz 298000 363000 477000 542000")
            if len(sys.argv) > 5:
                x_min = float(sys.argv[2])
                x_max = float(sys.argv[3])
                y_min = float(sys.argv[4])
                y_max = float(sys.argv[5])

        if filename == '': filename = raw_input('Enter the npz filename: ') # Get the filename

        print 'Processing',filename

        outfile = filename[:-4] + '_trim' + filename[-4:]
        
        try:
            # read data: width, height, max_hgt, east[], north[], hgt[]
            filedata = numpy.load(filename,mmap_mode='r')
            width = int(filedata['width'])
            height = int(filedata['height'])
            hgt_max = int(filedata['hgt_max'])
            points = len(filedata['hgt']) * len(filedata['hgt'][0]) # Get the number of data points
        except:
            raise Exception('Invalid file!')

        if points != width * height: # Check we've got the right number of data points
            raise Exception('Invalid file size!')

        print 'Points:',points
        print 'Maximum height:',hgt_max
        print 'Top Left:',filedata['east'][0,0],',',filedata['north'][0,0]
        print 'Bottom Right:',filedata['east'][height-1,width-1],',',filedata['north'][height-1,width-1]

        if x_min == 0 or x_max == 0 or y_min == 0 or y_max == 0:
            x_min = float(raw_input('Enter the left boundary (x_min): '))
            x_max = float(raw_input('Enter the right boundary (x_max): '))
            y_min = float(raw_input('Enter the bottom boundary (y_min): '))
            y_max = float(raw_input('Enter the top boundary (y_max): '))
            
        print 'Trimming the data...'

        # Go through the file a line at a time looking for where the boundaries are met
        pc = 0 # percent complete
        last_pc = 0
        misses = 0
        print 'Looking for Top'
        top = 0
        for l in range(height):
            if min(filedata['north'][l,:]) >= y_max:
                top = l
                misses = 0
            else:
                misses += 1
            if misses > 5:
                break
            pc = int(100. * l / height)
            if pc > last_pc:
                print str(pc),'% Complete'
                last_pc = pc
        print 'Top:',top
        pc = 0
        last_pc = 0
        misses = 0
        print 'Looking for Bottom'
        bottom = 0
        for l in range(top,height):
            if min(filedata['north'][l,:]) >= y_min:
                bottom = l
                misses = 0
            else:
                misses += 1
            if misses > 5:
                break
            pc = int(100. * l / height)
            if pc > last_pc:
                print str(pc),'% Complete'
                last_pc = pc
        print 'Bottom:',bottom
        pc = 0
        last_pc = 0
        misses = 0
        print 'Looking for Left'
        left = 0
        for l in range(width):
            if min(filedata['east'][:,l]) <= x_min:
                left = l
                misses = 0
            else:
                misses += 1
            if misses > 5:
                break
            pc = int(100. * l / width)
            if pc > last_pc:
                print str(pc),'% Complete'
                last_pc = pc
        print 'Left:',left
        pc = 0
        last_pc = 0
        misses = 0
        print 'Looking for Right'
        right = 0
        for l in range(left,width):
            if min(filedata['east'][:,l]) <= x_max:
                right = l
                misses = 0
            else:
                misses += 1
            if misses > 5:
                break
            pc = int(100. * l / width)
            if pc > last_pc:
                print str(pc),'% Complete'
                last_pc = pc
        print 'Right:',right

        # Trim the data
        east = filedata['east'][top:bottom,left:right]
        north = filedata['north'][top:bottom,left:right]
        hgt = filedata['hgt'][top:bottom,left:right]

        # Adjust the width and height
        width = right - left
        height = bottom - top

        # Correct the number of data points
        points = len(hgt) * len(hgt[0])

        if points != width * height: # Check the new number of data points
            raise Exception('Something bad happened!')

        # Find the minimum height, ignoring invalid data points (-32768)
        hgt_min = 32767.
        for h in range(height):
            for w in range(width):
                if (hgt[h,w] < hgt_min) and (hgt[h,w] > -32768.): hgt_min = hgt[h,w]

        # Find the maximum height
        hgt_max = hgt.max()

        print 'Points:',points
        print 'Maximum height:',hgt_max
        print 'Minimum height:',hgt_min

        print 'Top Left:',int(east[0,0]),',',int(north[0,0])
        print 'Bottom Right:',int(east[height-1,width-1]),',',int(north[height-1,width-1])

        print 'Saving to',outfile

        numpy.savez(outfile, width=width, height=height, hgt_max=hgt_max, east=east, north=north, hgt=hgt)

        filedata.close()

        print 'Complete!'

    except KeyboardInterrupt:
        print 'CTRL+C received...'
     
    finally:
        print 'Bye!'

