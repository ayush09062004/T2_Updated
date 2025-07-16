import numpy as np
import mozaik
import matplotlib.pyplot as plt
from mozaik.visualization.plotting import *
from mozaik.analysis.technical import NeuronAnnotationsToPerNeuronValues
from mozaik.analysis.analysis import *
from mozaik.analysis.TrialAveragedFiringRateCutout import TrialAveragedFiringRateCutout
from mozaik.analysis.vision import *
from mozaik.storage.queries import *
from mozaik.storage.datastore import PickledDataStore
from mozaik.tools.circ_stat import circular_dist
from mozaik.controller import Global

# import sys
# sys.path.append('/home/antolikjan/dev/pkg/mozaik/mozaik/contrib')
# import Kremkow_plots
# from Kremkow_plots import *


logger = mozaik.getMozaikLogger()

import time

def perform_analysis_test( data_store ):
    dsv = param_filter_query( data_store, st_name='InternalStimulus', sheet_name=['X_ON','X_OFF'] )  
    # TrialAveragedFiringRateCutout( dsv, ParameterSet({}) ).analyse(start=100, end=1000)
    # data_store.print_content(full_recordings=True)

    # dsv = param_filter_query( data_store, st_name='InternalStimulus', sheet_name=['X_ON','X_OFF'],analysis_algorithm='TrialAveragedFiringRateCutout')  
    # dsv.print_content(full_ADS=True)


    # PerNeuronValuePlot(dsv,ParameterSet({"cortical_view":True}), plot_file_name='test_LGN.png').plot()

    # dsv = param_filter_query( data_store, st_name='InternalStimulus', sheet_name=['PGN'] )  
    # TrialAveragedFiringRateCutout( dsv, ParameterSet({}) ).analyse(start=100, end=1000)
    # dsv = param_filter_query( data_store, st_name='InternalStimulus', sheet_name=['PGN'],analysis_algorithm='TrialAveragedFiringRateCutout')  

    # PerNeuronValuePlot(dsv,ParameterSet({"cortical_view":True}), plot_file_name='test_PGN.png').plot()
    
# analog_Xon_ids:  [2912]
# analog_Xoff_ids:  [10921]
# spike_Xon_ids:  [398, 1144, 1454, 1867, 2248, 2731, 2912, 3084, 3205, 3754, 4348, 4774]
# spike_Xoff_ids:  [9855, 9924, 10024, 10621, 10921, 11110, 11538, 11648, 12238, 12738, 13277, 13530, 13851, 14157, 14159]
# analog_PGN_ids:  [39836, 40359]
# spike_PGN_ids:  [39587, 39700, 39836, 40189, 40359]
# analog_ids:  [43039]
# spike_ids:  [42554, 43039, 44519, 44984, 47454, 47630, 48105, 50330, 50603, 50665, 51862, 51957, 52009, 52015]

def select_ids_by_radius(position, radius, sheet_ids, positions, show=True):
    radius_ids = []
    min_radius = radius[0] # over: 0. # non: 1.
    max_radius = radius[1] # over: .7 # non: 3.
    if show:
        print(min_radius, max_radius)
    for i in sheet_ids:
        a = np.array((positions[0][i],positions[1][i],positions[2][i]))
        if show:
            print("supplied:",positions[0][i],positions[1][i],positions[2][i])
        l = np.linalg.norm(a - position)
        if l>min_radius and l<max_radius:
            radius_ids.append([i][0])
            if show:
                print("chosen:",positions[0][i],positions[1][i],positions[2][i])            
    return radius_ids


def perform_analysis_and_visualization( data_store, atype='contrast', withPGN=False, withV1=False ):
    perform_analysis_and_visualization_radius( data_store, atype=atype, position=[[0.0],[0.0],[0.0]], radius=[0.0,0.5], withPGN=withPGN, withV1=withV1 )

def perform_analysis_and_visualization_radius( data_store, atype='contrast', position=[[0.0],[0.0],[0.0]], radius=[], withPGN=False, withV1=False ):
    label = "_"+str(position[0][0])+"_"
    analog_Xon_ids = []
    analog_Xoff_ids = []
    # Gather indexes
    analog_Xon_ids = sorted( param_filter_query(data_store,sheet_name="X_ON").get_segments()[0].get_stored_vm_ids() )
    analog_Xoff_ids = sorted( param_filter_query(data_store,sheet_name="X_OFF").get_segments()[0].get_stored_vm_ids() )
    spike_Xon_ids = param_filter_query(data_store,sheet_name="X_ON").get_segments()[0].get_stored_spike_train_ids()
    spike_Xoff_ids = param_filter_query(data_store,sheet_name="X_OFF").get_segments()[0].get_stored_spike_train_ids()
    print("analog_Xon_ids: ",analog_Xon_ids)
    print("analog_Xoff_ids: ",analog_Xoff_ids)
    print("spike_Xon_ids: ",spike_Xon_ids)
    print("spike_Xoff_ids: ",spike_Xoff_ids)

    # RADIUS-DEPENDENT INDEXES
    # we want to have only the spike_Xon_ids that lie outside of the excitatory zone overlapping with the cortical one
    position_Xon = data_store.get_neuron_positions()['X_ON']
    position_Xoff = data_store.get_neuron_positions()['X_OFF']
    Xon_sheet_ids = data_store.get_sheet_indexes(sheet_name='X_ON',neuron_ids=spike_Xon_ids)
    Xoff_sheet_ids = data_store.get_sheet_indexes(sheet_name='X_OFF',neuron_ids=spike_Xoff_ids)
    radius_Xon_ids = select_ids_by_radius(position, radius, Xon_sheet_ids, position_Xon)
    radius_Xoff_ids = select_ids_by_radius(position, radius, Xoff_sheet_ids, position_Xoff)
    radius_Xon_ids = data_store.get_sheet_ids(sheet_name='X_ON',indexes=radius_Xon_ids)
    radius_Xoff_ids = data_store.get_sheet_ids(sheet_name='X_OFF',indexes=radius_Xoff_ids)
    print("radius_Xon_ids: ",radius_Xon_ids)
    print("radius_Xoff_ids: ",radius_Xoff_ids)
    if len(analog_Xon_ids)<1:
        analog_Xon_ids = radius_Xon_ids
    if len(analog_Xoff_ids)<1:
        analog_Xoff_ids = radius_Xoff_ids


    analog_PGN_ids = []
    spike_PGN_ids = []
    if withPGN:
        analog_PGN_ids = sorted( param_filter_query(data_store,sheet_name="PGN").get_segments()[0].get_stored_vm_ids() )
        print("analog_PGN_ids: ",analog_PGN_ids)
        spike_PGN_ids = param_filter_query(data_store,sheet_name="PGN").get_segments()[0].get_stored_spike_train_ids()
        position_PGN = data_store.get_neuron_positions()['PGN']
        PGN_sheet_ids = data_store.get_sheet_indexes(sheet_name='PGN',neuron_ids=spike_PGN_ids)
        radius_PGN_ids = select_ids_by_radius(position, radius, PGN_sheet_ids, position_PGN)
        radius_PGN_ids = data_store.get_sheet_ids(sheet_name='PGN',indexes=radius_PGN_ids)
        print("radius_Xon_ids: ",radius_PGN_ids)
        spike_PGN_ids = radius_PGN_ids
        print("spike_PGN_ids: ",spike_PGN_ids)
        if len(analog_PGN_ids)<1:
            analog_PGN_ids = spike_PGN_ids

    analog_ids = []
    spike_ids = []
    if withV1:        
        analog_ids = sorted( param_filter_query(data_store,sheet_name="V1_Exc_L4").get_segments()[0].get_stored_vm_ids() )
        spike_ids = param_filter_query(data_store,sheet_name="V1_Exc_L4").get_segments()[0].get_stored_spike_train_ids()

        NeuronAnnotationsToPerNeuronValues(data_store,ParameterSet({})).analyse()
        l4_exc_or = data_store.get_analysis_result(identifier='PerNeuronValue',value_name = 'LGNAfferentOrientation', sheet_name = 'V1_Exc_L4')[0]
        l4_exc_or_many = np.array(spike_ids)[np.nonzero(np.array([circular_dist(l4_exc_or.get_value_by_id(i),0,np.pi)  for i in spike_ids]) < 0.1)[0]]
        spike_ids = l4_exc_or_many

        position_V1 = data_store.get_neuron_positions()['V1_Exc_L4']
        V1_sheet_ids = data_store.get_sheet_indexes(sheet_name='V1_Exc_L4',neuron_ids=l4_exc_or_many)
        print ("# of V1 cells within radius range having orientation close to 0:", len(V1_sheet_ids))
        radius_V1_ids = select_ids_by_radius(position, radius, V1_sheet_ids, position_V1)
        radius_V1_ids = data_store.get_sheet_ids(sheet_name='V1_Exc_L4',indexes=radius_V1_ids)
        spike_ids = radius_V1_ids
        if len(analog_ids)<1:
            analog_ids = spike_ids
        print("analog_ids: ",analog_ids)
        print("spike_ids: ",spike_ids)



    ##############
    # ANALYSES
    if atype == 'luminance':
        perform_analysis_luminance( data_store, withPGN, withV1 )

    if atype in ['contrast', 'spatial_frequency', 'temporal_frequency', 'orientation']:
        perform_analysis_full_field( data_store, withPGN, withV1 )

    if atype in ['xcorr']:
        perform_analysis_xcorr( data_store, withPGN, withV1, radius_Xon_ids, radius_Xoff_ids, spike_ids )

    if atype in ['feedforward']:
        perform_analysis_feedforward( data_store, spike_ids )

    if atype == 'size' or atype == 'size_radius':
        perform_analysis_size( data_store, withPGN, withV1 )

    if atype == 'subcortical_conn':
        perform_analysis_and_visualization_subcortical_conn(data_store, withV1, spike_Xon_ids, spike_Xoff_ids, spike_PGN_ids, analog_ids)

    if atype == 'cortical_or_conn':
        perform_analysis_and_visualization_cortical_or_conn( data_store )

    if atype == 'cortical_map':
        dsv_map = param_filter_query(data_store, sheet_name=['V1_Exc_L4'], value_name='LGNAfferentOrientation')   
        # dsv_map.print_content(full_ADS=True)
        PerNeuronValuePlot( 
            dsv_map, 
            ParameterSet({'cortical_view' : True}),
            plot_file_name='Map.png'
        ).plot({'*.colorbar' : True})


    ##############
    # PLOTTING
    activity_plot_param =    {
           'frame_rate' : 5,  
           'bin_width' : 5.0, 
           'scatter' :  True,
           'resolution' : 0
    }

    # Tuning
    if atype == 'luminance':
        plot_luminance_tuning( data_store, spike_Xon_ids, spike_Xoff_ids, spike_PGN_ids, spike_ids)

    if atype == 'contrast':
        plot_contrast_tuning( data_store, spike_Xon_ids, spike_Xoff_ids, spike_PGN_ids, spike_ids)

    if atype == 'size':
        plot_size_tuning( data_store, spike_Xon_ids, spike_Xoff_ids, spike_PGN_ids, spike_ids )
    if atype == 'size_radius':
        plot_size_tuning( data_store, radius_Xon_ids, radius_Xoff_ids, spike_PGN_ids, spike_ids, radius )

    if atype == 'spatial_frequency':
        plot_spatial_frequency_tuning( data_store, spike_Xon_ids, spike_Xoff_ids, spike_PGN_ids, spike_ids)

    if atype == 'temporal_frequency':
        plot_temporal_frequency_tuning( data_store, spike_Xon_ids, spike_Xoff_ids, spike_PGN_ids, spike_ids)

    if atype == 'orientation':
        plot_orientation_tuning( data_store, spike_Xon_ids, spike_Xoff_ids, spike_PGN_ids, spike_ids)

    if atype == 'xcorr':
        plot_xcorr( data_store, label, radius_Xon_ids, radius_Xoff_ids, spike_PGN_ids, spike_ids)

    # Overview
    # plot_overview( data_store, analog_Xon_ids, analog_Xoff_ids, analog_PGN_ids, analog_ids, radius )
    # plot_overview( data_store, [], [], [], analog_ids, radius )


#########################################################################################
#########################################################################################
#########################################################################################




def perform_analysis_and_visualization_subcortical_conn(data_store, withV1, Xon_ids, Xoff_ids, PGN_ids=None, V1_ids=None):
    # LGN ON
    for i in Xon_ids:
        if not withV1:
            # LGN On -> PGN: 'LGN_PGN_ConnectionOn'
            ConnectivityPlot(
                data_store,
                ParameterSet({
                    'neuron': i,  # the target neuron whose connections are to be displayed
                    'reversed': False,  # False: outgoing connections from the given neuron are shown. True: incoming connections are shown
                    'sheet_name': 'X_ON',  # for neuron in which sheet to display connectivity
                }),
                # pnv_dsv=data_store,
                fig_param={'dpi':100, 'figsize': (10,12)},
                plot_file_name='LGN_On_'+str(i)+'_outgoing.png'
            ).plot({
                '*.line':True,
            })
            # PGN -> LGN On: 'PGN_LGN_ConnectionOn'
        ConnectivityPlot(
            data_store,
            ParameterSet({
                'neuron': i,  # the target neuron whose connections are to be displayed
                'reversed': True,  # False: outgoing connections from the given neuron are shown. True: incoming connections are shown
                'sheet_name': 'X_ON',  # for neuron in which sheet to display connectivity
            }),
            fig_param={'dpi':100, 'figsize': (10,12)},
            plot_file_name='LGN_On_'+str(i)+'_incoming.png'
        ).plot()    
    # LGN OFF
    for i in Xoff_ids:
        # LGN Off -> : ex 'LGN_PGN_ConnectionOff'
        if not withV1:
            ConnectivityPlot(
                data_store,
                ParameterSet({
                    'neuron': i,  # the target neuron whose connections are to be displayed
                    'reversed': False,  # False: outgoing connections from the given neuron are shown. True: incoming connections are shown
                    'sheet_name': 'X_OFF',  # for neuron in which sheet to display connectivity
                }),
                fig_param={'dpi':100, 'figsize': (10,12)},
                plot_file_name=f'LGN_On_{i}_outgoing.png'
            ).plot()    
        #  -> LGN Off: ex 'PGN_LGN_ConnectionOff'
        ConnectivityPlot(
            data_store,
            ParameterSet({
                'neuron': i,  # the target neuron whose connections are to be displayed
                'reversed': True,  # False: outgoing connections from the given neuron are shown. True: incoming connections are shown
                'sheet_name': 'X_OFF',  # for neuron in which sheet to display connectivity
            }),
            fig_param={'dpi':100, 'figsize': (10,12)},
            plot_file_name=f'LGN_Off_{i}_incoming.png'
        ).plot()
    # PGN
    for i in PGN_ids:
        # PGN lateral: 'PGN_PGN_Connection'
        if not withV1:
            ConnectivityPlot(
                data_store,
                ParameterSet({
                    'neuron': i,  # the target neuron whose connections are to be displayed
                    'reversed': False,  # False: outgoing connections from the given neuron are shown. True: incoming connections are shown
                    'sheet_name': 'PGN',  # for neuron in which sheet to display connectivity
                }),
                fig_param={'dpi':100, 'figsize': (24,12)},
                #plot_file_name='PGN_'+str(i)+'_outgoing.png'
                plot_file_name=f'PGN_{i}_outgoing.png'
            ).plot()    
        ConnectivityPlot(
            data_store,
            ParameterSet({
                'neuron': i,  # the target neuron whose connections are to be displayed
                'reversed': True,  # False: outgoing connections from the given neuron are shown. True: incoming connections are shown
                'sheet_name': 'PGN',  # for neuron in which sheet to display connectivity
            }),
            fig_param={'dpi':100, 'figsize': (24,12)},
            #plot_file_name='PGN_'+str(i)+'_incoming.png'
            plot_file_name=f'PGN_{i}_incoming.png'
        ).plot()    
    # V1
    for i in V1_ids:
        # Cx ->
        ConnectivityPlot(
            data_store,
            ParameterSet({
                'neuron': i,  # the target neuron whose connections are to be displayed
                'reversed': False,  # False: outgoing connections from the given neuron are shown. True: incoming connections are shown
                'sheet_name': 'V1_Exc_L4',  # for neuron in which sheet to display connectivity
            }),
            fig_param={'dpi':100, 'figsize': (24,12)},
            #plot_file_name='V1_'+str(i)+'_outgoing.png'
            plot_file_name=f'V1_{i}_outgoing.png'
        ).plot()   
        # -> Cx 
        # ConnectivityPlot(
        #     data_store,
        #     ParameterSet({
        #         'neuron': i,  # the target neuron whose connections are to be displayed
        #         'reversed': True,  # False: outgoing connections from the given neuron are shown. True: incoming connections are shown
        #         'sheet_name': 'V1_Exc_L4',  # for neuron in which sheet to display connectivity
        #     }),
        #     fig_param={'dpi':100, 'figsize': (24,12)},
        #     plot_file_name='V1_'+str(i)+'_incoming.png'
        # ).plot()    



def perform_analysis_and_visualization_cortical_or_conn(data_store):
    analog_ids = sorted( param_filter_query(data_store,sheet_name="V1_Exc_L4").get_segments()[0].get_stored_vm_ids() )
    spike_ids = param_filter_query(data_store,sheet_name="V1_Exc_L4").get_segments()[0].get_stored_spike_train_ids()
    print("analog_ids: ",analog_ids)
    print("spike_ids: ",spike_ids)

    NeuronAnnotationsToPerNeuronValues( data_store, ParameterSet({}) ).analyse()
    l4_exc_or = data_store.get_analysis_result(identifier='PerNeuronValue', value_name='LGNAfferentOrientation', sheet_name='V1_Exc_L4')[0]

    l4_exc_or_many = np.array(spike_ids)[np.nonzero(np.array([circular_dist(l4_exc_or.get_value_by_id(i),0,np.pi)  for i in spike_ids]) < 0.1)[0]]

    dsv = param_filter_query(data_store,identifier='PerNeuronValue',value_name = 'LGNAfferentOrientation')
    mozaik.visualization.plotting.ConnectivityPlot(data_store,ParameterSet({'neuron' : l4_exc_or_many[0], 'reversed' : True,'sheet_name' : 'V1_Exc_L4'}),pnv_dsv=dsv,fig_param={'dpi' : 100,'figsize': (34,12)},plot_file_name='ExcConnections1.png').plot()
    mozaik.visualization.plotting.ConnectivityPlot(data_store,ParameterSet({'neuron' : l4_exc_or_many[1], 'reversed' : True,'sheet_name' : 'V1_Exc_L4'}),pnv_dsv=dsv,fig_param={'dpi' : 100,'figsize': (34,12)},plot_file_name='ExcConnections2.png').plot()
    mozaik.visualization.plotting.ConnectivityPlot(data_store,ParameterSet({'neuron' : l4_exc_or_many[2], 'reversed' : True,'sheet_name' : 'V1_Exc_L4'}),pnv_dsv=dsv,fig_param={'dpi' : 100,'figsize': (34,12)},plot_file_name='ExcConnections3.png').plot()
    mozaik.visualization.plotting.ConnectivityPlot(data_store,ParameterSet({'neuron' : l4_exc_or_many[3], 'reversed' : True,'sheet_name' : 'V1_Exc_L4'}),pnv_dsv=dsv,fig_param={'dpi' : 100,'figsize': (34,12)},plot_file_name='ExcConnections4.png').plot()
    mozaik.visualization.plotting.ConnectivityPlot(data_store,ParameterSet({'neuron' : l4_exc_or_many[4], 'reversed' : True,'sheet_name' : 'V1_Exc_L4'}),pnv_dsv=dsv,fig_param={'dpi' : 100,'figsize': (34,12)},plot_file_name='ExcConnections5.png').plot()
    


def perform_analysis_luminance( data_store, withPGN=False, withV1=False ):
    dsv0_Xon = param_filter_query( data_store, st_name='Null', sheet_name='X_ON' )  
    # TrialAveragedFiringRate( dsv0_Xon, ParameterSet({}) ).analyse()
    TrialAveragedFiringRateCutout( dsv0_Xon, ParameterSet({}) ).analyse(start=100, end=2000)
    dsv0_Xoff = param_filter_query( data_store, st_name='Null', sheet_name='X_OFF' )  
    # TrialAveragedFiringRate( dsv0_Xoff, ParameterSet({}) ).analyse()
    TrialAveragedFiringRateCutout( dsv0_Xoff, ParameterSet({}) ).analyse(start=100, end=2000)

    if withPGN:
        dsv0_PGN = param_filter_query( data_store, st_name='Null', sheet_name='PGN' )  
        # TrialAveragedFiringRate( dsv0_PGN, ParameterSet({}) ).analyse()
        TrialAveragedFiringRateCutout( dsv0_PGN, ParameterSet({}) ).analyse(start=100, end=2000)
    if withV1:
        dsv0_V1e = param_filter_query( data_store, st_name='Null', sheet_name='V1_Exc_L4' )  
        # TrialAveragedFiringRate( dsv0_V1e, ParameterSet({}) ).analyse()
        TrialAveragedFiringRateCutout( dsv0_V1e, ParameterSet({}) ).analyse(start=100, end=2000)



def perform_analysis_full_field( data_store, withPGN=False, withV1=False ):
    # dsv = param_filter_query( data_store, st_name='FullfieldDriftingSinusoidalGrating',st_temporal_frequency=0.05, sheet_name='X_ON' )  
    # print dsv.get_segments()[0].spiketrains[0]
    # print dsv.get_segments()[0].spiketrains[0].t_start
    # print dsv.get_segments()[0].spiketrains[0].t_stop
    # dsv = param_filter_query( data_store, st_name='FullfieldDriftingSinusoidalGrating',st_temporal_frequency=8.0, sheet_name='X_ON' )  
    # print dsv.get_segments()[0].spiketrains[0]

    dsv10 = param_filter_query( data_store, st_name='FullfieldDriftingSinusoidalGrating', sheet_name='X_ON' )  
    # TrialAveragedFiringRate( dsv10, ParameterSet({}) ).analyse()
    TrialAveragedFiringRateCutout( dsv10, ParameterSet({}) ).analyse(start=100, end=10000)
    dsv11 = param_filter_query( data_store, st_name='FullfieldDriftingSinusoidalGrating', sheet_name='X_OFF' )  
    # TrialAveragedFiringRate( dsv11, ParameterSet({}) ).analyse()
    TrialAveragedFiringRateCutout( dsv11, ParameterSet({}) ).analyse(start=100, end=10000)
    if withPGN:
        dsv12 = param_filter_query( data_store, st_name='FullfieldDriftingSinusoidalGrating', sheet_name='PGN' )  
        # TrialAveragedFiringRate( dsv12, ParameterSet({}) ).analyse()
        TrialAveragedFiringRateCutout( dsv12, ParameterSet({}) ).analyse(start=100, end=10000)
    if withV1:
        dsv1_V1e = param_filter_query( data_store, st_name='FullfieldDriftingSinusoidalGrating', sheet_name='V1_Exc_L4' )  
        # TrialAveragedFiringRate( dsv1_V1e, ParameterSet({}) ).analyse()
        TrialAveragedFiringRateCutout( dsv1_V1e, ParameterSet({}) ).analyse(start=100, end=10000)
        # dsv1_V1i = param_filter_query( data_store, st_name='FullfieldDriftingSinusoidalGrating', sheet_name='V1_Inh_L4' )  
        # TrialAveragedFiringRate( dsv1_V1i, ParameterSet({}) ).analyse()
        # NeuronAnnotationsToPerNeuronValues(data_store,ParameterSet({})).analyse()



def perform_analysis_xcorr( data_store, withPGN=False, withV1=False, analog_Xon_ids=None, analog_Xoff_ids=None, analog_ids=None):
    # data_store.print_content(full_ADS=True)
    # print "get_sensory_stimulus:", data_store.get_sensory_stimulus()
    # RetinalInputMovie( data_store, ParameterSet({}), plot_file_name="XCorr",frame_duration=100).plot({'*.fontsize':7})
    analog_Xon_ids = [] if analog_Xon_ids is None else analog_Xon_ids
    analog_Xoff_ids = [] if analog_Xoff_ids is None else analog_Xoff_ids
    analog_ids = [] if analog_ids is None else analog_ids
    PSTH( param_filter_query(data_store,sheet_name='X_ON',st_name="FlashingSquares"), ParameterSet({'bin_length' : 2.0 }) ).analyse()
    PSTH( param_filter_query(data_store,sheet_name='X_OFF',st_name="FlashingSquares"), ParameterSet({'bin_length' : 2.0 }) ).analyse()
    PSTH( param_filter_query(data_store,sheet_name='X_ON',st_name="FlashingSquares"), ParameterSet({'bin_length' : 2.0 }) ).analyse()
    PSTH( param_filter_query(data_store,sheet_name='X_OFF',st_name="FlashingSquares"), ParameterSet({'bin_length' : 2.0 }) ).analyse()
    if withPGN:
        PSTH( param_filter_query(data_store,sheet_name='PGN',st_name="FlashingSquares"), ParameterSet({'bin_length' : 2.0 }) ).analyse()
    if withV1:
        PSTH( param_filter_query(data_store,sheet_name='V1_Exc_L4',st_name="FlashingSquares"), ParameterSet({'bin_length' : 2.0 }) ).analyse()

    PSTH( param_filter_query(data_store,sheet_name='X_ON',st_name="FullfieldDriftingSquareGrating"), ParameterSet({'bin_length' : 2.0 }) ).analyse()
    PSTH( param_filter_query(data_store,sheet_name='X_OFF',st_name="FullfieldDriftingSquareGrating"), ParameterSet({'bin_length' : 2.0 }) ).analyse()
    PSTH( param_filter_query(data_store,sheet_name='X_ON',st_name="FullfieldDriftingSquareGrating"), ParameterSet({'bin_length' : 2.0 }) ).analyse()
    PSTH( param_filter_query(data_store,sheet_name='X_OFF',st_name="FullfieldDriftingSquareGrating"), ParameterSet({'bin_length' : 2.0 }) ).analyse()
    if withPGN:
        PSTH( param_filter_query(data_store,sheet_name='PGN',st_name="FullfieldDriftingSquareGrating"), ParameterSet({'bin_length' : 2.0 }) ).analyse()
    if withV1:
        PSTH( param_filter_query(data_store,sheet_name='V1_Exc_L4',st_name="FullfieldDriftingSquareGrating"), ParameterSet({'bin_length' : 2.0 }) ).analyse()


    # TrialAveragedCorrectedCrossCorrelation( 
    #     param_filter_query(data_store,sheet_name='X_ON',st_name="FlashingSquares"), 
    #     ParameterSet({'bins':35,'bin_length':5.0,'neurons1':analog_Xon_ids,'size':0.1}) 
    # ).analyse()


    # TrialToTrialCrossCorrelationOfAnalogSignalList( param_filter_query(data_store,sheet_name='X_ON',st_name="FullfieldDriftingSquareGrating",analysis_algorithm='PSTH'), ParameterSet({'neurons' : list(analog_Xon_ids)})).analyse()
    # TrialToTrialCrossCorrelationOfAnalogSignalList( param_filter_query(data_store,sheet_name='X_OFF',st_name="FullfieldDriftingSquareGrating",analysis_algorithm='PSTH'), ParameterSet({'neurons' : list(analog_Xoff_ids)})).analyse()
    # TrialToTrialCrossCorrelationOfAnalogSignalList( param_filter_query(data_store,sheet_name='V1_Exc_L4',st_name="FullfieldDriftingSquareGrating",analysis_algorithm='PSTH'), ParameterSet({'neurons' : list(analog_ids)})).analyse()
    # TrialToTrialCrossCorrelationOfAnalogSignalList( param_filter_query(data_store,sheet_name='X_ON',st_name="FlashingSquares",analysis_algorithm='PSTH'), ParameterSet({'neurons' : list(analog_Xon_ids)})).analyse()
    # TrialToTrialCrossCorrelationOfAnalogSignalList( param_filter_query(data_store,sheet_name='X_OFF',st_name="FlashingSquares",analysis_algorithm='PSTH'), ParameterSet({'neurons' : list(analog_Xoff_ids)})).analyse()
    # TrialToTrialCrossCorrelationOfAnalogSignalList( param_filter_query(data_store,sheet_name='V1_Exc_L4',st_name="FlashingSquares",analysis_algorithm='PSTH'), ParameterSet({'neurons' : list(analog_ids)})).analyse()

    # # FullfieldDriftingSquareGrating
    # dsv10 = param_filter_query( data_store, st_name='FullfieldDriftingSquareGrating', sheet_name='X_ON' )  
    # # TrialAveragedFiringRate( dsv10, ParameterSet({}) ).analyse()
    # TrialAveragedFiringRateCutout( dsv10, ParameterSet({}) ).analyse(start=10, end=10000)
    # dsv11 = param_filter_query( data_store, st_name='FullfieldDriftingSquareGrating', sheet_name='X_OFF' )  
    # # TrialAveragedFiringRate( dsv11, ParameterSet({}) ).analyse()
    # TrialAveragedFiringRateCutout( dsv11, ParameterSet({}) ).analyse(start=10, end=10000)
    # if withPGN:
    #     dsv12 = param_filter_query( data_store, st_name='FullfieldDriftingSquareGrating', sheet_name='PGN' )  
    #     # TrialAveragedFiringRate( dsv12, ParameterSet({}) ).analyse()
    #     TrialAveragedFiringRateCutout( dsv12, ParameterSet({}) ).analyse(start=10, end=10000)
    # if withV1:
    #     dsv1_V1e = param_filter_query( data_store, st_name='FullfieldDriftingSquareGrating', sheet_name='V1_Exc_L4' )  
    #     # TrialAveragedFiringRate( dsv1_V1e, ParameterSet({}) ).analyse()
    #     TrialAveragedFiringRateCutout( dsv1_V1e, ParameterSet({}) ).analyse(start=100, end=10000)

    # # FlashingSquares
    # dsv10 = param_filter_query( data_store, st_name='FlashingSquares', sheet_name='X_ON' )  
    # # TrialAveragedFiringRate( dsv10, ParameterSet({}) ).analyse()
    # TrialAveragedFiringRateCutout( dsv10, ParameterSet({}) ).analyse(start=10, end=10000)
    # dsv11 = param_filter_query( data_store, st_name='FlashingSquares', sheet_name='X_OFF' )  
    # # TrialAveragedFiringRate( dsv11, ParameterSet({}) ).analyse()
    # TrialAveragedFiringRateCutout( dsv11, ParameterSet({}) ).analyse(start=10, end=10000)
    # if withPGN:
    #     dsv12 = param_filter_query( data_store, st_name='FlashingSquares', sheet_name='PGN' )  
    #     # TrialAveragedFiringRate( dsv12, ParameterSet({}) ).analyse()
    #     TrialAveragedFiringRateCutout( dsv12, ParameterSet({}) ).analyse(start=10, end=10000)
    # if withV1:
    #     dsv1_V1e = param_filter_query( data_store, st_name='FlashingSquares', sheet_name='V1_Exc_L4' )  
    #     # TrialAveragedFiringRate( dsv1_V1e, ParameterSet({}) ).analyse()
    #     TrialAveragedFiringRateCutout( dsv1_V1e, ParameterSet({}) ).analyse(start=10, end=10000)



def perform_analysis_feedforward( data_store, analog_ids=None):
    analog_ids=[] if analog_ids is None else analog_ids
    print("Feedforward Analysis")
    # dsv1_V1e = param_filter_query( data_store, st_name='DriftingSinusoidalGratingDisk', sheet_name='V1_Exc_L4' )  
    # TrialAveragedFiringRateCutout( dsv1_V1e, ParameterSet({}) ).analyse(start=100, end=10000)
    PSTH( param_filter_query( data_store, sheet_name='V1_Exc_L4',st_name="DriftingSinusoidalGratingDisk"), ParameterSet({'bin_length':20.0}) ).analyse()
    TrialMean( data_store, ParameterSet({'vm':False,  'cond_exc':False, 'cond_inh':False})).analyse()
    dsv = param_filter_query( data_store, st_name='DriftingSinusoidalGratingDisk', sheet_name='V1_Exc_L4', analysis_algorithm=['TrialMean'] )
    # dsv.print_content(full_ADS=True)

    if len(analog_ids):
        # AnalogSignalListPlot(
        #     dsv,
        #     ParameterSet({
        #         'mean': True,
        #         'neurons': list(analog_ids), 
        #         'sheet_name': 'V1_Exc_L4'
        #     }),
        #     fig_param={'dpi' : 100,'figsize': (14,14)}, 
        #     plot_file_name='DriftingSinusoidalGratingDisk_PSTH_V1_Exc_L4.png'
        # ).plot({
        #     '*.fontsize':24
        # })
        for lid in analog_ids:
            AnalogSignalListPlot(
                dsv,
                ParameterSet({
                    'mean': False,
                    'neurons': list([lid]), 
                    'sheet_name': 'V1_Exc_L4'
                }),
                fig_param={'dpi' : 100,'figsize': (140,14)}, 
                #plot_file_name='DriftingSinusoidalGratingDisk_PSTH_V1_Exc_L4_'+str(lid)+'.png'
                plot_file_name=f'DriftingSinusoidalGratingDisk_PSTH_V1_Exc_L4_{lid}.png'
            ).plot({
                '*.fontsize':24
            })



def perform_analysis_size( data_store, withPGN=False, withV1=False ):
    dsv10 = param_filter_query( data_store, st_name='DriftingSinusoidalGratingDisk', sheet_name='X_ON' )  
    TrialAveragedFiringRateCutout( dsv10, ParameterSet({}) ).analyse(start=100, end=1000)
    dsv11 = param_filter_query( data_store, st_name='DriftingSinusoidalGratingDisk', sheet_name='X_OFF' )  
    TrialAveragedFiringRateCutout( dsv11, ParameterSet({}) ).analyse(start=100, end=1000)
    dsv12 = param_filter_query( data_store, st_name='FlatDisk', sheet_name='X_ON' )  
    TrialAveragedFiringRateCutout( dsv12, ParameterSet({}) ).analyse(start=100, end=1000)

    if withPGN:
        dsv12 = param_filter_query( data_store, st_name='DriftingSinusoidalGratingDisk', sheet_name='PGN' )  
        TrialAveragedFiringRateCutout( dsv12, ParameterSet({}) ).analyse(start=100, end=1000)
        dsv12f = param_filter_query( data_store, st_name='FlatDisk', sheet_name='PGN' )  
        TrialAveragedFiringRateCutout( dsv12f, ParameterSet({}) ).analyse(start=100, end=1000)

    if withV1:
        #analog_ids = sorted( param_filter_query(data_store,sheet_name="V1_Exc_L4").get_segments()[0].get_stored_vm_ids() )
        spike_ids = param_filter_query(data_store,sheet_name="V1_Exc_L4").get_segments()[0].get_stored_spike_train_ids()
        analog_ids = spike_ids
        #analog_ids_inh = param_filter_query(data_store,sheet_name="V1_Inh_L4").get_segments()[0].get_stored_esyn_ids()
        #spike_ids_inh = param_filter_query(data_store,sheet_name="V1_Inh_L4").get_segments()[0].get_stored_spike_train_ids()

        # Size Tuning
        dsv1_V1eg = param_filter_query(data_store, st_name='DriftingSinusoidalGratingDisk', sheet_name='V1_Exc_L4' )
        TrialAveragedFiringRateCutout( dsv1_V1eg, ParameterSet({}) ).analyse(start=100, end=1000)
        dsv1_V1ed = param_filter_query(data_store, st_name='FlatDisk', sheet_name='V1_Exc_L4' )
        TrialAveragedFiringRateCutout( dsv1_V1ed, ParameterSet({}) ).analyse(start=100, end=1000)


        # NeuronAnnotationsToPerNeuronValues(data_store,ParameterSet({})).analyse()
        # l4_exc_or = data_store.get_analysis_result(identifier='PerNeuronValue',value_name = 'LGNAfferentOrientation', sheet_name = 'V1_Exc_L4')[0]

        # l4_exc_or_many = numpy.array(spike_ids)[numpy.nonzero(numpy.array([circular_dist(l4_exc_or.get_value_by_id(i),0,numpy.pi)  for i in spike_ids]) < 0.1)[0]]

        # idx4 = data_store.get_sheet_indexes(sheet_name='V1_Exc_L4',neuron_ids=l4_exc_or_many)

        # x = data_store.get_neuron_positions()['V1_Exc_L4'][0][idx4]
        # y = data_store.get_neuron_positions()['V1_Exc_L4'][1][idx4]
        # center4 = l4_exc_or_many[numpy.nonzero(numpy.sqrt(numpy.multiply(x,x)+numpy.multiply(y,y)) < 0.1)[0]]
        
        # analog_center4 = set(center4).intersection(analog_ids)

        # print len(l4_exc_or_many)

        # dsv = param_filter_query(data_store,st_name='DriftingSinusoidalGratingDisk',analysis_algorithm=['TrialAveragedFiringRate'])    
        # PlotTuningCurve(dsv,ParameterSet({'parameter_name' : 'radius', 'neurons': list(center4), 'sheet_name' : 'V1_Exc_L4','centered'  : False,'mean' : False, 'polar' : False, 'pool'  : False}),plot_file_name='SizeTuningExcL4.png',fig_param={'dpi' : 100,'figsize': (32,7)}).plot()
        # PlotTuningCurve(dsv,ParameterSet({'parameter_name' : 'radius', 'neurons': list(center4), 'sheet_name' : 'V1_Exc_L4','centered'  : False,'mean' : True, 'polar' : False, 'pool'  : False}),plot_file_name='SizeTuningExcL4M.png',fig_param={'dpi' : 100,'figsize': (32,7)}).plot()
        # data_store.save()
        
        # if True:
        #     dsv = param_filter_query(data_store,st_name=['DriftingSinusoidalGratingDisk'])    
        #     OverviewPlot(dsv,ParameterSet({'sheet_name' : 'V1_Exc_L4', 'neuron' : analog_center4[0], 'sheet_activity' : {}, 'spontaneous' : True}),fig_param={'dpi' : 100,'figsize': (28,12)},plot_file_name='Overview_ExcL4_1.png').plot()
        #     OverviewPlot(dsv,ParameterSet({'sheet_name' : 'V1_Exc_L4', 'neuron' : analog_center4[1], 'sheet_activity' : {}, 'spontaneous' : True}),fig_param={'dpi' : 100,'figsize': (28,12)},plot_file_name='Overview_ExcL4_2.png').plot()
        #     OverviewPlot(dsv,ParameterSet({'sheet_name' : 'V1_Exc_L4', 'neuron' : analog_center4[2], 'sheet_activity' : {}, 'spontaneous' : True}),fig_param={'dpi' : 100,'figsize': (28,12)},plot_file_name='Overview_ExcL4_3.png').plot()



#########################################################################################
#########################################################################################
#########################################################################################



def plot_luminance_tuning( data_store, Xon_ids, Xoff_ids, PGN_ids=None, V1_ids=None ):
    # firing rate against luminance levels              
    # dsv = param_filter_query( data_store, st_name='Null', analysis_algorithm=['TrialAveragedFiringRate'] )
    dsv = param_filter_query( data_store, st_name='Null', analysis_algorithm=['TrialAveragedFiringRateCutout'] )
    # ON
    PlotTuningCurve(
       dsv,
       ParameterSet({
            'polar': False,
            'pool': False,
            'centered': False,
            'mean': True,
            'parameter_name' : 'background_luminance', 
            'neurons': list(Xon_ids), 
            'sheet_name' : 'X_ON'
       }), 
       fig_param={'dpi' : 100,'figsize': (8,8)}, 
       plot_file_name="FlatLuminanceSensitivity_LGN_On_mean.png"
    ).plot({
       '*.y_lim':(0,30), 
       '*.x_scale':'log', '*.x_scale_base':10,
       '*.fontsize':24,
    })
    # for lid in Xon_ids:
    #     PlotTuningCurve(
    #         dsv,
    #         ParameterSet({
    #             'polar': False,
    #             'pool': False,
    #             'centered': False,
    #             'percent': False,
    #             'mean': False,
    #             'parameter_name' : 'background_luminance', 
    #             'neurons': list([lid]), 
    #             'sheet_name' : 'X_ON'
    #         }), 
    #         fig_param={'dpi' : 100,'figsize': (8,8)}, 
    #         plot_file_name="FlatLuminanceSensitivity_LGN_On_"+str(lid)+".png"
    #     ).plot({
    #        '*.y_lim':(0,30), 
    #        '*.x_scale':'log', '*.x_scale_base':10,
    #        '*.fontsize':24,
    #     })
    # OFF
    PlotTuningCurve(
        dsv,
        ParameterSet({
            'polar': False,
            'pool': False,
            'centered': False,
            'mean': True,
            'parameter_name' : 'background_luminance', 
            'neurons': list(Xoff_ids), 
            'sheet_name' : 'X_OFF'
        }), 
        fig_param={'dpi' : 100,'figsize': (8,8)}, 
        plot_file_name="FlatLuminanceSensitivity_LGN_Off_mean.png"
    ).plot({
        '*.y_lim':(0,30), 
        '*.x_scale':'log', '*.x_scale_base':10,
        '*.fontsize':24,
    })
    # for lid in Xoff_ids:
    #     PlotTuningCurve(
    #         dsv,
    #         ParameterSet({
    #             'polar': False,
    #             'pool': False,
    #             'centered': False,
    #             'percent': False,
    #             'mean': False,
    #             'parameter_name' : 'background_luminance', 
    #             'neurons': list([lid]), 
    #             'sheet_name' : 'X_OFF'
    #         }), 
    #         fig_param={'dpi' : 100,'figsize': (8,8)}, 
    #         plot_file_name="FlatLuminanceSensitivity_LGN_Off_"+str(lid)+".png"
    #     ).plot({
    #        '*.y_lim':(0,30), 
    #        '*.x_scale':'log', '*.x_scale_base':10,
    #        '*.fontsize':24,
    #     })
    if len(PGN_ids)>1:
        PlotTuningCurve(
           dsv,
           ParameterSet({
                'polar': False,
                'pool': False,
                'centered': False,
                'mean': True,
                'parameter_name' : 'background_luminance', 
                'neurons': list(PGN_ids), 
                'sheet_name' : 'PGN'
           }), 
           fig_param={'dpi' : 100,'figsize': (8,8)}, 
           plot_file_name="FlatLuminanceSensitivity_PGN_mean.png"
        ).plot({
           '*.y_lim':(0,30), 
           '*.x_scale':'log', '*.x_scale_base':10,
           '*.fontsize':24
        })
        for lid in PGN_ids:
            PlotTuningCurve(
               dsv,
               ParameterSet({
                    'polar': False,
                    'pool': False,
                    'centered': False,
                    'mean': False,
                    'parameter_name' : 'background_luminance', 
                    'neurons': list([lid]), 
                    'sheet_name' : 'PGN'
               }), 
               fig_param={'dpi' : 100,'figsize': (8,8)}, 
               #plot_file_name="FlatLuminanceSensitivity_PGN_"+str(lid)+".png"
               plot_file_name=f'FlatLuminanceSensitivity_PGN_{lid}.png'
            ).plot({
               '*.y_lim':(0,30), 
               '*.x_scale':'log', '*.x_scale_base':10,
               '*.fontsize':24
            })



def plot_contrast_tuning( data_store, Xon_ids, Xoff_ids, PGN_ids=None, V1_ids=None ):
    # CONTRAST SENSITIVITY LGNon_ids
    # dsv = param_filter_query( data_store, st_name='FullfieldDriftingSinusoidalGrating', analysis_algorithm=['TrialAveragedFiringRate'] )
    dsv = param_filter_query( data_store, st_name='FullfieldDriftingSinusoidalGrating', analysis_algorithm=['TrialAveragedFiringRateCutout'] )
    PlotTuningCurve(
       dsv,
       ParameterSet({
            'polar': False,
            'pool': False,
            'centered': False,
            'mean': True,
            'parameter_name' : 'contrast', 
            'neurons': list(Xon_ids), 
            'sheet_name' : 'X_ON'
       }), 
       fig_param={'dpi' : 100,'figsize': (8,8)}, 
       plot_file_name="ContrastSensitivity_LGN_On_mean.png"
    ).plot({
        '*.y_lim':(0,100), 
        # '*.x_scale':'log', '*.x_scale_base':10,
        '*.y_ticks':[0, 50, 100], 
        '*.x_ticks':[0, 25, 50, 75, 100], 
        '*.fontsize':24
    })
    for lid in Xon_ids:
        PlotTuningCurve(
           dsv,
           ParameterSet({
                'polar': False,
                'pool': False,
                'centered': False,
                'mean': False,
                'parameter_name' : 'contrast', 
                'neurons': list([lid]), 
                'sheet_name' : 'X_ON'
           }), 
           fig_param={'dpi' : 100,'figsize': (8,8)}, 
           plot_file_name="ContrastSensitivity_LGN_On_"+str(lid)+".png"
        ).plot({
            '*.y_lim':(0,100), 
            # '*.x_scale':'log', '*.x_scale_base':10,
            '*.y_ticks':[0, 50, 100], 
            '*.x_ticks':[0, 25, 50, 75, 100], 
            '*.fontsize':24
        })
    # OFF
    PlotTuningCurve(
       dsv,
       ParameterSet({
            'polar': False,
            'pool': False,
            'centered': False,
            'mean': True,
            'parameter_name' : 'contrast', 
            'neurons': list(Xoff_ids), 
            'sheet_name' : 'X_OFF'
       }), 
       fig_param={'dpi' : 100,'figsize': (10,8)}, 
       plot_file_name="ContrastSensitivity_LGN_Off_mean.png"
    ).plot({
       '*.y_lim':(0,100), 
       # '*.x_scale':'log', '*.x_scale_base':10,
       '*.fontsize':24
    })
    for lid in Xoff_ids:
        PlotTuningCurve(
           dsv,
           ParameterSet({
                'polar': False,
                'pool': False,
                'centered': False,
                'mean': False,
                'parameter_name' : 'contrast', 
                'neurons': list([lid]), 
                'sheet_name' : 'X_OFF'
           }), 
           fig_param={'dpi' : 100,'figsize': (8,8)}, 
           plot_file_name="ContrastSensitivity_LGN_Off_"+str(lid)+".png"
        ).plot({
            '*.y_lim':(0,100), 
            # '*.x_scale':'log', '*.x_scale_base':10,
            '*.y_ticks':[0, 50, 100], 
            '*.x_ticks':[0, 25, 50, 75, 100], 
            '*.fontsize':24
        })
    if PGN_ids.any():
        PlotTuningCurve(
           dsv,
           ParameterSet({
                'polar': False,
                'pool': False,
                'centered': False,
                'mean': True,
                'parameter_name' : 'contrast', 
                'neurons': list(PGN_ids), 
                'sheet_name' : 'PGN'
           }), 
           fig_param={'dpi' : 100,'figsize': (8,8)}, 
           plot_file_name="ContrastSensitivity_PGN_mean.png"
        ).plot({
            '*.y_lim':(0,100), 
            # '*.x_scale':'log', '*.x_scale_base':10,
            '*.y_ticks':[0, 50, 100], 
            '*.x_ticks':[0, 25, 50, 75, 100], 
            '*.fontsize':24
        })
        for lid in PGN_ids:
            PlotTuningCurve(
               dsv,
               ParameterSet({
                    'polar': False,
                    'pool': False,
                    'centered': False,
                    'mean': False,
                    'parameter_name' : 'contrast', 
                    'neurons': list([lid]), 
                    'sheet_name' : 'PGN'
               }), 
               fig_param={'dpi' : 100,'figsize': (8,8)}, 
               plot_file_name="ContrastSensitivity_PGN_"+str(lid)+".png"
            ).plot({
                '*.y_lim':(0,100), 
                # '*.x_scale':'log', '*.x_scale_base':10,
                '*.y_ticks':[0, 50, 100], 
                '*.x_ticks':[0, 25, 50, 75, 100], 
                '*.fontsize':24
            })
    if V1_ids.any():
        PlotTuningCurve(
           dsv,
           ParameterSet({
                'polar': False,
                'pool': False,
                'centered': False,
                'mean': True,
                'parameter_name' : 'contrast', 
                'neurons': list(V1_ids), 
                'sheet_name' : 'V1_Exc_L4'
           }), 
           fig_param={'dpi' : 100,'figsize': (8,8)}, 
           plot_file_name="ContrastSensitivity_V1e_mean.png"
        ).plot({
            '*.y_lim':(0,100), 
            # '*.x_scale':'log', '*.x_scale_base':10,
            '*.y_ticks':[0, 50, 100], 
            '*.x_ticks':[0, 25, 50, 75, 100], 
            '*.fontsize':24
        })
        for lid in V1_ids:
            PlotTuningCurve(
               dsv,
               ParameterSet({
                    'polar': False,
                    'pool': False,
                    'centered': False,
                    'mean': False,
                    'parameter_name' : 'contrast', 
                    'neurons': list([lid]), 
                    'sheet_name' : 'V1_Exc_L4'
               }), 
               fig_param={'dpi' : 100,'figsize': (8,8)}, 
               plot_file_name="ContrastSensitivity_V1e_"+str(lid)+".png"
            ).plot({
                '*.y_lim':(0,100), 
                # '*.x_scale':'log', '*.x_scale_base':10,
                '*.y_ticks':[0, 50, 100], 
                '*.x_ticks':[0, 25, 50, 75, 100], 
                '*.fontsize':24
            })



def plot_spatial_frequency_tuning( data_store, Xon_ids, Xoff_ids, PGN_ids=None, V1_ids=None ):
    # firing rate against spatial frequencies
    # dsv = param_filter_query( data_store, st_name='FullfieldDriftingSquareGrating', analysis_algorithm=['TrialAveragedFiringRate'] )
    dsv = param_filter_query( data_store, st_name='FullfieldDriftingSinusoidalGrating', analysis_algorithm=['TrialAveragedFiringRateCutout'] )
    # dsv.print_content(full_ADS=True)
    # ON
    PlotTuningCurve(
       dsv,
       ParameterSet({
           'polar': False,
           'pool': False,
           'centered': False,
           'mean': True,
           'parameter_name' : 'spatial_frequency', 
           'neurons': list(Xon_ids), 
           'sheet_name' : 'X_ON'
       }), 
       fig_param={'dpi' : 100,'figsize': (8,8)}, 
       plot_file_name="SpatialFrequencyTuning_LGN_On_mean.png"
    ).plot({
        '*.y_lim':(5,100), 
        '*.y_scale':'log', '*.y_scale_base':2,
        '*.y_ticks':[5, 10, 25, 50, 75, 100], 
        '*.x_scale':'log', '*.x_scale_base':2,
        '*.x_ticks':[0.1, 0.2, 0.5, 1, 1.5, 2, 8], 
        '*.fontsize':24
    })
    for lid in Xon_ids:
        PlotTuningCurve(
            dsv,
            ParameterSet({
                'polar': False,
                'pool': False,
                'centered': False,
                'mean': False,
                'parameter_name' : 'spatial_frequency', 
                'neurons': list([lid]), 
                'sheet_name' : 'X_ON'
            }), 
            fig_param={'dpi' : 100,'figsize': (8,8)}, 
            #plot_file_name="SpatialFrequencyTuning_LGN_On_"+str(lid)+".png"
            plot_file_name=f'SpatialFrequencyTuning_LGN_On_{lid}.png'
        ).plot({
            '*.y_lim':(5,100), 
            '*.y_scale':'log', '*.y_scale_base':2,
            '*.y_ticks':[5, 10, 25, 50, 75, 100], 
            '*.x_scale':'log', '*.x_scale_base':2,
            '*.x_ticks':[0.1, 0.2, 0.5, 1, 1.5, 2, 8], 
            '*.fontsize':24
        })
    # OFF
    PlotTuningCurve(
       dsv,
       ParameterSet({
           'polar': False,
           'pool': False,
           'centered': False,
           'mean': True,
           'parameter_name' : 'spatial_frequency', 
           'neurons': list(Xoff_ids), 
           'sheet_name' : 'X_OFF'
       }), 
       fig_param={'dpi' : 100,'figsize': (8,8)}, 
       plot_file_name="SpatialFrequencyTuning_LGN_Off_mean.png"
    ).plot({
        '*.y_lim':(5,100), 
        '*.y_scale':'log', '*.y_scale_base':2,
        '*.y_ticks':[5, 10, 25, 50, 75, 100], 
        '*.x_scale':'log', '*.x_scale_base':2,
        '*.x_ticks':[0.1, 0.2, 0.5, 1, 1.5, 2, 8], 
        '*.fontsize':24
    })
    for lid in Xoff_ids:
        PlotTuningCurve(
            dsv,
            ParameterSet({
                'polar': False,
                'pool': False,
                'centered': False,
                'mean': False,
                'parameter_name' : 'spatial_frequency', 
                'neurons': list([lid]), 
                'sheet_name' : 'X_OFF'
            }), 
            fig_param={'dpi' : 100,'figsize': (8,8)}, 
            #plot_file_name="SpatialFrequencyTuning_LGN_Off_"+str(lid)+".png"
            plot_file_name=f'SpatialFrequencyTuning_LGN_Off_{lid}.png'
        ).plot({
            '*.y_lim':(5,100), 
            '*.y_scale':'log', '*.y_scale_base':2,
            '*.y_ticks':[5, 10, 25, 50, 75, 100], 
            '*.x_scale':'log', '*.x_scale_base':2,
            '*.x_ticks':[0.1, 0.2, 0.5, 1, 1.5, 2, 8], 
            '*.fontsize':24
        })
    if PGN_ids.any():
        PlotTuningCurve(
           dsv,
           ParameterSet({
               'polar': False,
               'pool': False,
               'centered': False,
               'mean': True,
               'parameter_name' : 'spatial_frequency', 
               'neurons': list(PGN_ids), 
               'sheet_name' : 'PGN'
           }), 
           fig_param={'dpi' : 100,'figsize': (8,8)}, 
           plot_file_name="SpatialFrequencyTuning_PGN_mean.png"
        ).plot({
            '*.y_lim':(5,100), 
            '*.y_scale':'log', '*.y_scale_base':2,
            '*.y_ticks':[5, 10, 25, 50, 75, 100], 
            '*.x_scale':'log', '*.x_scale_base':2,
            '*.x_ticks':[0.1, 0.2, 0.5, 1, 1.5, 2, 8], 
            '*.fontsize':24
        })
        for lid in PGN_ids:
            PlotTuningCurve(
                dsv,
                ParameterSet({
                    'polar': False,
                    'pool': False,
                    'centered': False,
                    'mean': False,
                    'parameter_name' : 'spatial_frequency', 
                    'neurons': list([lid]), 
                    'sheet_name' : 'PGN'
                }), 
                fig_param={'dpi' : 100,'figsize': (8,8)}, 
                #plot_file_name="SpatialFrequencyTuning_PGN_"+str(lid)+".png"
                plot_file_name=f'SpatialFrequencyTuning_PGN_{lid}.png'
            ).plot({
                '*.y_lim':(5,100), 
                '*.y_scale':'log', '*.y_scale_base':2,
                '*.y_ticks':[5, 10, 25, 50, 75, 100], 
                '*.x_scale':'log', '*.x_scale_base':2,
                '*.x_ticks':[0.1, 0.2, 0.5, 1, 1.5, 2, 8], 
                '*.fontsize':24
            })
    if V1_ids.any():
        PlotTuningCurve(
           dsv,
           ParameterSet({
               'polar': False,
               'pool': False,
               'centered': False,
               'mean': True,
               'parameter_name' : 'spatial_frequency', 
               'neurons': list(V1_ids), 
               'sheet_name' : 'V1_Exc_L4'
           }), 
           fig_param={'dpi' : 100,'figsize': (8,8)}, 
           plot_file_name="SpatialFrequencyTuning_V1e_mean.png"
        ).plot({
            '*.y_lim':(5,100), 
            '*.y_scale':'log', '*.y_scale_base':2,
            '*.y_ticks':[5, 10, 25, 50, 75, 100], 
            '*.x_scale':'log', '*.x_scale_base':2,
            '*.x_ticks':[0.1, 0.2, 0.5, 1, 1.5, 2, 8], 
            '*.fontsize':24
        })
        for lid in V1_ids:
            PlotTuningCurve(
                dsv,
                ParameterSet({
                    'polar': False,
                    'pool': False,
                    'centered': False,
                    'mean': False,
                    'parameter_name' : 'spatial_frequency', 
                    'neurons': list([lid]), 
                    'sheet_name' : 'V1_Exc_L4'
                }), 
                fig_param={'dpi' : 100,'figsize': (8,8)}, 
                #plot_file_name="SpatialFrequencyTuning_V1e_"+str(lid)+".png"
                plot_file_name=f'SpatialFrequencyTuning_V1e_{lid}.png'
            ).plot({
                '*.y_lim':(5,100), 
                '*.y_scale':'log', '*.y_scale_base':2,
                '*.y_ticks':[5, 10, 25, 50, 75, 100], 
                '*.x_scale':'log', '*.x_scale_base':2,
                '*.x_ticks':[0.1, 0.2, 0.5, 1, 1.5, 2, 8], 
                '*.fontsize':24
            })



def plot_temporal_frequency_tuning( data_store, Xon_ids, Xoff_ids, PGN_ids=None, V1_ids=None ):
    # dsv = param_filter_query( data_store, st_name='FullfieldDriftingSinusoidalGrating', analysis_algorithm=['TrialAveragedFiringRate'] )
    dsv = param_filter_query( data_store, st_name='FullfieldDriftingSinusoidalGrating', analysis_algorithm=['TrialAveragedFiringRateCutout'] )
    PlotTuningCurve(
       dsv,
       ParameterSet({
           'polar': False,
           'pool': False,
           'centered': False,
           'mean': True,
           'parameter_name' : 'temporal_frequency', 
           'neurons': list(Xon_ids), 
           'sheet_name' : 'X_ON'
      }), 
      fig_param={'dpi' : 100,'figsize': (8,8)}, 
      plot_file_name="TemporalFrequencyTuning_LGN_On_mean.png"
    ).plot({
        '*.x_scale':'log', '*.x_scale_base':2,
        '*.y_ticks':[5, 10, 25, 50, 75, 100], 
        # '*.y_scale':'linear', 
        '*.y_scale':'log', '*.y_scale_base':2,
        '*.fontsize':24
    })
    for lid in Xon_ids:
        PlotTuningCurve(
            dsv,
            ParameterSet({
                'polar': False,
                'pool': False,
                'centered': False,
                'mean': False,
                'parameter_name' : 'temporal_frequency', 
                'neurons': list([lid]), 
                'sheet_name' : 'X_ON'
            }), 
            fig_param={'dpi' : 100,'figsize': (8,8)}, 
            #plot_file_name="TemporalFrequencyTuning_LGN_On_"+str(lid)+".png"
            plot_file_name=f'TemporalFrequencyTuning_LGN_On_{lid}.png'
        ).plot({
            '*.x_scale':'log', '*.x_scale_base':2,
            '*.y_ticks':[5, 10, 25, 50, 75, 100], 
            # '*.y_scale':'linear', 
            '*.y_scale':'log', '*.y_scale_base':2,
            '*.fontsize':24
        })
    # OFF
    PlotTuningCurve(
       dsv,
       ParameterSet({
           'polar': False,
           'pool': False,
           'centered': False,
           'mean': True,
           'parameter_name' : 'temporal_frequency', 
           'neurons': list(Xoff_ids), 
           'sheet_name' : 'X_OFF'
      }), 
      fig_param={'dpi' : 100,'figsize': (8,8)}, 
      plot_file_name="TemporalFrequencyTuning_LGN_Off_mean.png"
    ).plot({
        '*.x_scale':'log', '*.x_scale_base':2,
        '*.y_ticks':[5, 10, 25, 50, 75, 100], 
        # '*.y_scale':'linear', 
        '*.y_scale':'log', '*.y_scale_base':2,
        '*.fontsize':24
    })
    for lid in Xoff_ids:
        PlotTuningCurve(
            dsv,
            ParameterSet({
                'polar': False,
                'pool': False,
                'centered': False,
                'mean': False,
                'parameter_name' : 'temporal_frequency', 
                'neurons': list([lid]), 
                'sheet_name' : 'X_OFF'
            }), 
            fig_param={'dpi' : 100,'figsize': (8,8)}, 
            #plot_file_name="TemporalFrequencyTuning_LGN_Off_"+str(lid)+".png"
            plot_file_name=f'TemporalFrequencyTuning_LGN_Off_{lid}.png'
        ).plot({
            '*.x_scale':'log', '*.x_scale_base':2,
            '*.y_ticks':[5, 10, 25, 50, 75, 100], 
            # '*.y_scale':'linear', 
            '*.y_scale':'log', '*.y_scale_base':2,
            '*.fontsize':24
        })
    if PGN_ids.any():
        PlotTuningCurve(
           dsv,
           ParameterSet({
               'polar': False,
               'pool': False,
               'centered': False,
               'mean': True,
               'parameter_name' : 'temporal_frequency', 
               'neurons': list(PGN_ids), 
               'sheet_name' : 'PGN'
           }), 
           fig_param={'dpi' : 100,'figsize': (8,8)}, 
           plot_file_name="TemporalFrequencyTuning_PGN_mean.png"
        ).plot({
            '*.x_scale':'log', '*.x_scale_base':2,
            '*.y_ticks':[5, 10, 25, 50, 75, 100], 
            # '*.y_scale':'linear', 
            '*.y_scale':'log', '*.y_scale_base':2,
            '*.fontsize':24
        })
        for lid in PGN_ids:
            PlotTuningCurve(
                dsv,
                ParameterSet({
                    'polar': False,
                    'pool': False,
                    'centered': False,
                    'mean': False,
                    'parameter_name' : 'temporal_frequency', 
                    'neurons': list([lid]), 
                    'sheet_name' : 'PGN'
                }), 
                fig_param={'dpi' : 100,'figsize': (8,8)}, 
                #plot_file_name="TemporalFrequencyTuning_PGN_"+str(lid)+".png"
                plot_file_name=f'TemporalFrequencyTuning_PGN_{lid}.png'
            ).plot({
                '*.x_scale':'log', '*.x_scale_base':2,
                '*.y_ticks':[5, 10, 25, 50, 75, 100], 
                # '*.y_scale':'linear', 
                '*.y_scale':'log', '*.y_scale_base':2,
                '*.fontsize':24
            })
    if V1_ids.any():
        PlotTuningCurve(
            dsv,
            ParameterSet({
                'polar': False,
                'pool': False,
                'centered': False,
                'mean': True,
                'parameter_name' : 'temporal_frequency', 
                'neurons': list(V1_ids), 
                'sheet_name' : 'V1_Exc_L4'
            }), 
            fig_param={'dpi' : 100,'figsize': (8,8)}, 
            plot_file_name="TemporalFrequencyTuning_V1e_mean.png"
        ).plot({
            '*.y_lim':(0,60), 
            '*.x_scale':'log', '*.x_scale_base':2,
            '*.y_ticks':[5, 10, 25, 50, 60], 
            # '*.y_scale':'linear', 
            '*.y_scale':'log', '*.y_scale_base':2,
            '*.fontsize':24
        })
        for lid in PGN_ids:
            PlotTuningCurve(
               dsv,
               ParameterSet({
                   'polar': False,
                   'pool': False,
                   'centered': False,
                   'mean': False,
                   'parameter_name' : 'temporal_frequency', 
                   'neurons': list(V1_ids), 
                   'sheet_name' : 'V1_Exc_L4'
              }), 
              fig_param={'dpi' : 100,'figsize': (8,8)}, 
              #plot_file_name="TemporalFrequencyTuning_V1e_"+str(lid)+".png"
              plot_file_name=f'TemporalFrequencyTuning_v1e_{lid}.png'
            ).plot({
                '*.y_lim':(0,60), 
                '*.x_scale':'log', '*.x_scale_base':2,
                '*.y_ticks':[5, 10, 25, 50, 60], 
                #'*.y_scale':'linear', 
                '*.y_scale':'log', '*.y_scale_base':2,
                '*.fontsize':24
            })



def plot_size_tuning( data_store, Xon_ids, Xoff_ids, PGN_ids=None, V1_ids=None, radius=None ):
    if radius:
        addon = "_"+str(radius[0]) +"_"+str(radius[1])
    else:
        addon = "_"+str(int(time.time()))
    # DISKS
    # dsv = param_filter_query( data_store, st_name='FlatDisk', analysis_algorithm=['TrialAveragedFiringRateCutout'] )
    # PlotTuningCurve(
    #     dsv,
    #     ParameterSet({
    #         'polar': False,
    #         'pool': False,
    #         'centered': False,
    #         'mean': False,
    #         'parameter_name' : 'radius', 
    #         'neurons': list(Xon_ids[0:1]), 
    #         'sheet_name' : 'X_ON'
    #     }), 
    #     fig_param={'dpi' : 100,'figsize': (8,8)}, 
    #     plot_file_name="SizeTuning_Disk_LGN_On.png"
    # ).plot({
    #     '*.y_lim':(0,200), 
    #     '*.x_ticks':[0.1, 1, 2, 4, 8], 
    #     '*.x_scale':'linear',
    #     #'*.x_scale':'log', '*.x_scale_base':2,
    #     '*.fontsize':24
    # })
    # PlotTuningCurve(
    #     dsv,
    #     ParameterSet({
    #         'polar': False,
    #         'pool': False,
    #         'centered': False,
    #         'mean': True,
    #         'parameter_name' : 'radius', 
    #         'neurons': list(Xon_ids), 
    #         'sheet_name' : 'X_ON'
    #     }), 
    #     fig_param={'dpi' : 100,'figsize': (8,8)}, 
    #     plot_file_name="SizeTuning_Disk_LGN_On_mean.png"
    # ).plot({
    #     '*.y_lim':(0,200), 
    #     '*.x_ticks':[0.1, 1, 2, 4, 8], 
    #     '*.x_scale':'linear',
    #     #'*.x_scale':'log', '*.x_scale_base':2,
    #     '*.fontsize':24
    # })
    # if PGN_ids:
    #     PlotTuningCurve(
    #         dsv,
    #         ParameterSet({
    #             'polar': False,
    #             'pool': False,
    #             'centered': False,
    #             'mean': True,
    #             'parameter_name' : 'radius', 
    #             'neurons': list(PGN_ids), 
    #             'sheet_name' : 'PGN'
    #         }), 
    #         fig_param={'dpi' : 100,'figsize': (8,8)}, 
    #         plot_file_name="SizeTuning_Disk_PGN_mean.png"
    #     ).plot({
    #         '*.y_lim':(0,200), 
    #         '*.x_ticks':[0.1, 1, 2, 4, 8], 
    #         '*.x_scale':'linear',
    #         #'*.x_scale':'log', '*.x_scale_base':2,
    #         '*.fontsize':24
    #     })
    # if V1_ids:
    #     PlotTuningCurve(
    #         dsv,
    #         ParameterSet({
    #             'polar': False,
    #             'pool': False,
    #             'centered': False,
    #             'mean': True,
    #             'parameter_name' : 'radius', 
    #             'neurons': list(V1_ids), 
    #             'sheet_name' : 'V1_Exc_L4'
    #         }), 
    #         fig_param={'dpi' : 100,'figsize': (8,8)}, 
    #         plot_file_name="SizeTuning_Disk_V1_mean.png"
    #     ).plot({
    #         '*.y_lim':(0,200), 
    #         '*.x_ticks':[0.1, 1, 2, 4, 8], 
    #         '*.x_scale':'linear',
    #         #'*.x_scale':'log', '*.x_scale_base':2,
    #         '*.fontsize':24
    #     })
    # GRATINGS
    # ON cells
    dsv = param_filter_query( data_store, st_name='DriftingSinusoidalGratingDisk', analysis_algorithm=['TrialAveragedFiringRateCutout'] )
    if len(Xon_ids):
        PlotTuningCurve(
            dsv,
            ParameterSet({
                'polar': False,
                'pool': False,
                'centered': False,
                'mean': True,
                # 'all': True,
                'parameter_name' : 'radius', 
                'neurons': list(Xon_ids), 
                'sheet_name' : 'X_ON'
            }), 
            fig_param={'dpi' : 100,'figsize': (8,8)}, 
            plot_file_name="SizeTuning_Grating_LGN_On_mean"+addon+".png"
        ).plot({
            '*.y_lim':(0,100), 
            # '*.y_ticks':[10, 20, 30, 40, 50], 
            '*.x_ticks':[0.1, 1, 2, 4, 6], 
            '*.x_scale':'linear',
            #'*.x_scale':'log', '*.x_scale_base':2,
            '*.fontsize':24
        })
    # for lid in Xon_ids:
    #     PlotTuningCurve(
    #         dsv,
    #         ParameterSet({
    #             'polar': False,
    #             'pool': False,
    #             'centered': False,
    #             'mean': False,
    #             'parameter_name' : 'radius', 
    #             'neurons': list([lid]), 
    #             'sheet_name' : 'X_ON'
    #         }), 
    #         fig_param={'dpi' : 100,'figsize': (8,8)}, 
    #         plot_file_name="SizeTuning_Grating_LGN_On_"+str(lid)+".png"
    #     ).plot({
    #         '*.y_lim':(0,100), 
    #         '*.x_ticks':[0.1, 1, 2, 4, 6], 
    #         '*.x_scale':'linear',
    #         #'*.x_scale':'log', '*.x_scale_base':2,
    #         '*.fontsize':24
    #     })
    # OFF cells
    if len(Xoff_ids):
        PlotTuningCurve(
            dsv,
            ParameterSet({
                'polar': False,
                'pool': False,
                'centered': False,
                'mean': True,
                # 'all': True,
                'parameter_name' : 'radius', 
                'neurons': list(Xoff_ids), 
                'sheet_name' : 'X_OFF'
            }), 
            fig_param={'dpi' : 100,'figsize': (8,8)}, 
            plot_file_name="SizeTuning_Grating_LGN_Off_mean"+addon+".png"
        ).plot({
            '*.y_lim':(0,100), 
            # '*.y_ticks':[10, 20, 30, 40, 50], 
            '*.x_ticks':[0.1, 1, 2, 4, 6], 
            '*.x_scale':'linear',
            #'*.x_scale':'log', '*.x_scale_base':2,
            '*.fontsize':24
        })
    # for lid in Xoff_ids:
    #     PlotTuningCurve(
    #         dsv,
    #         ParameterSet({
    #             'polar': False,
    #             'pool': False,
    #             'centered': False,
    #             'mean': False,
    #             'parameter_name' : 'radius', 
    #             'neurons': list([lid]), 
    #             'sheet_name' : 'X_OFF'
    #         }), 
    #         fig_param={'dpi' : 100,'figsize': (8,8)}, 
    #         plot_file_name="SizeTuning_Grating_LGN_Off_"+str(lid)+".png"
    #     ).plot({
    #         '*.y_lim':(0,100), 
    #         '*.x_ticks':[0.1, 1, 2, 4, 6], 
    #         '*.x_scale':'linear',
    #         #'*.x_scale':'log', '*.x_scale_base':2,
    #         '*.fontsize':24
    #     })

    if len(PGN_ids):
        PlotTuningCurve(
            dsv,
            ParameterSet({
                'polar': False,
                'pool': False,
                'centered': False,
                'mean': True,
                # 'all': True,
                'parameter_name' : 'radius', 
                'neurons': list(PGN_ids), 
                'sheet_name' : 'PGN'
            }), 
            fig_param={'dpi' : 100,'figsize': (8,8)}, 
            plot_file_name="SizeTuning_Grating_PGN_mean"+addon+".png"
        ).plot({
            '*.y_lim':(0,100), 
            '*.x_ticks':[0.1, 1, 2, 4, 6], 
            '*.x_scale':'linear',
            #'*.x_scale':'log', '*.x_scale_base':2,
            '*.fontsize':24
        })
        # for lid in PGN_ids:
        #     PlotTuningCurve(
        #         dsv,
        #         ParameterSet({
        #             'polar': False,
        #             'pool': False,
        #             'centered': False,
        #             'mean': False,
        #             'parameter_name' : 'radius', 
        #             'neurons': list([lid]), 
        #             'sheet_name' : 'PGN'
        #         }), 
        #         fig_param={'dpi' : 100,'figsize': (8,8)}, 
        #         plot_file_name="SizeTuning_Grating_PGN_"+str(lid)+".png"
        #     ).plot({
        #         '*.y_lim':(0,100), 
        #         '*.x_ticks':[0.1, 1, 2, 4, 6], 
        #         '*.x_scale':'linear',
        #         #'*.x_scale':'log', '*.x_scale_base':2,
        #         '*.fontsize':24
        #     })

    if len(V1_ids): # V1
        PlotTuningCurve(
            dsv,
            ParameterSet({
                'polar': False,
                'pool': False,
                'centered': False,
                'mean': True,
                # 'all': True,
                'parameter_name' : 'radius', 
                'neurons': list(V1_ids), 
                'sheet_name' : 'V1_Exc_L4'
            }), 
            fig_param={'dpi' : 100,'figsize': (8,8)}, 
            plot_file_name="SizeTuning_Grating_l4_exc_mean"+addon+".png"
        ).plot({
            '*.y_lim':(0,30), 
            '*.x_ticks':[0.1, 1, 2, 4, 6], 
            '*.x_scale':'linear',
            #'*.x_scale':'log', '*.x_scale_base':2,
            '*.fontsize':24
        })
        # for aid in V1_ids:
        #     PlotTuningCurve(
        #         dsv,
        #         ParameterSet({
        #             'polar': False,
        #             'pool': False,
        #             'centered': False,
        #             'mean': False,
        #             'parameter_name' : 'radius', 
        #             'neurons': list([aid]), 
        #             'sheet_name' : 'V1_Exc_L4'
        #         }), 
        #         fig_param={'dpi' : 100,'figsize': (8,8)}, 
        #         plot_file_name="SizeTuning_Grating_V1_Exc_L4_"+str(aid)+".png"
        #     ).plot({
        #         '*.y_lim':(0,30), 
        #         '*.x_ticks':[0.1, 1, 2, 4, 6], 
        #         '*.x_scale':'linear',
        #         #'*.x_scale':'log', '*.x_scale_base':2,
        #         '*.fontsize':24
        #     })

    # dsv = param_filter_query( data_store, st_name='FlatDisk', analysis_algorithm=['TrialAveragedFiringRate'] )
    # PlotTuningCurve(
    #    dsv,
    #    ParameterSet({
    #         'polar': False,
    #         'pool': False,
    #         'centered': False,
    #         'mean': False,
    #         'parameter_name' : 'radius', 
    #         'neurons': list(Xon_ids[0:1]), 
    #         'sheet_name' : 'X_ON'
    #    }), 
    #     fig_param={'dpi' : 100,'figsize': (8,8)}, 
    #    plot_file_name="SizeTuning_Disk_LGN_On.png"
    # ).plot({
    #    #'*.y_lim':(0,50), 
    #    '*.x_scale':'log', '*.x_scale_base':2,
    #    '*.fontsize':24
    # })
    # PlotTuningCurve(
    #    dsv,
    #    ParameterSet({
    #         'polar': False,
    #         'pool': False,
    #         'centered': False,
    #         'mean': False,
    #         'parameter_name' : 'radius', 
    #         'neurons': list(Xoff_ids[0:1]), 
    #         'sheet_name' : 'X_OFF'
    #    }), 
    #     fig_param={'dpi' : 100,'figsize': (8,8)}, 
    #    plot_file_name="SizeTuning_Disk_LGN_Off.png"
    # ).plot({
    #    #'*.y_lim':(0,50), 
    #    '*.x_scale':'log', '*.x_scale_base':2,
    #    '*.fontsize':24
    # })
    # PlotTuningCurve(
    #    dsv,
    #    ParameterSet({
    #         'polar': False,
    #         'pool': False,
    #         'centered': False,
    #         'mean': False,
    #         'parameter_name' : 'radius', 
    #         'neurons': list(V1_ids), 
    #         'sheet_name' : 'V1_Exc_L4'
    #    }), 
    #     fig_param={'dpi' : 100,'figsize': (8,8)}, 
    #    plot_file_name="SizeTuning_Disk_l4_exc.png"
    # ).plot({
    #    '*.y_lim':(0,100), 
    #    '*.x_scale':'log', '*.x_scale_base':2,
    #    '*.fontsize':24
    # })



#--------------------
# LIFELONG SPARSENESS
# # per neuron FanoFactor level
# dsv = param_filter_query(data_store, analysis_algorithm=['Analog_MeanSTDAndFanoFactor'], sheet_name=['X_ON'], value_name='FanoFactor(VM)')   
# PerNeuronValuePlot(
#    dsv,
#    ParameterSet({'cortical_view':True}),
#    fig_param={'dpi' : 100,'figsize': (6,6)}, 
#    plot_file_name="FanoFactor_LGN_On.png"
# ).plot({
#    '*.x_axis' : None, 
#    '*.fontsize':24
# })
# # # per neuron Activity Ratio
# dsv = param_filter_query(data_store, analysis_algorithm=['TrialAveragedSparseness'], sheet_name=['X_ON'], value_name='Sparseness')   
# PerNeuronValuePlot(
#     dsv,
#     ParameterSet({'cortical_view':True}),
#     fig_param={'dpi' : 100,'figsize': (6,6)}, 
#     plot_file_name="Sparseness_LGN_On.png"
# ).plot({
#     '*.x_axis' : None, 
#     '*.fontsize':24
# })



#-------------------
# ORIENTATION TUNING

def plot_orientation_tuning( data_store, Xon_ids, Xoff_ids, PGN_ids=None, V1_ids=None ):
    # firing rate against spatial frequencies
    dsv = param_filter_query( data_store, st_name='FullfieldDriftingSinusoidalGrating', analysis_algorithm=['TrialAveragedFiringRateCutout'] )
    # dsv.print_content(full_ADS=True)
    # ON
    PlotTuningCurve(
       dsv,
       ParameterSet({
           'polar': False,
           'pool': False,
           'centered': False,
           'mean': True,
           'parameter_name' : 'orientation', 
           'neurons': list(Xon_ids), 
           'sheet_name' : 'X_ON'
       }), 
       fig_param={'dpi' : 100,'figsize': (8,8)}, 
       plot_file_name="OrientationTuning_LGN_On_mean.png"
    ).plot({
        '*.fontsize':24
    })
    for lid in Xon_ids:
        PlotTuningCurve(
            dsv,
            ParameterSet({
                'polar': False,
                'pool': False,
                'centered': False,
                'mean': False,
                'parameter_name' : 'orientation', 
                'neurons': list([lid]), 
                'sheet_name' : 'X_ON'
            }), 
            fig_param={'dpi' : 100,'figsize': (8,8)}, 
            #plot_file_name="OrientationTuning_LGN_On_"+str(lid)+".png"
            plot_file_name=f'OrientationTuning_LGN_On_{lid}.png'
        ).plot({
            '*.fontsize':24
        })
    # OFF
    PlotTuningCurve(
       dsv,
       ParameterSet({
           'polar': False,
           'pool': False,
           'centered': False,
           'mean': True,
           'parameter_name' : 'orientation', 
           'neurons': list(Xoff_ids), 
           'sheet_name' : 'X_OFF'
       }), 
       fig_param={'dpi' : 100,'figsize': (8,8)}, 
       plot_file_name="OrientationTuning_LGN_Off_mean.png"
    ).plot({
        '*.fontsize':24
    })
    for lid in Xoff_ids:
        PlotTuningCurve(
            dsv,
            ParameterSet({
                'polar': False,
                'pool': False,
                'centered': False,
                'mean': False,
                'parameter_name' : 'orientation', 
                'neurons': list([lid]), 
                'sheet_name' : 'X_OFF'
            }), 
            fig_param={'dpi' : 100,'figsize': (8,8)}, 
            #plot_file_name="OrientationTuning_LGN_Off_"+str(lid)+".png"
            plot_file_name=f'OrientationTuning_LGN_Off_{lid}.png'
        ).plot({
            '*.fontsize':24
        })
    if PGN_ids.any():
        PlotTuningCurve(
           dsv,
           ParameterSet({
               'polar': False,
               'pool': False,
               'centered': False,
               'mean': True,
               'parameter_name' : 'orientation', 
               'neurons': list(PGN_ids), 
               'sheet_name' : 'PGN'
           }), 
           fig_param={'dpi' : 100,'figsize': (8,8)}, 
           plot_file_name="OrientationTuning_PGN_mean.png"
        ).plot({
            '*.fontsize':24
        })
        for lid in PGN_ids:
            PlotTuningCurve(
                dsv,
                ParameterSet({
                    'polar': False,
                    'pool': False,
                    'centered': False,
                    'mean': False,
                    'parameter_name' : 'orientation', 
                    'neurons': list([lid]), 
                    'sheet_name' : 'PGN'
                }), 
                fig_param={'dpi' : 100,'figsize': (8,8)}, 
                #plot_file_name="OrientationTuning_PGN_"+str(lid)+".png"
                plot_file_name=f'OrientationTuning_PGN_{lid}.png'
            ).plot({
                '*.fontsize':24
            })
    if len(V1_ids):
        PlotTuningCurve(
           dsv,
           ParameterSet({
               'polar': False,
               'pool': False,
               'centered': False,
               'mean': True,
               'parameter_name' : 'orientation', 
               'neurons': list(V1_ids), 
               'sheet_name' : 'V1_Exc_L4'
           }), 
           fig_param={'dpi' : 100,'figsize': (8,8)}, 
           plot_file_name="OrientationTuning_V1e_mean.png"
        ).plot({
            '*.fontsize':24
        })
        for lid in V1_ids:
            PlotTuningCurve(
                dsv,
                ParameterSet({
                    'polar': False,
                    'pool': False,
                    'centered': False,
                    'mean': False,
                    'parameter_name' : 'orientation', 
                    'neurons': list([lid]), 
                    'sheet_name' : 'V1_Exc_L4'
                }), 
                fig_param={'dpi' : 100,'figsize': (8,8)}, 
                #plot_file_name="OrientationTuning_V1e_"+str(lid)+".png"
                plot_file_name=f'OrientationTuning_V1e_{lid}.png'
            ).plot({
                '*.fontsize':24
            })
            dsv = param_filter_query(data_store, sheet_name=['V1_Exc_L4'], value_name='LGNAfferentOrientation')   
            PerNeuronValuePlot(dsv,ParameterSet({"cortical_view":True, "neuron_ids": list(V1_ids)}), plot_file_name='ORSet.png').plot()
            dsv = param_filter_query(data_store, sheet_name=['V1_Exc_L4'], value_name='Firing rate')   
            PerNeuronValuePlot(dsv,ParameterSet({"cortical_view":True, "neuron_ids": list(V1_ids)}), plot_file_name='FR.png').plot()



#-----------
# ## CONTOUR COMPLETION
def plot_xcorr( data_store, label, Xon_ids, Xoff_ids, PGN_ids, V1_ids):
    dsvFS = param_filter_query( data_store, st_name='FlashingSquares', analysis_algorithm=['PSTH'] )
    dsvFS.print_content(full_ADS=True)

    if len(Xon_ids):
        AnalogSignalListPlot(
            dsvFS,
            ParameterSet({
                'mean': True,
                'neurons': list(Xon_ids), 
                'sheet_name': 'X_ON'
            }),
            fig_param={'dpi' : 100,'figsize': (14,14)}, 
            plot_file_name='FlashingSquares'+label+'PSTH_LGN_On.png'
        ).plot({
            '*.fontsize':24
        })

        # for lid in Xon_ids:
        #     AnalogSignalListPlot(
        #         dsvFS,
        #         ParameterSet({
        #             'mean': False,
        #             'neurons': list([lid]), 
        #             'sheet_name': 'X_ON'
        #         }),
        #         fig_param={'dpi' : 100,'figsize': (14,14)}, 
        #         plot_file_name='FlashingSquares'+label+'PSTH_LGN_On_'+str(lid)+'.png'
        #     ).plot({
        #         '*.fontsize':24
        #     })

    if len(Xoff_ids):
        AnalogSignalListPlot(
            dsvFS,
            ParameterSet({
                'mean': True,
                'neurons': list(Xoff_ids), 
                'sheet_name': 'X_OFF'
            }),
            fig_param={'dpi' : 100,'figsize': (14,14)}, 
            plot_file_name='FlashingSquares'+label+'PSTH_LGN_Off.png'
        ).plot({
            '*.fontsize':24
        })

        # for lid in spike_Xoff_ids:
        #     AnalogSignalListPlot(
        #         dsvFS,
        #         ParameterSet({
        #             'mean': False,
        #             'neurons': list([lid]), 
        #             'sheet_name': 'X_OFF'
        #         }),
        #         fig_param={'dpi' : 100,'figsize': (14,14)}, 
        #         plot_file_name='FlashingSquares'+label+'PSTH_LGN_Off_'+str(lid)+'.png'
        #     ).plot({
        #         '*.fontsize':24
        #     })

    dsvDSG = param_filter_query( data_store, st_name='FullfieldDriftingSquareGrating', analysis_algorithm=['PSTH'] )
    dsvDSG.print_content(full_ADS=True)

    if len(Xon_ids):
        AnalogSignalListPlot(
            dsvDSG,
            ParameterSet({
                'mean': True,
                'neurons': list(Xon_ids), 
                'sheet_name': 'X_ON'
            }),
            fig_param={'dpi' : 100,'figsize': (14,14)}, 
            plot_file_name='SquareGrating'+label+'PSTH_LGN_On.png'
        ).plot({
            '*.fontsize':24
        })
    #     for lid in spike_Xon_ids:
    #         AnalogSignalListPlot(
    #             dsvDSG,
    #             ParameterSet({
    #                 'mean': False,
    #                 'neurons': list([lid]), 
    #                 'sheet_name': 'X_ON'
    #             }),
    #             fig_param={'dpi' : 100,'figsize': (14,14)}, 
    #             plot_file_name='SquareGrating'+label+'PSTH_LGN_On_'+str(lid)+'.png'
    #         ).plot({
    #             '*.fontsize':24
    #         })

    if len(Xoff_ids):
        AnalogSignalListPlot(
            dsvDSG,
            ParameterSet({
                'mean': True,
                'neurons': list(Xoff_ids), 
                'sheet_name': 'X_OFF'
            }),
            fig_param={'dpi' : 100,'figsize': (14,14)}, 
            plot_file_name='SquareGrating'+label+'PSTH_LGN_Off.png'
        ).plot({
            '*.fontsize':24
        })
    #     for lid in spike_Xoff_ids:
    #         AnalogSignalListPlot(
    #             dsvDSG,
    #             ParameterSet({
    #                 'mean': False,
    #                 'neurons': list([lid]), 
    #                 'sheet_name': 'X_OFF'
    #             }),
    #             fig_param={'dpi' : 100,'figsize': (14,14)}, 
    #             plot_file_name='SquareGrating'+label+'PSTH_LGN_Off_'+str(lid)+'.png'
    #         ).plot({
    #             '*.fontsize':24
    #         })



    # dsv = param_filter_query( data_store, st_name='FullfieldDriftingSquareGrating', analysis_algorithm=['TrialAveragedCorrectedCrossCorrelation'] )
    # PerNeuronPairAnalogSignalListPlot(
    #     dsv,
    #     ParameterSet({
    #         'sheet_name': 'X_ON'
    #     }),
    #     fig_param={'dpi' : 100,'figsize': (14,14)}, 
    #     plot_file_name='SquareGrating_XCorr_LGN_On.png'
    # ).plot({
    #     '*.y_lim':(-30,30), 
    #     '*.fontsize':24
    # })
   # PerNeuronPairAnalogSignalListPlot(
    #     dsv,
    #     ParameterSet({
    #         'sheet_name' : 'V1_Exc_L4', 
    #     }),
    #     fig_param={'dpi' : 100,'figsize': (14,14)}, 
    #     plot_file_name='SquareGrating_XCorr_V1e.png'
    # ).plot({
    #     '*.y_lim':(-30,30), 
    #     '*.fontsize':24
    # })
    ## Flashing squares
    # dsv = param_filter_query( data_store, st_name='FlashingSquares', analysis_algorithm=['TrialAveragedCorrectedCrossCorrelation'] )
    # PerNeuronPairAnalogSignalListPlot(
    #     dsv,
    #     ParameterSet({
    #         'sheet_name': 'X_ON'
    #     }),
    #     fig_param={'dpi' : 100,'figsize': (14,14)}, 
    #     plot_file_name='FlashingSquare_XCorr_LGN_On.png'
    # ).plot({
    #     '*.y_lim':(-30,30), 
    #     '*.fontsize':24
    # })
    # PerNeuronPairAnalogSignalListPlot(
    #     dsv,
    #     ParameterSet({
    #         'sheet_name' : 'V1_Exc_L4', 
    #     }),
    #     fig_param={'dpi' : 100,'figsize': (14,14)}, 
    #     plot_file_name='FlashingSquare_XCorr_V1e.png'
    # ).plot({
    #     '*.y_lim':(-30,30), 
    #     '*.fontsize':24
    # })






#########################################################################################
# ---- OVERVIEW ----
def plot_overview( data_store, Xon_ids, Xoff_ids, PGN_ids=None, V1_ids=None, radius="" ):
    if radius:
        addon = f"_{radius[0]}_{radius[1]}"
    else:
        addon = f"_{int(time.time())}"
        
    if len(Xon_ids):
        logger.info(f"Xon_ids: {Xon_ids}")
        for i in Xon_ids:
            OverviewPlot(
               data_store,
               ParameterSet({
                   'spontaneous': False,
                   'sheet_name' : 'X_ON', 
                   'neuron' : i, 
                   'sheet_activity' : {}
               }),
               fig_param={'dpi':100, 'figsize':(19,12)},
               plot_file_name=f"LGN_On_{addon}.png"
            ).plot({
                'Vm_plot.*.y_lim' : (-100,-40),
                '*.fontsize':7
            })

    if len(Xoff_ids):
        logger.info(f"Xoff_ids: {Xoff_ids}")
        for i in Xoff_ids:
            OverviewPlot(
               data_store,
               ParameterSet({
                   'spontaneous': False,
                   'sheet_name' : 'X_OFF', 
                   'neuron' : i, 
                   'sheet_activity' : {}
               }),
               fig_param={'dpi' : 100,'figsize': (19,12)},
               plot_file_name=f"LGN_Off_{i}_{addon}.png"
            ).plot({
                'Vm_plot.*.y_lim' : (-100,-40),
                '*.fontsize':7
            })

    if len(PGN_ids):
        logger.info(f"PGN_ids: {PGN_ids}")
        for i in PGN_ids:
            OverviewPlot(
               data_store,
               ParameterSet({
                   'spontaneous': False,
                   'sheet_name' : 'PGN', 
                   'neuron' : i, 
                   'sheet_activity' : {}
               }),
               fig_param={'dpi' : 100,'figsize': (19,12)},
               plot_file_name=f"PGN_{i}_{addon}.png"
            ).plot({
                'Vm_plot.*.y_lim' : (-100,-40),
                '*.fontsize':7
            })

    if len(V1_ids):
        logger.info(f"V1_ids: {V1_ids}")
        for i in V1_ids:
            OverviewPlot( 
                data_store, 
                ParameterSet({
                    'spontaneous':False, 
                    'sheet_name':'V1_Exc_L4', 
                    'neuron':i, 
                    'sheet_activity':{}
                }), 
                fig_param={'dpi':100,'figsize':(19,12)}, 
                plot_file_name=f"V1_Exc_L4_{i}_{addon}.png"
            ).plot({
                'Vm_plot.*.y_lim':(-110,-50), 
                'Conductance_plot.y_lim':(0,40.0), 
                '*.fontsize':7
            })

