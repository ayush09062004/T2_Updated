import numpy as np
from mozaik.experiments import *
from mozaik.experiments.vision import *
from mozaik.experiments.MyInterruptedBarStimulus import *
from mozaik.sheets.population_selector import RCRandomPercentage
from mozaik.sheets.population_selector import RCSpace
from parameters import ParameterSet

def create_experiments_spontaneous(model):
    return [
        MeasureSpontaneousActivity(
            model,
            parameters=ParameterSet({
                'num_trials': 6,
                'duration': 1029
            })
        )
    ]

def create_experiments_luminance(model):
    return [
        NoStimulation(
            model,
            parameters=ParameterSet({'duration': 1029})
        ),
        MeasureFlatLuminanceSensitivity(
            model,
            parameters=ParameterSet({
                'luminances': [0.0, 0.00001, 0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 100.0],
                'step_duration': 2*147*7,
                'num_trials': 6,
                'shuffle_stimuli': False
            })
        )
    ]

def create_experiments_contrast(model):
    return [
        NoStimulation(
            model,
            parameters=ParameterSet({'duration': 147*7})
        ),
        MeasureContrastSensitivity(
            model,
            parameters=ParameterSet({
                #'size': 20.0,
                'orientation': 0.0,
                'spatial_frequency': 0.5,
                'temporal_frequency': 2.0,
                'grating_duration': 2*147*7,
                'contrasts': [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0],
                'num_trials': 6,
                'shuffle_stimuli': False
            })
        )
    ]

def create_experiments_spatial(model):
    return [
        NoStimulation(
            model,
            parameters=ParameterSet({'duration': 147*7})
        ),
        MeasureFrequencySensitivity(
            model,
            parameters=ParameterSet({
                'orientation': 0.0,
                'contrasts': [80],
                'spatial_frequencies': [0.07, 0.1, 0.2, 0.3, 0.5, 0.8, 1.0, 1.5, 2.0, 8.0],
                'temporal_frequencies': [2.0],
                'grating_duration': 2*147*7,
                #'frame_duration': 7,
                'num_trials': 6,
                'square': False,
                'shuffle_stimuli': False,
            })
        )
    ]

def create_experiments_temporal(model):
    return [
        NoStimulation(
            model,
            parameters=ParameterSet({'duration': 147*7})
        ),
        MeasureFrequencySensitivity(
            model,
            parameters=ParameterSet({
                'orientation': 0.0,
                'contrasts': [80],
                'spatial_frequencies': [0.5],
                'temporal_frequencies': [0.05, 0.2, 1.2, 3.0, 6.4, 8, 12, 30],
                'grating_duration': 10*147*7,
                #'frame_duration': 7,
                'num_trials': 1,
                'square': False,
                'shuffle_stimuli': False
            })
        )
    ]

def create_experiments_orientation(model):
    return [
        NoStimulation(
            model,
            parameters=ParameterSet({'duration': 147*7})
        ),
        MeasureOrientationTuningFullfield(
            model,
            parameters=ParameterSet({
                'num_orientations': 1,
                'spatial_frequency': 0.5,
                'temporal_frequency': 2.0,
                'grating_duration': 1*147*7,
                'contrasts': [80],
                'num_trials': 15,
                'shuffle_stimuli': False
            })
        )
    ]

def create_experiments_size(model):
    return [
        NoStimulation(
            model,
            parameters=ParameterSet({'duration': 147*7})
        ),
        MeasureSizeTuning(
            model,
            parameters=ParameterSet({
                'num_sizes': 1,
                'max_size': 2.0,
                'orientations': [0.0],
                'spatial_frequency': 0.5,
                'temporal_frequency': 2.0,
                'grating_duration': 1*147*7,
                'contrasts': [80],
                'num_trials': 15,
                'log_spacing': False,
                'positions': [(0,0)],
                'shuffle_stimuli': False,
                #'with_flat': False

            })
        )
    ]

def create_experiments_size_overlapping(model):
    return [
        NoStimulation(
            model,
            parameters=ParameterSet({'duration': 147*7})
        ),
        MeasureSizeTuning(
            model,
            parameters=ParameterSet({
                'num_sizes': 10,
                'max_size': 5.0,
                'orientations': [0.0],
                'spatial_frequency': 0.5,
                'temporal_frequency': 2.0,
                'grating_duration': 1*147*7,
                'contrasts': [80],
                'num_trials': 6,
                'log_spacing': True,
                'shuffle_stimuli': False,
                'positions': [(0,0)]
                #'with_flat': False
            })
        )
    ]

def create_experiments_size_nonoverlapping(model):
    return [
        NoStimulation(
            model,
            parameters=ParameterSet({'duration': 147*7})
        ),
        MeasureSizeTuning(
            model,
            parameters=ParameterSet({
                'num_sizes': 10,
                'max_size': 5.0,
                'orientations': [np.pi/2],
                'spatial_frequency': 0.5,
                'temporal_frequency': 2.0,
                'grating_duration': 1*147*7,
                'contrasts': [80],
                'num_trials': 6,
                'log_spacing': True,
                'shuffle_stimuli': False,
                'positions': [(0,0)]
                #'with_flat': False
            })
        )
    ]

def create_experiments_size_V1_inactivated_overlapping(model):
    return [
        NoStimulation(
            model,
            duration=147*7
        ),
        MeasureSizeTuningWithInactivation(
            model,
            sheet_list=["V1_Exc_L4"],
            injection_configuration={
                'component': 'mozaik.sheets.population_selector.RCAnnulus',
                'params': {'inner_radius': 0.0, 'outer_radius': 0.4}
            },
            injection_current=-0.5,
            num_sizes=10,
            max_size=5.0,
            orientations=[0.0],
            spatial_frequency=0.5,
            temporal_frequency=2.0,
            grating_duration=1*147*7,
            contrasts=[80],
            num_trials=6,
            log_spacing=True
        )
    ]

def create_experiments_size_V1_inactivated_nonoverlapping(model):
    return [
        NoStimulation(
            model,
            duration=147*7
        ),
        MeasureSizeTuningWithInactivation(
            model,
            sheet_list=["V1_Exc_L4"],
            injection_configuration={
                'component': 'mozaik.sheets.population_selector.RCAnnulus',
                'params': {'inner_radius': 0.4, 'outer_radius': 1.0}
            },
            injection_current=-0.5,
            num_sizes=10,
            max_size=5.0,
            orientations=[np.pi/2],
            spatial_frequency=0.5,
            temporal_frequency=2.0,
            grating_duration=1*147*7,
            contrasts=[80],
            num_trials=6,
            log_spacing=True
        )
    ]

def create_experiments_annulus(model):
    return [
        NoStimulation(
            model,
            parameters=ParameterSet({'duration': 147*7})
        ),
        MeasureAnnulusTuning(
            model,
            parameters=ParameterSet({
                'num_sizes': 10,
                'max_inner_diameter': 3.0,
                'outer_diameter': 10.0,
                'orientation': 0,
                'log_spacing': False,
                'spatial_frequency': 0.5,
                'temporal_frequency': 2.0,
                'grating_duration': 2*147*7,
                'contrasts': [100],
                'num_trials': 10
            })
        )
    ]

def create_interrupted_bar(model):
    return [
        CustomInterruptedBarStimulus(
            model,
            parameters=ParameterSet({
                'x': 0,
                'y': 0,
                'length': 20,
                'width': 1/0.8/4.0,
                'orientation': 0,
                'max_offset': 2.4*1/0.8/4.0,
                'steps': 3,
                'duration': 2*143*7,
                'flash_duration': 2*143*7,
                'relative_luminances': [1.0],
                'num_trials': 10,
                'gap_lengths': [0.4],
                'shuffle_stimuli': True,
                'disalignment': 0
            })
        )
    ]


