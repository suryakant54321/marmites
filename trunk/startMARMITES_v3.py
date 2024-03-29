﻿# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        startMARMITES
# Purpose:
#
# Author:      frances08512
#
# Created:     25-11-2010
# Copyright:   (c) frances08512 2010
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

""" See info in MARMITESsoil_v3.py"""

__author__ = "Alain P. Francés <frances.alain@gmail.com>"
__version__ = "0.3"
__date__ = "2012"

import sys, os, h5py, shutil, glob, itertools
from win32com.shell import shell, shellcon
import matplotlib as mpl
if mpl.get_backend!='agg':
    mpl.use('agg')
import matplotlib.pyplot as plt
plt.ioff()
import numpy as np
import startMARMITESsurface as startMMsurf
import MARMITESsoil_v3 as MMsoil
import ppMODFLOW_flopy_v3 as ppMF
import MARMITESplot_v3 as MMplot
import MARMITESutilities as MMutils
#import MARMITESprocess_v3 as MMproc

# TODO verify if thickness of MF layer 1 > thickness of soil

#####################################

timestart = mpl.dates.datestr2num(mpl.dates.datetime.datetime.today().isoformat())
fmt_DH = mpl.dates.DateFormatter('%Y-%m-%d %H:%M')
print '\n##############\nMARMITES v0.3 started!\n%s\n##############' % mpl.dates.DateFormatter.format_data(fmt_DH, timestart)

cUTIL = MMutils.clsUTILITIES(fmt = fmt_DH)

# workspace (ws) definition
# read input file (called _input.ini in the MARMITES workspace
# the first character on the first line has to be the character used to comment
# the file can contain any comments as the user wish, but the sequence of the input has to be respected
# 00_TESTS\MARMITESv3_r13c6l2  00_TESTS\r40c20  00_TESTS\r20c40  r130c60l2   r130c60l2new
# SARDON2013  CARRIZAL3 CARRIZAL3newera LAMATA LaMata_new
startMM_fn = shell.SHGetFolderPath (0, shellcon.CSIDL_DESKTOP, 0, 0)
inputFile = cUTIL.readFile(startMM_fn, 'startMM_fn.txt')

try:
    MM_ws = str(inputFile[0].strip())
    MM_ini_fn = str(inputFile[1].strip())
except:
    cUTIL.ErrorExit(msg = '\nFATAL ERROR!\nInput ini MM file [%s] is not correct.' % inputFile)

inputFile = cUTIL.readFile(MM_ws,MM_ini_fn)

l=0
try:
    # run_name
    run_name = inputFile[l].strip()
    l += 1
    fmt_DHshort = mpl.dates.DateFormatter('%Y%m%d%H%M')
    MM_ws_out = os.path.join(MM_ws,'out_%s_%s'% (mpl.dates.DateFormatter.format_data(fmt_DHshort, timestart), run_name))
    f = 1
    if os.path.exists(MM_ws_out):
        MM_ws_out1 = MM_ws_out
        while os.path.exists(MM_ws_out1):
            MM_ws_out1 = os.path.join(MM_ws,'out_%s_%s_%s' % (mpl.dates.DateFormatter.format_data(fmt_DHshort, timestart), run_name, f))
            f +=1
        os.makedirs(MM_ws_out1)
        MM_ws_out = MM_ws_out1
        del MM_ws_out1
    else:
        os.makedirs(MM_ws_out)
    # # ECHO ON/OFF (1 - interpreter verbose BUT NO report, 0 - NO interpreter verbose BUT report)
    verbose = int(inputFile[l].strip())
    l += 1
    # output plot (1 is YES, 0 is NO)
    plt_out  = int(inputFile[l].strip())
    l += 1
    plt_freq =  int(inputFile[l].strip())
    l += 1
    nrangeMM =  int(inputFile[l].strip())
    l += 1
    nrangeMF =  int(inputFile[l].strip())
    l += 1
    ctrsMM =  int(inputFile[l].strip())
    if ctrsMM == 1:
        ctrsMM = True
    else:
        ctrsMM = False
    l += 1
    ctrsMF =  int(inputFile[l].strip())
    if ctrsMF == 1:
        ctrsMF = True
    else:
        ctrsMF = False
    l += 1
    ntick =  int(inputFile[l].strip())
    l += 1
    animation =  int(inputFile[l].strip())
    l += 1
    animation_freq = int(inputFile[l].strip())
    l += 1
    # export time series/water balance at observation points and catch. scale?  (1 is YES, 0 is NO)
    plt_out_obs = int(inputFile[l].strip())
    l += 1
    # water balance Sankey plot (1 is YES, 0 is NO)
    WBsankey_yn = int(inputFile[l].strip())
    l += 1    
    # define if unit of the water balance plots are in mm/day or mm/year
    # value MUST be 'year' or 'day'
    plt_WB_unit = inputFile[l].strip()
    if plt_WB_unit == 'year':
        facTim = 365.0
    else:
        facTim = 1.0
    l += 1
    # starting month of the hydrologic year (integer value between 1 and 12)
    iniMonthHydroYear = int(inputFile[l].strip())
    if iniMonthHydroYear < 1 or iniMonthHydroYear > 12:
        print '\nWARNING!\nInvalid starting month of the hydrologic year. Please correct your input (currently %d) to a value between 1 and 12 inclusive. The starting month was now defined as October (10).' % iniMonthHydroYear
        iniMonthHydroYear = 10
    l += 1
    # map of inputs (1 is YES, 0 is NO)
    plt_input = int(inputFile[l].strip())
    l += 1
    #run MARMITESsurface  (1 is YES, 0 is NO)
    MMsurf_yn = int(inputFile[l].strip())
    l += 1
    #plot MARMITESsurface  (1 is YES, 0 is NO)
    MMsurf_plot = int(inputFile[l].strip())
    l += 1
    #run MARMITESsoil  (1 is YES, 0 is NO)
    MMsoil_yn = int(inputFile[l].strip())
    l += 1
    #run MODFLOW  (1 is YES, 0 is NO)
    MF_yn = int(inputFile[l].strip())
    l += 1
    MF_lastrun = int(inputFile[l].strip())
    l += 1
    # MM-MF loop
    convcrit = float(inputFile[l].strip())
    l += 1
    convcritmax = float(inputFile[l].strip())
    l += 1
    ccnum = int(inputFile[l].strip())
    l += 1
    # Define MARMITESsurface folder
    MMsurf_ws = inputFile[l].strip()
    l += 1
    # METEO/VEGETATION/SOIL/WATER PARAMETERS file name
    inputFile_PAR_fn = inputFile[l].strip()
    l += 1
    # METEO TIME SERIES file name
    inputFile_TS_fn = inputFile[l].strip()
    l += 1
    # OPTIONNAL IRRIGATION FILES
    irr_yn = int(inputFile[l].strip())
    if irr_yn == 1 :
        l += 1
        inputFile_TSirr_fn = inputFile[l].strip()
        l += 1
        gridIRR_fn = inputFile[l].strip()
        l += 1
    else:
        l += 3
    # ouputprefix
    outputFILE_fn = inputFile[l].strip()
    l += 1
    # ZONEVEGSOILfile
    outMMsurf_fn = inputFile[l].strip()
    l += 1
    # Define MODFLOW ws folders
    MF_ws = inputFile[l].strip()
    l += 1
    MF_ini_fn = inputFile[l].strip()
    l += 1
    #GRID (ll means lower left)
    xllcorner = float(inputFile[l].strip())
    l += 1
    yllcorner = float(inputFile[l].strip())
    l += 1
    gridMETEO_fn = inputFile[l].strip()
    l += 1
    gridSOIL_fn = inputFile[l].strip()
    l += 1
    gridSOILthick_fn = inputFile[l].strip()
    l += 1
    gridSsurfhmax_fn =  inputFile[l].strip()
    l += 1
    gridSsurfw_fn =  inputFile[l].strip()
    l += 1
    SOILparam_fn = inputFile[l].strip()
    l += 1
    inputObs_fn = inputFile[l].strip()
    l += 1
    inputObsHEADS_fn = inputFile[l].strip()
    l += 1
    inputObsSM_fn = inputFile[l].strip()
    l += 1
    inputObsRo_fn = inputFile[l].strip()
    l += 1
    rmseHEADSmax  = float(inputFile[l].strip())
    l += 1
    rmseSMmax  = float(inputFile[l].strip())
    l += 1
    chunks = int(inputFile[l].strip())
    if MMsoil_yn != 0:
        MF_yn = 1
    if MMsurf_plot == 1:
        plt_out = 0
        plt_out_obs = 0
        print "\nYou required the MMsurf plots to appear on the screen. Due to backends limitation, MM and MF plots were disabled. Run again MM with MMsurf_plot = 0 to obtain the MM and MF plots."
    if animation == 1:
        if MF_yn == 1:
            print '\nWARNING!\nIt is not currently possible to create animation if MODFLOW is running. Please run MM-MF, set them to 0 and run MM again with animation set to 1.'
            animation = 0
        else:
            test_ffmpeg = cUTIL.which(program = 'ffmpeg.exe')
            if test_ffmpeg == None:
                print '\nWARNING!\nFFmpeg was not found on your computer!\nSpatial animations will not be produced.\nYou can solve this problem downloading FFmpeg at www.ffmpeg.org and install it.'
                animation = 0
            del test_ffmpeg
except:
    cUTIL.ErrorExit(msg = '\nFATAL ERROR!\nType error in the input file %s' % MM_ini_fn)

del inputFile

# copy MM ini file into MM output folder
shutil.copy2(os.path.join(MM_ws,MM_ini_fn), os.path.join(MM_ws_out,'__%s%s'% (mpl.dates.DateFormatter.format_data(fmt_DHshort, timestart), MM_ini_fn)))
# copy MF ini file into MM output folder
shutil.copy2(os.path.join(MM_ws, MF_ws,MF_ini_fn), os.path.join(MM_ws_out,'__%s%s'% (mpl.dates.DateFormatter.format_data(fmt_DHshort, timestart), MF_ini_fn)))
# copy MMsurf ini file into MM output folder
shutil.copy2(os.path.join(MM_ws, MMsurf_ws,inputFile_PAR_fn), os.path.join(MM_ws_out,'__%s%s'% (mpl.dates.DateFormatter.format_data(fmt_DHshort, timestart), inputFile_PAR_fn)))
# copy MM soil parameters file into MM output folder
shutil.copy2(os.path.join(MM_ws, SOILparam_fn), os.path.join(MM_ws_out,'__%s__%s'% (mpl.dates.DateFormatter.format_data(fmt_DHshort, timestart), SOILparam_fn.split('\\')[-1])))
# copy MM input asc file
files = glob.iglob(os.path.join(MM_ws, "*.asc"))
path_out = os.path.join(MM_ws_out, 'MM_asc')
os.makedirs(path_out)
for file in files:
    if os.path.isfile(file):
        shutil.copy2(file, path_out)
# copy MF input asc file
files = glob.iglob(os.path.join(MM_ws, MF_ws, "*.asc"))
path_out = os.path.join(MM_ws_out, 'MF_asc')
os.makedirs(path_out)
for file in files:
    if os.path.isfile(file):
        shutil.copy2(file, path_out) 
del path_out, file, files

if verbose == 0:
# capture interpreter output to be written in to a report file
    report_fn = os.path.join(MM_ws_out,'__%s_MMMFrun_report.txt' % (mpl.dates.DateFormatter.format_data(fmt_DHshort, timestart)))
    print '\nECHO OFF (no screen output).\nSee the report of the MM-MF run in file:\n%s\n' % report_fn
    stdout = sys.stdout
    report = open(report_fn, 'w')
    sys.stdout = report
    print '\n##############\nMARMITES v0.3 started!\n%s\n##############' % mpl.dates.DateFormatter.format_data(fmt_DH, timestart)
    cUTIL = MMutils.clsUTILITIES(fmt = fmt_DH, verbose = verbose, report_fn = report_fn)
else:
    report = None
    stdout = None

MMsurf_ws = os.path.join(MM_ws,MMsurf_ws)
MF_ws = os.path.join(MM_ws,MF_ws)
if os.path.exists(MM_ws):
    if os.path.exists(MMsurf_ws):
        if os.path.exists(MF_ws):
            print ('\nMARMITES workspace:\n%s\n\nMARMITESsurf workspace:\n%s\n\nMODFLOW workspace:\n%s' % (MM_ws, MMsurf_ws, MF_ws))
        else:
            print "The folder %s doesn't exist!\nPlease create it and run the model again." % (MF_ws)
    else:
        print "The folder %s doesn't exist!\nPlease create it and run the model again." % (MMsurf_ws)
else:
    print "The folder %s doesn't exist!\nPlease create it and run the model again." % (MM_ws)

# #############################
# 1st phase: INITIALIZATION #####
# #############################

# #############################
# ###  MARMITES surface  ######
# #############################
print'\n##############'
print 'MARMITESsurf RUN'
if MMsurf_yn>0:
    durationMMsurf = 0.0
    timestartMMsurf = mpl.dates.datestr2num(mpl.dates.datetime.datetime.today().isoformat())
    if irr_yn == 1 :
        outMMsurf_fn = startMMsurf.MMsurf(cUTIL, MMsurf_ws, inputFile_TS_fn, inputFile_PAR_fn, outputFILE_fn, MM_ws, outMMsurf_fn, MMsurf_plot, inputFile_TSirr_fn)
    else:
        outMMsurf_fn = startMMsurf.MMsurf(cUTIL, MMsurf_ws, inputFile_TS_fn, inputFile_PAR_fn, outputFILE_fn, MM_ws, outMMsurf_fn, MMsurf_plot)
    timeendMMsurf = mpl.dates.datestr2num(mpl.dates.datetime.datetime.today().isoformat())
    durationMMsurf=(timeendMMsurf-timestartMMsurf)
inputFile = cUTIL.readFile(MM_ws,outMMsurf_fn)
l=0
VegName = []
Zr = []
kT_min = []
kT_max = []
kT_n = []
try:
    NMETEO = int(inputFile[l].strip())
    l += 1
    NVEG = int(inputFile[l].strip())
    l += 1
    NSOIL = int(inputFile[l].strip())
    l += 1
    inputDate_fn = str(inputFile[l].strip())
    l += 1
    inputZON_dSP_RF_veg_fn = str(inputFile[l].strip())
    l += 1
    inputZON_dSP_RFe_veg_fn = str(inputFile[l].strip())
    l += 1
    inputZON_dSP_PT_fn = str(inputFile[l].strip())
    l += 1
    input_dSP_LAI_veg_fn = str(inputFile[l].strip())
    l += 1
    inputZON_dSP_PE_fn = str(inputFile[l].strip())
    l += 1
    inputZON_dSP_E0_fn = str(inputFile[l].strip())
    l += 1
    line = inputFile[l].split()
    for v in range(NVEG):
        VegName.append((line[v]))
    l += 1
    line = inputFile[l].split()
    for v in range(NVEG):
        Zr.append(float(line[v]))
    l += 1
    line = inputFile[l].split()
    for v in range(NVEG):
        kT_min.append(float(line[v]))
    l += 1
    line = inputFile[l].split()
    for v in range(NVEG):
        kT_max.append(float(line[v]))
    l += 1
    line = inputFile[l].split()
    for v in range(NVEG):
        kT_n.append(float(line[v]))
    if irr_yn == 1:
        l += 1
        NCROP = int(inputFile[l].strip())
        l += 1
        NFIELD = int(inputFile[l].strip())
        l += 1
        inputZON_dSP_RF_irr_fn = str(inputFile[l].strip())
        l += 1
        inputZON_dSP_RFe_irr_fn = str(inputFile[l].strip())
        l += 1
        inputZON_dSP_PT_irr_fn = str(inputFile[l].strip())
        l += 1
        Zr_c = []
        kT_min_c = []
        kT_max_c = []
        kT_n_c = []
        line = inputFile[l].split()
        for c in range(NCROP):
            Zr_c.append(float(line[c]))
        Zr_c = np.asarray(Zr_c)
        l += 1
        line = inputFile[l].split()
        for c in range(NCROP):
            kT_min_c.append(float(line[c]))
        kT_min_c = np.asarray(kT_min_c)
        l += 1
        line = inputFile[l].split()
        for c in range(NCROP):
            kT_max_c.append(float(line[c]))
        kT_max_c = np.asarray(kT_max_c)
        l += 1
        line = inputFile[l].split()
        for c in range(NCROP):
            kT_n_c.append(float(line[c]))
        kT_n_c = np.asarray(kT_n_c)
        l += 1
        input_dSP_crop_irr_fn = str(inputFile[l].strip())
except:
    cUTIL.ErrorExit('\nFATAL ERROR!\Error in reading file [%s].' % outMMsurf_fn, stdout = stdout, report = report)

del inputFile
numDays = len(cUTIL.readFile(MM_ws, inputDate_fn))

# Compute hydrologic year start and end dates

inputFile_fn = os.path.join(MM_ws, inputDate_fn)    
if os.path.exists(inputFile_fn):
    date = np.loadtxt(inputFile_fn, skiprows = 1, dtype = str, delimiter = ',')[:,0]
else:
    cUTIL.ErrorExit(msg = "\nFATAL ERROR!\nThe input file [" + inputFile_fn + "] doesn't exist, verify name and path!", stdout = stdout, report = report)
DATE = np.zeros(len(date), dtype = float)
for i, d in enumerate(date):
    DATE[i] = mpl.dates.datestr2num(d)
del date

year_lst = []
HYindex = []
if mpl.dates.num2date(DATE[0]).month<iniMonthHydroYear or (mpl.dates.num2date(DATE[0]).month == iniMonthHydroYear and mpl.dates.num2date(DATE[0]).day == 1):
    year_lst.append(mpl.dates.num2date(DATE[0]).year)
else:
    year_lst.append(mpl.dates.num2date(DATE[0]).year + 1)
HYindex.append(np.argmax(DATE[:] == mpl.dates.datestr2num('%d-%d-01' % (year_lst[0], iniMonthHydroYear))))

if sum(DATE[:] == mpl.dates.datestr2num('%d-%d-01' % (year_lst[0]+1, iniMonthHydroYear)))==0:
    HYindex.append(HYindex[0])
    HYindex.append(len(DATE)-1)
    HYindex.append(len(DATE)-1)
    print '\nWARNING!\nThe data file does not contain a full hydrological year!'
else:
    y = 0    
    while DATE[-1] >= mpl.dates.datestr2num('%d-%d-01' % (year_lst[y]+1, iniMonthHydroYear)):
        if iniMonthHydroYear == 1:
            iniMonth_prev = 12
            add = 0
        else:
            iniMonth_prev = iniMonthHydroYear - 1
            add = 1
        indexend = np.argmax(DATE[:] == mpl.dates.datestr2num('%d-%d-30' % (year_lst[y]+add, iniMonth_prev)))
        if DATE[-1] >= mpl.dates.datestr2num('%d-%d-30' % (year_lst[y]+2, iniMonth_prev)):
            year_lst.append(year_lst[y]+1)
            HYindex.append(np.argmax(DATE[:] == mpl.dates.datestr2num('%d-%d-01' % (year_lst[y]+1, iniMonthHydroYear))))
            indexend = np.argmax(DATE[:] == mpl.dates.datestr2num('%d-%d-30' % (year_lst[y]+2, iniMonth_prev)))
            y += 1
        else:
            break
    HYindex.append(indexend)
    HYindex.insert(0, 0)
    HYindex.append(len(DATE)-1)
    del indexend, iniMonth_prev
        
#    print year_lst
#    print index
print '-------\nStarting date of time series:\n%s' % mpl.dates.DateFormatter.format_data(fmt_DH, DATE[HYindex[0]])
print '-------\nStarting date of hydrological year(s):'
for j in HYindex[1:-2]:
    print mpl.dates.DateFormatter.format_data(fmt_DH, DATE[j])
print 'End date of last hydrological year:'
print mpl.dates.DateFormatter.format_data(fmt_DH, DATE[HYindex[-2]])
print '-------\nEnd date of time series:\n%s' % mpl.dates.DateFormatter.format_data(fmt_DH, DATE[HYindex[-1]])

# #############################
# ###  READ MODFLOW CONFIG ####
# #############################
print'\n##############'
print 'MODFLOW initialization'
durationMF = 0.0
timestartMF = mpl.dates.datestr2num(mpl.dates.datetime.datetime.today().isoformat())
cMF = ppMF.clsMF(cUTIL, MM_ws, MM_ws_out, MF_ws, MF_ini_fn, xllcorner, yllcorner, numDays = numDays, stdout = stdout, report = report)
# compute cbc conversion factor from volume to mm
if cMF.lenuni == 1:
    conv_fact = 304.8
    lenuni_str = 'feet'
elif cMF.lenuni == 2:
    conv_fact = 1000.0
    lenuni_str = 'm'
elif cMF.lenuni == 3:
    conv_fact = 10.0
    lenuni_str = 'cm'
else:
    cUTIL.ErrorExit('\nFATAL ERROR!\nDefine the length unit in the MODFLOW ini file!\n (see USGS Open-File Report 00-92)', stdout = stdout, report = report)
    # TODO if lenuni!=2 apply conversion factor to delr, delc, etc...
if cMF.laytyp[0]==0:
    cUTIL.ErrorExit('\nFATAL ERROR!\nThe first layer cannot be confined type!\nChange the laytyp parameter in the MODFLOW lpf/upw package.\n(see USGS Open-File Report 00-92)', stdout = stdout, report = report)
if cMF.itmuni != 4:
    cUTIL.ErrorExit('\nFATAL ERROR!\nTime unit is not in days!', stdout = stdout, report = report)
else:
    itmuni_str = 'day'
if cMF.wel_yn == 0:
    print '\nWARNING!\nWEL package inactive: ETg, Eg and Tg will not be computed.'    

ncell_MF = []
ncell_MM = []
cMF.outcropL = np.zeros((cMF.nrow, cMF.ncol), dtype = int)
mask_tmp = np.zeros((cMF.nrow, cMF.ncol), dtype = int)
mask = []
mask_Lsup = np.zeros((cMF.nrow, cMF.ncol), dtype = int)
for l in range(cMF.nlay):
    mask_Lsup += np.asarray(cMF.ibound)[l,:,:]
    ncell_MF.append((np.asarray(cMF.ibound)[l,:,:] != 0).sum())
    ncell_MM.append((mask_Lsup*np.asarray(cMF.ibound)[l,:,:] == 1).sum())
    iboundBOL = (np.asarray(cMF.ibound)[l,:,:] != 0)
    mask.append(np.ma.make_mask(iboundBOL-1))
    mask_tmp += (np.asarray(cMF.ibound)[l,:,:] != 0)
    cMF.outcropL += ((cMF.outcropL == 0) & (iboundBOL == 1))*(l+1)    
cMF.maskAllL = (mask_tmp == 0)
del iboundBOL, mask_tmp
timeendMF = mpl.dates.datestr2num(mpl.dates.datetime.datetime.today().isoformat())
durationMF +=  timeendMF-timestartMF

# #############################
# ### MF time processing
# #############################
# if required by user, compute nper, perlen,etc based on RF analysis in the METEO zones
if isinstance(cMF.nper, str):
    try:
        perlenmax = int(cMF.nper.split()[1].strip())
    except:
        cUTIL.ErrorExit('\nFATAL ERROR!\nError in nper format of the MODFLOW ini file!', stdout = stdout, report = report)
if irr_yn == 0:
    cMF.ppMFtime(inputDate_fn, inputZON_dSP_RF_veg_fn, inputZON_dSP_RFe_veg_fn, inputZON_dSP_PT_fn,input_dSP_LAI_veg_fn, inputZON_dSP_PE_fn, inputZON_dSP_E0_fn, NMETEO, NVEG, NSOIL, stdout = stdout, report = report)
else:
    cMF.ppMFtime(inputDate_fn, inputZON_dSP_RF_veg_fn, inputZON_dSP_RFe_veg_fn, inputZON_dSP_PT_fn, input_dSP_LAI_veg_fn, inputZON_dSP_PE_fn, inputZON_dSP_E0_fn, NMETEO, NVEG, NSOIL, inputZON_dSP_RF_irr_fn, inputZON_dSP_RFe_irr_fn, inputZON_dSP_PT_irr_fn, input_dSP_crop_irr_fn, NFIELD, stdout = stdout, report = report)
# make list of day/stress period
sp_days_lst = []
for i in range(len(cMF.perlen)):
    for t in range(cMF.perlen[i]):
        sp_days_lst.append(i+1)

print'\n##############'
print 'MARMITESsoil initialization'
MM_SOIL = MMsoil.clsMMsoil(hnoflo = cMF.hnoflo)
MM_SATFLOW = MMsoil.SATFLOW()

# READ input ESRI ASCII rasters
print "\nImporting ESRI ASCII files to initialize MARMITES..."
gridMETEO = cMF.cPROCESS.inputEsriAscii(grid_fn = gridMETEO_fn, datatype = int, stdout = None, report = None)
gridSOIL = cMF.cPROCESS.inputEsriAscii(grid_fn = gridSOIL_fn, datatype = int, stdout = None, report = None)
gridSOILthick = cMF.cPROCESS.inputEsriAscii(grid_fn = gridSOILthick_fn, datatype = float, stdout = None, report = None)
gridSsurfhmax = cMF.cPROCESS.inputEsriAscii(grid_fn = gridSsurfhmax_fn, datatype = float, stdout = None, report = None)
gridSsurfw = cMF.cPROCESS.inputEsriAscii(grid_fn = gridSsurfw_fn, datatype = float, stdout = None, report = None)
if irr_yn == 1:
    gridIRR = cMF.cPROCESS.inputEsriAscii(grid_fn = gridIRR_fn, datatype = int, stdout = None, report = None)
    if gridIRR.max() > NFIELD:
        cUTIL.ErrorExit('\nFATAL ERROR!\nThere is more fields in the asc file than in the MMsurf file!', stdout = stdout, report = report)

# READ input time series and parameters
if irr_yn == 0:
    gridVEGarea, RF_veg_zoneSP, E0_zonesSP, PT_veg_zonesSP, RFe_veg_zonesSP, LAI_veg_zonesSP, PE_zonesSP = cMF.cPROCESS.inputSP(
                                NMETEO                   = NMETEO,
                                NVEG                     = NVEG,
                                NSOIL                    = NSOIL,
                                nper                     = cMF.nper,
                                inputZON_SP_RF_veg_fn    = cMF.inputZON_SP_RF_veg_fn,
                                inputZON_SP_RFe_veg_fn   = cMF.inputZON_SP_RFe_veg_fn,
                                inputZON_SP_LAI_veg_fn   = cMF.inputZON_SP_LAI_veg_fn,
                                inputZON_SP_PT_fn        = cMF.inputZON_SP_PT_fn,
                                inputZON_SP_PE_fn        = cMF.inputZON_SP_PE_fn,
                                inputZON_SP_E0_fn        = cMF.inputZON_SP_E0_fn,
                                stdout = None, report = None)
else:
    gridVEGarea, RF_veg_zoneSP, E0_zonesSP, PT_veg_zonesSP, RFe_veg_zonesSP, LAI_veg_zonesSP, PE_zonesSP, RF_irr_zoneSP, RFe_irr_zoneSP, PT_irr_zonesSP, crop_irr_SP = cMF.cPROCESS.inputSP(
                                NMETEO                   = NMETEO,
                                NVEG                     = NVEG,
                                NSOIL                    = NSOIL,
                                nper                     = cMF.nper,
                                inputZON_SP_RF_veg_fn    = cMF.inputZON_SP_RF_veg_fn,
                                inputZON_SP_RFe_veg_fn   = cMF.inputZON_SP_RFe_veg_fn,
                                inputZON_SP_LAI_veg_fn   = cMF.inputZON_SP_LAI_veg_fn,
                                inputZON_SP_PT_fn        = cMF.inputZON_SP_PT_fn,
                                inputZON_SP_PE_fn        = cMF.inputZON_SP_PE_fn,
                                inputZON_SP_E0_fn        = cMF.inputZON_SP_E0_fn,
                                NFIELD                   = NFIELD,
                                inputZON_SP_RF_irr_fn    = cMF.inputZON_SP_RF_irr_fn,
                                inputZON_SP_RFe_irr_fn   = cMF.inputZON_SP_RFe_irr_fn,
                                inputZON_SP_PT_irr_fn    = cMF.inputZON_SP_PT_irr_fn,
                                input_SP_crop_irr_fn     = cMF.input_SP_crop_irr_fn,
                                stdout = None, report = None)

# SOIL PARAMETERS
_nsl, _nam_soil, _st, _slprop, _Sm, _Sfc, _Sr, _S_ini, _Ks = cMF.cPROCESS.inputSoilParam(SOILparam_fn = SOILparam_fn, NSOIL = NSOIL, stdout = None, report = None)
_nslmax = max(_nsl)
for l in range(NSOIL):
    _slprop[l] = np.asarray(_slprop[l])

# compute thickness, top and bottom elevation of each soil layer
cMF.elev = np.ma.masked_values(np.asarray(cMF.elev), cMF.hnoflo, atol = 0.09)
cMF.top = np.ma.masked_values(cMF.elev, cMF.hnoflo, atol = 0.09) - np.ma.masked_values(gridSOILthick, cMF.hnoflo, atol = 0.09)
cMF.botm = np.asarray(cMF.botm)
cMF.LandSurface = np.zeros(cMF.elev.shape, dtype = np.float16) 
for l in range(cMF.nlay):
    cMF.botm[l,:,:] = np.ma.masked_values(cMF.botm[l,:,:], cMF.hnoflo, atol = 0.09) - np.ma.masked_values(gridSOILthick, cMF.hnoflo, atol = 0.09)
    cMF.LandSurface += cMF.top*(np.asarray(cMF.iuzfbnd) == l+1)
cMF.botm = np.ma.masked_values(cMF.botm, cMF.hnoflo, atol = 0.09)
botm_l0 = np.asarray(cMF.botm)[0,:,:]

# create MM array
h5_MM_fn = os.path.join(MM_ws,'_h5_MM.h5')
# indexes of the HDF5 output arrays
index_MM = {'iRF':0, 'iPT':1, 'iPE':2, 'iRFe':3, 'iSsurf':4, 'iRo':5, 'iEXFg':6, 'iEsurf':7, 'iMB':8, 'iI':9, 'iE0':10, 'iEg':11, 'iTg':12, 'idSsurf':13, 'iETg':14, 'iETsoil':15, 'iSsoil_pc':16, 'idSsoil':17, 'iperc':18, 'ihcorr':19, 'idgwt':20, 'iuzthick':21, 'iInf':22, 'iMBsurf':23}
index_MM_soil = {'iEsoil':0, 'iTsoil':1,'iSsoil_pc':2, 'iRsoil':3, 'iExf':4, 'idSsoil':5, 'iSsoil':6, 'iSAT':7, 'iMB':8}

# READ observations time series (heads and soil moisture)
print "\nReading observations time series (hydraulic heads and soil moisture)..."
obs, obs_list, obs_catch, obs_catch_list = cMF.cPROCESS.inputObs(
                              inputObs_fn      = inputObs_fn,
                              inputObsHEADS_fn = inputObsHEADS_fn,
                              inputObsSM_fn    = inputObsSM_fn,
                              inputObsRo_fn    = inputObsRo_fn,
                              inputDate        = cMF.inputDate,
                              _nslmax          = _nslmax,
                              nlay             = cMF.nlay,
                              stdout = stdout, report = report
                              )
i = []
j = []
lay = []
lbl = []
for o_ref in obs_list:
    for o in obs.keys():
        if o == o_ref:
            i.append(obs.get(o)['i']+1)
            j.append(obs.get(o)['j']+1)
            lay.append(obs.get(o)['lay'])
            lbl.append(obs.get(o)['lbl'])
obs4map = [lbl, i, j, lay]
if cMF.uzf_yn == 1:
    cMF.uzf_obs(obs = obs)

# EXPORT INPUT MAPS
if plt_input == 1:
    ibound = np.asarray(cMF.ibound)
    print'\n##############'
    print 'Exporting input maps...'
    i_lbl = 1
    T = np.zeros((cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
    hk_actual_tmp = cMF.cPROCESS.float2array(cMF.hk_actual)
    if cMF.nlay > 1:
        T = hk_actual_tmp * np.asarray(cMF.thick)
    else:
        T[0,:,:] = hk_actual_tmp * np.asarray(cMF.thick[0,:,:])
    top_tmp = np.zeros((cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
    top_tmp[0,:,:] = cMF.top
    for l in range(1,cMF.nlay):
        top_tmp[l,:,:] = cMF.botm[l-1,:,:]
    lst = [cMF.elev, top_tmp, cMF.botm, cMF.thick, np.asarray(cMF.strt), gridSOILthick, gridSsurfhmax, gridSsurfw, np.asarray(cMF.hk_actual), T, np.asarray(cMF.ss_actual), np.asarray(cMF.sy_actual), np.asarray(cMF.vka_actual)]
    lst_lbl = ['elev', 'top', 'botm', 'thick', 'strt', 'gridSOILthick', 'gridSsurfhmax', 'gridSsurfw', 'hk', 'T', 'Ss', 'Sy', 'vka']
    lst_lblCB = ['Elev.', 'Aq. top - $top$', 'Aq. bot. - $botm$', 'Aq. thick.', 'Init. heads - $strt$', 'Soil thick.', 'Max. stream heigth', 'Stream width', 'Horizontal hydraulic cond. - $hk$', 'Transmissivity - $T$','Specific storage - $S_s$', 'Specific yield - $S_y$', 'Vertical hydraulic cond. - $vka$']
    if cMF.drn_yn == 1:
        lst.append(cMF.drn_cond_array)
        lst_lbl.append('drn_cond')
        lst_lblCB.append('Drain cond.')
        lst.append(cMF.drn_elev_array)
        lst_lbl.append('drn_elev')
        lst_lblCB.append('Drain elev.')
    if cMF.ghb_yn == 1:
        lst.append(cMF.ghb_cond_array)
        lst_lbl.append('ghb_cond')
        lst_lblCB.append('GHB cond.')
        lst.append(cMF.ghb_head_array)
        lst_lbl.append('ghb_head')
        lst_lblCB.append('GHB head')
    if cMF.uzf_yn == 1:
        lst.append(np.asarray(cMF.eps_actual))
        lst_lbl.append('eps')
        lst_lblCB.append('Epsilon - $eps$')
        lst.append(np.asarray(cMF.thts_actual))
        lst_lbl.append('thts')
        lst_lblCB.append('Sat. water content - $thts$')
        if cMF.iuzfopt == 1:
            lst.append(np.asarray(cMF.vks_actual))
            lst_lbl.append('vks')
            lst_lblCB.append('Sat. vert. hydraulic conductivity - $vks$')
        lst.append(np.asarray(cMF.thti_actual))
        lst_lbl.append('thti')
        lst_lblCB.append('Initial water content - $thti$')
        lst.append(np.asarray(cMF.thtr_actual))
        lst_lbl.append('thtr')
        lst_lblCB.append('Residual water content - $thtr$')
    elev_max = []
    elev_min = []
    for e in [cMF.elev, cMF.top, cMF.botm]:
        elev_max.append(np.max(e))
        elev_min.append(np.min(e))
    elev_max = max(elev_max)
    elev_min = min(elev_min)
    for i, l in enumerate(lst):
        V = np.zeros((1, cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
        Vmax = []
        Vmin = []
        mask_tmp = np.zeros((cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
        for L in range(cMF.nlay):
            if l.shape == (cMF.nlay, cMF.nrow, cMF.ncol) or l.shape == (cMF.nrow, cMF.ncol):
                try:
                    V[0,L,:,:] = l[L,:,:]
                    mask_tmp[L,:,:] = mask[L]
                    Vmax.append(np.ma.max(np.ma.masked_values(np.ma.masked_array(V[0,L,:,:], mask[L]), cMF.hnoflo, atol = 0.09)))
                    Vmin.append(np.ma.min(np.ma.masked_values(np.ma.masked_array(V[0,L,:,:], mask[L]), cMF.hnoflo, atol = 0.09)))
                    nplot = cMF.nlay
                except:
                    V[0,L,:,:] = l
                    mask_tmp[L,:,:] = cMF.maskAllL
                    Vmax.append(np.ma.max(np.ma.masked_values(np.ma.masked_array(V[0,L,:,:], cMF.maskAllL), cMF.hnoflo, atol = 0.09)))
                    Vmin.append(np.ma.min(np.ma.masked_values(np.ma.masked_array(V[0,L,:,:], cMF.maskAllL), cMF.hnoflo, atol = 0.09)))
                    nplot = 1
            elif l.shape != ():
                V[0,L,:,:] = l[L]*ibound[L,:,:]
                mask_tmp[L,:,:] = mask[L]
                Vmax.append(np.ma.max(np.ma.masked_values(np.ma.masked_array(V[0,L,:,:], mask[L]), cMF.hnoflo, atol = 0.09)))
                Vmin.append(np.ma.min(np.ma.masked_values(np.ma.masked_array(V[0,L,:,:], mask[L]), cMF.hnoflo, atol = 0.09)))
                nplot = cMF.nlay
            else:
                V[0,L,:,:] = l*np.invert(cMF.maskAllL)
                mask_tmp[L,:,:] = cMF.maskAllL
                Vmax.append(np.ma.max(np.ma.masked_values(np.ma.masked_array(V[0,L,:,:], cMF.maskAllL), cMF.hnoflo, atol = 0.09)))
                Vmin.append(np.ma.min(np.ma.masked_values(np.ma.masked_array(V[0,L,:,:], cMF.maskAllL), cMF.hnoflo, atol = 0.09)))
                nplot = 1
        if lst_lbl[i] == 'Ss' or lst_lbl[i] == 'hk' or lst_lbl[i] == 'T' or lst_lbl[i] == 'drn_cond' or lst_lbl[i] == 'ghb_cond' or lst_lbl[i] == 'vks':
            fmt = '%5.e'
        elif lst_lbl[i] == 'Sy' or lst_lbl[i] == 'thts' or lst_lbl[i] == 'thti' or lst_lbl[i] == 'thtr' or lst_lbl[i] == 'gridSOILthick' or lst_lbl[i] == 'gridSsurfhmax' or lst_lbl[i] == 'gridSsurfw':
            fmt = '%5.3f'
        else:
            fmt = '%5.1f'
        if lst_lbl[i] == 'Ss' or lst_lbl[i] == 'eps':
           CBlabel = lst_lblCB[i] + ' ([-])'
        elif lst_lbl[i] == 'hk' or lst_lbl[i] == 'drn_cond' or lst_lbl[i] == 'ghb_cond':
            CBlabel = lst_lblCB[i] + ' (%s.%s$^{-1}$)' % (lenuni_str, itmuni_str)
        elif lst_lbl[i] == 'T':
            CBlabel = lst_lblCB[i] + ' (%s$^{2}$.%s$^{-1}$)' % (lenuni_str, itmuni_str)
        elif lst_lbl[i] == 'Sy' or lst_lbl[i] == 'thts' or lst_lbl[i] == 'thti' or lst_lbl[i] == 'thtr':
            CBlabel = lst_lblCB[i] + ' ([L]$^3$/[L]$^{-3}$)'
        elif lst_lbl[i] == 'vka':
            CBlabel = lst_lblCB[i] + ' ([-] or %s.%s$^{-1}$, layvka = %s)' % (lenuni_str, itmuni_str, cMF.layvka)
        elif lst_lbl[i] == 'vks':
            CBlabel = lst_lblCB[i] + ' (m, $iuzfopt$ = %d)' % cMF.iuzfopt     
        else:
            CBlabel = lst_lblCB[i] + ' (m)'
        if lst_lbl[i] == 'elev' or lst_lbl[i] == 'top' or lst_lbl[i] == 'botm':
            Vmax_tmp = elev_max
            Vmin_tmp = elev_min
        else:
            Vmax_tmp = np.ma.max(Vmax)
            Vmin_tmp = np.ma.min(Vmin)
        MMplot.plotLAYER(days = [0], str_per = [0], Date = 'NA', JD = 'NA', ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = nplot, V = V,  cmap = plt.cm.gist_rainbow_r, CBlabel = CBlabel, msg = '', plt_title = 'IN_%03d_%s' % (i_lbl,lst_lbl[i]), MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, contours = ctrsMM, Vmax = [Vmax_tmp], Vmin = [Vmin_tmp], ntick = ntick, fmt = fmt, points = obs4map, mask = mask_tmp, hnoflo = cMF.hnoflo)
        if lst_lbl[i] == 'elev' or lst_lbl[i] == 'top' or lst_lbl[i] == 'botm':
            i_lbl += 1
            Vmax_tmp = np.ma.max(Vmax)
            Vmin_tmp = np.ma.min(Vmin)
            MMplot.plotLAYER(days = [0], str_per = [0], Date = 'NA', JD = 'NA', ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = nplot, V = V,  cmap = plt.cm.gist_rainbow_r, CBlabel = CBlabel, msg = '', plt_title = 'IN_%03d_%s' % (i_lbl,lst_lbl[i]), MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, contours = ctrsMM, Vmax = [Vmax_tmp], Vmin = [Vmin_tmp], ntick = ntick, fmt = fmt, points = obs4map, ptslbl = 1, mask = mask_tmp, hnoflo = cMF.hnoflo)
        i_lbl += 1
    del V, lst, lst_lbl, nplot, Vmax, Vmin, Vmax_tmp, Vmin_tmp, top_tmp, hk_actual_tmp

    Vmax = 100.0
    Vmin = 0.0
    V = np.zeros((1, cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
    Vvegtot = np.zeros((1, cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
    for v in range(NVEG):
        V[0,0,:,:] = gridVEGarea[v,:,:]
        Vvegtot += gridVEGarea[v,:,:]
        V_lbl = 'veg%02d_%s' %(v+1, VegName[v])
        V_lblCB = 'Frac. area of veg. #%02d - $%s$ (%%)' %(v+1, VegName[v])
        for L in range(cMF.nlay):
            mask_tmp[L,:,:] = cMF.maskAllL
        #print V_lbl
        MMplot.plotLAYER(days = [0], str_per = [0], Date = 'NA', JD = 'NA', ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = 1, V = V,  cmap = plt.cm.gist_rainbow_r, CBlabel = V_lblCB, msg = '', plt_title = 'IN_%03d_%s'% (i_lbl,V_lbl), MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, contours = False, Vmax = [Vmax], Vmin = [Vmin], ntick = ntick, fmt = '%5.1f', points = obs4map, mask = mask_tmp, hnoflo = cMF.hnoflo)
        i_lbl += 1
    del V, V_lbl, V_lblCB
    VareaSoil = 100.0 - Vvegtot
    lst = [Vvegtot,VareaSoil]
    lst_lbl = ['veg_tot','soil']
    lst_lblCB = ['Frac. area of veg. tot. (%)','Frac. area of soil (%)']    
    for i, l in enumerate(lst):
        MMplot.plotLAYER(days = [0], str_per = [0], Date = 'NA', JD = 'NA', ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = 1, V = l,  cmap = plt.cm.gist_rainbow_r, CBlabel = lst_lblCB[i], msg = '', plt_title = 'IN_%03d_%s'% (i_lbl,lst_lbl[i]), MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, contours = False, Vmax = [Vmax], Vmin = [Vmin], ntick = ntick, fmt = '%5.1f', points = obs4map, mask = mask_tmp, hnoflo = cMF.hnoflo)
        i_lbl += 1
    del Vmax, Vmin
    
    lst = [ibound, gridSOIL, gridMETEO]
    lst_lbl = ['ibound', 'gridSOIL', 'gridMETEO']
    lst_lblCB = ['MF cell type - $ibound$', 'Soil type', 'Meteo. zone']
    if irr_yn == 1:
        lst.append(gridIRR)
        lst_lbl.append('gridIRR')
        lst_lblCB.append('Irrigation plots')
    if cMF.uzf_yn == 1:
        lst.append(np.asarray(cMF.iuzfbnd))
        lst_lbl.append('iuzfbnd')
        lst_lblCB.append('UFZ1 - $iuzfbnd$, $nuztop$ = %d' % cMF.nuztop)
        lst.append(np.asarray(cMF.LandSurface))
        lst_lbl.append('LandSurface')
        lst_lblCB.append('Land surface UZF1 - (m)')  
        lst.append(cMF.outcropL)
        lst_lbl.append('outcropL')
        lst_lblCB.append('Outcropping MF layer')          
    for i, l in enumerate(lst):
        V = np.zeros((1, cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
        Vmax = []
        Vmin = []
        for L in range(cMF.nlay):
            try:
                V[0,L,:,:] = l[L,:,:]
                mask_tmp[L,:,:] = mask[L]
                Vmax.append(np.ma.max(np.ma.masked_values(np.ma.masked_array(V[0,L,:,:], cMF.maskAllL), cMF.hnoflo, atol = 0.09)))
                Vmin.append(np.ma.min(np.ma.masked_values(np.ma.masked_array(V[0,L,:,:], cMF.maskAllL), cMF.hnoflo, atol = 0.09)))
                nplot = cMF.nlay
            except:
                V[0,L,:,:] = l
                mask_tmp[L,:,:] = cMF.maskAllL
                Vmax.append(np.ma.max(np.ma.masked_values(np.ma.masked_array(V[0,L,:,:], cMF.maskAllL), cMF.hnoflo, atol = 0.09)))
                Vmin.append(np.ma.min(np.ma.masked_values(np.ma.masked_array(V[0,L,:,:], cMF.maskAllL), cMF.hnoflo, atol = 0.09)))
                nplot = 1
        Vmax = np.ma.max(Vmax)
        Vmin = np.ma.min(Vmin)
        MMplot.plotLAYER(days = [0], str_per = [0], Date = 'NA', JD = 'NA', ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = nplot, V = V,  cmap = plt.cm.gist_rainbow_r, CBlabel = lst_lblCB[i], msg = '', plt_title = 'IN_%03d_%s'% (i_lbl,lst_lbl[i]), MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, contours = False, Vmax = [Vmax], Vmin = [Vmin], ntick = ntick, fmt = '%2.2f', points = obs4map, mask = mask_tmp, hnoflo = cMF.hnoflo)
        i_lbl += 1
    del V, lst, lst_lbl, lst_lblCB, nplot, Vmax, Vmin

# #############################
# ### 1st MODFLOW RUN with initial user-input recharge
# #############################
print'\n##############'
if MF_yn == 1 :
    timestartMF = mpl.dates.datestr2num(mpl.dates.datetime.datetime.today().isoformat())
    print 'MODFLOW RUN (initial user-input fluxes)\n'
    if verbose == 0:
        print '\n--------------'
        sys.stdout = stdout
        report.close()
        stdout = sys.stdout
        report = open(report_fn, 'a')
        sys.stdout = report
    cMF.runMF(perc_MM = (h5_MM_fn, 'perc'), wel_MM = (h5_MM_fn, 'ETg'), verbose = verbose, chunks = chunks, numDays = numDays, stdout = stdout, report = report)
    timeendMF = mpl.dates.datestr2num(mpl.dates.datetime.datetime.today().isoformat())
    durationMFtmp =  timeendMF - timestartMF
    durationMF +=  durationMFtmp
    print 'MF run time: %02.fmn%02.fs' % (int(durationMFtmp*24.0*60.0), (durationMFtmp*24.0*60.0-int(durationMFtmp*24.0*60.0))*60)
    del durationMFtmp
    print '%s'% mpl.dates.DateFormatter.format_data(fmt_DH, mpl.dates.datestr2num(mpl.dates.datetime.datetime.today().isoformat()))

if os.path.exists(cMF.h5_MF_fn):
    print 'Reading MF fluxes...'
    try:
        h5_MF = h5py.File(cMF.h5_MF_fn, 'r')
        # heads format is : timestep, nlay, nrow, ncol
        # cbc format is: (kstp), kper, textprocess, nlay, nrow, ncol
        cbc_nam = []
        cbc_uzf_nam = []
        for c in h5_MF['cbc_nam']:
            cbc_nam.append(c.strip())
        if cMF.uzf_yn == 1:
            for c in h5_MF['cbc_uzf_nam']:
                cbc_uzf_nam.append(c.strip())
        elif cMF.rch_yn == 1:
            #imfRCH = cbc_nam.index_MM('RECHARGE')
            cUTIL.ErrorExit('\nFATAL ERROR!\nMM has to be run together with the UZF1 package of MODFLOW-NWT, thus the RCH package should be desactivacted!\nExisting MM.', stdout = stdout, report = report)
        cbc_uzf_nam_tex = [0]*len(cbc_uzf_nam)
        imfSTO = cbc_nam.index('STORAGE')
        imfFRF = cbc_nam.index('FLOW RIGHT FACE')
        imfFFF = cbc_nam.index('FLOW FRONT FACE')
        if cMF.nlay>1:
            imfFLF = cbc_nam.index('FLOW LOWER FACE')
        if cMF.ghb_yn == 1:
            imfGHB = cbc_nam.index('HEAD DEP BOUNDS')
        if cMF.drn_yn == 1:
            imfDRN = cbc_nam.index('DRAINS')
        if cMF.wel_yn == 1:
            imfWEL = cbc_nam.index('WELLS')
        if cMF.uzf_yn == 1:
            imfEXF   = cbc_uzf_nam.index('SURFACE LEAKAGE')
            imfRCH   = cbc_uzf_nam.index('UZF RECHARGE')
        if MMsoil_yn == 0:
            h5_MF.close()
    except:
        cUTIL.ErrorExit('\nFATAL ERROR!\nInvalid MODFLOW HDF5 file. Run MARMITES and/or MODFLOW again.', stdout = stdout, report = report)

# #############################
# 2nd phase : MM/MF loop #####
# #############################
h_diff_surf = None
if MMsoil_yn != 0:
    durationMMsoil = 0.0
    h_pSP_average = 0
    h_pSP = 0
    LOOP = 0
    endloop = 0
    LOOPlst = [LOOP]
    h_diff = [1000]
    h_diff_log = [1]
    h_diff_all = [1000]
    h_diff_all_log = [1]
    plt_ConvLoop_fn = os.path.join(MM_ws_out, '__plt_MM_MF_ConvLoop.png')
    # Create HDF5 arrays to store MARMITES output
    try:
        h5_MM = h5py.File(h5_MM_fn, 'w')
    except:
        try:
            h5_MM.close()
        except:
            pass
        h5_MM = h5py.File(h5_MM_fn, 'w')
        print "WARNING! Previous h5_MM file corrupted!\nDeleted, new one created."
    # arrays for fluxes independent of the soil layering
    h5_MM.create_dataset(name = 'iMM', data = np.asarray(index_MM.items()))
    if chunks == 1:
        h5_MM.create_dataset(name = 'MM', shape = (sum(cMF.perlen),cMF.nrow,cMF.ncol,len(index_MM)), dtype = np.float, chunks = (1,cMF.nrow,cMF.ncol,len(index_MM)),  compression = 'gzip', compression_opts = 5, shuffle = True)
    else:
        h5_MM.create_dataset(name = 'MM', shape = (sum(cMF.perlen),cMF.nrow,cMF.ncol,len(index_MM)), dtype = np.float)
    # arrays for fluxes in each soil layer
    h5_MM.create_dataset(name = 'iMM_S', data = np.asarray(index_MM_soil.items()))
    if chunks == 1:
        h5_MM.create_dataset(name = 'MM_S', shape = (sum(cMF.perlen),cMF.nrow,cMF.ncol,_nslmax,len(index_MM_soil)), dtype = np.float, chunks = (1,cMF.nrow,cMF.ncol,_nslmax,len(index_MM_soil)),  compression = 'gzip', compression_opts = 5, shuffle = True)
    else:
        h5_MM.create_dataset(name = 'MM_S', shape = (sum(cMF.perlen),cMF.nrow,cMF.ncol,_nslmax,len(index_MM_soil)), dtype = np.float)
    # arrays to compute net recharge to be exported to MF
    if chunks == 1:
        h5_MM.create_dataset(name = 'perc', shape = (cMF.nper,cMF.nrow,cMF.ncol), dtype = np.float, chunks = (1,cMF.nrow,cMF.ncol),  compression = 'gzip', compression_opts = 5, shuffle = True)
        h5_MM.create_dataset(name = 'ETg', shape = (cMF.nper,cMF.nrow,cMF.ncol), dtype = np.float, chunks = (1,cMF.nrow,cMF.ncol),  compression = 'gzip', compression_opts = 5, shuffle = True)
    else:
        h5_MM.create_dataset(name = 'perc', shape = (cMF.nper,cMF.nrow,cMF.ncol), dtype = np.float)
        h5_MM.create_dataset(name = 'ETg', shape = (cMF.nper,cMF.nrow,cMF.ncol), dtype = np.float)

    # #############################
    # ###  CONVERGENCE LOOP   #####
    # #############################

    while (abs(h_diff[LOOP]) > convcrit or abs(h_diff_all[LOOP]) > convcritmax) and LOOP <= ccnum :
        if LOOP == 0:
            print '\n##############\nCONVERGENCE LOOP %d (initialization)\n##############' % (LOOP)
        else:
            print '\n##############\nCONVERGENCE LOOP %d/%d\n##############' % (LOOP, ccnum)
        h_MF_average = 0.0
        timestartMMloop = mpl.dates.datestr2num(mpl.dates.datetime.datetime.today().isoformat())
        # ###########################
        # ###  MARMITES INPUT #######
        # ###########################
        print'\n##############'
        print 'MARMITESsoil RUN'
        # SOIL PARAMETERS
        _nsl, _nam_soil, _st, _slprop, _Sm, _Sfc, _Sr, _S_ini, _Ks = cMF.cPROCESS.inputSoilParam(SOILparam_fn = SOILparam_fn, NSOIL = NSOIL, stdout = None, report = None)
        _nslmax = max(_nsl)
        for l in range(NSOIL):
            _slprop[l] = np.asarray(_slprop[l])
        if LOOP > 0:
            h5_MM = h5py.File(h5_MM_fn)
        # ###############
        # # main loop: calculation of soil water balance in each cell-grid for each time step inside each stress period
#        t0=0
        print '\nComputing...'
        if irr_yn == 0:
            MM_SOIL.runMMsoil(_nsl, _nslmax, _st, _Sm, _Sfc, _Sr, _slprop, _S_ini, botm_l0, _Ks,
                          gridSOIL, gridSOILthick, cMF.elev*1000.0, gridMETEO,
                          index_MM, index_MM_soil, gridSsurfhmax, gridSsurfw,
                          RF_veg_zoneSP, E0_zonesSP, PT_veg_zonesSP, RFe_veg_zonesSP, PE_zonesSP, gridVEGarea,
                          LAI_veg_zonesSP, Zr, kT_min, kT_max, kT_n, NVEG,
                          cMF, conv_fact, h5_MF, h5_MM, irr_yn
                          )
        else:
            MM_SOIL.runMMsoil(_nsl, _nslmax, _st, _Sm, _Sfc, _Sr, _slprop, _S_ini, botm_l0, _Ks,
                          gridSOIL, gridSOILthick, cMF.elev*1000.0, gridMETEO,
                          index_MM, index_MM_soil, gridSsurfhmax, gridSsurfw,
                          RF_veg_zoneSP, E0_zonesSP, PT_veg_zonesSP, RFe_veg_zonesSP, PE_zonesSP, gridVEGarea,
                          LAI_veg_zonesSP, Zr, kT_min, kT_max, kT_n, NVEG,
                          cMF, conv_fact, h5_MF, h5_MM, irr_yn,
                          RF_irr_zoneSP, PT_irr_zonesSP, RFe_irr_zoneSP,
                          crop_irr_SP, gridIRR,
                          Zr_c, kT_min_c, kT_max_c, kT_n_c, NCROP
                          )

        # CHECK MM amd MF CONVERG.
        h_MF_m = np.ma.masked_values(np.ma.masked_values(h5_MF['heads'], cMF.hdry, atol = 1E+25), cMF.hnoflo, atol = 0.09)
        h5_MF.close()
        h_MF_average = np.ma.average(h_MF_m)
        h_diff.append(h_MF_average - h_pSP_average)
        h_diff_surf = h_MF_m - h_pSP
        h_diff_all_max = np.ma.max(h_diff_surf)
        h_diff_all_min = np.ma.min(h_diff_surf)
        if abs(h_diff_all_max)>abs(h_diff_all_min):
            h_diff_all.append(h_diff_all_max)
        else:
            h_diff_all.append(h_diff_all_min)
        del h_diff_all_max, h_diff_all_min
        LOOPlst.append(LOOP)
        LOOP += 1
        h_pSP_average = h_MF_average
        h_pSP = h_MF_m
        del h_MF_m
        if np.absolute(h_diff[LOOP])>0.0:
            h_diff_log.append(np.log10(np.absolute(h_diff[LOOP])))
            h_diff_all_log.append(np.log10(np.absolute(h_diff_all[LOOP])))
        else:
            h_diff_log.append(np.log10(convcrit))
            h_diff_all_log.append(np.log10(convcritmax))

        msg_end_loop = []
        msg_end_loop.append('Average heads:\n%.3f m' % h_MF_average)
        if LOOP > 1:
            msg_end_loop.append('Heads diff. from previous conv. loop: %.3f m' % h_diff[LOOP])
            msg_end_loop.append('Maximum heads difference:             %.3f m' % h_diff_all[LOOP])
        if h_MF_average == 0.0 or str(h_diff[LOOP]) == 'nan':
            print '\nWARNING!\nModel with DRY cells or NaN values!'
        elif abs(h_diff[LOOP]) < convcrit and abs(h_diff_all[LOOP]) < convcritmax:
            msg_end_loop.append('Successful convergence between MARMITES and MODFLOW!\n(Conv. criterion = %.4f and conv. crit. max. = %.4f)' % (convcrit, convcritmax))
            endloop += 1
        elif LOOP>ccnum:
            msg_end_loop.append('No convergence between MARMITES and MODFLOW!\n(Conv. criterion = %.4f and conv. crit. max. = %.4f)' % (convcrit, convcritmax))
            endloop += 1
        for txt in msg_end_loop:
            print txt
        del h_MF_average

        timeendMMloop = mpl.dates.datestr2num(mpl.dates.datetime.datetime.today().isoformat())
        durationMMloop = timeendMMloop-timestartMMloop
        print '\nMM run time: %02.fmn%02.fs' % (int(durationMMloop*24.0*60.0), (durationMMloop*24.0*60.0-int(durationMMloop*24.0*60.0))*60)
        durationMMsoil += durationMMloop
        print '%s'% mpl.dates.DateFormatter.format_data(fmt_DH, mpl.dates.datestr2num(mpl.dates.datetime.datetime.today().isoformat()))

        if not (endloop == 1 and MF_lastrun == 0):
            # MODFLOW RUN with MM-computed recharge
            timestartMF = mpl.dates.datestr2num(mpl.dates.datetime.datetime.today().isoformat())
            print'\n##############'
            if endloop < 1:
                print 'MODFLOW RUN (MARMITES fluxes)'
            else:
                print 'MODFLOW RUN (MARMITES fluxes after conv. loop)'
            if verbose == 0:
                print '\n--------------'
                sys.stdout = stdout
                report.close()
                stdout = sys.stdout
                report = open(report_fn, 'a')
                sys.stdout = report
            cMF.runMF(perc_MM = (h5_MM_fn, 'perc'), wel_MM = (h5_MM_fn, 'ETg'), verbose = verbose, chunks = chunks, numDays = numDays, stdout = stdout, report = report)
            try:
                h5_MF = h5py.File(cMF.h5_MF_fn, 'r')
            except:
                cUTIL.ErrorExit('\nFATAL ERROR!\nInvalid MODFLOW HDF5 file. Run MARMITES and/or MODFLOW again.', stdout = stdout, report = report)
            timeendMF = mpl.dates.datestr2num(mpl.dates.datetime.datetime.today().isoformat())
            durationMFtmp =  timeendMF-timestartMF
            durationMF +=  durationMFtmp
            print '\nMF run time: %02.fmn%02.fs' % (int(durationMFtmp*24.0*60.0), (durationMFtmp*24.0*60.0-int(durationMFtmp*24.0*60.0))*60)
            del durationMFtmp
            print '%s'% mpl.dates.DateFormatter.format_data(fmt_DH, mpl.dates.datestr2num(mpl.dates.datetime.datetime.today().isoformat()))
        
        if MMsoil_yn < 0:
            break
    if not (endloop == 1 and MF_lastrun == 0):   
        h5_MF.close()
    # #############################
    # ###  END CONVERGENCE LOOP ###
    # #############################

    # export loop plot
    if MMsoil_yn > 0:  
        print'\n##############'
        print 'Exporting plot of the convergence loop...'
        fig = plt.figure()
        fig.suptitle('Convergence loop plot between MM and MF based on heads differences.\nOrange: average heads for the whole model.\nGreen: maximun heads difference observed in the model (one cell)', fontsize=10)
        if LOOP>0:
            ax1=fig.add_subplot(3,1,1)
            plt.setp(ax1.get_xticklabels(), fontsize=8)
            plt.setp(ax1.get_yticklabels(), fontsize=8)
            ax1.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.3G'))
            plt.ylabel('h_diff [m]', fontsize=10, horizontalalignment = 'center')
            plt.grid(True)
            plt.plot(LOOPlst[1:], h_diff[1:], linestyle='-', marker='o', markersize=5, c = 'orange', markerfacecolor='orange', markeredgecolor='red')
            plt.plot(LOOPlst[1:], h_diff_all[1:], linestyle='-', marker='o', markersize=5, c = 'green', markerfacecolor='green', markeredgecolor='blue')
    
        if LOOP>1:
            ax2=fig.add_subplot(3,1,2, sharex = ax1)
            plt.setp(ax2.get_xticklabels(), fontsize=8)
            plt.setp(ax2.get_yticklabels(), fontsize=8)
            plt.plot(LOOPlst[2:], h_diff[2:], linestyle='-', marker='o', markersize=5, c = 'orange', markerfacecolor='orange', markeredgecolor='red')
            plt.plot(LOOPlst[2:], h_diff_all[2:], linestyle='-', marker='o', markersize=5, c = 'green', markerfacecolor='green', markeredgecolor='blue')
            ax2.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.3G'))
            plt.ylabel('h_diff [m]', fontsize=10, horizontalalignment = 'center')
        #        plt.ylabel.Text.position(0.5, -0.5)
            plt.grid(True)
    
            ax3=fig.add_subplot(3,1,3, sharex = ax1)
            plt.setp(ax3.get_xticklabels(), fontsize=8)
            plt.setp(ax3.get_yticklabels(), fontsize=8)
            ax3.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.3G'))
            plt.ylabel('log(abs(h_diff)) [log(m)]', fontsize=10, horizontalalignment = 'center')
            plt.grid(True)
            plt.xlabel('loop', fontsize=10)
            plt.plot(LOOPlst[2:], h_diff_log[2:], linestyle='-', marker='o', markersize=5, c = 'orange', markerfacecolor='orange', markeredgecolor='red')
            plt.plot(LOOPlst[2:], h_diff_all_log[2:], linestyle='-', marker='o', markersize=5, c = 'green', markerfacecolor='green', markeredgecolor='blue')
    
            ax2.xaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%2d'))
            ax3.xaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%2d'))
    
            plt.xlim(0,LOOP-1)
            ax1.xaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%2d'))
            ax1.xaxis.set_ticks(LOOPlst[1:])
    
        plt.savefig(plt_ConvLoop_fn)
        plt.cla()
        plt.clf()
        plt.close('all')
        del fig, LOOPlst, h_diff, h_diff_log, h_pSP

# #############################
# 3rd phase : export results #####
# #############################

timestartExport = mpl.dates.datestr2num(mpl.dates.datetime.datetime.today().isoformat())

print '\n##############\nMARMITES exporting...'

del RF_veg_zoneSP
del E0_zonesSP
del PT_veg_zonesSP
del RFe_veg_zonesSP
del PE_zonesSP
del gridSsurfhmax
del gridSsurfw

# reorganizing MF output in daily data
if MF_yn == 1 and isinstance(cMF.h5_MF_fn, str):
    print '\nConverting MODFLOW output into daily stress period...'
    try:
        h5_MF = h5py.File(cMF.h5_MF_fn)
    except:
        cUTIL.ErrorExit('\nFATAL ERROR!\nInvalid MODFLOW HDF5 file. Run MARMITES and/or MODFLOW again.', stdout = stdout, report = report)
    cMF.cPROCESS.procMF(cMF = cMF, h5_MF = h5_MF, ds_name = 'cbc', ds_name_new = 'STO_d', conv_fact = conv_fact, index = imfSTO)
    cMF.cPROCESS.procMF(cMF = cMF, h5_MF = h5_MF, ds_name = 'cbc', ds_name_new = 'FRF_d', conv_fact = conv_fact, index = imfFRF)
    cMF.cPROCESS.procMF(cMF = cMF, h5_MF = h5_MF, ds_name = 'cbc', ds_name_new = 'FFF_d', conv_fact = conv_fact, index = imfFFF)
    if cMF.nlay>1:
        cMF.cPROCESS.procMF(cMF = cMF, h5_MF = h5_MF, ds_name = 'cbc', ds_name_new = 'FLF_d', conv_fact = conv_fact, index = imfFLF)
    if cMF.drn_yn == 1:
        cMF.cPROCESS.procMF(cMF = cMF, h5_MF = h5_MF, ds_name = 'cbc', ds_name_new = 'DRN_d', conv_fact = conv_fact, index = imfDRN)
    if cMF.wel_yn == 1:
        cMF.cPROCESS.procMF(cMF = cMF, h5_MF = h5_MF, ds_name = 'cbc', ds_name_new = 'WEL_d', conv_fact = conv_fact, index = imfWEL)
    if cMF.ghb_yn == 1:
        cMF.cPROCESS.procMF(cMF = cMF, h5_MF = h5_MF, ds_name = 'cbc', ds_name_new = 'GHB_d', conv_fact = conv_fact, index = imfGHB)
    cMF.cPROCESS.procMF(cMF = cMF, h5_MF = h5_MF, ds_name = 'heads', ds_name_new = 'heads_d', conv_fact = conv_fact)
    if cMF.uzf_yn == 1:
        cMF.cPROCESS.procMF(cMF = cMF, h5_MF = h5_MF, ds_name = 'cbc_uzf', ds_name_new = 'RCH_d', conv_fact = conv_fact, index = imfRCH)
        cMF.cPROCESS.procMF(cMF = cMF, h5_MF = h5_MF, ds_name = 'cbc_uzf', ds_name_new = 'EXF_d', conv_fact = conv_fact, index = imfEXF)
    elif cMF.rch_yn == 1:
        cMF.cPROCESS.procMF(cMF = cMF, h5_MF = h5_MF, ds_name = 'cbc', ds_name_new = 'RCH_d', conv_fact = conv_fact, index = imfRCH)
    h5_MF.close()

if MMsoil_yn != 0 and isinstance(h5_MM_fn, str):
    try:
        h5_MM = h5py.File(h5_MM_fn)
    except:
        cUTIL.ErrorExit('\nFATAL ERROR!\nInvalid MARMITES HDF5 file. Run MARMITES and/or MODFLOW again.', stdout = stdout, report = report)
    cMF.cPROCESS.procMM(cMF = cMF, h5_MM = h5_MM, ds_name = 'perc', ds_name_new = 'perc_d')
    cMF.cPROCESS.procMM(cMF = cMF, h5_MM = h5_MM, ds_name = 'ETg', ds_name_new = 'ETg_d')
    h5_MM.close()

SP_d = np.ones(sum(cMF.perlen), dtype = int)
t = 0
for n in range(cMF.nper):
    for x in range(cMF.perlen[n]):
        SP_d[t] = n + 1
        t += 1

if h_diff_surf != None and MMsoil_yn > 0:
    h_diff_n = None
    for n in range(cMF.nper):
        for r, c in enumerate(h_diff_surf[n,:,:,:]):
            try:
                list(c.flatten()).index(h_diff_all[LOOP])
                h_diff_n = n
                break
            except:
                pass
        if h_diff_n <> None: break
    del n, l, r, c
    V = []
    Vmax = []
    Vmin = []
    V = np.zeros((1, cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
    mask_tmp = np.zeros((cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
    if h_diff_n <> None:
        for L in range(cMF.nlay):
            V[0,L,:,:] = h_diff_surf[h_diff_n,L,:,:]
            mask_tmp[L,:,:] = mask[L]
            Vmax.append(np.ma.max(np.ma.masked_values(np.ma.masked_array(V[0,L,:,:],cMF. maskAllL), cMF.hnoflo, atol = 0.09)))
            Vmin.append(np.ma.min(np.ma.masked_values(np.ma.masked_array(V[0,L,:,:], cMF.maskAllL), cMF.hnoflo, atol = 0.09)))
        Vmax = np.ma.max(Vmax) #float(np.ceil(max(Vmax)))
        Vmin = np.ma.min(Vmin) #float(np.floor(min(Vmin)))
        h_diff_d = sum(cMF.perlen[0:h_diff_n])
        MMplot.plotLAYER(days = [h_diff_d], str_per = [h_diff_n], Date = [cMF.inputDate[h_diff_d]], JD = [cMF.JD[h_diff_d]], ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = V,  cmap = plt.cm.Blues, CBlabel = ('(m)'), msg = 'no value', plt_title = 'HEADSmaxdiff_ConvLoop', MM_ws = MM_ws_out, interval_type = 'percentile', interval_num = 5, Vmax = [Vmax], Vmin = [Vmin], contours = ctrsMF, ntick = ntick, points = obs4map, mask = mask_tmp, hnoflo = cMF.hnoflo, pref_plt_title = '__sp_plt')
    for e in [h_diff_n, h_diff_d, V, Vmin, Vmax, mask_tmp]:
        try:
            del e
        except:
            pass

# exporting sm computed by MM for PEST (smp format)
if os.path.exists(h5_MM_fn):
    try:
        h5_MM = h5py.File(h5_MM_fn, 'r')
    except:
        cUTIL.ErrorExit('\nFATAL ERROR!\nInvalid MARMITES HDF5 file. Run MARMITES and/or MODFLOW again.', stdout = stdout, report = report)
    outPESTsmMM = open(os.path.join(MF_ws,'sm_MM4PEST.smp'), 'w')
    for o_ref in obs_list:
        for o in obs.keys():
            if o == o_ref:
                i = obs.get(o)['i']
                j = obs.get(o)['j']
                l = obs.get(o)['lay']
                obs_SM = obs.get(o)['obs_SM']
                if obs.get(o)['obs_sm_yn'] == 1:
                    cMF.cPROCESS.smMMname.append(o)
                MM_S = h5_MM['MM_S'][:,i,j,:,:]
                cMF.cPROCESS.ExportResultsMM4PEST(i, j, cMF.inputDate, _nslmax, MM_S, index_MM_soil, obs_SM, o)
                del i, j, l, obs_SM, MM_S
        del o
    # write PEST smp file with MM output
    inputFile = cUTIL.readFile(MM_ws,inputObs_fn)
    ind = 0
    for i in range(len(inputFile)):
        line = inputFile[i].split()
        name = line[0]
        for j in cMF.cPROCESS.smMMname:
            if j == name:
                for l in cMF.cPROCESS.smMM[ind]:
                    outPESTsmMM.write(l)
        ind += 1
    outPESTsmMM.close()

# computing max and min values in MF fluxes for plotting
hmax = []
hmin = []
hmaxMM = []
hminMM = []
hdiff = []
cbcmax_d = []
cbcmin_d = []
axefact = 1.05
if os.path.exists(cMF.h5_MF_fn):
    # TODO missing STOuz and FLF (however this is not very relevant since these fluxes should not be the bigger in magnitude)
    try:
        h5_MF = h5py.File(cMF.h5_MF_fn, 'r')
    except:
        cUTIL.ErrorExit('\nFATAL ERROR!\nInvalid MODFLOW HDF5 file. Run MARMITES and/or MODFLOW again.', stdout = stdout, report = report)
    # STO
    cbc_STO = h5_MF['STO_d']
    cbcmax_d.append(-1*np.ma.max(cbc_STO))
    cbcmin_d.append(-1*np.ma.min(cbc_STO))
    del cbc_STO
    # RCH
    cbc_RCH = h5_MF['RCH_d']
    RCHmax = np.ma.max(cbc_RCH)
    cbcmax_d.append(RCHmax)
    RCHmin = np.ma.min(cbc_RCH)
    print '\nMaximum GW recharge (%.2f mm/day) observed at:' % RCHmax
    tRCHmax = -1
    if RCHmax > 0.0:
        tmp = np.where(cbc_RCH[:,:,:,:]==RCHmax)
        tRCHmax = tmp[0][0]
        l = tmp[1][0]
        i = tmp[2][0]
        j = tmp[3][0]
        print 'row %d, col %d, layer %d and stress period %d (day %d, date %s)' % (i+1, j+1, l+1, sp_days_lst[tRCHmax], tRCHmax+1, mpl.dates.num2date(cMF.inputDate[tRCHmax] + 1.0).isoformat()[:10])
        if plt_out_obs == 1:
            x = cMF.delc[i]*i + xllcorner
            y = cMF.delr[j]*j + yllcorner
            obs['RCHmax'] = {'x':x,'y':y, 'i': i, 'j': j, 'lay': l, 'hi':999, 'h0':999, 'RC':999, 'STO':999, 'obs_h':[], 'obs_h_yn':0, 'obs_SM':[], 'obs_sm_yn':0, 'obs_Ro':[], 'obs_Ro_yn':0}
            obs_list.append('RCHmax')
            obs4map[0].append('RCHmax')
            obs4map[1].append(float(i)+1.0)
            obs4map[2].append(float(j)+1.0)
            obs4map[3].append(float(l))
            del x, y            
        for e in tmp:
            if len(e)>1:
                print "\nWARNING!\nR max occurred at several cells and/or stress periods"
                break
        del tmp
        if tRCHmax < 0:
            print 'WARNING!\nNo Rg max found!'             
    del cbc_RCH
    RCHmax = np.ma.max(RCHmax) #float(np.ceil(np.ma.max(RCHmax)))  #
    RCHmin = np.ma.min(RCHmin) #float(np.floor(np.ma.min(RCHmin))) #
    # WEL
    if cMF.wel_yn == 1:
        cbc_WEL = h5_MF['WEL_d']
        ETgmax = np.ma.min(cbc_WEL)
        cbcmax_d.append(np.ma.max(cbc_WEL))
        cbcmin_d.append(np.ma.min(cbc_WEL))
        print '\nMaximum ETg (%.2f mm/day) observed at:' % ETgmax
        tETgmax = -1
        if ETgmax < 0.0:
            tmp = np.where(cbc_WEL[:,:,:,:]==ETgmax)
            tETgmax = tmp[0][0]
            l = tmp[1][0]
            i = tmp[2][0]
            j = tmp[3][0]
            print 'row %d, col %d, layer %d and stress period %d (day %d, date %s)' % (i+1, j+1, l+1, sp_days_lst[tETgmax], tETgmax+1, mpl.dates.num2date(cMF.inputDate[tETgmax] + 1.0).isoformat()[:10])
            if plt_out_obs == 1:
                x = cMF.delc[i]*i + xllcorner
                y = cMF.delr[j]*j + yllcorner
                obs['ETgmax'] = {'x':x,'y':y, 'i': i, 'j': j, 'lay': l, 'hi':999, 'h0':999, 'RC':999, 'STO':999, 'obs_h':[], 'obs_h_yn':0, 'obs_SM':[], 'obs_sm_yn':0, 'obs_Ro':[], 'obs_Ro_yn':0}
                obs_list.append('ETgmax')
                obs4map[0].append('ETgmax')
                obs4map[1].append(float(i)+1.0)
                obs4map[2].append(float(j)+1.0)
                obs4map[3].append(float(l))
                del x, y
            
            for e in tmp:
                if len(e)>1:
                    print "WARNING!\nETg max occurred at several cells and/or stress periods"
                    break
            del tmp
            if tETgmax < 0:
                print 'WARNING!\nNo ETg max found!'  
        del cbc_WEL
    # DRN
    if cMF.drn_yn == 1:
        cbc_DRN = h5_MF['DRN_d']
        DRNmax = np.ma.max(cbc_DRN)
        cbcmax_d.append(DRNmax)
        DRNmin = np.ma.min(cbc_DRN)
        cbcmin_d.append(DRNmin)
        del cbc_DRN
        DRNmax = -1.0*DRNmin
        DRNmin = 0.0
    # GHB
    if cMF.ghb_yn == 1:
        cbc_GHB = h5_MF['GHB_d']
        GHBmax = np.ma.max(cbc_GHB)
        cbcmax_d.append(GHBmax)
        GHBmin = np.ma.min(cbc_GHB)
        cbcmin_d.append(GHBmin)
        del cbc_GHB
        GHBmax = -1.0*GHBmin
        GHBmin = 0.0
    # EXF
    cbc_EXF = h5_MF['EXF_d']
    EXFmax = np.ma.max(cbc_EXF)
    EXFmin = np.ma.min(cbc_EXF)
    del cbc_EXF
    EXFmax = -1.0*EXFmin
    EXFmin = 0.0
    cbcmax_d = np.ma.max(cbcmax_d) #float(np.ceil(np.ma.max(cbcmax_d)))
    cbcmin_d = np.ma.min(cbcmin_d) #float(np.floor(np.ma.min(cbcmin_d)))
    # h
    h_MF_m = np.ma.masked_values(np.ma.masked_values(h5_MF['heads_d'], cMF.hnoflo, atol = 0.09), cMF.hdry, atol = 1E+25)
    hmaxMF = np.ma.max(h_MF_m[:,:,:,:].flatten())
    hminMF = np.ma.min(h_MF_m[:,:,:,:].flatten())
    GWTD = cMF.elev[np.newaxis,np.newaxis,:,:] - h_MF_m
    GWTDmax = np.ma.max(GWTD.flatten())
    GWTDmin = np.ma.min(GWTD.flatten())
    h5_MF.close()
    del GWTD
else:
    DRNmax = GHBmax = cbcmax_d = 1.0
    DRNmin = GHBmin = cbcmin_d = -1.0
    hmaxMF = -9999.9
    hminMF = 9999.9

if os.path.exists(h5_MM_fn):
    try:
        h5_MM = h5py.File(h5_MM_fn, 'r')
    except:
        cUTIL.ErrorExit('\nFATAL ERROR!\nInvalid MARMITES HDF5 file. Run MARMITES and/or MODFLOW again.', stdout = stdout, report = report)
    # h
    headscorr_m = np.ma.masked_values(np.ma.masked_values(h5_MM['MM'][:,:,:,19], cMF.hnoflo, atol = 0.09), cMF.hdry, atol = 1E+25)
    hcorrmax = np.ma.max(headscorr_m.flatten())
    hcorrmin = np.ma.min(headscorr_m.flatten())
    GWTDcorr = cMF.elev[np.newaxis,:,:] - headscorr_m
    GWTDcorrmax = np.ma.max(GWTDcorr.flatten())
    GWTDcorrmin = np.ma.min(GWTDcorr.flatten())
    if GWTDcorrmin < 0.0:
        GWTDcorrmin = 0.0
    h5_MM.close()
    del headscorr_m, GWTDcorr
else:
    hcorrmax = -9999.9
    hcorrmin = 9999.9

if obs != None:
    x = 0
    for o in obs.keys():
        i = obs.get(o)['i']
        j = obs.get(o)['j']
        l = obs.get(o)['lay']
        obs_h = obs.get(o)['obs_h']
        if os.path.exists(cMF.h5_MF_fn):
            hmaxMF_tmp = np.ma.max(h_MF_m[:,l,i,j].flatten())
            hminMF_tmp = np.ma.min(h_MF_m[:,l,i,j].flatten())
        else:
            hmaxMF_tmp = -9999.9
            hminMF_tmp = -9999.9
        if obs_h != []:
            npa_m_tmp = np.ma.masked_values(obs_h, cMF.hnoflo, atol = 0.09)
            hmaxMM = np.ma.max(npa_m_tmp.flatten())
            hminMM = np.ma.min(npa_m_tmp.flatten())
            del npa_m_tmp
        else:
            hmaxMM = -9999.9
            hminMM = 9999.9
        hmax.append(np.ma.max((hmaxMF_tmp, hmaxMM)))
        hmin.append(np.ma.min((hminMF_tmp, hminMM)))
        hdiff.append(hmax[x]-hmin[x])
        x += 1
    hdiff = np.ma.max(hdiff)
    del hmaxMF_tmp, hminMF_tmp
else:
    hdiff = 2000

# #################################################
# plot SOIL/GW ts and water balance at the catchment scale
# #################################################
tTgmin = -1
if plt_out_obs == 1 and os.path.exists(h5_MM_fn) and os.path.exists(cMF.h5_MF_fn):
    try:
        h5_MM = h5py.File(h5_MM_fn, 'r')
    except:
        cUTIL.ErrorExit('\nFATAL ERROR!\nInvalid MARMITES HDF5 file. Run MARMITES and/or MODFLOW again.', stdout = stdout, report = report)
    # RMSE list to plot
    rmseSM = []
    rsrSM = []
    nseSM = []
    rSM = []
    obslstSM = []
    rmseHEADS = []
    rsrHEADS = []
    nseHEADS = []
    rHEADS = []
    obslstHEADS = []    
    rmseHEADSc = []
    rsrHEADSc = []
    nseHEADSc = []
    rHEADSc = []
    obslstHEADSc = []    
    # indexes of the HDF5 output arrays
    # index_MM = {'iRF':0, 'iPT':1, 'iPE':2, 'iRFe':3, 'iSsurf':4, 'iRo':5, 'iEXFg':6, 'iEsurf':7, 'iMB':8, 'iI':9, 'iE0':10, 'iEg':11, 'iTg':12, 'idSsurf':13, 'iETg':14, 'iETsoil':15, 'iSsoil_pc':16, 'idSsoil':17, 'iperc':18, 'ihcorr':19, 'idgwt':20, 'iuzthick':21, 'iInf':22, 'iMBsurf':23}
    # index_MM_soil = {'iEsoil':0, 'iTsoil':1,'iSsoil_pc':2, 'iRsoil':3, 'iExf':4, 'idSsoil':5, 'iSsoil':6, 'iSAT':7, 'iMB':8}
    #    # TODO Ro sould not be averaged by ncell_MM, as well as EXF
    print '\nExporting output ASCII files, time series plots and water balance sankey plots of water fluxes at the catchment scale...\n-------'
    flxCatch_lst   = []
    flxmax_d     = []
    flxmin_d     = []
    flxIndex_lst = {}
    count = 0
    TopSoilAverage = np.ma.masked_array(cMF.elev*1000.0, cMF.maskAllL).sum()*.001/sum(ncell_MM)
    # MM
    flx_lst = []
    for e in sorted(index_MM, key=index_MM.get): flx_lst.append(e)
    flxLbl_lst = [r'$RF$', r'$PT$', r'$PE$', r'$RFe$', r'$S_{surf}$', r'$Ro$', r'$Exf_g$', r'$E_{surf}$',  r'$MB_{soil}$', r'$I$',  r'$E_0$', r'$E_g$', r'$T_g$', r'$\Delta S_{surf}$', r'$ET_g$', r'$ET_{soil}$', r'$\theta$', r'\Delta S_{soil}', r'$perc$', r'$h \ corr$', '$d$', r'$thick_p}$', r'$Inf$', r'$MB_{surf}$']    
    for z, (i, i_tex) in enumerate(zip(flx_lst, flxLbl_lst)):
        flxIndex_lst[i] = count
        count += 1
        array_tmp = h5_MM['MM'][:,:,:,index_MM.get(i)]
        flx_tmp = np.ma.masked_values(array_tmp, cMF.hnoflo, atol = 0.09)
        flxmax_d.append(np.ma.max(flx_tmp))
        flxmin_d.append(np.ma.min(flx_tmp))
        array_tmp1 = np.sum(np.ma.masked_values(array_tmp, cMF.hnoflo, atol = 0.09), axis = 1)
        flxCatch_lst.append(np.sum(np.ma.masked_values(array_tmp1, cMF.hnoflo, atol = 0.09), axis = 1)/sum(ncell_MM))
        del flx_tmp, array_tmp, array_tmp1
    del flx_lst
    # MM_S
    flx_lst = []
    for e in sorted(index_MM_soil, key=index_MM_soil.get): flx_lst.append(e)
    for z, (i, i_tex) in enumerate(zip(flx_lst, [r'${E_{soil}}$', r'${T_{soil}}$', r'$\theta$', r'${R_p}$', r'$Exf$', r'${\Delta S_{soil}}$', r'${S_{soil}}}$', r'$SAT$', r'${MB_{soil}}$'])):
        flxLbl_lst.append(i_tex)
        flxIndex_lst[i] = count
        count += 1
        flx_tmp1 = 0.0
        array_tmp2 = np.zeros((sum(cMF.perlen)), dtype = np.float)
        for l in range(_nslmax):
            array_tmp = h5_MM['MM_S'][:,:,:,l,index_MM_soil.get(i)]
            flx_tmp = np.ma.masked_values(array_tmp, cMF.hnoflo, atol = 0.09)
            flxmax_d.append(np.ma.max(flx_tmp))
            flxmin_d.append(np.ma.min(flx_tmp))
            flx_tmp1 += flx_tmp.sum()
            array_tmp1 = np.sum(flx_tmp, axis = 1)
            array_tmp2 += np.sum(np.ma.masked_values(array_tmp1, cMF.hnoflo, atol = 0.09), axis = 1)
        del flx_tmp, array_tmp, array_tmp1
        flxCatch_lst.append(array_tmp2/sum(ncell_MM))
        del flx_tmp1, array_tmp2
    # Exf_l0
    flxLbl_lst.append('$iExf_1$')
    flxIndex_lst['iExf_1'] = count
    count += 1        
    array_tmp = h5_MM['MM_S'][:,:,:,0,index_MM_soil.get('iExf')]
    flx_tmp = np.ma.masked_values(array_tmp, cMF.hnoflo, atol = 0.09)
    flxmax_d.append(np.ma.max(flx_tmp))
    flxmin_d.append(np.ma.min(flx_tmp))
    array_tmp1 = np.sum(np.ma.masked_values(array_tmp, cMF.hnoflo, atol = 0.09), axis = 1)
    flxCatch_lst.append(np.sum(np.ma.masked_values(array_tmp1, cMF.hnoflo, atol = 0.09), axis = 1)/sum(ncell_MM))
    del flx_tmp, array_tmp, array_tmp1    
    if cMF.wel_yn == 1:
        array_tmp = h5_MM['MM'][:,:,:,index_MM.get('iEg')]
        flx_tmp = np.ma.masked_values(array_tmp, cMF.hnoflo, atol = 0.09)
        flxmax_d.append(np.ma.max(flx_tmp))
        flxmin_d.append(np.ma.min(flx_tmp))
        Eg_tmp = np.zeros((sum(cMF.perlen)), dtype = np.float)
        for L in range(cMF.nlay):
            mask_temp = mask_Lsup == (cMF.nlay-L)
            array_tmp1 = np.sum(array_tmp*mask_temp, axis = 1)
            array_tmp2 = np.sum(np.ma.masked_values(array_tmp1, cMF.hnoflo, atol = 0.09), axis = 1)
            flxCatch_lst.append(array_tmp2/sum(ncell_MM))
            Eg_tmp += array_tmp2
            flxLbl_lst.append(r'$E_{g,%d}$'%(L+1))
            flxIndex_lst['iEg_%d' % (L+1)] = count
            count += 1
        flxCatch_lst.append(Eg_tmp/sum(ncell_MM))
        flxLbl_lst.append(r'$E_g$')
        flxIndex_lst['iEg'] = count
        count += 1
        del flx_tmp, array_tmp, array_tmp1, array_tmp2, mask_temp
        # Tg          
        i = 'iTg'
        array_tmp = h5_MM['MM'][:,:,:,index_MM.get(i)]
        flx_tmp = np.ma.masked_values(array_tmp, cMF.hnoflo, atol = 0.09)
        flxmax_d.append(np.ma.max(flx_tmp))
        Tg_min = np.ma.min(flx_tmp)
        flxmin_d.append(Tg_min)
        if abs(Tg_min) > 1E-6:
            print '\nTg negative (%.2f) observed at:' % Tg_min
            for row in range(cMF.nrow):
                for t,col in enumerate(flx_tmp[:,row,:]):
                    try:
                        print 'row %d, col %d and day %d' % (row + 1, list(col).index(Tg_min) + 1, t + 1)
                        tTgmin = t
                        if plt_out_obs == 1:
                            obs['PzTgmin'] = {'x':999,'y':999, 'i': row, 'j': list(col).index(Tg_min), 'lay': 0, 'hi':999, 'h0':999, 'RC':999, 'STO':999, 'obs_h':[], 'obs_h_yn':0, 'obs_SM':[], 'obs_sm_yn':0, 'obs_Ro':[], 'obs_Ro_yn':0}
                            obs_list.append('Tgm')
                            obs4map[0].append('Tgm')
                            obs4map[1].append(float(row)+1.0)
                            obs4map[2].append(list(col).index(Tg_min)+1.0)
                            obs4map[3].append(0)
                            try:
                                hmin.append(hmin[0])
                            except:
                                hmin.append(999.9)
                    except:
                        pass
        Tg_tmp = np.zeros((sum(cMF.perlen)), dtype = np.float)
        for L in range(cMF.nlay):
            mask_temp = mask_Lsup == (cMF.nlay-L)
            array_tmp1 = np.sum(array_tmp*mask_temp, axis = 1)
            array_tmp2 = np.sum(np.ma.masked_values(array_tmp1, cMF.hnoflo, atol = 0.09), axis = 1)
            flxCatch_lst.append(array_tmp2/sum(ncell_MM))
            Tg_tmp += array_tmp2
            flxLbl_lst.append(r'$T_{g%d}$'%(L+1))
            flxIndex_lst['iTg_%d' % (L+1)] = count
            count += 1
        flxCatch_lst.append(Tg_tmp/sum(ncell_MM))
        flxLbl_lst.append(r'$T_g$')
        flxIndex_lst['iTg'] = count
        count += 1            
        del flx_tmp, array_tmp, array_tmp1, array_tmp2, mask_temp
    flxmax_d = float(np.ceil(np.ma.max(flxmax_d)))
    flxmin_d = float(np.floor(np.ma.min(flxmin_d)))
    if os.path.exists(cMF.h5_MF_fn):
        # compute UZF_STO and store GW_RCH
        try:
            h5_MF = h5py.File(cMF.h5_MF_fn, 'r')
        except:
            cUTIL.ErrorExit('\nFATAL ERROR!\nInvalid MF HDF5 file. Run MARMITES and/or MODFLOW again.', stdout = stdout, report = report)        
        cbc_RCH = h5_MF['RCH_d']
        array_tmp2 = np.zeros((sum(cMF.perlen)), dtype = np.float)
        rch_tot = 0
        # GW_RCH
        for L in range(cMF.nlay):
            flxLbl_lst.append(r'$Rg_%d$' % (L+1))
            array_tmp = cbc_RCH[:,L,:,:]
            array_tmp1 = np.sum(np.ma.masked_values(array_tmp, cMF.hnoflo, atol = 0.09), axis = 1)
            rch_tmp = np.sum(np.ma.masked_values(array_tmp1, cMF.hnoflo, atol = 0.09), axis = 1)
            rch_tot += rch_tmp
            flxCatch_lst.append(rch_tmp/sum(ncell_MM))
            i = 'iRg_%d'%(L+1)
            flxIndex_lst[i] = count
            count += 1
        flxLbl_lst.append(r'$Rg$')
        flxCatch_lst.append(rch_tot/sum(ncell_MM))
        flxIndex_lst['iRg'] = count
        count += 1
        flxLbl_lst.append(r'$\Delta S_{u}$')
        flxCatch_lst.append(flxCatch_lst[flxIndex_lst['iperc']] - rch_tot/sum(ncell_MM))
        flxIndex_lst['idSu'] = count
        count += 1        
        del array_tmp, array_tmp1, rch_tmp, rch_tot, cbc_RCH
        for L in range(cMF.nlay):
            # ADD heads averaged
            flxLbl_lst.append(r'$h_%d$' % (L+1))
            array_tmp = h_MF_m[:,L,:,:]
            array_tmp1 = np.sum(array_tmp, axis = 1)
            flxCatch_lst.append(np.sum(array_tmp1, axis = 1)/ncell_MF[L])
            i = 'ih_%d'%(L+1)
            flxIndex_lst[i] = count
            count += 1            
            del array_tmp
            # ADD depth GWT
            flxLbl_lst.append(r'$d_%d$' % (L+1))
            flxCatch_lst.append(flxCatch_lst[-1] - TopSoilAverage)
            i = 'id_%d'%(L+1)
            flxIndex_lst[i] = count
            count += 1   
            del array_tmp1
        for L in range(cMF.nlay):
            # GW_STO
            cbc_STO = h5_MF['STO_d'][:,L,:,:]
            array_tmp1 = np.sum(np.ma.masked_values(cbc_STO, cMF.hnoflo, atol = 0.09), axis = 1)
            flxCatch_lst.append(np.sum(np.ma.masked_values(array_tmp1, cMF.hnoflo, atol = 0.09), axis = 1)/sum(ncell_MM))
            del cbc_STO, array_tmp1
            flxLbl_lst.append(r'$\Delta S_{g,%d}$'%(L+1))
            i = 'idSg_%d'%(L+1)
            flxIndex_lst[i] = count
            count += 1   
            # GW_FRF
#            cbc_FRF = h5_MF['FRF_d'][:,L,:,:]
#            array_tmp1 = np.sum(np.ma.masked_values(cbc_FRF, cMF.hnoflo, atol = 0.09), axis = 1)
#            flxCatch_lst.append(np.sum(np.ma.masked_values(array_tmp1, cMF.hnoflo, atol = 0.09), axis = 1)/sum(ncell_MM))
#            del cbc_FRF, array_tmp1
            flxCatch_lst.append(np.zeros((sum(cMF.perlen)), dtype = np.int))
            flxLbl_lst.append('$FRF_%d$'%(L+1))
            i = 'iFRF_%d'%(L+1)
            flxIndex_lst[i] = count
            count += 1   
            # GW_FFF
#            cbc_FFF = h5_MF['FFF_d'][:,L,:,:]
#            array_tmp1 = np.sum(np.ma.masked_values(cbc_FFF, cMF.hnoflo, atol = 0.09), axis = 1)
#            flxCatch_lst.append(np.sum(np.ma.masked_values(array_tmp1, cMF.hnoflo, atol = 0.09), axis = 1)/sum(ncell_MM))
#            del cbc_FFF, array_tmp1
            flxCatch_lst.append(np.zeros((sum(cMF.perlen)), dtype = np.int))
            flxLbl_lst.append('$FFF_%d$'%(L+1))
            i = 'iFFF_%d'%(L+1)
            flxIndex_lst[i] = count
            count += 1               
            # GW_FLF
            if cMF.nlay>1:
                try:
                    cbc_FLF_L   = h5_MF['FLF_d'][:,L,:,:]
                    cbc_FLF_Lm1 = h5_MF['FLF_d'][:,L-1,:,:]
                    array_tmp1_L   = np.sum(np.ma.masked_values(cbc_FLF_L, cMF.hnoflo, atol = 0.09), axis = 1)
                    array_tmp1_Lm1 = np.sum(np.ma.masked_values(cbc_FLF_Lm1, cMF.hnoflo, atol = 0.09), axis = 1)
                    array_tmp2_L   = np.sum(np.ma.masked_values(array_tmp1_L, cMF.hnoflo, atol = 0.09), axis = 1)/sum(ncell_MM)
                    array_tmp2_Lm1 = np.sum(np.ma.masked_values(array_tmp1_Lm1, cMF.hnoflo, atol = 0.09), axis = 1)/sum(ncell_MM)
                    flxCatch_lst.append(-array_tmp2_Lm1 + array_tmp2_L)
                    del cbc_FLF_L, cbc_FLF_Lm1, array_tmp1_L, array_tmp2_L, array_tmp1_Lm1, array_tmp2_Lm1
                except:
                    cbc_FLF = h5_MF['FLF_d'][:,L,:,:]
                    array_tmp1 = np.sum(np.ma.masked_values(cbc_FLF, cMF.hnoflo, atol = 0.09), axis = 1)
                    flxCatch_lst.append(np.sum(np.ma.masked_values(array_tmp1, cMF.hnoflo, atol = 0.09), axis = 1)/sum(ncell_MM))
                    del cbc_FLF, array_tmp1
#                cbc_FLF = h5_MF['FLF_d'][:,L,:,:]
#                array_tmp1 = np.sum(np.ma.masked_values(cbc_FLF, cMF.hnoflo, atol = 0.09), axis = 1)
#                flxCatch_lst.append(np.sum(np.ma.masked_values(array_tmp1, cMF.hnoflo, atol = 0.09), axis = 1)/sum(ncell_MM))
#                del cbc_FLF, array_tmp1
                flxLbl_lst.append('$FLF_%d$'%(L+1))
                i = 'iFLF_%d'%(L+1)
                flxIndex_lst[i] = count
                count += 1              
            # EXF
            cbc_EXF = h5_MF['EXF_d'][:,L,:,:]
            array_tmp1 = np.sum(np.ma.masked_values(cbc_EXF, cMF.hnoflo, atol = 0.09), axis = 1)
            flxCatch_lst.append(np.sum(np.ma.masked_values(array_tmp1, cMF.hnoflo, atol = 0.09), axis = 1)/sum(ncell_MM))
            del cbc_EXF, array_tmp1            
            flxLbl_lst.append('$Exf_{g,%d}$'%(L+1))
            i = 'iEXFg_%d'%(L+1)
            flxIndex_lst[i] = count
            count += 1              
            # WEL
            if cMF.wel_yn == 1:
                cbc_WEL = h5_MF['WEL_d'][:,L,:,:]
                array_tmp1 = np.sum(np.ma.masked_values(cbc_WEL, cMF.hnoflo, atol = 0.09), axis = 1)
                flxCatch_lst.append(np.sum(np.ma.masked_values(array_tmp1, cMF.hnoflo, atol = 0.09), axis = 1)/sum(ncell_MM))
                flxLbl_lst.append('$WEL_%d$'%(L+1))
                i = 'iWEL_%d'%(L+1)
                flxIndex_lst[i] = count
                count += 1                  
                del cbc_WEL               
           # DRN
            if cMF.drn_yn == 1:
                cbc_DRN = h5_MF['DRN_d'][:,L,:,:]
                if cMF.drncells[L]>0:
                    array_tmp1 = np.sum(np.ma.masked_values(cbc_DRN, cMF.hnoflo, atol = 0.09), axis = 1)
                    flxCatch_lst.append(np.sum(np.ma.masked_values(array_tmp1, cMF.hnoflo, atol = 0.09), axis = 1)/sum(ncell_MM))
                    del array_tmp1
                else:
                    flxCatch_lst.append(np.zeros((sum(cMF.perlen)), dtype = np.int))
                flxLbl_lst.append('$DRN_%d$'%(L+1))
                i = 'iDRN_%d'%(L+1)
                flxIndex_lst[i] = count
                count += 1  
                del cbc_DRN
            # GHB
            if cMF.ghb_yn == 1:
                cbc_GHB = h5_MF['GHB_d'][:,L,:,:]
                if cMF.ghbcells[L] > 0:
                    array_tmp1 = np.sum(np.ma.masked_values(cbc_GHB, cMF.hnoflo, atol = 0.09), axis = 1)
                    flxCatch_lst.append(np.sum(np.ma.masked_values(array_tmp1, cMF.hnoflo, atol = 0.09), axis = 1)/sum(ncell_MM))
                    del array_tmp1
                else:
                    flxCatch_lst.append(np.zeros((sum(cMF.perlen)), dtype = np.int))                    
                flxLbl_lst.append('$GHB_%d$'%(L+1))
                i = 'iGHB_%d'%(L+1)
                flxIndex_lst[i] = count
                count += 1                  
                del cbc_GHB
            del i
        h5_MF.close()
        plt_exportCATCH_fn = os.path.join(MM_ws_out, '_0CATCHMENT_ts.png')
        plt_titleCATCH = 'Time series of fluxes averaged over the whole catchment'
        try:
            rmseHEADS_tmp, rmseSM_tmp, rsrHEADS_tmp, rsrSM_tmp, nseHEADS_tmp, nseSM_tmp, rHEADS_tmp, rSM_tmp = MMplot.plotTIMESERIES_CATCH(cMF, flxCatch_lst, flxLbl_lst, plt_exportCATCH_fn, plt_titleCATCH, hmax = hmaxMF, hmin = hminMF, iniMonthHydroYear = iniMonthHydroYear, date_ini = DATE[HYindex[1]], date_end = DATE[HYindex[-2]], flxIndex_lst = flxIndex_lst, obs_catch = obs_catch, obs_catch_list = obs_catch_list, TopSoilAverage = TopSoilAverage, MF = 1)
            print 'TS plot done!'
        except:
            print 'TS plot error!'            
    if rmseHEADS_tmp <> None:
        rmseHEADS.append(rmseHEADS_tmp)
        rsrHEADS.append(rsrHEADS_tmp)
        nseHEADS.append(nseHEADS_tmp)
        rHEADS.append(rHEADS_tmp)
        obslstHEADS.append('catch.')
    if rmseSM_tmp <> None:
        rmseSM.append(rmseSM_tmp)
        rsrSM.append(rsrSM_tmp)
        nseSM.append(nseSM_tmp)
        rSM.append(rSM_tmp)
        obslstSM.append('catch.')
    del rmseHEADS_tmp, rmseSM_tmp, rsrHEADS_tmp, rsrSM_tmp, nseHEADS_tmp, nseSM_tmp, rHEADS_tmp, rSM_tmp
    # export average time series of fluxes in txt
    plt_exportCATCH_txt_fn = os.path.join(MM_ws_out, '_0CATCHMENT_ts4sankey.txt')
    plt_exportCATCH_txt = open(plt_exportCATCH_txt_fn, 'w')
    flxlbl_CATCH_str = r'Date'
    for e in flxLbl_lst:
        flxlbl_CATCH_str += ',' + e
    flxlbl_CATCH_str += ',%s' % '$h \ obs$'
    flxlbl_CATCH_str += ',%s' % '$\theta \ obs$'
    flxlbl_CATCH_str += ',%s' % '$\\Ro \ obs$'
    plt_exportCATCH_txt.write(flxlbl_CATCH_str)
    plt_exportCATCH_txt.write('\n')
    for t in range(len(cMF.inputDate)):
        flxCatch_lst_str = str(flxCatch_lst[0][t])
        for e in (flxCatch_lst[1:]):
            flxCatch_lst_str += ',%s' % str(e[t])
        if obs_catch_list[0] == 1:
            flxCatch_lst_str += ',%s' % (obs_catch.get('catch')['obs_h'][0][t])
        else:
            flxCatch_lst_str += ',%s' % cMF.hnoflo
        if obs_catch_list[1] == 1:
            flxCatch_lst_str += ',%s' % (obs_catch.get('catch')['obs_SM'][0][t])
        else:
            flxCatch_lst_str += ',%s' % cMF.hnoflo
        if obs_catch_list[2] == 1:
            flxCatch_lst_str += ',%s' % (obs_catch.get('catch')['obs_Ro'][0][t])
        else:
            flxCatch_lst_str += ',%s' % cMF.hnoflo            
        out_line = '%s,%s' % (mpl.dates.num2date(cMF.inputDate[t]).isoformat()[:10], flxCatch_lst_str)
        for l in out_line:
            plt_exportCATCH_txt.write(l)
        plt_exportCATCH_txt.write('\n')
    plt_exportCATCH_txt.close()
    del flxlbl_CATCH_str
    if WBsankey_yn == 1:
        try:
            MMplot.plotWBsankey(MM_ws_out, cMF.inputDate, flxCatch_lst, flxIndex_lst, fn = plt_exportCATCH_txt_fn.split('\\')[-1], indexTime = HYindex, year_lst = year_lst, cMF = cMF, ncell_MM = ncell_MM, obspt = 'whole catchment', fntitle = '0CATCHMENT', ibound4Sankey = np.ones((cMF.nlay), dtype = int), stdout = stdout, report = report)
            print 'WB Sankey plot done!\n-------'
        except:
            print 'WB Sankey plot error!\n-------'
    del flxCatch_lst, flxCatch_lst_str, out_line, plt_exportCATCH_fn, plt_exportCATCH_txt_fn, plt_titleCATCH

# #################################################
# EXPORT AT OBSERVATION POINTS
# exporting MM time series results to ASCII files and plots at observations cells
# #################################################
if plt_out_obs == 1 and os.path.exists(h5_MM_fn) and os.path.exists(cMF.h5_MF_fn):
    print '\nExporting output ASCII files, time series plots and water balance sankey plots of water fluxes at observation points...'
    valid = 0
    try:
        h5_MF = h5py.File(cMF.h5_MF_fn, 'r')
        h5_MM = h5py.File(h5_MM_fn, 'r')
    except:
        cUTIL.ErrorExit('\nFATAL ERROR!\nInvalid MM or MF HDF5 file. Run MARMITES and/or MODFLOW again.', stdout = stdout, report = report)
        valid  = 1
    if valid == 0:
        clr_lst = ['darkgreen', 'firebrick', 'darkmagenta', 'goldenrod', 'green', 'tomato', 'magenta', 'yellow']
        for o_ref in obs_list:
            for o in obs.keys():
                if o == o_ref:
                    print '-------\nObs. point [%s]' % o
                    flxObs_lst = []
                    i = obs.get(o)['i']
                    j = obs.get(o)['j']
                    l_obs = obs.get(o)['lay']
                    l_highest = cMF.outcropL[i,j]-1
                    obs_h = obs.get(o)['obs_h']
                    obs_S = obs.get(o)['obs_SM']
                    obs_Ro = obs.get(o)['obs_Ro']
                    SOILzone_tmp = gridSOIL[i,j]-1
                    nsl = _nsl[SOILzone_tmp]
                    soilnam = _nam_soil[SOILzone_tmp]
                    slprop = _slprop[SOILzone_tmp]
                    # thickness of soil layers
                    Tl = list(gridSOILthick[i,j]*slprop)
                    for ii, ll in enumerate(Tl):
                        Tl[ii] = float('%.3f' % ll)
                    MM = h5_MM['MM'][:,i,j,:]
                    MM_S = h5_MM['MM_S'][:,i,j,:,:]
                    # SATFLOW
                    cbc_RCH = h5_MF['RCH_d']
                    h_satflow = MM_SATFLOW.runSATFLOW(cbc_RCH[:,l_highest,i,j], float(obs.get(o)['hi']),float(obs.get(o)['h0']),float(obs.get(o)['RC']),float(obs.get(o)['STO']))
                    # export ASCII file at piezometers location
                    #TODO extract heads at piezo location and not center of cell
                    if obs_h != []:
                        obs_h_tmp = obs_h[0,:]
                    else:
                        obs_h_tmp = []
                    if obs_Ro != []:
                        obs_Ro_tmp = obs_Ro[0,:]
                    else:
                        obs_Ro_tmp = []
                    obs_S_tmp = []
                    if obs_S!= []:
                        for l in range(nsl):
                            if obs_S[l] != []:
                                obs_S_tmp.append(obs_S[l,:])
                            else:
                                obs_S_tmp.append([])
                    else:
                        for l in range(nsl): obs_S_tmp.append([])
                    VEGarea = []
                    VEGareaTot = 0.0
                    for v in range(NVEG):
                        VEGarea.append(round(gridVEGarea[v,i,j],2))
                        VEGareaTot += gridVEGarea[v,i,j]
                    SOILarea = 100.0 - VEGareaTot
                    if irr_yn == 0:
                        index_veg = np.ones((NVEG, sum(cMF.perlen)), dtype = float)
                        for v in range(NVEG):
                            index_veg[v] = cMF.LAI_veg_d[gridMETEO[i,j]-1,v,:]*gridVEGarea[v,i,j]
                        index_veg = (np.sum(index_veg, axis = 0) > 0.0)*(-1)
                    else:
                        IRRfield = gridIRR[i,j]
                        if IRRfield == 0:
                            index_veg = np.ones((NVEG, sum(cMF.perlen)), dtype = float)
                            for v in range(NVEG):
                                index_veg[v] = cMF.LAI_veg_d[gridMETEO[i,j]-1,v,:]*gridVEGarea[v,i,j]
                            index_veg = (np.sum(index_veg, axis = 0) > 0.0)*(-1)
                        else:
                            index_veg = cMF.crop_irr_d[gridMETEO[i,j]-1, IRRfield-1,:]
                    # make flx list and corresponding labels (tex)
                    flxIndex_lst = {}
                    flxObs_lst = []
                    count = 0
                    # flx from MM
                    # index_MM = {'iRF':0, 'iPT':1, 'iPE':2, 'iRFe':3, 'iSsurf':4, 'iRo':5, 'iEXFg':6, 'iEsurf':7, 'iMB':8, 'iI':9, 'iE0':10, 'iEg':11, 'iTg':12, 'idSsurf':13, 'iETg':14, 'iETsoil':15, 'iSsoil_pc':16, 'idSsoil':17, 'iperc':18, 'ihcorr':19, 'idgwt':20, 'iuzthick':21, 'iInf': 22, 'iMBsurf':23}
                    flx_lst = []
                    for e in sorted(index_MM, key=index_MM.get): flx_lst.append(e)
                    flxLbl_lst = [r'$RF$', r'$PT$', r'$PE$', r'$RFe$', r'$S_{surf}$', r'$Ro$', r'$Exf_g$', r'$E_{surf}$',  r'$MB_{soil}$', r'$I$',  r'$E_0$', r'$E_g$', r'$T_g$', r'$\Delta S_{surf}$', r'$ET_g$', r'$ET_{soil}$', r'$\theta$', r'\Delta S_{soil}', r'$perc$', r'$h \ corr$', '$d$', r'$thick_p$', r'$Inf$', r'$MB_{surf}$']    
                    for ii in flx_lst:              
                        flxObs_lst.append((MM[:,index_MM.get(ii)]))
                        flxIndex_lst[ii] = count
                        count += 1
                    # flx from MM_S
                    # whole soil reservoir
                    # index_MM_soil = {'iEsoil':0, 'iTsoil':1,'iSsoil_pc':2, 'iRsoil':3, 'iExf':4, 'idSsoil':5, 'iSsoil':6, 'iSAT':7, 'iMB':8}
                    flx_lst = []
                    for e in sorted(index_MM_soil, key=index_MM_soil.get): flx_lst.append(e)
                    for z, (ii, ii_tex) in enumerate(zip(flx_lst, ['E_{soil}', 'T_{soil}', '\\thetaWRONG', 'R_p', 'Exf', '\Delta S_{soil}WRONG', 'S_{soil}WRONG', 'SATWRONG', 'MB_{soil}'])):
                        flxLbl_lst.append(r'$%s$'%ii_tex)
                        flxObs_lst.append((np.sum(np.ma.masked_values(MM_S[:,:,index_MM_soil.get(ii)], cMF.hnoflo, atol = 0.09), axis = 1)))
                        flxIndex_lst[ii] = count
                        count += 1
                    # each layer of soil reservoir
                    for z, (ii, ii_tex) in enumerate(zip(flx_lst, [r'E_{soil}', 'T_{soil}', '\\theta', 'R_{soil}', 'Exf','\Delta \\theta', 'S_{soil}', 'SAT', 'MB_{soil}'])):
                        for l in range(nsl):
                            try:
                                pos = ii_tex.index('}')
                                str_tmp = r'$%s,%d}$'  % (ii_tex[:pos], l+1)
                                flxLbl_lst.append(str_tmp)
                                del pos, str_tmp
                            except:
                                flxLbl_lst.append(r'$%s_%d$'%(ii_tex,l+1))
                            flxObs_lst.append(np.ma.masked_values(MM_S[:,l,index_MM_soil.get(ii)], cMF.hnoflo, atol = 0.09))
                            flxIndex_lst['%s_%d'%(ii,l+1)] = count
                            count += 1
                    del flx_lst
                    # ET fluxes
                    if cMF.wel_yn == 1:
                        flx_lst = ['iEg','iTg']
                        for L in range(cMF.nlay): flxLbl_lst.append(r'$E_{g,%d}$'%(L+1))
                        for L in range(cMF.nlay): flxLbl_lst.append(r'$T_{g,%d}$'%(L+1))
                        for ii in flx_lst:                                                         
                            array_tmp = MM[:,index_MM.get(ii)]
                            for L in range(cMF.nlay):
                                mask_temp = mask_Lsup == (cMF.nlay-L)
                                flxObs_lst.append(array_tmp*mask_temp[i,j])
                                flxIndex_lst['%s_%d' % (ii, L+1)] = count
                                count += 1
                            del array_tmp
                        del flx_lst
                    # h
                    for L in range(cMF.nlay):
                        flxLbl_lst.append(r'$h_%d$' % (L+1))
                        flxObs_lst.append(h_MF_m[:,L,i,j])
                        flxIndex_lst['ih_%d'%(L+1)] = count
                        count += 1
                        # ADD depth GWT
                        flxLbl_lst.append( r'$d_%d$' % (L+1))
                        flxObs_lst.append(flxObs_lst[-1] - cMF.elev[i,j])
                        flxIndex_lst['id_%d'%(L+1)] = count
                        count += 1                        
                    # h SATFLOW
                    flxLbl_lst.append(r'$hSF$')
                    flxObs_lst.append(h_satflow)
                    flxIndex_lst['ih_SF'] = count
                    count += 1
                    # depth GWT SATFLOW
                    flxLbl_lst.append(r'$dSF$')
                    flxObs_lst.append(flxObs_lst[-1] - cMF.elev[i,j])
                    flxIndex_lst['id_SF'] = count
                    count += 1     
                    # depth GWT HEADS corr
                    flxLbl_lst.append(r'$d \ corr$')
                    flxObs_lst.append(flxObs_lst[flxIndex_lst['ihcorr']] - cMF.elev[i,j])
                    flxIndex_lst['idcorr'] = count
                    count += 1                         
                    # h obs
                    if obs_h_tmp != []:
                        flxLbl_lst.append(r'$h \ obs$')
                        flxObs_lst.append(np.ma.masked_values(obs_h_tmp, cMF.hnoflo, atol = 0.09))
                        flxIndex_lst['ihobs'] = count
                        count += 1
                        flxLbl_lst.append(r'$d \ obs$')
                        flxObs_lst.append(np.ma.masked_values(obs_h_tmp, cMF.hnoflo, atol = 0.09)-cMF.elev[i,j])
                        flxIndex_lst['idobs'] = count
                        count += 1
                    del obs_h_tmp
                    # S obs
                    for l in range(nsl):
                        if obs_S_tmp[l] != []:
                            flxLbl_lst.append(r'$\theta_%d \ obs$'%(l+1))
                            flxObs_lst.append(np.ma.masked_values(obs_S_tmp[l], cMF.hnoflo, atol = 0.09))
                            flxIndex_lst['iSobs_%d'%(l+1)] = count
                            count += 1
                    del obs_S_tmp
                    # Roobs
                    if obs_Ro_tmp != []:
                        flxLbl_lst.append(r'$Ro \ obs$')
                        flxObs_lst.append(np.ma.masked_values(obs_Ro_tmp, cMF.hnoflo, atol = 0.09))
                        flxIndex_lst['iRoobs'] = count
                        count += 1
                    del obs_Ro_tmp
                    # GW_RCH
                    flxLbl_lst.append(r'$Rg$')
                    flxObs_lst.append(cbc_RCH[:,l_highest,i,j])
                    flxIndex_lst['iRg'] = count
                    count += 1
                    # STO UZF
                    flxLbl_lst.append(r'$Perc_p$')
                    flxObs_lst.append(conv_fact*h5_MM['perc_d'][:,i,j])
                    flxIndex_lst['iperc'] = count
                    count += 1
                    flxLbl_lst.append(r'$\Delta S_{u}$')
                    flxObs_lst.append(flxObs_lst[flxIndex_lst['iperc']] - flxObs_lst[flxIndex_lst['iRg']])
                    flxIndex_lst['idSu'] = count
                    count += 1
                    for L in range(cMF.nlay):
                        # GW STO
                        cbc_STO = h5_MF['STO_d']
                        flxObs_lst.append(cbc_STO[:,L,i,j])
                        del cbc_STO
                        flxLbl_lst.append(r'$\Delta S_{g,%d}$'%(L+1))
                        flxIndex_lst['idSg_%d'%(L+1)] = count
                        count += 1
                        # GW Rg
                        cbc_R = h5_MF['RCH_d']
                        flxObs_lst.append(cbc_R[:,L,i,j])
                        del cbc_R
                        flxLbl_lst.append(r'$Rg_%d$'%(L+1))
                        flxIndex_lst['iRg_%d'%(L+1)] = count
                        count += 1                        
                        # GW FRF
                        try:
                            flxObs_lst.append(-h5_MF['FRF_d'][:,L,i,j-1]+h5_MF['FRF_d'][:,L,i,j])
                        except:
                            flxObs_lst.append(h5_MF['FRF_d'][:,L,i,j])
                        flxLbl_lst.append('$FRF_%d$'%(L+1))
                        flxIndex_lst['iFRF_%d'%(L+1)] = count
                        count += 1
                        # GW FFF
                        try:
                            flxObs_lst.append(-h5_MF['FFF_d'][:,L,i-1,j]+h5_MF['FFF_d'][:,L,i,j])
                        except:
                            flxObs_lst.append(h5_MF['FFF_d'][:,L,i,j])
                        flxLbl_lst.append('$FFF_%d$'%(L+1))
                        flxIndex_lst['iFFF_%d'%(L+1)] = count
                        count += 1
                        # GW FLF
                        if cMF.nlay>1:
                            try:
                                flxObs_lst.append(-h5_MF['FLF_d'][:,L-1,i,j]+h5_MF['FLF_d'][:,L,i,j])
                            except:
                                flxObs_lst.append(h5_MF['FLF_d'][:,L,i,j])
                            flxLbl_lst.append('$FLF_%d$'%(L+1))
                            flxIndex_lst['iFLF_%d'%(L+1)] = count
                            count += 1
                        # EXF
                        flxObs_lst.append(h5_MF['EXF_d'][:,L,i,j])
                        flxLbl_lst.append('$Exf_{g,%d}$'%(L+1))
                        flxIndex_lst['iEXFg_%d'%(L+1)] = count
                        count += 1              
                        # WEL
                        if cMF.wel_yn == 1:
                            flxObs_lst.append(h5_MF['WEL_d'][:,L,i,j])
                            flxLbl_lst.append('$WEL_%d$'%(L+1))
                            flxIndex_lst['iWEL_%d'%(L+1)] = count
                            count += 1              
                        # DRN
                        if cMF.drn_yn == 1:
                            flxObs_lst.append(h5_MF['DRN_d'][:,L,i,j])
                            flxLbl_lst.append('$DRN_%d$'%(L+1))
                            flxIndex_lst['iDRN_%d'%(L+1)] = count
                            count += 1                                  
                        # GHB
                        if cMF.ghb_yn == 1:
                            flxObs_lst.append(h5_MF['GHB_d'][:,L,i,j])
                            flxLbl_lst.append('$GHB_%d$'%(L+1))
                            flxIndex_lst['iGHB_%d'%(L+1)] = count
                            count += 1                                  

                    # export time series of fluxes in txt
                    plt_export_txt_fn = os.path.join(MM_ws_out, '_0%s_ts4sankey.txt'%o)
                    plt_export_obs_txt = open(plt_export_txt_fn, 'w')
                    flxObs_str = 'Date'
                    for e in flxLbl_lst:
                        flxObs_str += ',' + e
                    plt_export_obs_txt.write(flxObs_str)
                    plt_export_obs_txt.write('\n')
                    del flxObs_str
                    for t in range(len(cMF.inputDate)):
                        flxObs_str = str(flxObs_lst[0][t])
                        for e in flxObs_lst[1:]:
                            flxObs_str += ',%s' % str(e[t])
                        out_line = '%s,%s' % (mpl.dates.num2date(cMF.inputDate[t]).isoformat()[:10], flxObs_str)
                        del flxObs_str
                        for l in out_line:
                            plt_export_obs_txt.write(l)
                        plt_export_obs_txt.write('\n')
                    plt_export_obs_txt.close()

                    # plot time series at each obs. cell
                    plt_suptitle = 'Time series of fluxes at observation point %s' % o
                    plt_title = 'i = %d, j = %d, l_obs = %d, l_highest = %d, x = %.2f, y = %.2f, elev. = %.2f, %s\nSm = %s, Sfc = %s, Sr = %s, Ks = %s, thick. = %.3f %s\nfrac. area veg. = %s (veg. name = %s)\nfrac. area veg. tot. = %.1f, frac. area soil = %.1f' % (i+1, j+1, l_obs+1, l_highest+1, obs.get(o)['x'], obs.get(o)['y'], cMF.elev[i,j], soilnam, _Sm[SOILzone_tmp], _Sfc[SOILzone_tmp], _Sr[SOILzone_tmp], _Ks[SOILzone_tmp], gridSOILthick[i,j], Tl, VEGarea, VegName, VEGareaTot, SOILarea)
                    # index_MM = {'iRF':0, 'iPT':1, 'iPE':2, 'iRFe':3, 'iSsurf':4, 'iRo':5, 'iEXFg':6, 'iEsurf':7, 'iMB':8, 'iI':9, 'iE0':10, 'iEg':11, 'iTg':12, 'idSsurf':13, 'iETg':14, 'iETsoil':15, 'iSsoil_pc':16, 'idSsoil':17, 'iperc':18, 'ihcorr':19, 'idgwt':20, 'iuzthick':21, 'iInf': 22, 'iMBsurf':23}
                    # index_MM_soil = {'iEsoil':0, 'iTsoil':1,'iSsoil_pc':2, 'iRsoil':3, 'iExf':4, 'idSsoil':5, 'iSsoil':6, 'iSAT':7, 'iMB':8}
                    plt_export_fn = os.path.join(MM_ws_out, '_0%s_ts.png'%o)
                    # def plotTIMESERIES(DateInput, P, PT, PE, Pe, dPOND, POND, Ro, Eu, Tu, Eg, Tg, S, dS, Spc, Rp, EXF, ETg, Es, MB, MB_l, dgwt, SAT, Rg, h_MF, h_MF_corr, h_SF, hobs, Sobs, Sm, Sr, hnoflo, plt_export_fn, plt_title, colors_nsl, hmax, hmin):
                    try:
                        MMplot.plotTIMESERIES(cMF, i, j, flxObs_lst, flxLbl_lst, flxIndex_lst,
                                        _Sm[gridSOIL[i,j]-1], _Sr[gridSOIL[i,j]-1],
                                        plt_export_fn, plt_suptitle, plt_title,
                                        clr_lst,
                                        max(hmax), min(hmin),
                                        o, l_obs, nsl,
                                        iniMonthHydroYear, date_ini = DATE[HYindex[1]], date_end = DATE[HYindex[-2]]
                                        )
                        print 'TS plot done!'
                    except:
                        print 'TS plot error!'
                   # plot GW flux time series at each obs. cell
                    try:
                        MMplot.plotTIMESERIES_flxGW(cMF, flxObs_lst, flxLbl_lst, flxIndex_lst, plt_export_fn, plt_suptitle, iniMonthHydroYear = iniMonthHydroYear, date_ini = DATE[HYindex[1]], date_end = DATE[HYindex[-2]])
                        print 'TS GW plot done!'
                    except:
                       print 'TS GW error!'
                    # plot water balance at each obs. cell
                    if WBsankey_yn == 1:
                        try:
                            MMplot.plotWBsankey(MM_ws_out, cMF.inputDate , flxObs_lst, flxIndex_lst, fn = plt_export_txt_fn.split('\\')[-1], indexTime = HYindex, year_lst = year_lst, cMF = cMF, ncell_MM = ncell_MM, obspt = 'obs. pt. %s'%o, fntitle = '0%s'%o, ibound4Sankey = cMF.ibound[:,i,j], stdout = stdout, report = report)
                            print 'WB Sankey plot done!'
                        except:
                           print 'WB Sankey plot error!'
                           
                    # CALIBRATION CRITERIA
                    # RMSE, RSR, Nash-Sutcliffe efficiency NSE, Pearson's correlation coefficient r
                    # Moriasi et al, 2007, ASABE 50(3):885-900
                    # TODO insert Ro            
                    if obs_S != []:
                        obs_SM_tmp = obs_S[:,HYindex[1]:HYindex[-2]]
                    else:
                        obs_SM_tmp = []
                    MM_S = h5_MM['MM_S'][HYindex[1]:HYindex[-2],i,j,0:nsl,index_MM_soil.get('iSsoil_pc')]
                    if obs_h != []:
                        obs_h_tmp = obs_h[0,HYindex[1]:HYindex[-2]]
                    else:
                        obs_h_tmp = []    
                    h_MF = h_MF_m[HYindex[1]:HYindex[-2],l_obs,i,j]
                    rmseHEADS_tmp, rmseHEADSc_tmp, rmseSM_tmp, rsrHEADS_tmp, rsrHEADSc_tmp, rsrSM_tmp, nseHEADS_tmp, nseHEADSc_tmp, nseSM_tmp, rHEADS_tmp, rHEADSc_tmp, rSM_tmp = cMF.cPROCESS.compCalibCritObs(MM_S, h_MF, obs_SM_tmp, obs_h_tmp, cMF.hnoflo, o, nsl, MM[HYindex[1]:HYindex[-2],index_MM.get('ihcorr')])
                    del obs_h_tmp, obs_SM_tmp
                    if rmseHEADS_tmp <> None:
                        rmseHEADS.append(rmseHEADS_tmp)
                        rsrHEADS.append(rsrHEADS_tmp)
                        nseHEADS.append(nseHEADS_tmp)
                        rHEADS.append(rHEADS_tmp)
                        obslstHEADS.append(o)
                    if rmseHEADSc_tmp <> None:
                        rmseHEADSc.append(rmseHEADSc_tmp)
                        rsrHEADSc.append(rsrHEADSc_tmp)
                        nseHEADSc.append(nseHEADSc_tmp)
                        rHEADSc.append(rHEADSc_tmp)
                        obslstHEADSc.append(o)                        
                    if rmseSM_tmp <> None:
                        rmseSM.append(rmseSM_tmp)
                        rsrSM.append(rsrSM_tmp)
                        nseSM.append(nseSM_tmp)
                        rSM.append(rSM_tmp)
                        obslstSM.append(o)
                    del rmseHEADS_tmp, rmseSM_tmp, rsrHEADS_tmp, rsrSM_tmp, nseHEADS_tmp, nseSM_tmp, rHEADS_tmp, rSM_tmp, h_MF, MM_S
        for cc, (calibcritSM, calibcritHEADS, calibcritHEADSc, calibcrit, title, calibcritSMmax, calibcritHEADSmax, ymin, units) in enumerate(zip([rmseSM, rsrSM, nseSM, rSM], [rmseHEADS, rsrHEADS, nseHEADS, rHEADS], [rmseHEADSc, rsrHEADSc, nseHEADSc, rHEADSc], ['RMSE', 'RSR', 'NSE', 'r'], ['Root mean square error', 'Root mean square error - observations standard deviation ratio', 'Nash-Sutcliffe efficiency', "Pearson's correlation coefficient"], [rmseSMmax, None, 1.0, 1.0], [rmseHEADSmax, None, 1.0, 1.0], [0, 0, None, -1.0], [['(m)', '(%wc)'], ['',''], ['',''], ['','']])):
            try:
                MMplot.plotCALIBCRIT(calibcritSM = calibcritSM, calibcritSMobslst = obslstSM, calibcritHEADS = calibcritHEADS, calibcritHEADSobslst = obslstHEADS, calibcritHEADSc = calibcritHEADSc, calibcritHEADScobslst = obslstHEADSc, plt_export_fn = os.path.join(MM_ws_out, '__plt_calibcrit%s.png'% calibcrit), plt_title = 'Calibration criteria between simulated and observed state variables\n%s'%title, calibcrit = calibcrit, calibcritSMmax = calibcritSMmax, calibcritHEADSmax = calibcritHEADSmax, ymin = ymin, units = units, hnoflo = cMF.hnoflo)
            except:
                print '-------\nError in exporting %s at obs. pt. %s' % (calibcrit, obs_list[cc])
        if len(obslstHEADS)> 0 or len(obslstSM) > 0:
            print '-------\nRMSE/RSR/NSE/r averages of the obs. pts. (except catch.)'
            try:
                for cc, (rmse, rsr, nse, r, obslst, msg) in enumerate(zip([rmseSM,rmseHEADS],[rsrSM,rsrHEADS],[nseSM,nseHEADS],[rSM,rHEADS],[obslstSM,obslstHEADS],['SM (all layers): %.1f %% /','h: %.2f m /'])):
                    if obslst <> []:
                        # TODO filter cMF.hnoflo data
                        if obslst[0] == 'catch.' and len(rmse)> 1:
                            rmseaverage = list(itertools.chain.from_iterable(rmse[1:]))
                            rsraverage = list(itertools.chain.from_iterable(rsr[1:]))
                            nseaverage = list(itertools.chain.from_iterable(nse[1:]))
                            raverage = list(itertools.chain.from_iterable(r[1:]))
                            numobs = len(obslst[1:])
                        else:
                            rmseaverage = list(itertools.chain.from_iterable(rmse))
                            rsraverage = list(itertools.chain.from_iterable(rsr))
                            nseaverage = list(itertools.chain.from_iterable(nse))
                            raverage = list(itertools.chain.from_iterable(r))
                            numobs = len(obslst)
                        if len(rmse)> 1:
                            rmseaverage = sum(rmseaverage)/float(len(rmseaverage))
                            rsraverage = sum(rsraverage)/float(len(rsraverage))
                            nseaverage = sum(nseaverage)/float(len(nseaverage))
                            raverage = sum(raverage)/float(len(raverage))
                            msg = '%s %s' % (msg, '%.2f / %.2f / %.2f (%d obs. points)')
                            print msg % (rmseaverage, rsraverage, nseaverage, raverage, numobs)
            except:
                print '-------\nError! Check observations data.'
            print '-------'
                    
        del flxObs_lst, flxLbl_lst, flxIndex_lst
        del h_satflow, MM
        del i, j, l_obs, l_highest, SOILzone_tmp, nsl, soilnam, slprop, Tl, plt_export_fn                
        h5_MM.close()
        h5_MF.close()

# #################################################
# PLOT SPATIAL MF and MM OUTPUT
# #################################################
if plt_out == 1 and os.path.exists(h5_MM_fn) and os.path.exists(cMF.h5_MF_fn):
    print '\nExporting output maps...'
    sp_lst = []
    days_lst = []
    Date_lst = []
    JD_lst = []
    day = HYindex[1]
    if animation == 0:
        while day < sum(cMF.perlen):  #len(h_MF_m):
            days_lst.append(day)
            sp_lst.append(sp_days_lst[day])
            Date_lst.append(cMF.inputDate[day])
            JD_lst.append(cMF.JD[day])
            day += plt_freq        
        lst = [sum(cMF.perlen)-1]
        if tRCHmax > 0:
            lst.append(tRCHmax)
        if cMF.wel_yn == 1:
            if tETgmax > 0:
                lst.append(tETgmax)
            if tTgmin > 0:
                lst.append(tTgmin)
        for e in lst:
            days_lst.append(e)
            Date_lst.append(cMF.inputDate[e])
            JD_lst.append(cMF.JD[e])
            sp_lst.append(sp_days_lst[e])
    else:
        for t, e in enumerate(HYindex[1:-2]):
            days_lst.append(e)
            sp_lst.append(sp_days_lst[e])
            Date_lst.append(cMF.inputDate[e])
            JD_lst.append(cMF.JD[e])
            for i in range(1,animation_freq):
                inter=HYindex[t+2]-HYindex[t+1]
                days_lst.append(int(e+inter*i/float(animation_freq)))
                sp_lst.append(sp_days_lst[int(e+inter*i/float(animation_freq))])
                Date_lst.append(cMF.inputDate[int(e+inter*i/float(animation_freq))])
                JD_lst.append(cMF.JD[int(e+inter*i/float(animation_freq))])
#        days_lst.append(HYindex[-1])
#        sp_lst.append(sp_days_lst[HYindex[-1]])
#        Date_lst.append(cMF.inputDate[HYindex[-1]])
#        JD_lst.append(cMF.JD[HYindex[-1]])
    del day

    # ##############################
    # #### MODFLOW OUTPUT ##########
    # ##############################
    h5_MF = h5py.File(cMF.h5_MF_fn, 'r')
    h5_MM = h5py.File(h5_MM_fn, 'r')
    cbc_RCH = h5_MF['RCH_d']
    cbc_EXF = h5_MF['EXF_d']
    if cMF.wel_yn == 1:
        cbc_WEL = h5_MF['WEL_d']
    if cMF.drn_yn == 1:
        cbc_DRN = h5_MF['DRN_d']
    if cMF.ghb_yn == 1:
        cbc_GHB = h5_MF['GHB_d']

    # ############################################
    # plot at specified day
    # ############################################
    # plot heads [m]
    V = np.zeros((len(days_lst), cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
    mask_tmp = np.zeros((cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
    maskAllL_tmp  = np.zeros((cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
    Vmax = np.zeros((len(days_lst)), dtype = np.float)
    Vmin = np.zeros((len(days_lst)), dtype = np.float)
    Vmax1 = np.zeros((len(days_lst)), dtype = np.float)
    Vmin1 = np.zeros((len(days_lst)), dtype = np.float)
    for i, t in enumerate(days_lst):
        for L in range(cMF.nlay):
            V[i,L,:,:] = h_MF_m[t,L,:,:]
            mask_tmp[L,:,:] = mask[L]
            maskAllL_tmp[L,:,:] = cMF.maskAllL
        Vmax[i] = hmaxMF
        Vmin[i] = hminMF
    MMplot.plotLAYER(days = days_lst, str_per = sp_lst, Date = Date_lst, JD = JD_lst, ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = V,  cmap = plt.cm.Blues, CBlabel = 'hydraulic heads elevation - $h$ (m)', msg = 'DRY', plt_title = 'OUT_MF_HEADS', MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, contours = ctrsMF, Vmax = Vmax, Vmin = Vmin, ntick = ntick, points = obs4map, mask = mask_tmp, hnoflo = cMF.hnoflo, animation = animation, cMF = cMF)

    # plot GWTD [m]
    for i, t in enumerate(days_lst):
       for L in range(cMF.nlay):
        V[i,L,:,:] = cMF.elev - V[i,L,:,:]
        Vmin[i] = GWTDmin
        Vmax[i] = GWTDmax
    MMplot.plotLAYER(days = days_lst, str_per = sp_lst, Date = Date_lst, JD = JD_lst, ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = V,  cmap = plt.cm.Blues, CBlabel = 'depth to groundwater table - $d$ (m)', msg = 'DRY', plt_title = 'OUT_MF_GWTD', MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, contours = ctrsMF, Vmax = Vmax, Vmin = Vmin, ntick = ntick, points = obs4map, mask = mask_tmp, hnoflo = cMF.hnoflo, animation = animation, cMF = cMF)

    # plot heads corrigidas [m]
    headscorr_m = np.zeros((len(days_lst), cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
    for i, t in enumerate(days_lst):
        headscorr_m[i,0,:,:] = np.ma.masked_values(np.ma.masked_values(h5_MM['MM'][t,:,:,index_MM.get('ihcorr')], cMF.hnoflo, atol = 0.09), cMF.hdry, atol = 1E+25)
        Vmin[i] = hcorrmin
        Vmax[i] = hcorrmax
    MMplot.plotLAYER(days = days_lst, str_per = sp_lst, Date = Date_lst, JD = JD_lst, ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = 1, V = headscorr_m,  cmap = plt.cm.Blues, CBlabel = 'hydraulic heads elevation - $h$ (m)', msg = 'DRY', plt_title = 'OUT_MF_HEADScorr', MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, contours = ctrsMF, Vmax = Vmax, Vmin = Vmin, ntick = ntick, points = obs4map, mask = mask_tmp, hnoflo = cMF.hnoflo, animation = animation, cMF = cMF)

    # plot GWTD correct [m]
    GWTDcorr = np.zeros((len(days_lst), cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
    for i, t in enumerate(days_lst):
        GWTDcorr[i,0,:,:] = cMF.elev-headscorr_m[i,0,:,:]
        Vmin[i] = GWTDcorrmin
        Vmax[i] = GWTDcorrmax
    MMplot.plotLAYER(days = days_lst, str_per = sp_lst, Date = Date_lst, JD = JD_lst, ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = 1, V = GWTDcorr,  cmap = plt.cm.Blues, CBlabel = 'depth to groundwater table - $d$ (m)', msg = 'DRY', plt_title = 'OUT_MF_GWTDcorr', MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, contours = ctrsMF, Vmax = Vmax, Vmin = Vmin, ntick = ntick, points = obs4map, mask = mask_tmp, hnoflo = cMF.hnoflo, animation = animation, cMF = cMF)

    # plot GW GROSS RCH [mm]
    Rg = np.zeros((len(days_lst), cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
    for i, t in enumerate(days_lst):
        for L in range(cMF.nlay):
            Rg[i,L,:,:] = np.ma.masked_array(cbc_RCH[t,L,:,:], mask[L])
        Vmin[i] = RCHmin
        Vmax[i] = RCHmax
        Vmin1[i] = np.ma.min(Rg[i,:,:,:])
        Vmax1[i] = np.ma.max(Rg[i,:,:,:])
    MMplot.plotLAYER(days = days_lst, str_per = sp_lst, Date = Date_lst, JD = JD_lst, ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = Rg,  cmap = plt.cm.Blues, CBlabel = 'groundwater gross recharge - $Rg$ (mm.day$^{-1}$)', msg = '- no flux', plt_title = 'OUT_MF_Rg', MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, Vmin = Vmin, contours = ctrsMF, Vmax = Vmax, ntick = ntick, points = obs4map, hnoflo = cMF.hnoflo, mask = mask_tmp, animation = animation, cMF = cMF)
    MMplot.plotLAYER(days = days_lst, str_per = sp_lst, Date = Date_lst, JD = JD_lst, ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = Rg,  cmap = plt.cm.Blues, CBlabel = 'groundwater gross recharge - $Rg$ (mm.day$^{-1}$)', msg = '- no flux', plt_title = 'OUT_MF_Rg1', MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, Vmin = Vmin1, contours = ctrsMF, Vmax = Vmax1, ntick = ntick, points = obs4map, hnoflo = cMF.hnoflo, mask = mask_tmp, animation = animation, cMF = cMF)
    
    # plot GW EFFECTIVE RCH [mm]
    Re = np.zeros((len(days_lst), cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
    for i, t in enumerate(days_lst):
        for L in range(cMF.nlay):
            Re[i,L,:,:] = Rg[i,L,:,:] + np.ma.masked_array(cbc_EXF[t,L,:,:], mask[L])
        Vmin[i] = np.ma.min(Re)
        Vmax[i] = np.ma.max(Re)
        Vmin1[i] = np.ma.min(Re[i,:,:,:])
        Vmax1[i] = np.ma.max(Re[i,:,:,:])
    MMplot.plotLAYER(days = days_lst, str_per = sp_lst, Date = Date_lst, JD = JD_lst, ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = Re,  cmap = plt.cm.Blues, CBlabel = 'groundwater effective recharge - $Re$ (mm.day$^{-1}$)', msg = '- no flux', plt_title = 'OUT_MF_Re', MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, Vmin = Vmin, contours = ctrsMF, Vmax = Vmax, ntick = ntick, points = obs4map, hnoflo = cMF.hnoflo, mask = mask_tmp, animation = animation, cMF = cMF)
    MMplot.plotLAYER(days = days_lst, str_per = sp_lst, Date = Date_lst, JD = JD_lst, ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = Re,  cmap = plt.cm.Blues_r, CBlabel = 'groundwater effective recharge - $Re$ (mm.day$^{-1}$)', msg = '- no flux', plt_title = 'OUT_MF_Re1', MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, Vmin = Vmin1, contours = ctrsMF, Vmax = Vmax1, ntick = ntick, points = obs4map, hnoflo = cMF.hnoflo, mask = mask_tmp, animation = animation, cMF = cMF)

    # plot GW NET RCH [mm]
    if cMF.wel_yn == 1: 
        Rn = np.zeros((len(days_lst), cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
        for i, t in enumerate(days_lst):
            for L in range(cMF.nlay):
                Rn[i,L,:,:] = Re[i,L,:,:] + cbc_WEL[t,L,:,:]
            Vmin[i] = np.ma.min(Rn)
            Vmax[i] = np.ma.max(Rn)
            Vmin1[i] = np.ma.min(Rn[i,:,:,:])
            Vmax1[i] = np.ma.max(Rn[i,:,:,:])
        MMplot.plotLAYER(days = days_lst, str_per = sp_lst, Date = Date_lst, JD = JD_lst, ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = Rn,  cmap = plt.cm.Blues, CBlabel = 'groundwater net recharge - $Rn$ (mm.day$^{-1}$)', msg = '- no flux', plt_title = 'OUT_MF_Rn', MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, Vmin = Vmin, contours = ctrsMF, Vmax = Vmax, ntick = ntick, points = obs4map, hnoflo = cMF.hnoflo, mask = mask_tmp, animation = animation, cMF = cMF)
        MMplot.plotLAYER(days = days_lst, str_per = sp_lst, Date = Date_lst, JD = JD_lst, ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = Rn,  cmap = plt.cm.Blues, CBlabel = 'groundwater net recharge - $Rn$ (mm.day$^{-1}$)', msg = '- no flux', plt_title = 'OUT_MF_Rn1', MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, Vmin = Vmin1, contours = ctrsMF, Vmax = Vmax1, ntick = ntick, points = obs4map, hnoflo = cMF.hnoflo, mask = mask_tmp, animation = animation, cMF = cMF)  
        del Rn

    del Rg, Re        

    # plot GW drainage [mm]
    if cMF.drn_yn == 1:
        V = np.zeros((len(days_lst), cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
        for i, t in enumerate(days_lst):
            for L in range(cMF.nlay):
                V[i,L,:,:] = np.ma.masked_array(cbc_DRN[t,L,:,:], mask[L])*(-1.0)
            Vmin[i] = DRNmin
            Vmax[i] = DRNmax
            Vmin1[i] = np.ma.min(V[i,:,:,:])
            Vmax1[i] = np.ma.max(V[i,:,:,:])
        MMplot.plotLAYER(days = days_lst, str_per = sp_lst, Date = Date_lst, JD = JD_lst, ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = V,  cmap = plt.cm.Blues, CBlabel = 'groundwater drainage - $DRN$ (mm.day$^{-1}$)', msg = '- no drainage', plt_title = 'OUT_MF_DRN', MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, Vmin = Vmin, contours = ctrsMF, Vmax = Vmax, ntick = ntick, points = obs4map, mask = mask_tmp, hnoflo = cMF.hnoflo, animation = animation, cMF = cMF)
        MMplot.plotLAYER(days = days_lst, str_per = sp_lst, Date = Date_lst, JD = JD_lst, ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = V,  cmap = plt.cm.Blues, CBlabel = 'groundwater drainage - $DRN$ (mm.day$^{-1}$)', msg = '- no drainage', plt_title = 'OUT_MF_DRN1', MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, Vmin = Vmin1, contours = ctrsMF, Vmax = Vmax1, ntick = ntick, points = obs4map, mask = mask_tmp, hnoflo = cMF.hnoflo, animation = animation, cMF = cMF)

    # plot GHB [mm]
    if cMF.ghb_yn == 1:
        V = np.zeros((len(days_lst), cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
        for i, t in enumerate(days_lst):
            for L in range(cMF.nlay):
                V[i,L,:,:] = np.ma.masked_array(cbc_GHB[t,L,:,:], mask[L])*(-1.0)
            Vmin[i] = GHBmin
            Vmax[i] = GHBmax
            Vmin1[i] = np.ma.min(V[i,:,:,:])
            Vmax1[i] = np.ma.max(V[i,:,:,:])
        MMplot.plotLAYER(days = days_lst, str_per = sp_lst, Date = Date_lst, JD = JD_lst, ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = V,  cmap = plt.cm.Blues, CBlabel = 'general head bdry - $GHB$ (mm.day$^{-1}$)', msg = '- no flux', plt_title = 'OUT_MF_GHB', MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, Vmin = Vmin, contours = ctrsMF, Vmax = Vmax, ntick = ntick, points = obs4map, hnoflo = cMF.hnoflo, mask = mask_tmp, animation = animation, cMF = cMF)
        MMplot.plotLAYER(days = days_lst, str_per = sp_lst, Date = Date_lst, JD = JD_lst, ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = V,  cmap = plt.cm.Blues, CBlabel = 'general head bdry - $GHB$ (mm.day$^{-1}$)', msg = '- no flux', plt_title = 'OUT_MF_GHB1', MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, Vmin = Vmin1, contours = ctrsMF, Vmax = Vmax1, ntick = ntick, points = obs4map, hnoflo = cMF.hnoflo,mask = mask_tmp, animation = animation, cMF = cMF)
    
    # plot EXF [mm]
    V = np.zeros((len(days_lst), cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
    for i, t in enumerate(days_lst):
        for L in range(cMF.nlay):
            V[i,L,:,:] = np.ma.masked_array(cbc_EXF[t,L,:,:], mask[L])*(-1.0)
        Vmin[i] = EXFmin
        Vmax[i] = EXFmax
        Vmin1[i] = np.ma.min(V[i,:,:,:])
        Vmax1[i] = np.ma.max(V[i,:,:,:])
    MMplot.plotLAYER(days = days_lst, str_per = sp_lst, Date = Date_lst, JD = JD_lst, ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = V,  cmap = plt.cm.Blues, CBlabel = 'groundwater exfiltration - $Exf_g$ (mm.day$^{-1}$)', msg = '- no exfiltration', plt_title = 'OUT_MF_EXF', MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, Vmin = Vmin, contours = ctrsMF, Vmax = Vmax, ntick = ntick, points = obs4map, mask = mask_tmp, hnoflo = cMF.hnoflo, animation = animation, cMF = cMF)
    MMplot.plotLAYER(days = days_lst, str_per = sp_lst, Date = Date_lst, JD = JD_lst, ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = V,  cmap = plt.cm.Blues, CBlabel = 'groundwater exfiltration - $Exf_g$ (mm.day$^{-1}$)', msg = '- no exfiltration', plt_title = 'OUT_MF_EXF1', MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, Vmin = Vmin1, contours = ctrsMF, Vmax = Vmax1, ntick = ntick, points = obs4map, mask = mask_tmp, hnoflo = cMF.hnoflo, animation = animation, cMF = cMF)                       

    del V
    del Vmin1, Vmax1, Vmin, Vmax

    # ############################################
    # plot average of all hydrologic years
    # ############################################

    # plot heads average [m]
    V = np.zeros((1, cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
    for L in range(cMF.nlay):
        V[0,L,:,:] = np.ma.masked_array(np.sum(h_MF_m[HYindex[1]:HYindex[-2],L,:,:], axis = 0)/(HYindex[-2]-HYindex[1]+1), mask[L])
    for i, int_typ in enumerate(['percentile','linspace']):
        MMplot.plotLAYER(days = ['NA'], str_per = ['NA'], Date = ['NA'], JD = ['NA'], ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = V,  cmap = plt.cm.Blues, CBlabel = 'hydraulic heads elevation - $h$ (m)', msg = 'DRY', plt_title = 'OUT_average_MF_HEADS%s'%int_typ, MM_ws = MM_ws_out, interval_type = int_typ, interval_num = 5, contours = ctrsMF, Vmax = [hmaxMF], Vmin = [hminMF], ntick = ntick, points = obs4map, ptslbl = 0, mask = mask_tmp, hnoflo = cMF.hnoflo, cMF = cMF)

    # plot GWTD average [m]
    for L in range(cMF.nlay):
        V[0,L,:,:] = cMF.elev-V[0,L,:,:]
    for i, int_typ in enumerate(['percentile','linspace']):
        MMplot.plotLAYER(days = ['NA'], str_per = ['NA'], Date = ['NA'], JD = ['NA'], ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = V,  cmap = plt.cm.Blues, CBlabel = 'depth to groundwater table - $d$ (m)', msg = 'DRY', plt_title = 'OUT_average_MF_GWTD%s'%int_typ, MM_ws = MM_ws_out, interval_type = int_typ, interval_num = 5, contours = ctrsMF, Vmax = [GWTDmax], Vmin = [GWTDmin], ntick = ntick, points = obs4map, ptslbl = 0, mask = mask_tmp, hnoflo = cMF.hnoflo, cMF = cMF)

    # plot heads corrigidas average [m]
    headscorr_m = np.zeros((1, cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
    headscorr_m[0,0,:,:] = np.ma.masked_values(np.ma.masked_values(np.sum(h5_MM['MM'][HYindex[1]:HYindex[-2],:,:,19], axis = 0)/(HYindex[-2]-HYindex[1]+1), cMF.hnoflo, atol = 0.09), cMF.hdry, atol = 1E+25)
    for i, int_typ in enumerate(['percentile','linspace']):
        MMplot.plotLAYER(days = ['NA'], str_per = ['NA'], Date = ['NA'], JD = ['NA'], ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = 1, V = headscorr_m,  cmap = plt.cm.Blues, CBlabel = 'hydraulic heads elevation - $h$ (m)', msg = 'DRY', plt_title = 'OUT_average_MF_HEADScorr%s'%int_typ, MM_ws = MM_ws_out, interval_type = int_typ, interval_num = 5, contours = ctrsMF, Vmax = [hcorrmax], Vmin = [hcorrmin], ntick = ntick, points = obs4map, ptslbl = 0, mask = maskAllL_tmp, hnoflo = cMF.hnoflo, cMF = cMF)

    # plot GWTD correct average [m]
    GWTDcorr = np.zeros((1, cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
    GWTDcorr[0,0,:,:] = cMF.elev-headscorr_m[0,0,:,:]
    for i, int_typ in enumerate(['percentile','linspace']):
        MMplot.plotLAYER(days = ['NA'], str_per = ['NA'], Date = ['NA'], JD = ['NA'], ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = 1, V = GWTDcorr, cmap = plt.cm.Blues, CBlabel = 'depth to groundwater table - $d$ (m)', msg = 'DRY', plt_title = 'OUT_average_MF_GWTDcorr%s'%int_typ, MM_ws = MM_ws_out, interval_type = int_typ, interval_num = 5, contours = ctrsMF, Vmax = [GWTDcorrmax], Vmin = [GWTDcorrmin], ntick = ntick, points = obs4map, ptslbl = 0, mask = maskAllL_tmp, hnoflo = cMF.hnoflo, cMF = cMF)

    # plot GW GROSS RCH average [mm]
    Rg = np.zeros((1, cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
    for L in range(cMF.nlay):
        Rg[0,L,:,:] = np.ma.masked_array(np.sum(cbc_RCH[HYindex[1]:HYindex[-2],L,:,:], axis = 0)/(HYindex[-2]-HYindex[1]+1), mask[L])
    for i, int_typ in enumerate(['percentile','linspace']):
        MMplot.plotLAYER(days = ['NA'], str_per = ['NA'], Date = ['NA'], JD = ['NA'], ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = Rg,  cmap = plt.cm.Blues, CBlabel = 'groundwater gross recharge - $Rg$ (mm.day$^{-1}$)', msg = '- no flux', plt_title = 'OUT_average_MF_Rg%s'%int_typ, MM_ws = MM_ws_out, interval_type = int_typ, interval_num = 5, Vmax = [RCHmax], Vmin = [RCHmin], contours = ctrsMF, ntick = ntick, points = obs4map, ptslbl = 1, mask = mask_tmp, hnoflo = cMF.hnoflo, cMF = cMF)
    Vmin_tmp1 = np.min(Rg)
    Vmax_tmp1 = np.max(Rg)
    for i, int_typ in enumerate(['linspace']):
        MMplot.plotLAYER(days = ['NA'], str_per = ['NA'], Date = ['NA'], JD = ['NA'], ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = Rg,  cmap = plt.cm.Blues, CBlabel = 'groundwater gross recharge - $Rg$ (mm.day$^{-1}$)', msg = '- no flux', plt_title = 'OUT_average_MF_Rg1%s'%int_typ, MM_ws = MM_ws_out, interval_type = int_typ, interval_num = 5, Vmax = [Vmax_tmp1], Vmin = [Vmin_tmp1], contours = ctrsMF, ntick = ntick, points = obs4map, ptslbl = 0, mask = mask_tmp, hnoflo = cMF.hnoflo, cMF = cMF)
    
    # plot GW EFFECTIVE RCH average [mm]
    Re = np.zeros((1, cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
    for L in range(cMF.nlay):
        Re[0,L,:,:] = Rg[0,L,:,:] + np.ma.masked_array(np.sum(cbc_EXF[HYindex[1]:HYindex[-2],L,:,:], axis = 0)/(HYindex[-2]-HYindex[1]+1), mask[L])
    for i, int_typ in enumerate(['percentile','linspace']):
        MMplot.plotLAYER(days = ['NA'], str_per = ['NA'], Date = ['NA'], JD = ['NA'], ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = Re,  cmap = plt.cm.Blues, CBlabel = 'groundwater effective recharge - $Re$ (mm.day$^{-1}$)', msg = '- no flux', plt_title = 'OUT_average_MF_Re1%s'%int_typ, MM_ws = MM_ws_out, interval_type = int_typ, interval_num = 5, Vmax = [np.ma.max(Re)], Vmin = [np.ma.min(Re)], contours = ctrsMF, ntick = ntick, points = obs4map, ptslbl = 0, mask = mask_tmp, hnoflo = cMF.hnoflo, cMF = cMF)
    Vmin_tmp1 = np.min(Re)
    Vmax_tmp1 = np.max(Re)
    
    # plot GW NET RCH average [mm]
    if cMF.wel_yn == 1: 
        Rn = np.zeros((1, cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
        for L in range(cMF.nlay):
            Rn[0,L,:,:] = Re[0,L,:,:] + np.sum(cbc_WEL[HYindex[1]:HYindex[-2],L,:,:], axis = 0)/(HYindex[-2]-HYindex[1]+1)
        for i, int_typ in enumerate(['percentile','linspace']):
            MMplot.plotLAYER(days = ['NA'], str_per = ['NA'], Date = ['NA'], JD = ['NA'], ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = Rn,  cmap = plt.cm.Blues, CBlabel = 'groundwater net recharge - $Rn$ (mm.day$^{-1}$)', msg = '- no flux', plt_title = 'OUT_average_MF_Rn1%s'%int_typ, MM_ws = MM_ws_out, interval_type = int_typ, interval_num = 5, Vmax = [np.ma.max(Rn)], Vmin = [np.ma.min(Rn)], contours = ctrsMF, ntick = ntick, points = obs4map, ptslbl = 0, mask = mask_tmp, hnoflo = cMF.hnoflo, cMF = cMF)
        del Rn, cbc_WEL
    
    del cbc_RCH, Rg, Re

    # plot GW drainage average [mm]
    if cMF.drn_yn == 1:
        V = np.zeros((1, cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
        for L in range(cMF.nlay):
            V[0,L,:,:] = np.ma.masked_array(np.sum(cbc_DRN[HYindex[1]:HYindex[-2],L,:,:], axis = 0)/(HYindex[-2]-HYindex[1]+1)*(-1.0), mask[L])
        for i, int_typ in enumerate(['percentile','linspace']):
            MMplot.plotLAYER(days = ['NA'], str_per = ['NA'], Date = ['NA'], JD = ['NA'], ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = V,  cmap = plt.cm.Blues, CBlabel = 'groundwater drainage - $DRN$ (mm.day$^{-1}$)', msg = '- no drainage', plt_title = 'OUT_average_MF_DRN%s'%int_typ, MM_ws = MM_ws_out, interval_type = int_typ, interval_num = 5, Vmax = [DRNmax], Vmin = [DRNmin], contours = ctrsMF, ntick = ntick, points = obs4map, ptslbl = 1, mask = mask_tmp, hnoflo = cMF.hnoflo, cMF = cMF)
        del cbc_DRN, DRNmax, DRNmin
        Vmin_tmp1 = np.min(V)
        Vmax_tmp1 = np.max(V)
        for i, int_typ in enumerate(['linspace']):
            MMplot.plotLAYER(days = ['NA'], str_per = ['NA'], Date = ['NA'], JD = ['NA'], ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = V,  cmap = plt.cm.Blues, CBlabel = 'groundwater drainage - $DRN$ (mm.day$^{-1}$)', msg = '- no drainage', plt_title = 'OUT_average_MF_DRN1%s'%int_typ, MM_ws = MM_ws_out, interval_type = int_typ, interval_num = 5, Vmax = [Vmax_tmp1], Vmin = [Vmin_tmp1], contours = ctrsMF, ntick = ntick, points = obs4map, ptslbl = 0, mask = mask_tmp, hnoflo = cMF.hnoflo, cMF = cMF)

    # plot GHB average [mm]
    if cMF.ghb_yn == 1:
        V = np.zeros((1, cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
        for L in range(cMF.nlay):
            V[0,L,:,:] = np.ma.masked_array(np.sum(cbc_GHB[HYindex[1]:HYindex[-2],L,:,:], axis = 0)/(HYindex[-2]-HYindex[1]+1)*(-1.0), mask[L])
        for i, int_typ in enumerate(['percentile','linspace']):
            MMplot.plotLAYER(days = ['NA'], str_per = ['NA'], Date = ['NA'], JD = ['NA'], ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = V,  cmap = plt.cm.Blues, CBlabel = 'general head bdry - $GHB$ (mm.day$^{-1}$)', msg = '- no flux', plt_title = 'OUT_average_MF_GHB%s'%int_typ, MM_ws = MM_ws_out, interval_type = int_typ, interval_num = 5, Vmax = [GHBmax], Vmin = [GHBmin], contours = ctrsMF, ntick = ntick, points = obs4map, ptslbl = 1, mask = mask_tmp, hnoflo = cMF.hnoflo, cMF = cMF)
        del cbc_GHB, GHBmax, GHBmin
        Vmin_tmp1 = np.min(V)
        Vmax_tmp1 = np.max(V)
        for i, int_typ in enumerate(['linspace']):
            MMplot.plotLAYER(days = ['NA'], str_per = ['NA'], Date = ['NA'], JD = ['NA'], ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = V,  cmap = plt.cm.Blues, CBlabel = 'general head bdry - $GHB$ (mm.day$^{-1}$)', msg = '- no flux', plt_title = 'OUT_average_MF_GHB1%s'%int_typ, MM_ws = MM_ws_out, interval_type = int_typ, interval_num = 5, Vmax = [Vmax_tmp1], Vmin = [Vmin_tmp1], contours = ctrsMF, ntick = ntick, points = obs4map, ptslbl = 0, mask = mask_tmp, hnoflo = cMF.hnoflo, cMF = cMF)

    # plot GW exfiltration average [mm]
    V = np.zeros((1, cMF.nlay, cMF.nrow, cMF.ncol), dtype = np.float)
    for L in range(cMF.nlay):
        V[0,L,:,:] = np.ma.masked_array(np.sum(cbc_EXF[HYindex[1]:HYindex[-2],L,:,:], axis = 0)/(HYindex[-2]-HYindex[1]+1)*(-1.0), mask[L])
    for i, int_typ in enumerate(['percentile','linspace']):
        MMplot.plotLAYER(days = ['NA'], str_per = ['NA'], Date = ['NA'], JD = ['NA'], ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = V,  cmap = plt.cm.Blues, CBlabel = 'groundwater exfiltration - $Exf_g$ (mm.day$^{-1}$)', msg = '- no exfiltration', plt_title = 'OUT_average_MF_EXF%s'%int_typ, MM_ws = MM_ws_out, interval_type = int_typ, interval_num = 5, Vmax = [EXFmax], Vmin = [EXFmin], contours = ctrsMF, ntick = ntick, points = obs4map, ptslbl = 1, mask = mask_tmp, hnoflo = cMF.hnoflo, cMF = cMF)
    del cbc_EXF, EXFmax, EXFmin
    Vmin_tmp1 = np.min(V)
    Vmax_tmp1 = np.max(V)
    for i, int_typ in enumerate(['linspace']):
        MMplot.plotLAYER(days = ['NA'], str_per = ['NA'], Date = ['NA'], JD = ['NA'], ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = cMF.nlay, V = V,  cmap = plt.cm.Blues, CBlabel = 'groundwater exfiltration - $Exf_g$ (mm.day$^{-1}$)', msg = '- no exfiltration', plt_title = 'OUT_average_MF_EXF1%s'%int_typ, MM_ws = MM_ws_out, interval_type = int_typ, interval_num = 5, Vmax = [Vmax_tmp1], Vmin = [Vmin_tmp1], contours = ctrsMF, ntick = ntick, points = obs4map, ptslbl = 0, mask = mask_tmp, hnoflo = cMF.hnoflo, cMF = cMF)
        
    h5_MF.close()
    h5_MM.close()
    del V, Vmax_tmp1, Vmin_tmp1
##
    # ##############################
    # #### MARMITES OUTPUT #########
    # ##############################
    if os.path.exists(h5_MM_fn):
        h5_MM = h5py.File(h5_MM_fn, 'r')
        flx_lst = ['RF', 'RFe', 'I', 'EXFg', 'dSsurf', 'Ro', 'Esurf', 'Eg', 'Tg', 'ETg', 'ETsoil', 'dSsoil']
        flxLbl_lst = [r'$RF$', r'$RFe$', r'$I$', r'$Exf_g$', r'$\Delta S_{surf}$', r'$Ro$', r'$E_{surf}$', r'$E_g$', r'$T_g$', r'$ET_g$', r'$ET_{soil}$', r'$\Delta S_{soil}$']
        for z, (i, i_lbl) in enumerate(zip(flx_lst, flxLbl_lst)):
            # ############################################
            # plot average of all hydrologic years
            # ############################################
            i1 = 'i'+i
            MM = h5_MM['MM'][:,:,:,index_MM.get(i1)]
            V = np.zeros((1, 1, cMF.nrow, cMF.ncol), dtype = np.float)
            V[0,0,:,:] = np.sum(np.ma.masked_values(MM[HYindex[1]:HYindex[-2],:,:], cMF.hnoflo, atol = 0.09), axis = 0)/(HYindex[-2]-HYindex[1]+1)
            V[0,0,:,:] = np.ma.masked_values(V[0,0,:,:], cMF.hnoflo, atol = 0.09)
            Vmax = [np.ma.max(V)]
            Vmin = [np.ma.min(V)]
            MMplot.plotLAYER(days = ['NA'], str_per = ['NA'], Date = ['NA'], JD = ['NA'], ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = 1, V = V,  cmap = plt.cm.Blues, CBlabel = (i_lbl + ' (mm.day$^{-1}$)'), msg = 'no flux', plt_title = ('OUT_average_MM_' + i), MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, Vmax = Vmax, Vmin = Vmin, contours = ctrsMM, ntick = ntick, points = obs4map, mask = maskAllL_tmp, hnoflo = cMF.hnoflo, cMF = cMF)
            del V
            # ############################################
            # plot for selected time step
            # ############################################
            V = np.zeros((len(days_lst), 1, cMF.nrow, cMF.ncol), dtype = np.float)
            Vmax = np.zeros((len(days_lst)), dtype = np.float)
            Vmin = np.zeros((len(days_lst)), dtype = np.float)
            Vmax1 = np.zeros((len(days_lst)), dtype = np.float)
            Vmin1 = np.zeros((len(days_lst)), dtype = np.float)
            for ii, t in enumerate(days_lst):
                V[ii,0,:,:] = np.ma.masked_values(MM[t,:,:], cMF.hnoflo, atol = 0.09)
                V[ii,0,:,:] = np.ma.masked_values(V[ii,0,:,:], cMF.hnoflo, atol = 0.09)
                Vmin1[ii] = np.ma.min(np.ma.masked_values(V[ii,0,:,:], cMF.hnoflo, atol = 0.09))
                Vmax1[ii] = np.ma.max(np.ma.masked_values(V[ii,0,:,:], cMF.hnoflo, atol = 0.09))
            for ii, t in enumerate(days_lst):
                Vmax[ii] = np.ma.max(Vmax1)
                Vmin[ii] = np.ma.min(Vmin1)
            MMplot.plotLAYER(days = days_lst, str_per = sp_lst, Date = Date_lst, JD = JD_lst, ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = 1, V = V,  cmap = plt.cm.Blues, CBlabel = (i_lbl + ' (mm.day$^{-1}$)'), msg = 'no flux', plt_title = ('OUT_MM_'+i), MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, Vmax = Vmax, Vmin = Vmin, contours = ctrsMM, ntick = ntick, points = obs4map, hnoflo = cMF.hnoflo, mask = maskAllL_tmp, animation = animation, cMF = cMF)
            MMplot.plotLAYER(days = days_lst, str_per = sp_lst, Date = Date_lst, JD = JD_lst, ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = 1, V = V,  cmap = plt.cm.Blues, CBlabel = (i_lbl + ' (mm.day$^{-1}$)'), msg = 'no flux', plt_title = ('OUT_MM_%s1'%i), MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, Vmax = Vmax1, Vmin = Vmin1, contours = ctrsMM, ntick = ntick, points = obs4map, hnoflo = cMF.hnoflo, mask = maskAllL_tmp, animation = animation, cMF = cMF)
            del V, MM, Vmax, Vmin

        flx_lst = ['Esoil', 'Tsoil']
        flxLbl_lst = [r'$E_{soil}$', r'$T_{soil}$']
        for z, (i, i_lbl) in enumerate(zip(flx_lst, flxLbl_lst)):
            # ############################################
            # plot average of all hydrologic years
            # ############################################
            i1 = 'i'+i
            V = np.zeros((1, 1, cMF.nrow, cMF.ncol), dtype = np.float)
            for l in range(_nslmax):
                MM = h5_MM['MM_S'][:,:,:,l,index_MM_soil.get(i1)]
                V[0,0,:,:] += np.sum(np.ma.masked_values(MM[HYindex[1]:HYindex[-2],:,:], cMF.hnoflo, atol = 0.09), axis = 0)/(HYindex[-2]-HYindex[1]+1)
                V[0,0,:,:] = np.ma.masked_values(V[0,0,:,:], cMF.hnoflo, atol = 0.09)
            Vmax = [np.ma.max(V)]
            Vmin = [np.ma.min(V)]
            MMplot.plotLAYER(days = ['NA'], str_per = ['NA'], Date = ['NA'], JD = ['NA'], ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = 1, V = V,  cmap = plt.cm.Blues, CBlabel = (i_lbl + ' (mm.day$^{-1}$)'), msg = 'no flux', plt_title = ('OUT_average_MM_%s' % i), MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, Vmax = Vmax, Vmin = Vmin, contours = ctrsMM, ntick = ntick, points = obs4map, mask = maskAllL_tmp, hnoflo = cMF.hnoflo, cMF = cMF)
            del V

            # ############################################
            # plot for selected day
            # ############################################
            Vmax = np.zeros((len(days_lst)), dtype = np.float)
            Vmin = np.zeros((len(days_lst)), dtype = np.float)
            Vmax1 = np.zeros((len(days_lst)), dtype = np.float)
            Vmin1 = np.zeros((len(days_lst)), dtype = np.float)
            V = np.zeros((len(days_lst), 1, cMF.nrow, cMF.ncol), dtype = np.float)
            for ii, t in enumerate(days_lst):
                for l in range(_nslmax):
                    V[ii,0,:,:] += h5_MM['MM_S'][t,:,:,l,index_MM_soil.get(i1)]
                Vmin1[ii] = np.ma.min(np.ma.masked_values(np.ma.masked_array(V[ii,0,:,:], cMF.maskAllL), cMF.hnoflo, atol = 0.09))
                Vmax1[ii] = np.ma.max(np.ma.masked_values(np.ma.masked_array(V[ii,0,:,:], cMF.maskAllL), cMF.hnoflo, atol = 0.09))
            for ii, t in enumerate(days_lst):
                Vmax[ii] = np.ma.max(Vmax1)
                Vmin[ii] = np.ma.min(Vmin1)
            MMplot.plotLAYER(days = days_lst, str_per = sp_lst, Date = Date_lst, JD = JD_lst, ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = 1, V = V,  cmap = plt.cm.Blues, CBlabel = (i_lbl + ' (mm.day$^{-1}$)'), msg = 'no flux', plt_title = ('OUT_MM_'+i), MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, Vmax = Vmax, Vmin = Vmin, contours = ctrsMM, ntick = ntick, points = obs4map, hnoflo = cMF.hnoflo, mask = maskAllL_tmp, animation = animation, cMF = cMF)
            MMplot.plotLAYER(days = days_lst, str_per = sp_lst, Date = Date_lst, JD = JD_lst, ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = 1, V = V,  cmap = plt.cm.Blues, CBlabel = (i_lbl + ' (mm.day$^{-1}$)'), msg = 'no flux', plt_title = ('OUT_MM_%s1'%i), MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, Vmax = Vmax1, Vmin = Vmin1, contours = ctrsMM, ntick = ntick, points = obs4map, hnoflo = cMF.hnoflo, mask = maskAllL_tmp, animation = animation, cMF = cMF)

        # ##############################
        # ####   PERCOLATION   #########
        # ##############################
        i = 'Rp'
        i_lbl = r'$R_p$'
        # ############################################
        # plot average of all hydrologic years
        # ############################################
        V = np.zeros((1, 1, cMF.nrow, cMF.ncol), dtype = np.float)
        MM = conv_fact*h5_MM['perc_d'][:,:,:]
        V[0,0,:,:] = np.sum(np.ma.masked_values(MM[HYindex[1]:HYindex[-2],:,:], cMF.hnoflo, atol = 0.09), axis = 0)/(HYindex[-2]-HYindex[1]+1)   
        Vmax = [np.ma.max(V)]
        Vmin = [np.ma.min(V)]
        MMplot.plotLAYER(days = ['NA'], str_per = ['NA'], Date = ['NA'], JD = ['NA'], ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = 1, V = V,  cmap = plt.cm.Blues, CBlabel = (i_lbl + ' (mm.day$^{-1}$)'), msg = 'no flux', plt_title = ('OUT_average_MM_%s'% i), MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, Vmax = Vmax, Vmin = Vmin, contours = ctrsMM, ntick = ntick, points = obs4map, mask = maskAllL_tmp, hnoflo = cMF.hnoflo, cMF = cMF)

        # ############################################
        # plot for selected day
        # ############################################
        Vmax = np.zeros((len(days_lst)), dtype = np.float)
        Vmin = np.zeros((len(days_lst)), dtype = np.float)
        Vmax1 = np.zeros((len(days_lst)), dtype = np.float)
        Vmin1 = np.zeros((len(days_lst)), dtype = np.float)
        V = np.zeros((len(days_lst), 1, cMF.nrow, cMF.ncol), dtype = np.float)
        for ii, t in enumerate(days_lst):
            MM = conv_fact*h5_MM['perc_d'][t,:,:]
            V[ii,0,:,:] = np.ma.masked_values(MM, cMF.hnoflo, atol = 0.09)
            Vmin1[ii] = np.ma.min(np.ma.masked_values(V[ii,0,:,:], cMF.hnoflo, atol = 0.09))
            Vmax1[ii] = np.ma.max(np.ma.masked_values(V[ii,0,:,:], cMF.hnoflo, atol = 0.09))
        for ii, t in enumerate(days_lst):
            Vmax[ii] = np.ma.max(Vmax1)
            Vmin[ii] = np.ma.min(Vmin1)
        MMplot.plotLAYER(days = days_lst, str_per = sp_lst, Date = Date_lst, JD = JD_lst, ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = 1, V = V,  cmap = plt.cm.Blues, CBlabel = (i_lbl + ' (mm.day$^{-1}$)'), msg = 'no flux', plt_title = ('OUT_MM_'+i), MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, Vmax = Vmax, Vmin = Vmin, contours = ctrsMM, ntick = ntick, points = obs4map, hnoflo = cMF.hnoflo, mask = maskAllL_tmp, animation = animation, cMF = cMF)
        MMplot.plotLAYER(days = days_lst, str_per = sp_lst, Date = Date_lst, JD = JD_lst, ncol = cMF.ncol, nrow = cMF.nrow, nlay = cMF.nlay, nplot = 1, V = V,  cmap = plt.cm.Blues, CBlabel = (i_lbl + ' (mm.day$^{-1}$)'), msg = 'no flux', plt_title = ('OUT_MM_%s1'%i), MM_ws = MM_ws_out, interval_type = 'linspace', interval_num = 5, Vmax = Vmax1, Vmin = Vmin1, contours = ctrsMM, ntick = ntick, points = obs4map, hnoflo = cMF.hnoflo, mask = maskAllL_tmp, animation = animation, cMF = cMF)

        h5_MM.close()
        del V, MM, t, Vmax, Vmin
        del days_lst, flx_lst, i, i1, h_diff_surf
    del hmaxMF, hminMF, hmin, hdiff, cbcmax_d, cbcmin_d

timeendExport = mpl.dates.datestr2num(mpl.dates.datetime.datetime.today().isoformat())
durationExport=(timeendExport-timestartExport)
durationTotal = (timeendExport-timestart)

# final report of successful run
print '\n##############\nMARMITES executed successfully!\n%s' % mpl.dates.DateFormatter.format_data(fmt_DH, mpl.dates.datestr2num(mpl.dates.datetime.datetime.today().isoformat()))
if MMsoil_yn != 0:
    print '\nLOOP %d/%d' % (LOOP-1, ccnum)
    for txt in msg_end_loop:
        print txt
print '\n%d stress periods, %d days' % (cMF.nper,sum(cMF.perlen))
print '%d layers x %d rows x %d cols (%d cells)' % (cMF.nlay, cMF.nrow, cMF.ncol, cMF.nrow*cMF.ncol)
print '%d MM active cells in total' % (sum(ncell_MM))
L = 1
for n in ncell_MF:
    print  'LAYER %d' % L
    print '%d MF active cells' % (n)
    print '%d MM active cells' % (ncell_MM[L-1])
    L += 1
print ('\nApproximate run times:')
if MMsurf_yn > 0:
    print ('MARMITES surface: %s minute(s) and %.1f second(s)') % (str(int(durationMMsurf*24.0*60.0)), (durationMMsurf*24.0*60.0-int(durationMMsurf*24.0*60.0))*60)
if MMsoil_yn != 0:
    print ('MARMITES soil zone: %s minute(s) and %.1f second(s)') % (str(int(durationMMsoil*24.0*60.0)), (durationMMsoil*24.0*60.0-int(durationMMsoil*24.0*60.0))*60)
if MF_yn == 1:
    print ('MODFLOW: %s minute(s) and %.1f second(s)') % (str(int(durationMF*24.0*60.0)), (durationMF*24.0*60.0-int(durationMF*24.0*60.0))*60)
print ('Export: %s minute(s) and %.1f second(s)') % (str(int(durationExport*24.0*60.0)), (durationExport*24.0*60.0-int(durationExport*24.0*60.0))*60)
print ('Total: %s minute(s) and %.1f second(s)') % (str(int(durationTotal*24.0*60.0)), (durationTotal*24.0*60.0-int(durationTotal*24.0*60.0))*60)
print ('\nOutput written in folder: \n%s\n##############\n') % MM_ws_out

if verbose == 0:
    sys.stdout = stdout
    report.close()
    print '##############\nMARMITES terminated normally!\n%s\n##############' % mpl.dates.DateFormatter.format_data(fmt_DH, mpl.dates.datestr2num(mpl.dates.datetime.datetime.today().isoformat()))
    
# EOF    