#!/usr/bin/env python

#
# System imports
#

import sys
from optparse import OptionParser
import numpy as np
import math

#===============================================================================================================
#
#  Python script to convert UAH iMet sounding files to SHARPpy format
#
#===============================================================================================================

# Extra help

myhelp = """\n

            A general run script to convert windsonde sounding files to SHARPpy format.

            Usage examples:
 
            python convert2SHARPpy_UAH_iMet.py --filename 759_001.log --stationID UAH --date 160324 --time 1515
                                                                            
         """

#==============================================================================================================
#
# Command line arguments
#
#==============================================================================================================

usage  = "usage: %prog [options] arg"
parser = OptionParser(usage)
parser.add_option( "--filename",      dest="filename",      type="string", help="sounding file name")
parser.add_option( "--stationID",     dest="stationID",     type="string", help="3 digit station ID")
parser.add_option( "--date",          dest="date",          type="string", help="date of launch in YYMMDD")
parser.add_option( "--time",          dest="time",          type="string", help="time of launch in UTC")

(options, args) = parser.parse_args()

# Check for proper file name and stationID

if options.filename == None: 
	print "\nERROR: File name not supplied...exiting\n"
	sys.exit()
else:
	filename = options.filename
	
if options.stationID == None:
	print "\nStation ID not supplied..."
	print "Using default MSU\n"
	stationID = "MSU"
else:
	stationID = options.stationID

if options.date == None:
        print "\nDate of launch not supplied...exiting"
        sys.exit()
else:
        date = options.date

if options.time == None:
        print "\nTime of launch not supplied...exiting"
        sys.exit()
else:
        time = options.time

#==============================================================================================================
#
# Convert sounding
#
#==============================================================================================================

# read in data from input file
DAT = np.genfromtxt(filename,missing_values="-----",filling_values=-9999.0)
pres=DAT[:,3]  # pressure (mb)
tc=DAT[:,0]    # temperature (C)
rh=DAT[:,2]    # relative humidity (%)
wspd=DAT[:,8]  # wind speed (knots)
wdir=DAT[:,7]  # wind direction (deg)
hght=DAT[:,4]  # height (MSL)

# determine YY,MM,DD
year=date[0:2]
month=date[2:4]
day=date[4:6]

# check for length of file
filelen=len(pres)-1
if pres[filelen] >= 400.0:
	print "\nSounding did not reach 400 mb and thus may not plot properly in SHARPpy."
	print "Creating SHARPpy sounding file anyways...\n"

# convert RH to tdc
tk=273.15+tc
esl=611.2*np.exp(17.67*(tk-273.15)/(tk-29.65))
qvs=0.6219718*esl/(pres*100-esl)
qv=(rh/100)*qvs
el=np.log((qv/0.622)*pres/(1+(qv/0.622)))
tdc=(243.5*el-440.8)/(19.48-el)

# open output file
fout = open(year + month + day + time + "_UAH_SHARPpy", "wt")

# write out SHARPpy file
fout.write("%TITLE%\n")
fout.write(stationID + " " + year + month + day + "/" + time + "\n\n");
fout.write("LEVEL  HGHT  TEMP  DWPT WDIR  WSPD\n")
fout.write("----------------------------------\n")
fout.write("%RAW%\n")
n=0
while n <= filelen:
        wdir[n] = math.degrees(wdir[n])
        if wdir[n] == 360.0: wdir[n] = 0.0
	if pres[n] <= 100.0: # only output up to 100 mb (i.e. top of SHARPpy plots)
		print "pres"
		break
	if hght[n] <= hght[n-1] and n!=0: # check that balloon is rising
		n=n+1
		continue
        fout.write("%s, %s, %s, %s, %s, %s\n" %(pres[n], hght[n], tc[n], tdc[n], wdir[n], wspd[n]))
	n=n+1
fout.write("%END%\n")
