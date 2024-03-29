﻿# -*- coding: utf-8 -*-

__author__ = "Alain Francés <frances08512@itc.nl>"
__version__ = "0.4"
__date__ = "2012"

import os
import numpy as np
import matplotlib as mpl
import sys

def readFile(ws, fn):
    inputFile = []
    inputFile_fn = os.path.join(ws, fn)
    if os.path.exists(inputFile_fn):
        fin = open(inputFile_fn, 'r')
    else:
        raise SystemExit("File [" + inputFile_fn + "] doesn't exist, verify name and path!")
    line = fin.readline().split()
    delimChar = line[0]
    try:
        for line in fin:
            line_tmp = line.split(delimChar)
            if not line_tmp == []:
                if (not line_tmp[0] == '') and (not line_tmp[0] == '\n'):
                    inputFile.append(line_tmp[0])
            else:
                raise NameError('InputFileFormat')
    except NameError:
        raise SystemExit('Error in file [' + inputFile_fn + '], check format!')
    except:
        raise SystemExit("Unexpected error in file [" + inputFile_fn + "]\n", sys.exc_info()[0])
    fin.close()
    del fin
    return inputFile

class PROCESS:
    def __init__(self, MM_ws, MF_ws, nrow, ncol, xllcorner, yllcorner, cellsizeMF, hnoflo):
        self.MM_ws = MM_ws
        self.MF_ws = MF_ws
        self.nrow= nrow
        self.ncol= ncol
        self.xllcorner= xllcorner
        self.yllcorner=yllcorner
        self.cellsizeMF=cellsizeMF
        self.hnoflo=hnoflo
        self.smMM = []
        self.smMMname = []

    ######################

    def inputEsriAscii(self, grid_fn, datatype):
        try:
            if datatype == np.int or datatype == int:
                grid_fn = int(grid_fn)
            else:
                grid_fn = float(grid_fn)
            grid_out = np.ones((self.nrow,self.ncol), dtype = datatype)*grid_fn
        except:
            grid_fn=os.path.join(self.MM_ws,grid_fn)
            grid_out=np.zeros([self.nrow,self.ncol], dtype = datatype)
            grid_out = self.convASCIIraster2array(grid_fn,grid_out)
        return grid_out
        del grid_out

    ######################

    def checkarray(self, var, dtype = np.float):
        if type(var) == np.ndarray:
            lst_out = list(var)
        else:
            try:
                if len(var)>1:
                    lst_out = []
                    for v in var:
                        if dtype == np.int or dtype == int:
                            lst_out.append(int(v))
                        else:
                            lst_out.append(float(v))
                else:
                    if dtype == np.int or dtype == int:
                        lst_out = int(var[0])
                    else:
                        lst_out = float(var[0])
            except:
                array = np.zeros((self.nrow,self.ncol,len(var)), dtype = dtype)
                l = 0
                for v in var:
                    if isinstance(v, str):
                        array_path = os.path.join(self.MF_ws, v)
                        array[:,:,l] = self.convASCIIraster2array(array_path, array[:,:,l])
                    else:
                        print'\nFATAL ERROR!\nMODFLOW ini file incorrect, check files or values %s' % var
                    l += 1
                if len(var)>1:
                    lst_out = list(array)
                else:
                    lst_out = list(array[:,:,0])
        return lst_out

    ######################

    def convASCIIraster2array(self, filenameIN, arrayOUT):
        '''
        Read ESRI/MODFLOW ASCII file and convert to numpy array
        '''

        # Load the grid files
        if os.path.exists(filenameIN):
            fin = open(filenameIN, 'r')
        else:
            raise ValueError, "The file %s doesn't exist!!!" % filenameIN
    #        fout = open(outfile, 'w')

        # test if it is ESRI ASCII file or PEST grid
        line = fin.readline().split()
        testfile = line[0]
        if isinstance(testfile, str):
            # Read the header
            ncol_tmp = int(line[1])
            line = fin.readline().split()
            nrow_tmp = int(line[1])
            line = fin.readline().split()
            line = fin.readline().split()
            line = fin.readline().split()
            cellsizeEsriAscii = float(line[1])
            line = fin.readline().split()
            NODATA_value = line[1]
        elif isinstance(testfile, float):
            ncol_tmp = int(line[0])
            nrow_tmp = int(line[1])

        # Process the file
#        print "\nConverting %s to np.array" % (filenameIN)
        for row in range(nrow_tmp):
        #   if (row % 100) == 0: print ".",
            for col in range(ncol_tmp):
                # Get new data if necessary
                if col == 0: line = fin.readline().split()
                if line[col] == NODATA_value:
                    arrayOUT[row,col] = self.hnoflo
                else:
                    arrayOUT[row,col] = line[col]

        # verify grid consistency between MODFLOW and ESRI ASCII
        if arrayOUT.shape[0] != self.nrow or arrayOUT.shape[1] != self.ncol or self.cellsizeMF != cellsizeEsriAscii:
            raise BaseException, "\nFATAL ERROR!\nMODFLOW grid anf the ESRI ASCII grid from file %s don't correspond!.\nCheck the cell size and the number of rows, columns and cellsize." % filenameIN

        fin.close()
        del line, fin

        return arrayOUT
        del arrayOUT

    ######################

    def procMF(self, cMF, h5_MF, ds_name, ds_name_new, conv_fact, index = 0):

        # cbc format is : (kstp), kper, textprocess, nrow, ncol, nlay
        t = 0
        h5_MF.create_dataset(name = ds_name_new, data = np.zeros((sum(cMF.perlen), cMF.nrow, cMF.ncol, cMF.nlay)))
        if cMF.timedef>=0:
            for n in range(cMF.nper):
                if cMF.perlen[n] != 1:
                    for x in range(cMF.perlen[n]):
                        if ds_name == 'heads':
                            h5_MF[ds_name_new][t,:,:,:] = h5_MF['heads'][n,:,:,:]
                        else:
                            array_tmp = h5_MF[ds_name][n,:,:,index,:]
                            if cMF.reggrid == 1 and ds_name != 'heads':
                                h5_MF[ds_name_new][t,:,:,:] = conv_fact*array_tmp[:,:,:]/(cMF.delr[0]*cMF.delc[0])
                            else:
                                for i in range(cMF.nrow):
                                    for j in range(cMF.ncol):
                                        h5_MF[ds_name_new][t,i,j,:] = conv_fact*array_tmp[i,j,:]/(cMF.delr[j]*cMF.delc[i])
                            del array_tmp
                        t += 1
                else:
                    if ds_name == 'heads':
                        h5_MF[ds_name_new][t,:,:,:] = h5_MF['heads'][n,:,:,:]
                    else:
                        array_tmp = h5_MF[ds_name][n,:,:,index,:]
                        if cMF.reggrid == 1:
                            h5_MF[ds_name_new][t,:,:,:] = conv_fact*array_tmp[:,:,:]/(cMF.delr[0]*cMF.delc[0])
                        else:
                            for i in range(cMF.nrow):
                                for j in range(cMF.ncol):
                                    h5_MF[ds_name_new][t,i,j,:] = conv_fact*array_tmp[i,j,:]/(cMF.delr[j]*cMF.delc[i])
                        del array_tmp
                    t += 1
        else:
            if ds_name == 'heads':
                h5_MF[ds_name_new] = h5_MF['heads']
            else:
                array_tmp = h5_MF[ds_name][:,:,:,index,:]
                if cMF.reggrid == 1:
                    h5_MF[ds_name_new][:,:,:,:] = array_tmp[:,:,:]/(cMF.delr[0]*cMF.delc[0])
                else:
                    for i in range(cMF.nrow):
                        for j in range(cMF.ncol):
                            h5_MF[ds_name_new][:,i,j,:] = conv_fact*array_tmp[i,j,:]/(cMF.delr[j]*cMF.delc[i])
                    del array_tmp

    ######################

    def inputSP(self, NMETEO, NVEG, NSOIL, nper,
                inputZON_SP_RF_veg_fn, inputZON_SP_RFe_veg_fn, inputZON_SP_LAI_veg_fn,
                inputZON_SP_PT_fn, inputZON_SP_PE_fn,
                inputZON_SP_E0_fn,
                NFIELD = None,
                inputZON_SP_RF_irr_fn = None, inputZON_SP_RFe_irr_fn = None,
                inputZON_SP_PT_irr_fn = None, input_SP_crop_irr_fn = None
                ):

        # READ input ESRI ASCII rasters vegetation
        gridVEGarea_fn=[]
        for v in range(NVEG):
            gridVEGarea_fn.append(os.path.join(self.MM_ws,'inputVEG' + str(v+1)+'area.asc'))
        gridVEGarea=np.zeros([NVEG,self.nrow,self.ncol], dtype=float)
        for v in range(NVEG):
            grid_tmp=np.zeros([self.nrow,self.ncol], dtype=float)
            gridVEGarea[v,:,:]=self.convASCIIraster2array(gridVEGarea_fn[v],grid_tmp)
        gridVEGareatot = np.add.accumulate(gridVEGarea, axis = 0)
        area100_test = gridVEGareatot > 100.0
        if area100_test.sum() > 0:
            raise ValueError, '\nFATAL ERROR!\nThe total area of the vegetation in one cell cannot exceed 100.0%!'

        # READ RF and E0 for each zone
        # RF
        RF_veg_fn=os.path.join(self.MM_ws, inputZON_SP_RF_veg_fn)
        if os.path.exists(RF_veg_fn):
            RF_veg = np.loadtxt(RF_veg_fn)
        else:
            raise ValueError, "\nFATAL ERROR!\nThe file %s doesn't exist!!!" % RF_veg_fn
        RF_veg_zonesSP = np.zeros([NMETEO,nper], dtype=float)
        # E0
        E0_fn=os.path.join(self.MM_ws, inputZON_SP_E0_fn)
        if os.path.exists(E0_fn):
            E0 = np.loadtxt(E0_fn)
        else:
            raise ValueError, "\nFATAL ERROR!\nThe file %s doesn't exist!!!" % E0_fn
        E0_zonesSP = np.zeros([NMETEO,nper], dtype=float)
        for n in range(NMETEO):
            for t in range(nper):
                RF_veg_zonesSP[n,t]=RF_veg[n*nper+t]
                E0_zonesSP[n,t]=E0[n*nper+t]

        # READ PT/RFe for each zone and each vegetation
        # RFe
        RFe_veg_fn = os.path.join(self.MM_ws, inputZON_SP_RFe_veg_fn)
        if os.path.exists(RFe_veg_fn):
            RFe_veg_tmp = np.loadtxt(RFe_veg_fn)
        else:
            raise ValueError, "\nFATAL ERROR!\nThe file %s doesn't exist!!!" % RFe_veg_fn
        RFe_veg_zonesSP = np.zeros([NMETEO,NVEG,nper], dtype=float)
        # LAI
        LAI_veg_fn = os.path.join(self.MM_ws, inputZON_SP_LAI_veg_fn)
        if os.path.exists(LAI_veg_fn):
            LAI_veg_tmp = np.loadtxt(LAI_veg_fn)
        else:
            raise ValueError, "\nFATAL ERROR!\nThe file %s doesn't exist!!!" % LAI_veg_fn
        LAI_veg_zonesSP = np.zeros([NVEG,nper], dtype=float)
        # PT
        PT_veg_fn = os.path.join(self.MM_ws, inputZON_SP_PT_fn)
        if os.path.exists(PT_veg_fn):
            PT_veg_tmp = np.loadtxt(PT_veg_fn)
        else:
            raise ValueError, "\nFATAL ERROR!\nThe file %s doesn't exist!!!" % PT_veg_fn
        PT_veg_zonesSP = np.zeros([NMETEO,NVEG,nper], dtype=float)
        for n in range(NMETEO):
            for v in range(NVEG):
                for t in range(nper):
                    #structure is [number of zones, number of vegetation type, time]
                    RFe_veg_zonesSP[n,v,t] = RFe_veg_tmp[t+(n*NVEG+v)*nper]
                    PT_veg_zonesSP[n,v,t]      = PT_veg_tmp[t+(n*NVEG+v)*nper]
        for v in range(NVEG):
            for t in range(nper):
            #structure is [number of zones, number of vegetation type, time]
                LAI_veg_zonesSP[v,t] = LAI_veg_tmp[t+v*nper]

        # READ PE for each zone and each soil
        PE_fn = os.path.join(self.MM_ws, inputZON_SP_PE_fn)
        if os.path.exists(PE_fn):
            PE_tmp = np.loadtxt(PE_fn)
        else:
            raise ValueError, "\nFATAL ERROR!\nThe file %s doesn't exist!!!" % PE_fn
        PE_zonesSP=np.zeros([NMETEO,NSOIL,nper], dtype=float)
        for n in range(NMETEO):
            for v in range(NSOIL):
                for t in range(nper):
                    PE_zonesSP[n,v,t] = PE_tmp[t+(n*NSOIL+v)*nper]
                    #structure is [number of zones, number of vegetation type, time]

        # read IRRIGATION RF and RFe
        if NFIELD <> None:
            # RF_irr
            RF_irr_fn = os.path.join(self.MM_ws, inputZON_SP_RF_irr_fn)
            if os.path.exists(RF_irr_fn):
                RF_irr_tmp = np.loadtxt(RF_irr_fn)
            else:
                raise ValueError, "\nFATAL ERROR!\nThe file %s doesn't exist!!!" % RF_irr_fn
            RF_irr_zonesSP = np.zeros([NMETEO,NFIELD,nper], dtype=float)
            # RFe irr
            RFe_irr_fn = os.path.join(self.MM_ws, inputZON_SP_RFe_irr_fn)
            if os.path.exists(RFe_irr_fn):
                RFe_irr_tmp = np.loadtxt(RFe_irr_fn)
            else:
                raise ValueError, "\nFATAL ERROR!\nThe file %s doesn't exist!!!" % RFe_irr_fn
            RFe_irr_zonesSP = np.zeros([NMETEO,NFIELD,nper], dtype=float)
            # PT irr
            PT_irr_fn = os.path.join(self.MM_ws, inputZON_SP_PT_irr_fn)
            if os.path.exists(PT_irr_fn):
                PT_irr_tmp = np.loadtxt(PT_irr_fn)
            else:
                raise ValueError, "\nFATAL ERROR!\nThe file %s doesn't exist!!!" % PT_irr_fn
            PT_irr_zonesSP = np.zeros([NMETEO,NFIELD,nper], dtype=float)
            # crop irr
            crop_irr_fn = os.path.join(self.MM_ws, input_SP_crop_irr_fn)
            if os.path.exists(crop_irr_fn):
                crop_irr_tmp = np.loadtxt(crop_irr_fn)
            else:
                raise ValueError, "\nFATAL ERROR!\nThe file %s doesn't exist!!!" % crop_irr_fn
            crop_irr_SP = np.zeros([NFIELD,nper], dtype=int)
            for n in range(NMETEO):
                for f in range(NFIELD):
                    for t in range(nper):
                        #structure is [number of zones, number of field, time]
                        RF_irr_zonesSP[n,f,t]  = RF_irr_tmp[t+(n*NFIELD+f)*nper]
                        RFe_irr_zonesSP[n,f,t] = RFe_irr_tmp[t+(n*NFIELD+f)*nper]
                        PT_irr_zonesSP[n,f,t]  = PT_irr_tmp[t+(n*NFIELD+f)*nper]
            for f in range(NFIELD):
                for t in range(nper):
                    #structure is [number of field, time]
                    crop_irr_SP[f,t] = crop_irr_tmp[t+f*nper]

        if NFIELD == None:
            return gridVEGarea, RF_veg_zonesSP, E0_zonesSP, PT_veg_zonesSP, RFe_veg_zonesSP, LAI_veg_zonesSP, PE_zonesSP
        else:
            return gridVEGarea, RF_veg_zonesSP, E0_zonesSP, PT_veg_zonesSP, RFe_veg_zonesSP, LAI_veg_zonesSP, PE_zonesSP, RF_irr_zonesSP, RFe_irr_zonesSP, PT_irr_zonesSP, crop_irr_SP

    ######################

    def inputSoilParam(self, MM_ws, SOILparam_fn, NSOIL):

        # Soils parameter initialisation
        nam_soil=[]
        nsl=[]
        st =[]
        slprop=[]
        Sm =[]
        Sfc=[]
        Sr =[]
        Si =[]
        Ks =[]

        # soil parameters file
        inputFile = readFile(MM_ws,SOILparam_fn)
        SOILzones=int(int(inputFile[0]))
        if SOILzones>NSOIL:
            print '\nWARNING!\n' + str(SOILzones) + ' soil parameters groups in file [' + SOILparam_fn + ']\n Only ' + str(NSOIL) + ' PE time serie(s) found.'
        # trick to initialise the reading position in the next loop
        nsl.append(0)
        for i in range(SOILzones):
            nsl.append(int(inputFile[i+1]))
            if nsl[i+1]<1:
                raise ValueError, '\nFATAL ERROR!\nThe model requires at least 1 soil layer!'

        # soil parameter definition for each soil type
        nslst = SOILzones+1
        nam_soil = []
        st = []
        for z in range(SOILzones):
            nam_soil.append(inputFile[nslst].strip())
            nslst += 1
            st.append(inputFile[nslst].strip())
            nslst += 1
            slprop.append([])
            Sm.append([])
            Sfc.append([])
            Sr.append([])
            Si.append([])
            Ks.append([])
            for ns in range(nsl[z+1]):
                slprop[z].append(float(inputFile[nslst]))
                nslst += 1
                Sm[z].append(float(inputFile[nslst]))
                nslst += 1
                Sfc[z].append(float(inputFile[nslst]))
                nslst += 1
                Sr[z].append(float(inputFile[nslst]))
                nslst += 1
                Si[z].append(float(inputFile[nslst]))
                nslst += 1
                Ks[z].append(float(inputFile[nslst]))
                nslst += 1
                if not(Sm[z][ns]>Sfc[z][ns]>Sr[z][ns]) or not(Sm[z][ns]>=Si[z][ns]>=Sr[z][ns]):
                    raise SystemExit('\nFATAL ERROR!\nSoils parameters are not valid!\nThe conditions are Sm>Sfc>Sr and Sm>Si>Sr!')
            if sum(slprop[z][0:nsl[z+1]])>1:
                raise SystemExit('\nFATAL ERROR!\nThe sum of the soil layers proportion of %s is >1!\nCorrect your soil data input!\n' % nam_soil[z])
            if sum(slprop[z][0:nsl[z+1]])<1:
                raise SystemExit('\nFATAL ERROR!\nThe sum of the soil layers proportion of %s is <1!\nCorrect your soil data input!\n' % nam_soil[z])

        return nsl[1:len(nsl)], nam_soil, st, slprop, Sm, Sfc, Sr, Si, Ks
        del nsl, nam_soil, st, slprop, Sm, Sfc, Sr, Si, Ks

    ######################

    def inputObs(self, MM_ws, inputObs_fn, inputObsHEADS_fn, inputObsSM_fn, inputDate, _nslmax, nlay):
        '''
        observations cells for soil moisture and heads (will also compute SATFLOW)
        '''

        # read coordinates and SATFLOW parameters
        inputFile = readFile(MM_ws,inputObs_fn)

        # define a dictionnary of observations,  format is: Name (key) x y i j hi h0 RC STO
        obs = {}
        obs_list = []
        for o in range(len(inputFile)):
            line = inputFile[o].split()
            name = line[0]
            obs_list.append(name)
            x = float(line[1])
            y = float(line[2])
            lay = float(line[3])
            try:
                hi  = float(line[4])
                h0  = float(line[5])
                RC  = float(line[6])
                STO = float(line[7])
            except:
                hi = h0 = RC = STO =  self.hnoflo
            # verify if coordinates are inside MODFLOW grid
            if (x < self.xllcorner or
               x > (self.xllcorner+self.ncol*self.cellsizeMF) or
               y < self.yllcorner or
               y > (self.yllcorner+self.nrow*self.cellsizeMF)):
                   raise BaseException, 'The coordinates of the observation point %s are not inside the MODFLOW grid' % name
            if lay > nlay or lay < 1:
                lay = 0
                print 'WARNING!\nLayer %s of observation point %s is not valid (corrected to layer 1)!\nCheck your file %s (layer number should be between 1 and the number of layer of the MODFLOW model, in this case %s).' % (lay, name, inputObs_fn, nlay)
            else:
                lay = lay - 1
            # compute the cordinates in the MODFLOW grid
            #TODO use the PEST utilities for space extrapolation
            i = self.nrow - np.ceil((y-self.yllcorner)/self.cellsizeMF)
            j = np.ceil((x-self.xllcorner)/self.cellsizeMF) - 1
            #  read obs time series
            obsh_fn = os.path.join(self.MM_ws, inputObsHEADS_fn + '_' + name +'.txt')
            if os.path.exists(obsh_fn):
                obs_h, obs_h_yn = self.verifObs(inputDate, obsh_fn, obsnam = name)
            else:
                obs_h = []
                obs_h_yn = 0
            obssm_fn=os.path.join(self.MM_ws, inputObsSM_fn + '_' + name + '.txt')
            if os.path.exists(obssm_fn):
                obs_sm, obs_sm_yn = self.verifObs(inputDate, obssm_fn, _nslmax, obsnam = name)
            else:
                obs_sm = []
                obs_sm_yn = 0
            obs[name] = {'x':x,'y':y,'i': i, 'j': j, 'lay': lay, 'hi':hi, 'h0':h0, 'RC':RC, 'STO':STO, 'outpathname':os.path.join(self.MM_ws,'_MM_0'+name+'.txt'), 'obs_h':obs_h, 'obs_h_yn':obs_h_yn, 'obs_S':obs_sm, 'obs_sm_yn':obs_sm_yn}

        return obs, obs_list
        del inputObs_fn, inputObsHEADS_fn, inputObsSM_fn, inputDate, _nslmax
        del obs

    ######################

    def verifObs(self, inputDate, filename, _nslmax = 0, obsnam = 'unknown location'):
        '''
        Import and process data and parameters
        '''

        if os.path.exists(filename):
            try:
                obsData=np.loadtxt(filename, dtype = str)
                obsDate = mpl.dates.datestr2num(obsData[:,0])
                obsValue = []
                for l in range(1,len(obsData[0])):
                    obsValue.append(obsData[:,l].astype(float))
                if len(obsValue)<_nslmax:
                    for l in range(_nslmax-len(obsValue)):
                        obsValue.append(self.hnoflo)
            except:
                raise ValueError, '\nFATAL ERROR!\nFormat of observation file uncorrect!\n%s' % filename
            obsOutput = np.ones([len(obsValue),len(inputDate)], dtype=float)*self.hnoflo
            obs_yn = 0
            if (obsDate[len(obsDate)-1] < inputDate[0]) or (obsDate[0] > inputDate[len(inputDate)-1]):
                obsOutput = []
                print '\nObservations of file %s outside the modeling period!' % filename
            else:
                for l in range(len(obsValue)):
                    if not isinstance(obsValue[l], float):
                        j=0
                        if inputDate[0] > obsDate[0]:
                           while obsDate[j]<inputDate[0]:
                                j += 1
                        for i in range(len(inputDate)):
                            if j<len(obsDate):
                                if inputDate[i]==obsDate[j]:
                                    obsOutput[l,i]=obsValue[l][j]
                                    j += 1
                                    obs_yn = 1
                                else:
                                    obsOutput[l,i]=self.hnoflo
                            else:
                                obsOutput[l,i]=self.hnoflo
                    else:
                        obsOutput[l,:] = np.ones([len(inputDate)])*self.hnoflo
        else:
            obsOutput = []
        return obsOutput, obs_yn
        del inputDate, obsOutput

    ######################

    def outputEAgrd(self, outFile_fn, outFolder = []):

        if outFolder == []:
            outFolder = self.MM_ws

        outFile=open(os.path.join(outFolder, outFile_fn), 'w')

        outFile=self.writeHeaderESRIraster(outFile)

        return outFile
        del outFile

    ######################

    def writeHeaderESRIraster(self, file_asc):
        '''
        Write ESRI ASCII raster header
        '''
        file_asc.write('ncols  ' + str(self.ncol)+'\n' +
                       'nrows  '  + str(self.nrow)+'\n' +
                       'xllcorner  '+ str(self.xllcorner)+'\n' +
                        'yllcorner  '+ str(self.yllcorner)+'\n' +
                        'cellsize   '+ str(self.cellsizeMF)+'\n' +
                        'NODATA_value  '+ str(self.hnoflo)+'\n')
        return file_asc
        del file_asc

    ######################

    def ExportResultsMM(self, i, j, inputDate, SP_d, _nslmax, results, index, results_S, index_S, RCH, WEL, h_satflow, heads_MF, obs_h, obs_S, index_veg, outFileExport, obsname):
        """
        Export the processed data in a txt file
        INPUTS:      output fluxes time series and date
        OUTPUT:      ObsName.txt
        """
        for t in range(len(inputDate)):
            # 'Date,RF,E0,PT,PE,RFe,I,'+Eu_str+Tu_str+'Eg,Tg,ETg,WEL_MF,Es,'+Ssoil_str+Ssoilpc_str+dSsoil_str+'dSs,Ss,Ro,GW_EXF,GW_EXF_MF,'+Rp_str+Rexf_str+'R_MF,hSATFLOW,hMF,hMFcorr,hmeas,dgwt,' + Smeasout + MB_str + 'MB\n'
            out_date = mpl.dates.num2date(inputDate[t]).isoformat()[:10]
            Sout     = ''
            Spcout   = ''
            dSout    = ''
            Rpout    = ''
            Rexfout     = ''
            Euout    = ''
            Tuout    = ''
            Smeasout = ''
            MBout=''
            for l in range(_nslmax):
                Sout += str(results_S[t,l,index_S.get('iSsoil')]) + ','
                Spcout += str(results_S[t,l,index_S.get('iSsoil_pc')]) + ','
                dSout += str(results_S[t,l,index_S.get('idSsoil')]) + ','
                Rpout += str(results_S[t,l,index_S.get('iRp')]) + ','
                Rexfout += str(results_S[t,l,index_S.get('iRexf')]) + ','
                Euout += str(results_S[t,l,index_S.get('iEsoil')]) + ','
                Tuout += str(results_S[t,l,index_S.get('iTsoil')]) + ','
                MBout += str(results_S[t,l,index_S.get('iMB_l')]) + ','
                try:
                    Smeasout += str(obs_S[l,t]) + ','
                except:
                    Smeasout += str(self.hnoflo) + ','
            try:
                obs_h_tmp = obs_h[t]
            except:
                obs_h_tmp = self.hnoflo
            out1 = '%d,%d,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,' % (SP_d[t], index_veg[t], results[t,index.get('iRF')], results[t,index.get('iE0')],results[t,index.get('iPT')],results[t,index.get('iPE')],results[t,index.get('iRFe')],results[t,index.get('iI')])
            if type(WEL) == np.ndarray or type(WEL) == np.ma.core.MaskedArray:
                WEL_tmp = WEL[t]
            else:
                WEL_tmp = 0.0
            out2 = '%.8f,%.8f,%.8f,%.8f,%.8f,' % (results[t,index.get('iEg')], results[t,index.get('iTg')],results[t,index.get('iETg')], WEL_tmp, results[t,index.get('iEsurf')])
            out3 = '%.8f,%.8f,%.8f,%.8f,' % (results[t,index.get('idSsurf')],results[t,index.get('iSsurf')],results[t,index.get('iRo')],results[t,index.get('iEXF')])
            out4 = '%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,' % (RCH[t], h_satflow[t],heads_MF[t],results[t,index.get('iHEADScorr')],obs_h_tmp,results[t,index.get('idgwt')])
            out5 = '%.8f' % (results[t,index.get('iMB')])
            out_line =  out_date, ',', out1, Euout, Tuout, out2, Sout, Spcout, dSout, out3, Rpout, Rexfout, out4, Smeasout, MBout, out5, '\n'
            for l in out_line:
                outFileExport.write(l)
        del i, j, inputDate, _nslmax, results, index, results_S, index_S, RCH, WEL, h_satflow, heads_MF, obs_h, obs_S, outFileExport, obsname

    def ExportResultsMM4PEST(self, i, j, inputDate, _nslmax, results_S, index_S, obs_S, obsname):
        """
        Export the processed data in a txt file
        INPUTS:      output fluxes time series and date
        OUTPUT:      ObsName.txt
        """
        self.smMM.append([])
        len_smMM = len(self.smMM)
        for t in range(len(inputDate)):
            out_date = mpl.dates.num2date(inputDate[t]).strftime("%d/%m/%Y")
            for l in range(_nslmax):
                try:
                    obs_S_tmp = obs_S[l,t]
                except:
                    obs_S_tmp = -1.0
                if results_S[t,l,index_S.get('iSsoil_pc')] > 0.0 and obs_S_tmp > 0.0:
                    self.smMM[len_smMM-1].append((obsname+'SM_l'+str(l+1)).ljust(10,' ')+ out_date.ljust(10,' ')+ ' 00:00:00 ' + str(results_S[t,l,index_S.get('iSsoil_pc')]).ljust(10,' ') + '\n')
        del i, j, _nslmax, results_S, index_S, obs_S, obsname

    def ExportResultsPEST(self, i, j, inputDate, _nslmax, obs_h, obs_S, outPESTheads, outPESTsm, obsname):
        """
        Export the obs data in a txt file in PEST format
        INPUTS:      output fluxes time series and date
        OUTPUT:      PESTxxx.smp
        """
        self.smMM.append([])
        len_smMM = len(self.smMM)
        for t in range(len(inputDate)):
            date = mpl.dates.num2date(inputDate[t]).strftime("%d/%m/%Y")
            try:
                if obs_h[t] <> self.hnoflo:
                    outPESTheads.write(obsname.ljust(10,' ')+ date.ljust(10,' ')+ ' 00:00:00 ' + str(obs_h[t]).ljust(10,' ') + '\n')
            except:
                pass
            try:
                for l in range (_nslmax):
                    if obs_S[l,t] <> self.hnoflo:
                        self.smMM[len_smMM-1].append((obsname+'SM_l'+str(l+1)).ljust(10,' ')+ date.ljust(10,' ')+ ' 00:00:00 ' + str(obs_S[l,t]).ljust(10,' ') + '\n')
            except:
                pass
# EOF