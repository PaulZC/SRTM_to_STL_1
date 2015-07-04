## Code for the SRTM joiner

## Joins two NASA SRTM 1arcsec hgt files into a single file

## Run from the command line:
## python SRTM_Join.py filename1.hgt filename2.hgt

## The hgt filename refers to the lower left pixel or sample in the data
## Data is two byte signed integers (big endian)
## First row in the file is the ***northernmost*** one

import utm
import numpy
import sys
from scipy import *

if __name__ == '__main__':
    try:
        print 'Joining SRTM files'
        
        filename1 = ''
        filename2 = ''
        
        #filename1 = 'N27E086.hgt' # Everest S
        #filename2 = 'N28E086.hgt' # Everest N
        ## Cut at 1800

        if filename1 == '' or filename2 == '':
            # Check if the hgt filename was passed in argv
            if len(sys.argv) > 2:
                filename1 = sys.argv[1]
                filename2 = sys.argv[2]

        if filename1 == '' or filename2 == '':
            filename1 = raw_input('Enter the 1st hgt filename: ') # Get the hgt filename
            filename2 = raw_input('Enter the 2nd hgt filename: ') # Get the hgt filename

        # Find the starting lats & lons from the filenames
        start_lon1 = float(filename1[4:7])
        if filename1[3] == 'W': start_lon1 = -start_lon1
        start_lat1 = float(filename1[1:3])
        if filename1[0] == 'S': start_lat1 = -start_lat1
        start_lon2 = float(filename2[4:7])
        if filename2[3] == 'W': start_lon2 = -start_lon2
        start_lat2 = float(filename2[1:3])
        if filename2[0] == 'S': start_lat2 = -start_lat2

        # Check if files need to be joined L-R or T-B
        if start_lat1 == start_lat2:
            print 'Files have equal latitude. Joining Left-Right.'
            LR = True
            if start_lon1 < start_lon2:
                print 'File order does not need to be changed.'
            else:
                print 'Swapping file order.'
                filename = filename1 # Swap filenames
                filename1 = filename2
                filename2 = filename
        elif start_lon1 == start_lon2:
            print 'Files have equal longitude. Joining Top-Bottom.'
            LR = False
            if start_lat1 < start_lat2:
                print 'File order does not need to be changed.'
            else:
                print 'Swapping file order.'
                filename = filename1 # Swap filenames
                filename1 = filename2
                filename2 = filename
        else:
            raise Exception('Files do not have same lat or lon!')

        outfile = str(filename1[:-4] + '_join' + filename1[-4:])
        
        print 'Processing',filename1,'and',filename2
        print 'Outputting data to',outfile
        
        print 'Bottom Left: Latitude',start_lat1,'Longitude',start_lon1
        
        try:
            # read data
            hgt1 = numpy.fromfile(filename1,dtype='>i2')
        except:
            raise Exception('Invalid file1!')

        try:
            # read data
            hgt2 = numpy.fromfile(filename2,dtype='>i2')
        except:
            raise Exception('Invalid file2!')

        points1 = len(hgt1) # Get the number of points
        points2 = len(hgt2) # Get the number of points

        width = 3601 # SRTMGL1 files are 3601 * 3601
        height = 3601

        if points1 != width * height: # Check we've got the correct amount of data
            raise Exception('Invalid file1!')
        if points2 != width * height: # Check we've got the correct amount of data
            raise Exception('Invalid file2!')

        # Find the minimum height, ignoring invalid data points (-32768)
        hgt_min = 32767
        for l in range(points1):
            if (hgt1[l] < hgt_min) and (hgt1[l] > -32768): hgt_min = hgt1[l]
        for l in range(points2):
            if (hgt2[l] < hgt_min) and (hgt2[l] > -32768): hgt_min = hgt2[l]

        hgt_max = hgt1.max() # Find the maximum height
        if hgt2.max() > hgt_max: hgt_max = hgt2.max()
        
        print 'Tile size is: height',height,', width',width
        print 'Points:',points1,'+',points2
        print 'Maximum height:',hgt_max
        print 'Minimum height:',hgt_min

        # Check both files are the same size
        if points1 != points2: raise Exception('File sizes do not match!')

        # Reshape into Y,X format
        hgt1 = numpy.reshape(hgt1,(height,-1))
        hgt2 = numpy.reshape(hgt2,(height,-1))

        if LR:
            # remove duplicated column
            hgt1 = hgt1[:,:-1] 
            
            # join the data
            hgt = numpy.concatenate((hgt1,hgt2),1)

            # cut the data
            try:
                cut = int(raw_input('Which column do you want to cut from?: '))
            except:
                raise Exception('Invalid cut!')

            hgt = hgt[:,cut:(cut+width)]

        else:
            # remove duplicated row
            hgt1 = hgt1[1:,:]

            # join the data
            hgt = numpy.concatenate((hgt2,hgt1),0)

            # cut the data
            try:
                cut = int(raw_input('Which row do you want to cut from?: '))
            except:
                raise Exception('Invalid cut!')

            hgt = hgt[cut:(cut+height),:]

        hgt_max = hgt.max()

        # Convert back to a 1D array
        hgt = numpy.ravel(hgt)

        print 'Saving to',outfile
        fp = open(outfile,'wb')
        for i in hgt:
            fp.write(i.astype('>i2').byteswap())
        fp.close()

        print 'Complete!'
        print

        if cut > 0:
            cuts = str(cut / 3600.).rstrip("0")
            print 'When you run SRTM_to_NPZ.py you will need to enter:'
            if LR:
                print 'Latitude offset 0.0'
                print 'Longitude offset',cuts
            else:
                print 'Latitude offset',cuts
                print 'Longitude offset 0.0'
        print

    except KeyboardInterrupt:
        print 'CTRL+C received...'
     
    finally:
        print 'Bye!'

