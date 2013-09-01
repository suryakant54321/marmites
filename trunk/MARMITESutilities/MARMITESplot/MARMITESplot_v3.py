# -*- coding: utf-8 -*-

__author__ = "Alain P. Francés <frances08512@itc.nl>"
__version__ = "0.3"
__date__ = "2012"

import os
import matplotlib as mpl
import matplotlib.pyplot as plt
import subprocess as sp
import numpy as np
import itertools, shutil

#####################################

def rmse (x, y) :
    def sqre_diff (v, w) :
        return (v - w) ** 2
    s = len(x)
    v = sum(map(sqre_diff, x, y), 0.0)
    return np.sqrt(v / s)

#####################################

def plotTIMESERIES(DateInput, P, PT, PE, Pe, dPOND, POND, Ro, Esoil, Tsoil, Eg, Tg, S, dS, Spc, Rp, EXF, ETg, Es, MB, MB_l, dgwt, uzthick, SAT, R, h_MF, h_MF_corr, h_SF, hobs, Sobs, Sm, Sr, hnoflo, plt_export_fn, plt_title, colors_nsl, hmax, hmin, obs_name, elev, nlay, l_obs, nsl):
    """
    Plot the time serie of the fluxes observed at one point of the catchment
    Use Matplotlib
    _______________________________________________________________________________

    INPUTS
            STATE VARIABLES
                SP              Stress period
                P               Daily rainfall
                PT              Daily potential transpiration
                PE              Daily potential evaporation
                Pe              Daily Excess rainfall
                Esoil           Daily evaporation (bare soil)
                Tsoil           Daily transpiration
                S               Daily soil moisture
                Rp              Daily percolation
                POND            Daily ponding
                Ro              Daily runoff
                R               Daily recharge
                h               Daily water level
                hobs           Daily obsserved water level
    ______________________________________________________________________________
    ______________________________________________________________________________
    """

    monthsFmt=mpl.dates.DateFormatter('%Y-%m-%d')
    lblspc = 0.05
    mkscale = 0.5

    fig = plt.figure(num=None, figsize=(2*8.27, 2*11.7), dpi = 30)    #(8.5,15), dpi=30)

    fig.suptitle(plt_title)

    lbl_Spc = []
    lbl_S = []
    lbl_dS = []
    lbl_Sobs = []
    lbl_Rp = []
    lbl_Esoil = []
    lbl_Tsoil = []
    lbl_SAT = []
    lbl_MB =[]
    lbl_Esoil.append(r'$PE$')
    lbl_Esoil.append(r'$Etot$')
    lbl_Esoil.append(r'$Etot_{soil}$')
    lbl_Tsoil.append(r'$PT$')
    lbl_Tsoil.append(r'$Ttot$')
    lbl_Tsoil.append(r'$Ttot_{soil}$')
    lbl_MB.append(r'$MB$')
    Sobs_m = []
    Esoil1 = []
    Tsoil1 = []
    dS1 = []
    S1 = []
    Rp1 = []
    Spc1 = []
    Spc1full = []
    SAT1 = []
    MB_l1 = []
    for l in range(nsl):
        lbl_S.append(r'$S_{soil,%d}$'%(l+1))
        lbl_dS.append(r'$\Delta S_{soil,%d}$'%(l+1))
        lbl_Esoil.append(r'$E_{soil,%d}$'%(l+1))
        lbl_Tsoil.append(r'$T_{soil,%d}$'%(l+1))
        lbl_SAT.append(r'$l_{%d}$'%(l+1))
        lbl_MB.append(r'$MB_{soil,%d}$'%(l+1))
        lbl_Spc.append(r'$\theta _{%d}$'%(l+1))
        lbl_Rp.append(r'$Rp_{%d}$'%(l+1))
        Spc1full.append(Spc[:,l])
        Esoil1.append(Esoil[:,l])
        Tsoil1.append(Tsoil[:,l])
        dS1.append(dS[:,l])
        S1.append(S[:,l])
        SAT1.append(SAT[:,l])
        MB_l1.append(MB_l[:,l])
        Spc1.append(Spc[:,l])
        Rp1.append(Rp[:,l])
        try:
            Sobs_m.append(np.ma.masked_values(Sobs[l], hnoflo, atol = 0.09))
            lbl_Sobs.append(r'$\theta_{%d}obs$'%(l+1))
        except:
            Sobs_m.append([])
    del dS, S, SAT, MB_l
    del Rp, Spc
    Esoil1 = np.asarray(Esoil1)
    Tsoil1 = np.asarray(Tsoil1)
    dS1 = np.asarray(dS1)
    S1 = np.asarray(S1)
    Rp1 = np.asarray(Rp1)
    Spc1 = np.asarray(Spc1)
    SAT1 = np.asarray(SAT1)
    MB_l1 = np.asarray(MB_l1)
    lbl_Rp.append(r'$R$')
    lbl_Rp.append(r'$ET_g$')
    lbl_Rp.append(r'$EXF_g$')
    lbl_Tsoil.append(r'$T_g$')
    lbl_Esoil.append(r'$E_g$')

    ax1=fig.add_subplot(10,1,1)
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax1.get_yticklabels(), fontsize=8)
    ax1.bar(DateInput,P,color='darkblue', linewidth=0, align = 'center', label=r'$RF$')
    ax1.bar(DateInput,Pe,color='deepskyblue', linewidth=0, align = 'center', label=r'$RFe$')
    plt.xlim(DateInput[0]-1,DateInput[len(DateInput)-1]+1)
    plt.legend(loc=0, labelspacing=lblspc, markerscale=mkscale)
    leg = plt.gca().get_legend()
    ltext  = leg.get_texts()
    plt.setp(ltext, fontsize=8)
    plt.grid(True)
    plt.ylabel('mm', fontsize=10)
    ax1.xaxis.set_major_formatter(monthsFmt)
    ax1.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2G'))

    ax2=fig.add_subplot(10,1,2, sharex=ax1)
    plt.setp(ax2.get_xticklabels(), visible=False)
    plt.setp(ax2.get_yticklabels(), fontsize=8)
    plt.plot_date(DateInput,Ro,'r-', c='darkblue', linewidth=2, label = r'$Ro$')
    plt.plot_date(DateInput,Es,'r-', c='deepskyblue', linewidth=0.75, label = r'$E_{surf}$')
    plt.bar(DateInput, POND, color='lightblue', linewidth=0, align = 'center', label = r'$S_{surf}$')
    plt.bar(DateInput, dPOND, color='blue', width=0.60, linewidth=0, align = 'center', label = r'$\Delta S_{surf}$')
    plt.xlim(DateInput[0]-1,DateInput[len(DateInput)-1]+1)
    plt.ylabel('mm', fontsize=10)
    plt.legend(loc=0, labelspacing=lblspc, markerscale=mkscale)
    leg = plt.gca().get_legend()
    ltext  = leg.get_texts()
    plt.setp(ltext, fontsize=8)
    plt.grid(True)
    ax2.xaxis.set_major_formatter(monthsFmt)
    ax2.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2G'))

    Esoil_tot = []
    for e in Esoil:
        Esoil_tot.append(e.sum())
    Esoil_tot = np.asarray(Esoil_tot)
    E_tot = Esoil_tot + Eg
    del Esoil
    ax3=fig.add_subplot(10,1,3, sharex=ax1)
    plt.setp(ax3.get_xticklabels(), visible=False)
    plt.setp(ax3.get_yticklabels(), fontsize=8)
    plt.plot_date(DateInput,PE,'-', color='lightblue', linewidth=3)
    plt.plot_date(DateInput,E_tot,'-', color='darkblue', linewidth=1.5)
    plt.plot_date(DateInput,Esoil_tot,'-.', color=colors_nsl[len(colors_nsl)-1])
    for l, (y, color, lbl) in enumerate(zip(Esoil1, colors_nsl, lbl_Esoil[2:len(lbl_Esoil)])):
        ax3.plot_date(DateInput, y, '-', color=color, label=lbl)
    plt.plot_date(DateInput,Eg,'-', color='blue')
    plt.xlim(DateInput[0]-1,DateInput[len(DateInput)-1]+1)
    plt.legend(lbl_Esoil, loc=0, labelspacing=lblspc, markerscale=mkscale)
    leg = plt.gca().get_legend()
    ltext  = leg.get_texts()
    plt.setp(ltext, fontsize=8)
    plt.grid(True)
    plt.ylabel('mm', fontsize=10)
    ax3.xaxis.set_major_formatter(monthsFmt)
    ax3.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2G'))

    Tsoil_tot = []
    for t in Tsoil:
        Tsoil_tot.append(t.sum())
    Tsoil_tot = np.asarray(Tsoil_tot)
    T_tot = Tsoil_tot + Tg
    del Tsoil
    ax4=fig.add_subplot(10,1,4, sharex=ax1)
    plt.setp(ax4.get_xticklabels(), visible=False)
    plt.setp(ax4.get_yticklabels(), fontsize=8)
    plt.plot_date(DateInput,PT,'-', color='lightblue', linewidth=3)
    plt.plot_date(DateInput,T_tot,'-', color='darkblue',  linewidth=1.5)
    plt.plot_date(DateInput,Tsoil_tot,'-.', color=colors_nsl[len(colors_nsl)-1])
    for l, (y, color, lbl) in enumerate(zip(Tsoil1, colors_nsl, lbl_Tsoil[2:len(lbl_Tsoil)])):
        ax4.plot_date(DateInput, y, '-', color=color, label=lbl)
    plt.plot_date(DateInput,Tg,'-', color='blue')
    plt.xlim(DateInput[0]-1,DateInput[len(DateInput)-1]+1)
    plt.legend(lbl_Tsoil, loc=0, labelspacing=lblspc, markerscale=mkscale)
    leg = plt.gca().get_legend()
    ltext  = leg.get_texts()
    plt.setp(ltext, fontsize=8 )
    plt.grid(True)
    plt.ylabel('mm', fontsize=10)
    ax4.xaxis.set_major_formatter(monthsFmt)
    ax4.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2G'))

    ax5=fig.add_subplot(10,1,5, sharex=ax1)
    plt.setp(ax5.get_xticklabels(), visible=False)
    plt.setp(ax5.get_yticklabels(), fontsize=8)
    obs_tmp = []
    test = 0
    try:
        for l, (y, color, lbl) in enumerate(zip(Sobs_m, colors_nsl, lbl_Sobs)):
            obs_tmp.append(y)
            if y != []:
                ax5.plot_date(DateInput, y, ls = 'None', color = 'None', marker='o', markersize=2, markeredgecolor = color, markerfacecolor = 'None', label=lbl) #'--', color = color,
                test += 1
    except:
        print'WARNING! Error in plotting SM observations at %s' % obs_name
        pass
    sim_tmp = []
    for l, (y, color, lbl) in enumerate(zip(Spc1full, colors_nsl, lbl_Spc)):
        sim_tmp.append(y)
        y = np.ma.masked_where(y < 0.0, y)
        ax5.plot_date(DateInput, y, '-', color = color, label = lbl)
    # x axis
    plt.xlim(DateInput[0]-1,DateInput[len(DateInput)-1]+1)
    # y axis
    ybuffer=0.1*(max(Sm)-min(Sr))
    plt.ylim(min(Sr) - ybuffer,max(Sm) + ybuffer)
    plt.ylabel('%', fontsize=10)
    # legend
    #lbl_Spcobs = lbl_Sobs + lbl_S
    #plt.legend(lbl_Spcobs, loc=0, labelspacing=lblspc, markerscale=mkscale)
    plt.legend(loc=0, labelspacing=lblspc, markerscale=mkscale)
    leg = plt.gca().get_legend()
    ltext  = leg.get_texts()
    plt.setp(ltext, fontsize=8 )
    plt.grid(True)
    ax5.xaxis.set_major_formatter(monthsFmt)
    ax5.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2G'))

    ax6=fig.add_subplot(10,1,6, sharex=ax1)
    plt.setp(ax6.get_xticklabels(), visible=False)
    plt.setp(ax6.get_yticklabels(), fontsize=8)
    plt.bar(DateInput,EXF, color='lightblue', linewidth=0, align = 'center', label=r'$EXF_g$')
    for l, (y, color, lbl) in enumerate(zip(Rp1, colors_nsl, lbl_Rp[2:len(lbl_Rp)])) :
        ax6.plot_date(DateInput, y, '-', color=color, label=lbl)
    plt.plot_date(DateInput,R,'-', c='darkblue', linewidth=2)
    plt.plot_date(DateInput,ETg,'-', c='blue', linewidth=1.5)
    plt.xlim(DateInput[0]-1,DateInput[len(DateInput)-1]+1)
    plt.legend(lbl_Rp, loc = 0, labelspacing=lblspc, markerscale=mkscale)
    leg = plt.gca().get_legend()
    ltext  = leg.get_texts()
    plt.setp(ltext, fontsize=8 )
    plt.grid(True)
    plt.ylabel('mm', fontsize=10)
    ax6.xaxis.set_major_formatter(monthsFmt)
    ax6.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2G'))

    ax7=fig.add_subplot(10,1,7, sharex=ax1)
    plt.setp(ax7.get_xticklabels(), fontsize=8)
    plt.setp(ax7.get_yticklabels(), fontsize=8)
    obs_leg = None
    try:
        hobs_m = np.ma.masked_values(hobs, hnoflo, atol = 0.09)
        plt.plot_date(DateInput,hobs_m, ls = 'None', color = 'None', marker='o', markeredgecolor = 'blue', markerfacecolor = 'None', markersize = 2) # ls='--', color = 'blue'
        obs_leg = 1
    except:
        pass
    lines = itertools.cycle(['-','--','-.',':','.',',','o','v','^','<','>','1','2','3','4','s','p','*','h','H','+','x','D','d','|','_'])
    lbl_h = []
    for l in range(nlay):
        plt.plot_date(DateInput,h_MF[:,l],lines.next(), color = 'b')
        lbl_h.append(r'$hMF_{%d}$' % (l+1))
    plt.plot_date(DateInput,h_MF_corr,'-', color = 'g')
    plt.plot_date(DateInput,h_SF,'-', color = 'r')
    ax7.set_xticklabels(DateInput)
    plt.xlim(DateInput[0]-1,DateInput[len(DateInput)-1]+1)
    labels=ax7.get_xticklabels()
    plt.setp(labels, 'rotation', 90)
    ybuffer=0.1*(hmax-hmin)
    if ybuffer == 0.0:
        ybuffer = 1.0
    plt.ylim((hmin - ybuffer, hmax + ybuffer))
    plt.ylabel('m', fontsize=10)
    if obs_leg == None:
        lbl_h.append(r'$hMF corr$')
        lbl_h.append(r'$hSF$')
        plt.legend(tuple(lbl_h), loc=0, labelspacing=lblspc, markerscale=mkscale)
    elif obs_leg == 1:
        lbl_h.insert(0,r'$h obs$')
        lbl_h.append(r'$hMF corr$')
        lbl_h.append(r'$hSF$')
        plt.legend(tuple(lbl_h), loc=0, labelspacing=lblspc, markerscale=mkscale)
    leg = plt.gca().get_legend()
    ltext  = leg.get_texts()
    plt.setp(ltext, fontsize=8 )
    plt.xlabel('Date', fontsize=10)
    plt.grid(True)
    ax7.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2G'))
    ax7.xaxis.set_major_formatter(monthsFmt)

    # RMSE
    if test > 0 or obs_leg == 1:
        print '-------\nRMSE %s' % obs_name
        if test > 0:
            try:
                for l, (y, y_obs) in enumerate(zip(sim_tmp, obs_tmp)):
                    a = np.array([y,y_obs])
                    a = np.transpose(a)
                    b = a[~(a < hnoflo +1000.0).any(1)]
                    if b[:,0] <> []:
                        print 'SM layer %d: %.1f %%' % (l, 100.0*rmse(b[:,0], b[:,1]))
            except:
                print 'SM layer %d: error' % l
        if obs_leg == 1:
            try:
                a = np.array([hobs,h_MF_corr])
                a = np.transpose(a)
                b = a[~(a < hnoflo +1000.0).any(1)]
                if b[:,0] <> []:
                    print 'h: %.2f m' % rmse(b[:,0], b[:,1])
            except:
                print 'h: error'

    ax8b=fig.add_subplot(20,1,16, sharex=ax1)
    plt.setp(ax8b.get_xticklabels(), visible=False)
    plt.setp(ax8b.get_yticklabels(), fontsize=8)
    plt.plot_date(DateInput,MB,'-', c='r')
    for l, (y, color, lbl) in enumerate(zip(MB_l1, colors_nsl, lbl_MB[1:len(lbl_MB)])) :
        ax8b.plot_date(DateInput, y, '-', color=color, label=lbl)
    # y axis
    plt.ylabel('mm', fontsize=10)
    plt.grid(True)
    plt.xlim(DateInput[0]-1,DateInput[len(MB)-1]+1)
    if max(np.max(MB),np.max(MB_l1)) < 0.001 and min(np.min(MB), np.min(MB_l1)) > -0.001:
        plt.ylim(-0.1,0.1)
    else:
        minfact = 0.95
        maxfact = 1.05
        if min(np.min(MB), np.min(MB_l1)) > 0:
            minfact = 1.05
        if max(np.max(MB), np.max(MB_l1)) < 0:
            maxfact = 0.95
        plt.ylim(min(np.min(MB), np.min(MB_l1))*minfact,max(np.max(MB),np.max(MB_l1))*maxfact)
    # legend
    plt.legend(lbl_MB, loc=0, labelspacing=lblspc, markerscale=mkscale)
    leg = plt.gca().get_legend()
    ltext  = leg.get_texts()
    plt.setp(ltext, fontsize=8 )
    ax8b.xaxis.set_major_formatter(monthsFmt)
    ax8b.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2G'))

    ax9a=fig.add_subplot(20,1,17, sharex=ax1)
    plt.setp(ax9a.get_xticklabels(), visible=False)
    plt.setp(ax9a.get_yticklabels(), fontsize=8)
    for l, (y, color, lbl) in enumerate(zip(SAT1, colors_nsl, lbl_SAT)) :
        ax9a.plot_date(DateInput, y, '-', color = color, label = lbl)
    # x axis
    plt.xlim(DateInput[0]-1,DateInput[len(DateInput)-1]+1)
    # y axis
    plt.ylim(-0.1,1.1)
    plt.ylabel('SAT', fontsize=10)
    ax9a.yaxis.set_ticks(np.arange(0,1.25,1))
    ax9a.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%1d'))
    # legend
    plt.legend(loc=0, labelspacing=lblspc, markerscale=mkscale)
    leg = plt.gca().get_legend()
    ltext  = leg.get_texts()
    plt.setp(ltext, fontsize=8 )
    plt.grid(True)
    ax9a.xaxis.set_major_formatter(monthsFmt)

    ax9b=fig.add_subplot(20,1,18, sharex=ax1)
    plt.setp(ax9b.get_xticklabels(), visible=False)
    plt.setp(ax9b.get_yticklabels(), fontsize=8)
    obs_leg = None
    try:
        hobs_m = np.ma.masked_values(hobs, hnoflo, atol = 0.09) - elev
        plt.plot_date(DateInput,hobs_m, ls = 'None', color = 'None', marker='o', markeredgecolor = 'blue', markerfacecolor = 'None', markersize = 2) # ls='--', color = 'blue'
        obs_leg = 1
    except:
        pass
    plt.plot_date(DateInput,dgwt,'-', c='b')
    # y axis
    plt.ylabel('m', fontsize=10)
    plt.grid(True)
    plt.xlim(DateInput[0]-1,DateInput[len(dgwt)-1]+1)
    #plt.ylim(np.min(dgwt)*1.05,0.25)
    # legend
    if obs_leg == None:
        plt.legend([r'$DGWTMF$'], loc=0, labelspacing=lblspc, markerscale=mkscale)
    elif obs_leg == 1:
        plt.legend((r'$DGWT obs$',r'$DGWT MF$'), loc=0, labelspacing=lblspc, markerscale=mkscale)
    leg = plt.gca().get_legend()
    plt.ylim(ymax = 0.0)
    ltext  = leg.get_texts()
    plt.setp(ltext, fontsize=8 )
    ax9b.xaxis.set_major_formatter(monthsFmt)
    ax9b.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2G'))

    ax10a=fig.add_subplot(20,1,19, sharex=ax1)
    plt.setp(ax10a.get_xticklabels(), visible=False)
    plt.setp(ax10a.get_yticklabels(), fontsize=8)
    plt.plot_date(DateInput,uzthick,'-', c='brown')
    # y axis
    plt.ylabel('m', fontsize=10)
    plt.grid(True)
    plt.xlim(DateInput[0]-1,DateInput[len(uzthick)-1]+1)
    minfact = 0.95
    maxfact = 1.05
    if np.min(uzthick) < 0:
        minfact = 1.05
    if np.max(uzthick) < 0:
        maxfact = 0.95
    if np.min(uzthick) == np.max(uzthick) == 0.0:
        plt.ylim(-0.5, 0.5)
    else:
        plt.ylim(np.min(uzthick)*minfact, np.max(uzthick)*maxfact)
    # legend
    plt.legend([r'$uzthick$'], loc=0, labelspacing=lblspc, markerscale=mkscale)
    leg = plt.gca().get_legend()
    ltext  = leg.get_texts()
    plt.setp(ltext, fontsize=8 )
    ax10a.xaxis.set_major_formatter(monthsFmt)
    ax10a.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2G'))

    ax10b=fig.add_subplot(20,1,20, sharex=ax1)
    plt.setp(ax10b.get_xticklabels(), visible=False)
    plt.setp(ax10b.get_yticklabels(), fontsize=8)
    for l, (y, color, lbl) in enumerate(zip(S1, colors_nsl, lbl_S)) :
        y = np.ma.masked_where( y < 0.0, y)
        ax10b.plot_date(DateInput, y, '-', color=color, label=lbl)
    # x axis
    plt.xlim(DateInput[0]-1,DateInput[len(DateInput)-1]+1)
    # y axis
    plt.ylim(0,np.max(S1)*1.05)
    plt.ylabel('mm', fontsize=10)
    ax10b.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2G'))
    # legend
    plt.legend(loc=0, labelspacing=lblspc, markerscale=mkscale)
    leg = plt.gca().get_legend()
    ltext  = leg.get_texts()
    plt.setp(ltext, fontsize=8 )
    plt.grid(True)
    ax10b.xaxis.set_major_formatter(monthsFmt)

    plt.subplots_adjust(left=0.10, bottom=0.10, right=0.95, top=0.95, wspace=0.1, hspace=0.1)
    plt.savefig(plt_export_fn,dpi=150)
#    plt.show()
    plt.clf()
    plt.close('all')

##################

def plotTIMESERIES_CATCH(DateInput, flx, flx_lbl, plt_export_fn, plt_title, hmax, hmin, cMF = None, obs_catch = None, obs_catch_list = [0, 0], TopSoilAverage = None):
    """
    Plot the time serie of the fluxes observed from the whole catchment
    Use Matplotlib
    """

    monthsFmt=mpl.dates.DateFormatter('%Y-%m-%d')
    lblspc = 0.05
    mkscale = 0.5

    fig = plt.figure(num=None, figsize=(2*8.27, 2*11.7), dpi = 30)    #(8.5,15), dpi=30)

    fig.suptitle(plt_title)

    ax1=fig.add_subplot(10,1,1)
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax1.get_yticklabels(), fontsize=8)
    ax1.bar(DateInput,flx[0],color='darkblue', linewidth=0, align = 'center', label = flx_lbl[0])
    ax1.bar(DateInput,flx[2],color='deepskyblue', linewidth=0, align = 'center', label = flx_lbl[2])
    plt.xlim(DateInput[0]-1,DateInput[len(DateInput)-1]+1)
    plt.legend(loc=0, labelspacing=lblspc, markerscale=mkscale)
    leg = plt.gca().get_legend()
    ltext  = leg.get_texts()
    plt.setp(ltext, fontsize=8)
    plt.grid(True)
    plt.ylabel('mm', fontsize=10)
    ax1.xaxis.set_major_formatter(monthsFmt)
    ax1.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2G'))

    ax2=fig.add_subplot(10,1,2, sharex=ax1)
    plt.setp(ax2.get_xticklabels(), visible=False)
    plt.setp(ax2.get_yticklabels(), fontsize=8)
    plt.plot_date(DateInput,flx[4],'r-', c='darkblue', linewidth=2, label = flx_lbl[4])
    plt.plot_date(DateInput,flx[5],'r-', c='deepskyblue', linewidth=0.75, label = flx_lbl[5])
    plt.bar(DateInput, flx[14], color='lightblue', linewidth=0, align = 'center', label = flx_lbl[14])
    plt.bar(DateInput, flx[3], color='blue', width=0.60, linewidth=0, align = 'center', label = flx_lbl[3])
    plt.xlim(DateInput[0]-1,DateInput[len(DateInput)-1]+1)
    plt.ylabel('mm', fontsize=10)
    plt.legend(loc=0, labelspacing=lblspc, markerscale=mkscale)
    leg = plt.gca().get_legend()
    ltext  = leg.get_texts()
    plt.setp(ltext, fontsize=8)
    plt.grid(True)
    ax2.xaxis.set_major_formatter(monthsFmt)
    ax2.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2G'))

    E_tot = flx[8] + flx[11]
    ax3=fig.add_subplot(10,1,3, sharex=ax1)
    plt.setp(ax3.get_xticklabels(), visible=False)
    plt.setp(ax3.get_yticklabels(), fontsize=8)
    plt.plot_date(DateInput,flx[15],'-', color='lightblue', linewidth=3, label = flx_lbl[15])
    plt.plot_date(DateInput,E_tot,'-', color='darkblue', linewidth=1.5, label = r'$Etot$')
    plt.plot_date(DateInput,flx[8],'-.', color='brown', label = flx_lbl[8])
    plt.plot_date(DateInput,flx[11],'-', color='blue', label = flx_lbl[11])
    plt.xlim(DateInput[0]-1,DateInput[len(DateInput)-1]+1)
    plt.legend(loc=0, labelspacing=lblspc, markerscale=mkscale)
    leg = plt.gca().get_legend()
    ltext  = leg.get_texts()
    plt.setp(ltext, fontsize=8)
    plt.grid(True)
    plt.ylabel('mm', fontsize=10)
    ax3.xaxis.set_major_formatter(monthsFmt)
    ax3.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2G'))

    T_tot = flx[9] + flx[12]
    ax4=fig.add_subplot(10,1,4, sharex=ax1)
    plt.setp(ax4.get_xticklabels(), visible=False)
    plt.setp(ax4.get_yticklabels(), fontsize=8)
    plt.plot_date(DateInput,flx[16],'-', color='lightblue', linewidth=3, label = flx_lbl[16])
    plt.plot_date(DateInput,T_tot,'-', color='darkblue',  linewidth=1.5, label = r'$Ttot$')
    plt.plot_date(DateInput,flx[9],'-.', color='brown', label = flx_lbl[9])
    plt.plot_date(DateInput,flx[12],'-', color='blue', label = flx_lbl[12])
    plt.xlim(DateInput[0]-1,DateInput[len(DateInput)-1]+1)
    plt.legend(loc=0, labelspacing=lblspc, markerscale=mkscale)
    leg = plt.gca().get_legend()
    ltext  = leg.get_texts()
    plt.setp(ltext, fontsize=8 )
    plt.grid(True)
    plt.ylabel('mm', fontsize=10)
    ax4.xaxis.set_major_formatter(monthsFmt)
    ax4.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2G'))

    ax5=fig.add_subplot(10,1,5, sharex=ax1)
    plt.setp(ax5.get_xticklabels(), visible=False)
    plt.setp(ax5.get_yticklabels(), fontsize=8)
    plt.bar(DateInput,flx[7], color='lightblue', linewidth=0, align = 'center', label = flx_lbl[7])
    ax5.plot_date(DateInput, flx[17], '-', color = 'brown', label= r'$Rp$')
    if cMF != None:
        plt.plot_date(DateInput,flx[19],'-', c='darkblue', linewidth=2, label = flx_lbl[19])
    plt.plot_date(DateInput,flx[13],'-', c='blue', linewidth=1.5, label = flx_lbl[13])
    plt.xlim(DateInput[0]-1,DateInput[len(DateInput)-1]+1)
    plt.legend(loc = 0, labelspacing=lblspc, markerscale=mkscale)
    leg = plt.gca().get_legend()
    ltext  = leg.get_texts()
    plt.setp(ltext, fontsize=8 )
    plt.grid(True)
    plt.ylabel('mm', fontsize=10)
    ax5.xaxis.set_major_formatter(monthsFmt)
    ax5.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2G'))

    ax6=fig.add_subplot(10,1,6, sharex=ax1)
    plt.setp(ax6.get_yticklabels(), fontsize=8)
    ax6.plot_date(DateInput, flx[18], '-', color = 'brown', label = flx_lbl[18])
    if sum(obs_catch_list) > 0:
            print '-------\nRMSE'
    if obs_catch_list[1] == 1:
        obs_SM = obs_catch.get('catch')['obs_SM']
        Sobs_m = np.ma.masked_values(obs_SM[0], cMF.hnoflo, atol = 0.09)
        ax6.plot_date(DateInput, Sobs_m, 'o', color = 'brown', markersize=2, label = r'$\theta obs$')
        a = np.array([obs_SM[0],flx[18].data])
        a = np.transpose(a)
        b = a[~(a < cMF.hnoflo +1000.0).any(1)]
        print 'SM: %.1f %%' % (100.0*rmse(b[:,0], b[:,1]))
    # x axis
    plt.xlim(DateInput[0]-1,DateInput[len(DateInput)-1]+1)
    # y axis
    plt.ylabel('%', fontsize=10)
    plt.legend(loc=0, labelspacing=lblspc, markerscale=mkscale)
    leg = plt.gca().get_legend()
    ltext  = leg.get_texts()
    plt.setp(ltext, fontsize=8 )
    if cMF == None:
        plt.setp(ax6.get_xticklabels(), fontsize=8)
        plt.xlabel('Date', fontsize=10)
        labels=ax6.get_xticklabels()
        plt.setp(labels, 'rotation', 90)
    else:
        plt.setp(ax6.get_xticklabels(), visible=False)
    plt.grid(True)
    ax6.xaxis.set_major_formatter(monthsFmt)
    ax6.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2G'))

    if cMF != None:
        # plot heads
        lines = itertools.cycle(['-','--','-.',':','.',',','o','v','^','<','>','1','2','3','4','s','p','*','h','H','+','x','D','d','|','_'])
        ax7=fig.add_subplot(10,1,7, sharex=ax1)
        plt.setp(ax7.get_xticklabels(), visible=False)
        plt.setp(ax7.get_yticklabels(), fontsize=8)
        i = 20
        for l in range(cMF.nlay):
            plt.plot_date(DateInput,flx[i],lines.next(), color = 'b', label = flx_lbl[i])
            i += l + 2
        if obs_catch_list[0] == 1:
            obs_h = obs_catch.get('catch')['obs_h']
            hobs_m = np.ma.masked_values(obs_h[0], cMF.hnoflo, atol = 0.09)
            ax7.plot_date(DateInput, hobs_m, 'o', color = 'blue', markersize=2, label = r'$hobs$')
            a = np.array([obs_h[0],flx[20].data])
            a = np.transpose(a)
            b = a[~(a < cMF.hnoflo +1000.0).any(1)]
            print 'h: %.2G m' % rmse(b[:,0], b[:,1])
        plt.xlim(DateInput[0]-1,DateInput[len(DateInput)-1]+1)
        plt.ylim(hmin,hmax)
        plt.ylabel('m', fontsize=10)
        plt.legend(loc=0, labelspacing=lblspc, markerscale=mkscale)
        leg = plt.gca().get_legend()
        ltext  = leg.get_texts()
        plt.setp(ltext, fontsize=8 )
        plt.grid(True)
        ax7.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2G'))
        ax7.xaxis.set_major_formatter(monthsFmt)
        # plot GW fluxes
        ax8=fig.add_subplot(10,1,8, sharex=ax1)
        plt.setp(ax8.get_xticklabels(), fontsize=8)
        plt.setp(ax8.get_yticklabels(), fontsize=8)
        i = 20 + 2*cMF.nlay
        for l, (e, lbl) in enumerate(zip(flx[i:], flx_lbl[i:])):
            plt.plot_date(DateInput,e,'-', color = mpl.colors.rgb2hex(np.random.rand(1,3)[0]), label = lbl)
            i += l + 2
        plt.xlim(DateInput[0]-1,DateInput[len(DateInput)-1]+1)
        labels=ax8.get_xticklabels()
        plt.setp(labels, 'rotation', 90)
        del labels
        plt.xlabel('Date', fontsize=10)
        plt.ylabel('mm', fontsize=10)
        plt.legend(loc=0, labelspacing=lblspc, markerscale=mkscale)
        leg = plt.gca().get_legend()
        ltext  = leg.get_texts()
        plt.setp(ltext, fontsize=8 )
        plt.grid(True)
        ax8.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2G'))
        ax8.xaxis.set_major_formatter(monthsFmt)
        # plot GWT
        lines = itertools.cycle(['-','--','-.',':','.',',','o','v','^','<','>','1','2','3','4','s','p','*','h','H','+','x','D','d','|','_'])
        ax10=fig.add_subplot(10,1,10, sharex=ax1)
        plt.setp(ax10.get_xticklabels(), visible=False)
        plt.setp(ax10.get_yticklabels(), fontsize=8)
        i = 21
        for l in range(cMF.nlay):
            plt.plot_date(DateInput,flx[i],lines.next(), color = 'b', label = flx_lbl[i])
            i += l + 2
        if obs_catch <> None:
            hobs_m = hobs_m - TopSoilAverage
            ax10.plot_date(DateInput, hobs_m, 'o', color = 'blue', markersize=2, label = r'$hobs$')
        plt.xlim(DateInput[0]-1,DateInput[len(DateInput)-1]+1)
        plt.ylabel('m', fontsize=10)
        plt.legend(loc=0, labelspacing=lblspc, markerscale=mkscale)
        leg = plt.gca().get_legend()
        ltext  = leg.get_texts()
        plt.setp(ltext, fontsize=8 )
        plt.grid(True)
        ax10.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2G'))
        ax10.xaxis.set_major_formatter(monthsFmt)

    plt.subplots_adjust(left=0.10, bottom=0.10, right=0.95, top=0.95, wspace=0.1, hspace=0.1)
    plt.savefig(plt_export_fn,dpi=150)
#    plt.show()
    plt.clf()
    plt.close('all')

##################

def plotLAYER(timesteps, Date, JD, ncol, nrow, nlay, nplot, V, cmap, CBlabel, msg, plt_title, MM_ws, interval_type = 'arange', interval_diff = 1, interval_num = 1, Vmax = 0, Vmin = 0, fmt = None, contours = False, ntick = 1, axisbg = 'silver', points  = None, mask = None, hnoflo = -999.9, animation = 0, pref_plt_title = '_sp_plt'):

    # TODO put option to select axes tick as row/col index from MODFLOW or real coordinates (in this last case create it)

    def MinMax(min_, max_, ctrs_):
        if max_ == min_:
            if max_ < 10E-9:
                max_ = 1.0
                min_ = -1.0
            else:
                max_ *= 1.15
                min_ *= 0.85
            ctrs_ = False
        else:
            ctrs_ = ctrs_
        return min_, max_, ctrs_

    # Store some arrays for plotting
    x = np.arange(0.5, ncol+1.5, 1)
    y = np.arange(0.5, nrow+1.5, 1)
    xg,yg = np.meshgrid(x,y)

    x = np.arange(1, ncol+1, 1)
    y = np.arange(1, nrow+1, 1)
    xg1,yg1 = np.meshgrid(x,y)

    ims = []
    files_tmp = []
    for i, day in enumerate(timesteps):
        ax= []
        fig = plt.figure(num=None, figsize=(11.7, 8.27), dpi=30)
        figtitle = fig.suptitle('')
        ims.append([])
        if isinstance(Date[i], float):
            figtitle.set_text(plt_title + '\nDay %s, DOY %s, time step %s' % (mpl.dates.num2date(Date[i]).isoformat()[:10], JD[i], day+1))
        else:
            figtitle.set_text(plt_title)
        plt.draw()
        for L in range(nplot):
            if mask == None:
                Vtmp = V[i,:,:,L]
            else:
                Vtmp = np.ma.masked_array(V[i,:,:,L], mask[:,:,L])
            Vtmp = np.ma.masked_values(Vtmp, hnoflo, atol = 0.09)
            Vmin_tmp, Vmax_tmp, ctrs_tmp = MinMax(Vmin[i], Vmax[i], contours)
            if fmt == None:
                if Vmax_tmp > 0.0999 or abs(Vmin_tmp)> 0.0999:
                    fmt = '%5.2f'
                else:
                    fmt = '%5.e'
            if interval_type == 'arange':
                ticks = np.arange(Vmin_tmp,Vmax_tmp,interval_diff)
            elif interval_type == 'linspace':
                ticks = np.linspace(Vmin_tmp,Vmax_tmp,interval_num)
            ax.append(fig.add_subplot(1,nlay,L+1, axisbg = axisbg))
            ax[L].xaxis.set_ticks(np.arange(0,ncol+1,ntick))
            ax[L].yaxis.set_ticks(np.arange(0,nrow+1,ntick))
            plt.setp(ax[L].get_xticklabels(), fontsize=8)
            plt.setp(ax[L].get_yticklabels(), fontsize=8)
            plt.ylabel('row i', fontsize=10)
            plt.xlabel('col j', fontsize=10)
            if points <> None:
                for k, (xj,yi,lay, label) in enumerate(zip(points[2],points[1],points[3],points[0])):
                    if lay == L:
                        color = 'dimgrey'
                    else:
                        color = 'lightgrey'
                    ax[L].plot(xj, yi, 'o', linewidth=1, markersize = 6, color = color)
                    ax[L].annotate(label, xy = (xj, yi))
            ims[i].append(ax[L].pcolormesh(xg, yg, Vtmp, cmap = cmap, vmin = Vmin_tmp, vmax = Vmax_tmp))
            if ctrs_tmp == True:
                CS = ax[L].contour(xg1, yg1[::-1], Vtmp[::-1], ticks, colors = 'gray')
                plt.draw()
                ax[L].clabel(CS, inline=1, fontsize = 6, fmt=fmt, colors = 'gray')
            if np.ma.max(Vtmp)>np.ma.min(Vtmp):
                ax[L].set_title('layer ' + str(L+1), fontsize = 10)
            else:
                ax[L].set_title('layer ' + str(L+1) + ' ' + msg, fontsize = 10)
            ax[L].set_ylim(bottom = np.max(yg1), top = np.min(yg1))
            ax[L].axis('scaled')
        if max(x) > max(y):
            cax = fig.add_axes([.125, 0.035, 0.75, 0.025])
            CBorient = 'horizontal'
        else:
            cax = fig.add_axes([0.035, 0.125, 0.025, 0.75])
            CBorient = 'vertical'
        CB = fig.colorbar(ims[i][0], extend='both', ticks = ticks, format = fmt, cax = cax,  orientation = CBorient)
        CB.set_label(CBlabel, fontsize = 12)
        if max(x) > max(y):
            cax.xaxis.set_label_position('top')
            plt.setp(CB.ax.get_xticklabels(), fontsize = 7)
        else:
            cax.yaxis.set_label_position('left')
            plt.setp(CB.ax.get_yticklabels(), fontsize = 7)
        if isinstance(Date[i], float):
            plt_export_fn = os.path.join(MM_ws, '%s_%s_timestep%05d.png' % (pref_plt_title, plt_title, day+1))
        else:
            plt_export_fn = os.path.join(MM_ws, '%s_%s.png' % (pref_plt_title, plt_title))
        plt.savefig(plt_export_fn)
        if len(timesteps)>1 and animation == 1:
            try:
                if i == 0:
                    files_tmp.append(os.path.join(MM_ws,'%05d.png'%(0)))
                    shutil.copyfile(plt_export_fn, files_tmp[0])
                    files_tmp.append(os.path.join(MM_ws,'%05d.png'%(1)))
                    shutil.copyfile(plt_export_fn, files_tmp[1])
                else:
                    files_tmp.append(os.path.join(MM_ws,'%05d.png'%(i+1)))
                    shutil.copyfile(plt_export_fn, files_tmp[i+1])
            except:
                pass
        for L in range(nplot):
            ax[L].cla()

    if len(timesteps)>1 and animation == 1:
        batch_fn = os.path.join(MM_ws, 'run.bat')
        f = open(batch_fn, 'w')
        f.write('ffmpeg -r 1 -i %s -s:v 1280x720 -c:v libx264 -profile:v high -crf 23 -pix_fmt yuv420p -r 30 -y %s_mov.mp4' % ('%s\%%%%05d.png' % (MM_ws),'%s\%s_%s' % (MM_ws, pref_plt_title, plt_title)))
        f.close()
        run_report_fn = os.path.join(MM_ws, '__FFmpegRunReport.txt')
        run_report = open(run_report_fn, 'w')
        sp.Popen(batch_fn, shell=False, stdout = run_report, stderr = run_report).wait()
        run_report.close()
        os.remove(batch_fn)
        try:
            for f in files_tmp:
                os.remove(f)
        except:
            pass
    plt.close('all')

##################

def plotWB(flxlst, flxlbl, colors_flx, plt_export_fn, plt_title, fluxmax, fluxmin, unit = 'na'):
    """
    Plot GW budget
    """

    def autolabel(rects, unit):
    # attach some text labels
        for rect in rects:
            y = rect.get_y()
            height = rect.get_height()
            if y>=0:
                ytext = height + 0.1
                va = 'bottom'
            else:
                ytext = -height - 0.1
                height = - height
                va = 'top'
            if unit == 'year':
                ax1.text(rect.get_x()+rect.get_width()/2., ytext, '%.1f'% float(height), ha='center', va=va)
            elif unit == 'day':
                ax1.text(rect.get_x()+rect.get_width()/2., ytext, '%G' %float(height), ha='center', va=va)
            else:
                ax1.text(rect.get_x()+rect.get_width()/2., ytext, '%G'%float(height), ha='center', va=va)

    ##################

    fig = plt.figure(num=None, figsize=(2*11.7, 2*8.27), dpi=30)
    fig.suptitle(plt_title)

    ax1=fig.add_subplot(2,1,1)
    plt.setp( ax1.get_xticklabels(), fontsize=10)
    plt.setp( ax1.get_yticklabels(), fontsize=10)
    x = np.arange(len(flxlst))
    width = 0.8
    flxlst1 = np.asarray(flxlst)
    flxlst1 = np.ma.masked_invalid(flxlst1)
    rects = plt.bar(x , flxlst1, color=colors_flx, linewidth=0.5, width=width, align = 'edge', label=flxlbl)
    # y axis
    if unit == 'day':
        plt.ylabel('mm/d', fontsize=10)
        UnitFmt = '%1.4f'
    elif unit == 'year':
        plt.ylabel('mm/y', fontsize=10)
        UnitFmt = '%1.1f'
    else:
        plt.ylabel('mm/?', fontsize=10)
    plt.grid(True)
    # fmt xaxis
    ax1.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter(UnitFmt))
    ax1.set_xticks(x+width/2)
    ax1.set_xticklabels(flxlbl)
    labels=ax1.get_xticklabels()
    plt.setp(labels, 'rotation', 90)
    autolabel(rects, unit)
    plt.xlim(0,len(flxlst))
    plt.ylim(fluxmin, fluxmax)
    ax1.axhline(0, color='black', lw=1)

    plt.subplots_adjust(left=0.05, bottom=0.10, right=0.95, top=0.95, wspace=0.1, hspace=0.1)
    plt.savefig(plt_export_fn,dpi=150)
#    plt.show()
    plt.clf()
    plt.close('all')

##################

#EOF#