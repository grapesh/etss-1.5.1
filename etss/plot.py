import csdlpy
import numpy as np
import matplotlib
matplotlib.use('Agg',warn=False)
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from datetime import datetime
from datetime import timedelta as dt
import matplotlib.dates as mdates

##==============================================================================
#def maxele (maxele, grid, coast, cities, trk, adv, pp, titleStr, plotFile):
#    
#    # Default plotting limits, based on advisory track, first position
#    lonlim = np.min(grid['lon']), np.max(grid['lon'])
#    latlim = np.min(grid['lat']), np.max(grid['lat'])
#    clim   = 0.,4.5
#    try:
#        lonlim = float(pp['Limits']['lonmin']),float(pp['Limits']['lonmax'])
#        latlim = float(pp['Limits']['latmin']),float(pp['Limits']['latmax'])
#        clim   = float(pp['Limits']['cmin']),  float(pp['Limits']['cmax'])
#    except: #default limits, in case if not specified in ini file
#        pass
#
#    f = csdlpy.plotter.plotMap(lonlim, latlim, fig_w=20., coast=coast)
#    csdlpy.plotter.addSurface (grid, maxele['value'],clim=clim)
#    plt.text (lonlim[0]+0.01, latlim[0]+0.01, titleStr )
#
#    if int(pp['General']['plotmax']) ==1:
#        # Find maximal maxele value within the coord limits
#        maxmax = np.max(maxele['value'][np.where( \
#                       (lonlim[0] <= maxele['lon']) & (maxele['lon'] <= lonlim[1]) & \
#                       (latlim[0] <= maxele['lat']) & (maxele['lat'] <= latlim[1]))])
#        lonmax = maxele['lon'][np.where(maxele['value']==maxmax)]
#        latmax = maxele['lat'][np.where(maxele['value']==maxmax)]
#        print '[info]: max maxele = ',str(maxmax),'at ',str(lonmax),'x',str(latmax)
#        
#    	maxStr = 'MAX VAL='+ str(np.round(maxmax,1)) + ' '
#    	try:
#            maxStr = maxStr + pp['General']['units'] +', '+ pp['General']['datum']
#	except:
#            pass # in case if there is a problem with pp
#        plt.text (lonlim[0]+0.01, latlim[1]-2., maxStr, fontsize='7')
#        plt.plot(lonmax, latmax, 'ow',markerfacecolor='k',markersize=8)
#        plt.plot(lonmax, latmax, 'ow',markerfacecolor='r',markersize=4)
#        plt.text (lonmax+0.05,latmax+0.05, str(np.round(maxmax,1)),color='k',fontsize=6)
#    
#    plt.text (lonlim[0]+0.01, latlim[1]+0.1,'NOAA / OCEAN SERVICE')   
#    if int(pp['Cities']['plot']) ==1:
#        csdlpy.plotter.plotCities (cities, lonlim, latlim, col='k', fs=6)
#    ax = plt.gca()
#    if int(pp['Storm']['plot'])  ==1:
#        print '[info]: plotting tracks'
#        csdlpy.atcf.plot.track(ax, adv, color='r',   linestyle=':',markersize=1,zorder=10,fs=1)
#        csdlpy.atcf.plot.track(ax, trk, color='gray',linestyle=':',markersize=1,zorder=10,fs=1)
#    
#    #TODO Address the case when lon/lat ticks are not integers
#    ticks  = ax.get_xticks()
#    print '[info]: Converting longitude labels from negative Westerlies to positive Easterlies'
#    labels = ax.get_xticklabels()
#    newlabels = []
#    n = -1
#    for label in labels:
#        n += 1
#        if ticks[n]>=0:
#            newTick = str( int(ticks[n]) ) + 'E'
#        elif ticks[n] <= -180:
#            newTick = str( int(ticks[n]) + 360) + 'E'
#        else:
#            newTick = str (-1*int(ticks[n])) + 'W' 
#        label.set_text( newTick )
#        newlabels.append( label )
#    ax.set_xticklabels( newlabels )
#
#    ticks  = ax.get_yticks()
#    print '[info]: Converting latitude labels from negative Northerlies to positive Southerlies'
#    labels = ax.get_yticklabels()
#    newlabels = []
#    n = -1
#    for label in labels:
#        n += 1
#        if ticks[n]>=0:
#            newTick = str( int(ticks[n]) ) + 'N'
#        else:
#            newTick = str (-1*int(ticks[n])) + 'S'
#        label.set_text( newTick )
#        newlabels.append( label )
#    ax.set_yticklabels( newlabels )
#
#    csdlpy.plotter.save(titleStr, plotFile)
#    plt.close(f) 

#==============================================================================
def stations (stations, pp, titleStr, plotPath, args):

    clim = -0.5,3.5 # meters!

    ft2meters = 1.0/3.28
    DATUM_K = ft2meters
    try:
        clim = float(pp['Stations']['cmin']),  float(pp['Stations']['cmax'])
    except:
        pass
    
    # Download master list
    masterListRemote = pp['Stations']['url']
    masterListLocal  = 'masterlist.csv'
    csdlpy.transfer.download(masterListRemote, masterListLocal)

    nStations = len(stations)
    print '[info]: Plotting ' + str(nStations) + ' point stations.'
 #    Read model output
    
    now   = datetime.utcnow()
    dates = (now-dt(days=2), now+dt(days=7))
 
    # Plot limits
    xlim =    max(dates[0],  stations[100]['time'][0] ),    \
              max(dates[-1], stations[100]['time'][-1])
    ylim = clim[0], clim[1]
    
    
    for n in range(nStations):
        
        if len(stations[n]['time']) > 2:
            
            fullStationName = stations[n]['nosid']
            print '[info]: working on ', fullStationName
            # Get datums        
            datums, floodlevels, nosid, stationTitle = \
                csdlpy.obs.parse.setDatumsFloodLevels (fullStationName, masterListLocal)            
            
            # Stage the plot with datums and floodlevels   
            fig, ax, ax2 = csdlpy.plotter.stageStationPlot (xlim, ylim, now, datums, floodlevels, zero='MLLW')
            plt.title(titleStr + ' @ ' + stationTitle, fontsize=9)

            # Get OBS
            obs   = csdlpy.obs.coops.getData(nosid, 
                            dates, product='waterlevelrawsixmin', datum='MLLW') 
            # Plot
            now_obs = np.nan
            try:
               ax.plot(obs['dates'], obs['values'],
                       color='lime',label='OBSERVED',  linewidth=4.0)

               peak_obs_val = np.nanmax(obs['values'])
               peak_obs_dat = obs['dates'][np.argmax(obs['values'])]
            
               if ylim[0] <= peak_obs_val and peak_obs_val <= ylim[1]:
                    
                   ax.plot(peak_obs_dat, peak_obs_val, 'o',
                            markerfacecolor='limegreen', markeredgecolor='k')
                   ax.plot([peak_obs_dat, peak_obs_dat],[ylim[0],peak_obs_val], 
                            '--',c='limegreen')
                   ax.text(peak_obs_dat, 1.06*peak_obs_val, 
                            str(np.round(peak_obs_val,1)) + "m (" + 
                               str(np.round(3.28084*peak_obs_val,1)) +"ft)",
                               color='forestgreen', fontsize=7, weight='bold')
                        
                        # Find offset
                   now_obs = obs['values'][obs['dates'].index(min(obs['dates'], \
                                      key=lambda x: abs(x - now)))]
            except:
                pass     

            ax.plot(stations[n]['time'], DATUM_K*np.array(stations[n]['htp']),      
                    color='c',label='ASTRON TIDE',linewidth=.5)
            ax.plot(stations[n]['time'], DATUM_K*np.array(stations[n]['cwl']),      
                    color='navy',label='STORM TIDE',linewidth=2.0)
            ax.plot(stations[n]['time'], DATUM_K*np.array(stations[n]['swl']),
                    color='m',label='STORM SURGE',linewidth=.5)
        
#            # Find model value closest to Now
#            mint = min(stations[n]['time'], key=lambda x: abs(x - now))        
#            now_mod_ind = np.where(stations[n]['time'] == mint)[0][0]
#            now_mod = stations[n]['cwl'][now_mod_ind]
#            offset  = now_obs  -  now_mod 
#            print '[debug]: offset=', str(offset)
#        
#            peak_val = np.nanmax(stations[n]['cwl'])
#            peak_dat = stations[n]['time'][np.argmax(stations[n]['cwl'])]
#        
#            # Plot peak forecast value
#            ax.text(peak_dat, 1.05*peak_val, 
#                str(np.round(peak_val,1)) + "m (" +
#                str(np.round(3.28084*peak_val,1)) +"ft)", color='navy',fontsize=7)
#            ax.plot([peak_dat, peak_dat], [ylim[0], peak_val], '--',color='navy')
#            peak_str = str(peak_dat.hour).zfill(2) + ':' + str(peak_dat.minute).zfill(2) + 'z'
#            ax.text(peak_dat+dt(hours=0.5), ylim[0], peak_str ,color='navy', fontsize=7)            
#            ax.plot(peak_dat, peak_val, 'o',markeredgecolor='navy',markerfacecolor='b')
#
#            # Plot offset forecast
#            #ax.plot(cwl['time'][now_mod_ind:], offset + cwl['zeta'][now_mod_ind:,n],      
#                     #        color='gray', linestyle=':', linewidth=.5)
#        
#            # offset value
#            if ylim[0] <= 0.5*(now_mod+now_obs) and 0.5*(now_mod+now_obs) <= ylim[1]:
#                ax.text(stations[n]['time'][now_mod_ind]+dt(hours=1), 0.5*(now_mod+now_obs), 
#                        r'$\Delta$='+str(np.round(offset,2)) + 'm', color='gray',
#                                        fontsize=7, fontstyle='italic', fontweight='bold')
#
#            # add offseted peak forecast value
#            if ylim[0] <= peak_val+offset and peak_val+offset <= ylim[1]:
#                ax.plot(peak_dat, peak_val+offset, marker='+',
#                    markeredgecolor='gray', markerfacecolor='gray', markersize=5)
#                ax.text(peak_dat, 1.05*(peak_val+offset), 
#                        str(np.round(peak_val+offset,1)) + "m (" + 
#                        str(np.round(3.28084*(peak_val+offset),1)) +"ft)", color='gray',
#                        fontstyle='italic', fontsize=6)

            ax.legend(bbox_to_anchor=(0.8, 1.001, 0.17, 0.07), loc=3, 
                  ncol=2, mode="expand", borderaxespad=0., fontsize=7)

            ax.text(xlim[0],ylim[1]+0.05,'NOAA / MDL')
            ax.set_ylabel ('WATER LEVELS, meters MLLW')
            ax2.set_ylabel('WATER LEVELS, feet MLLW')
            ax.set_xlabel('DATE/TIME UTC')
            ax.grid(True,which='both')   
        
            ax.xaxis.set_major_locator(mdates.DayLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %m/%d\n00:00'))
            ax.xaxis.set_minor_locator(MultipleLocator(0.5))
        
            ax.set_xlim (        xlim)
            ax.set_ylim (        ylim)
            ax2.set_ylim(3.28084*ylim[0], 3.28084*ylim[1])
            ax2.plot([],[])

            plt.tight_layout()
            figFile = plotPath + stations[n]['nosid'] + '.png'
            plt.savefig(figFile)
            plt.close()
            csdlpy.transfer.upload(figFile, args.ftpLogin, args.ftpPath)
        
    csdlpy.transfer.cleanup()
        
