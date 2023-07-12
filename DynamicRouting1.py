# -*- coding: utf-8 -*-
"""
Created on Wed Feb 20 15:41:48 2019

@author: SVC_CCG
"""

from __future__ import division
import itertools, json, sys
import random
import numpy as np
from psychopy import visual
from TaskControl import TaskControl


class DynamicRouting1(TaskControl):
    
    def __init__(self,params=None):
        TaskControl.__init__(self,params)
        self.maxFrames = 60 * 3600
        self.maxTrials = None
        
        # block stim is one list per block containing one or more 'vis#' or 'sound#' or a list of these for multimodal stimuli
        # first element rewarded
        # last block continues until end of session
        self.blockStim = [['vis1','vis2']] 
        self.blockStimRewarded = ['vis1']
        self.blockStimProb = None # None for equal sampling or list of probabilities for each stimulus in each block adding to one
        self.customSampling = False # custom stimulus sampling for specific experiments
        self.evenSampling = True # evenly samples stimuli (weighted by their probabilities) within some number of trials
        self.minUnimodalTrials = 0 # min number of trials of each unimodal stimulus each block before presenting multimodal stimuli if evenSampling
        self.blockCatchProb = [0.1] # fraction of trials for each block with no stimulus and no reward
        self.newBlockAutoRewards = 5 # number of autorewarded trials at the start of each block
        self.newBlockGoTrials = 5 # number of consecutive go trials at the start of each block (otherwise random)
        self.newBlockNogoTrials = 0 # number of conscutive nogo trials (non-rewarded modality) at start of each block; set newBlockGoTrials to 0
        self.firstBlockNogoStim = None # use if newBlockNogoTrials > 0
        
        self.trialsPerBlock = None # None or sequence of trial numbers for each block; use this or framesPerBlock or variableBlocks
        self.framesPerBlock = None # None or sequence of frame numbers for each block
        self.variableBlocks = False
        self.variableBlockMinFrames = 10 * 3600
        self.variableBlockMaxFrames = 30 * 3600
        self.variableBlockThresholdTrials = 10
        self.variableBlockHitThreshold = 0.8
        self.variableBlockFalseAlarmThreshold = 0.4

        self.preStimFramesFixed = 90 # min frames between start of trial and stimulus onset
        self.preStimFramesVariableMean = 60 # mean of additional preStim frames drawn from exponential distribution
        self.preStimFramesMax = 360 # max total preStim frames
        self.quiescentFrames = 90 # frames before stim onset during which licks delay stim onset
        self.responseWindow = [6,60]
        self.postResponseWindowFrames = 180

        self.autoRewardOnsetFrame = 60 # frames after stimulus onset at which autoreward occurs
        self.autoRewardMissTrials = 10 # None or consecutive miss trials after which autoreward delivered on next go trial

        self.rewardProbGo = 1 # probability of reward after response on go trial
        self.rewardProbCatch = 0 # probability of autoreward at end of response window on catch trial
        
        self.rewardSound = None if self.configPath is None else 'device' # None, 'device' (external clicker), 'tone', or 'noise' for sound played with reward delivery
        self.rewardSoundDur = 0.1 # seconds
        self.rewardSoundVolume = 0.1 # 0-1
        self.rewardSoundLevel = 68 # dB
        self.rewardSoundFreq = 10000 # Hz
        
        self.incorrectTrialRepeats = 0 # maximum number of incorrect trial repeats
        self.incorrectTimeoutFrames = 0 # extended gray screen following incorrect trial
        self.incorrectTimeoutColor = 0 # -1 to 1
        self.incorrectSound = None # None, 'tone', or 'noise' for sound played after incorrect trial
        self.incorrectSoundDur = 3 # seconds
        self.incorrectSoundVolume = 0.1 # 0-1
        self.incorrectSoundLevel = 68 # dB
        self.incorrectSoundFreq = [2000,20000] # Hz
        
        # visual stimulus params
        # parameters that can vary across trials are lists
        self.visStimType = 'grating'
        self.visStimFrames = [30] # duration of visual stimulus
        self.visStimContrast = [1]
        self.gratingSize = 50 # degrees
        self.gratingSF = 0.04 # cycles/deg
        self.gratingTF = 0 # cycles/s
        self.gratingOri = {'vis1':[0],'vis2':[90]} # clockwise degrees from vertical
        self.gratingPhase = [0,0.5]
        self.gratingType = 'sqr' # 'sin' or sqr'
        self.gratingEdge= 'raisedCos' # 'circle' or 'raisedCos'
        self.gratingEdgeBlurWidth = 0.08 # only applies to raisedCos
        
        # auditory stimulus params
        self.saveSoundArray = False
        self.soundType = 'tone' # 'tone', 'linear sweep', 'log sweep', 'noise', 'AM noise', or dict
        self.soundDur = [0.5] # seconds
        self.soundVolume = [0.08] # 0-1; used if soundCalibrationFit is None
        self.soundLevel = [68] # dB; used if soundCalibrationFit is not None
        self.toneFreq = {'sound1':6000,'sound2':10000} # Hz
        self.linearSweepFreq = {'sound1':[6000,10000],'sound2':[10000,6000]}
        self.logSweepFreq = {'sound1':[3,2.5],'sound2':[3,3.5]} # log2(kHz)
        self.noiseFiltFreq = {'sound1':[4000,8000],'sound2':[8000,16000]} # Hz
        self.ampModFreq = {'sound1':12,'sound2':70} # Hz
            
        # opto params
        self.optoDevName = 'laser_488'
        self.optoProb = 0
        self.optoNewBlocks = [] # blocks to apply opto stim during new block go trials
        self.optoOnsetFrame = [0] # frame relative to stimulus onset
        self.optoDur = [1] # seconds
        self.optoSinFreq = 40 # Hz
        self.optoOnRamp = 0 # seconds
        self.optoOffRamp = 0.1 # seconds
        self.optoOffsetVoltage = 0
        self.optoVoltage = []
        self.optoPower = [] # mW
        self.importOptoRegions = False
        self.optoRegions = [] # ['V1']
        self.optoBregma = [] # [(x,y)]
        self.galvoVoltage = [] # [(x,y)]
        
        if params is not None and 'taskVersion' in params:
            self.taskVersion = params['taskVersion']
            self.setDefaultParams(params['taskVersion'])
        else:
            self.taskVersion = None

    
    def setDefaultParams(self,taskVersion):
        # dynamic routing task versions
        if taskVersion in ('stage 0','stage 0 moving'):
            # auto rewards
            self.blockStim = [['vis1','vis2']]
            self.blockStimRewarded = ['vis1']
            self.maxTrials = 150
            self.newBlockAutoRewards = 150
            self.quiescentFrames = 0
            self.blockCatchProb = [0]
            if 'moving' in taskVersion:
                self.gratingTF = 2

        elif taskVersion in ('stage 1','stage 1 moving','stage 1 timeouts','stage 1 moving timeouts',
                             'stage 1 AMN timeouts','stage 1 AMN moving timeouts'):
            # ori discrim with or without timeouts
            self.blockStim = [['vis1','vis2']]
            self.blockStimRewarded = ['vis1']
            self.incorrectTrialRepeats = 3
            if 'moving' in taskVersion:
                self.gratingTF = 2
            if 'timeouts' in taskVersion:
                if 'AMN' not in taskVersion:
                    self.incorrectSound = 'noise'
                self.incorrectTimeoutFrames = 180
                self.incorrectTimeoutColor = -1

        elif taskVersion in ('stage 2','stage 2 timeouts',
                             'stage 2 AMN','stage 2 AMN timeouts'):
            # tone discrim with or without timeouts
            self.soundType = 'AM noise' if 'AMN' in taskVersion else 'tone'
            self.blockStim = [['sound1','sound2']]
            self.blockStimRewarded = ['sound1']
            self.incorrectTrialRepeats = 3
            if 'timeouts' in taskVersion:
                if 'AMN' not in taskVersion:
                    self.incorrectSound = 'noise'
                self.incorrectTimeoutFrames = 180
                self.incorrectTimeoutColor = -1

        elif taskVersion in ('stage 3 ori','stage 3 ori moving','stage 3 ori timeouts','stage 3 ori moving timeouts',
                             'stage 3 tone','stage 3 tone timeouts','stage 3 AMN','stage 3 AMN timeouts'):
            # ori or tone discrim
            if 'ori' in taskVersion:
                self.blockStim = [['vis1','vis2']]
                self.blockStimRewarded = ['vis1']
            else:
                self.soundType = 'AM noise' if 'AMN' in taskVersion else 'tone'
                self.blockStim = [['sound1','sound2']]
                self.blockStimRewarded = ['sound1']
            if 'moving' in taskVersion:
                self.gratingTF = 2
            if 'timeouts' in taskVersion:
                if 'AMN' not in taskVersion:
                    self.incorrectSound = 'noise'
                self.incorrectTimeoutFrames = 180
                self.incorrectTimeoutColor = -1

        elif taskVersion in ('stage 3 ori distract','stage 3 ori distract moving',
                             'stage 3 ori distract timeouts','stage 3 ori distract moving timeouts',
                             'stage 3 tone distract','stage 3 tone distract timeouts',
                             'stage 3 ori AMN distract','stage 3 ori AMN distract moving',
                             'stage 3 ori AMN distract timeouts','stage 3 ori AMN distract moving timeouts',
                             'stage 3 AMN distract','stage 3 AMN distract timeouts'):
            # ori or tone discrim with distractors
            self.blockStim = [['vis1','vis2','sound1','sound2']]
            self.soundType = 'AM noise' if 'AMN' in taskVersion else 'tone'
            if 'ori' in taskVersion:
                self.blockStimRewarded = ['vis1']
            else:
                self.blockStimRewarded = ['sound1']
            if 'moving' in taskVersion:
                self.gratingTF = 2
            if 'timeouts' in taskVersion:
                if 'AMN' not in taskVersion:
                    self.incorrectSound = 'noise'
                self.incorrectTimeoutFrames = 180
                self.incorrectTimeoutColor = -1

        elif taskVersion in ('stage 4 ori tone','stage 4 tone ori',
                             'stage 4 ori tone moving','stage 4 tone ori moving',
                             'stage 4 ori tone timeouts','stage 4 tone ori timeouts',
                             'stage 4 ori tone moving timeouts','stage 4 tone ori moving timeouts',
                             'stage 4 ori tone ori','stage 4 ori tone ori timeouts',
                             'stage 4 ori tone ori moving','stage 4 ori tone ori moving timeouts',
                             'stage 4 ori AMN','stage 4 AMN ori',
                             'stage 4 ori AMN moving','stage 4 AMN ori moving',
                             'stage 4 ori AMN timeouts','stage 4 AMN ori timeouts',
                             'stage 4 ori AMN moving timeouts','stage 4 AMN ori moving timeouts',
                             'stage 4 ori AMN ori','stage 4 ori AMN ori timeouts',
                             'stage 4 ori AMN ori moving','stage 4 ori AMN ori moving timeouts'):
            # 2 or 3 blocks of all 4 stimuli, switch rewarded modality
            if 'ori tone ori' in taskVersion or 'ori AMN ori' in taskVersion:
                self.blockStim = [['vis1','vis2','sound1','sound2']] * 3
                self.blockStimRewarded = ['vis1','sound1','vis1']
                self.framesPerBlock = np.array([20] * 3) * 3600
                self.blockCatchProb = [0.1] * 3
            else:
                self.blockStim = [['vis1','vis2','sound1','sound2']] * 2
                if 'ori tone' in taskVersion or 'ori AMN' in taskVersion:
                    self.blockStimRewarded = ['vis1','sound1']
                else:
                    self.blockStimRewarded = ['sound1','vis1']
                self.framesPerBlock = np.array([30,30]) * 3600
                self.blockCatchProb = [0.1,0.1]
            self.soundType = 'AM noise' if 'AMN' in taskVersion else 'tone'
            self.maxFrames = None
            if 'moving' in taskVersion:
                self.gratingTF = 2
            if 'timeouts' in taskVersion:
                if 'AMN' not in taskVersion:
                    self.incorrectSound = 'noise'
                self.incorrectTimeoutFrames = 180
                self.incorrectTimeoutColor = -1

        elif taskVersion in ('stage 5 ori tone','stage 5 tone ori',
                             'stage 5 ori tone moving','stage 5 tone ori moving',
                             'stage 5 ori tone timeouts','stage 5 tone ori timeouts',
                             'stage 5 ori tone moving timeouts','stage 5 tone ori moving timeouts',
                             'stage 5 ori AMN','stage 5 AMN ori',
                             'stage 5 ori AMN moving','stage 5 AMN ori moving',
                             'stage 5 ori AMN timeouts','stage 5 AMN ori timeouts',
                             'stage 5 ori AMN moving timeouts','stage 5 AMN ori moving timeouts',
                             'stage 5 ori AMN moving timeouts repeats','stage 5 AMN ori moving timeouts repeats',
                             'stage 5 ori AMN moving nogo','stage 5 AMN ori moving nogo',
                             'stage 5 ori AMN moving timeouts nogo','stage 5 AMN ori moving timeouts nogo',
                             'stage 5 ori AMN moving noAR','stage 5 AMN ori moving noAR',
                             'stage 5 ori AMN moving timeouts noAR','stage 5 AMN ori moving timeouts noAR',
                             'ephys ori AMN moving','ephys AMN ori moving'):
            # 6 blocks
            self.blockStim = [['vis1','vis2','sound1','sound2']] * 6
            self.soundType = 'AM noise' if 'AMN' in taskVersion else 'tone'
            if 'ori tone' in taskVersion or 'ori AMN' in taskVersion:
                self.blockStimRewarded = ['vis1','sound1'] * 3
            else:
                self.blockStimRewarded = ['sound1','vis1'] * 3
            self.maxFrames = None
            self.framesPerBlock = np.array([10] * 6) * 3600
            self.blockCatchProb = [0.1] * 6
            if 'moving' in taskVersion:
                self.gratingTF = 2
            if 'timeouts' in taskVersion:
                if 'AMN' not in taskVersion:
                    self.incorrectSound = 'noise'
                self.incorrectTimeoutFrames = 180
                self.incorrectTimeoutColor = -1
            if 'repeats' in taskVersion:
                self.incorrectTrialRepeats = 3
            if 'nogo' in taskVersion:
                self.newBlockAutoRewards = 0
                self.newBlockGoTrials = 0
                self.newBlockNogoTrials = 5
                self.firstBlockNogoStim = 'sound1' if self.blockStimRewarded[0] == 'vis1' else 'vis1'
            if 'noAR' in taskVersion:
                self.newBlockAutoRewards = 0
                self.newBlockGoTrials = 0
            if 'ephys' in taskVersion and self.rigName in ('NP2','NP3'):
                self.saveSoundArray = True


        elif taskVersion in ('stage variable ori tone','stage variable tone ori',
                             'stage variable ori tone moving','stage variable tone ori moving',
                             'stage variable ori tone timeouts','stage variable tone ori timeouts',
                             'stage variable ori tone moving timeouts','stage variable tone ori moving timeouts',
                             'stage variable ori AMN','stage variable AMN ori',
                             'stage variable ori AMN moving','stage variable AMN ori moving',
                             'stage variable ori AMN timeouts','stage variable AMN ori timeouts',
                             'stage variable ori AMN moving timeouts','stage variable AMN ori moving timeouts'):
            # 6 blocks
            self.variableBlocks = True
            self.blockStim = [['vis1','vis2','sound1','sound2']] * 6
            self.soundType = 'AM noise' if 'AMN' in taskVersion else 'tone'
            if 'ori tone' in taskVersion or 'ori AMN' in taskVersion:
                self.blockStimRewarded = ['vis1','sound1'] * 3
            else:
                self.blockStimRewarded = ['sound1','vis1'] * 3
            self.blockCatchProb = [0.1] * 6
            if 'moving' in taskVersion:
                self.gratingTF = 2
            if 'timeouts' in taskVersion:
                if 'AMN' not in taskVersion:
                    self.incorrectSound = 'noise'
                self.incorrectTimeoutFrames = 180
                self.incorrectTimeoutColor = -1        

        elif taskVersion in ('multimodal ori tone','multimodal tone ori','multimodal ori AMN','multimodal AMN ori',
                             'multimodal ori tone moving','multimodal tone ori moving','multimodal ori AMN moving','multimodal AMN ori moving'):
            self.blockStim = [['vis1','vis2','sound1','sound2','vis1+sound1']] * 6
            self.customSampling = 'multimodal'
            self.soundType = 'AM noise' if 'AMN' in taskVersion else 'tone'
            if 'ori tone' in taskVersion or 'ori AMN' in taskVersion:
                self.blockStimRewarded = ['vis1','sound1'] * 3
            else:
                self.blockStimRewarded = ['sound1','vis1'] * 3
            self.maxFrames = None
            self.framesPerBlock = np.array([10] * 6) * 3600
            self.blockCatchProb = [0.1] * 6
            if 'moving' in taskVersion:
                self.gratingTF = 2

        elif taskVersion in ('contrast volume ori tone','contrast volume tone ori','contrast volume ori AMN','contrast volume AMN ori',
                             'contrast volume ori tone moving','contrast volume tone ori moving','contrast volume ori AMN moving','contrast volume AMN ori moving'):
            self.blockStim = [['vis1','vis2','sound1','sound2']] * 6
            self.customSampling = 'contrast volume'
            self.soundType = 'AM noise' if 'AMN' in taskVersion else 'tone'
            if 'ori tone' in taskVersion or 'ori AMN' in taskVersion:
                self.blockStimRewarded = ['vis1','sound1'] * 3
            else:
                self.blockStimRewarded = ['sound1','vis1'] * 3
            self.maxFrames = None
            self.framesPerBlock = np.array([10] * 6) * 3600
            self.blockCatchProb = [0.1] * 6
            if 'moving' in taskVersion:
                self.gratingTF = 2
            self.visStimContrast = [0.01,0.02,0.04,0.08,0.16]
            self.soundVolume = [0.005,0.01,0.02,0.04,0.08]

        elif taskVersion in ('opto stim ori tone','opto stim tone ori','opto stim ori tone moving','opto stim tone ori moving',
                             'opto stim ori AMN','opto stim AMN ori','opto stim ori AMN moving','opto stim AMN ori moving',
                             'opto new block ori tone','opto new block tone ori','opto new block ori tone moving','opto new block tone ori moving',
                             'opto new block ori AMN','opto new block AMN ori','opto new block ori AMN moving','opto new block AMN ori moving',
                             'opto pre ori tone','opto pre tone ori','opto pre ori tone moving','opto pre tone ori moving',
                             'opto pre ori AMN','opto pre AMN ori','opto pre ori AMN moving','opto pre AMN ori moving'):
            if 'ori tone' in taskVersion or 'ori AMN' in taskVersion:
                self.blockStimRewarded = ['vis1','sound1'] * 3
            else:
                self.blockStimRewarded = ['sound1','vis1'] * 3
            self.blockStim = [['vis1','vis2','sound1','sound2']] * 6
            self.blockCatchProb = [0.1] * 6
            if 'moving' in taskVersion:
                self.gratingTF = 2
            self.soundType = 'AM noise' if 'AMN' in taskVersion else 'tone'
            self.maxFrames = None
            self.framesPerBlock = np.array([10] * 6) * 3600
            self.importOptoParams = True
            if 'opto stim' in taskVersion:
                self.customSampling = 'opto even'
                self.optoProb = 0.2
                self.optoOnsetFrame = [0]
                self.optoDur = [1.0]
            elif 'opto new block' in taskVersion:
                self.optoNewBlocks = [2,3,5,6]
                self.optoOnsetFrame = [0]
                self.optoDur = [1.0] 
                self.optoRegions = ['V1','mFC','V1','mFC']
            elif 'opto pre' in taskVersion:
                self.customSampling = 'opto even'
                self.optoProb = 0.5
                self.optoOnsetFrame = [-42]
                self.optoDur = [0.5]     
        
        # templeton task versions
        elif 'templeton' in taskVersion:
            self.maxFrames = 60 * 3600
            self.autoRewardOnsetFrame = 6
            self.visStimFrames = [30]
            self.soundDur = [0.5]
            self.responseWindow = [6,60]
            self.quiescentFrames = 90
            self.blockCatchProb = [0.1]
            self.soundType = 'AM noise' if 'AMN' in taskVersion else 'tone'
            if 'DG' in taskVersion:
                self.gratingTF = 2
            # self.soundType = 'tone'
            self.newBlockGoTrials = 5
            self.newBlockAutoRewards = 5
            self.autoRewardMissTrials = 10

            if 'stage 0 vis' in taskVersion:
                self.blockStim = [['vis1','vis2']]
                self.blockStimRewarded = ['vis1']
                self.maxTrials = 150
                self.newBlockAutoRewards = 150
                self.quiescentFrames = 0
                self.blockCatchProb = [0]

            elif 'stage 1 vis' in taskVersion:
                self.blockStim = [['vis1','vis2']]
                self.blockStimRewarded = ['vis1']
                self.incorrectTimeoutFrames = 180
                self.incorrectTimeoutColor = -1
                self.incorrectTrialRepeats = 3

            elif 'stage 2 vis' in taskVersion:
                self.blockStim = [['vis1','vis2','sound1','sound2']]
                self.blockStimRewarded = ['vis1']
                self.visStimFrames = [30,45,60]
                self.soundDur = [0.5,0.75,1.0]
                self.preStimFramesVariableMean = 30 
                self.preStimFramesMax = 240
                self.postResponseWindowFrames = 120

            elif 'stage 0 aud' in taskVersion:
                self.blockStim = [['sound1','sound2']]
                self.blockStimRewarded = ['sound1']
                self.maxTrials = 150
                self.newBlockAutoRewards = 150
                self.quiescentFrames = 0
                self.blockCatchProb = [0]

            elif 'stage 1 aud' in taskVersion:
                self.blockStim = [['sound1','sound2']]
                self.blockStimRewarded = ['sound1']
                self.incorrectTimeoutFrames = 180
                if 'AMN' not in taskVersion:
                    self.incorrectSound = 'noise'
                self.incorrectTrialRepeats = 3

            elif 'stage 2 aud' in taskVersion:
                self.blockStim = [['sound1','sound2','vis1','vis2']]
                self.blockStimRewarded = ['sound1']
                self.visStimFrames = [30,45,60]
                self.soundDur = [0.5,0.75,1.0]
                self.preStimFramesVariableMean = 30 
                self.preStimFramesMax = 240
                self.postResponseWindowFrames = 120

            elif 'test' in taskVersion:
                self.maxFrames = 0.5 * 3600
                self.blockStim = [['vis1','vis2','sound1','sound2']]
                self.blockStimRewarded = ['vis1']
                self.visStimFrames = [30,45,60]
                self.soundDur = [0.5,0.75,1.0]
                self.preStimFramesVariableMean = 30 
                self.preStimFramesMax = 240
                self.postResponseWindowFrames = 120
                self.newBlockGoTrials = 0
                self.newBlockAutoRewards = 0
        else:
            raise ValueError(taskVersion + ' is not a recognized task version')        
    

    def checkParamValues(self):
        pass


    def variableBlockThresholdPassed(self,blockNumber,blockFrameCount):
        if blockFrameCount >= self.variableBlockMaxFrames:
            return True
        elif blockFrameCount < self.variableBlockMinFrames:
            return False
        else:
            trialStim = np.array(self.trialStim)
            blockTrials = (np.array(self.trialBlock) == blockNumber) & (~np.array(self.trialAutoRewarded)) & (trialStim != 'catch')
            rewardedStim = self.blockStimRewarded[blockNumber-1]
            goTrials = blockTrials & (trialStim == rewardedStim)
            nogoTrials = blockTrials & ~goTrials & np.in1d(trialStim,('vis1','sound1'))
            n = self.variableBlockThresholdTrials
            trialResponse = np.array(self.trialResponse)
            if (goTrials.sum() < n or nogoTrials.sum() < n or
                trialResponse[goTrials][-n:].sum() < self.variableBlockHitThreshold * n or
                trialResponse[nogoTrials][-n:].sum() > self.variableBlockFalseAlarmThreshold * n):
                return False
            else:
                return True
            
    
    def setRewardSound(self):
        if self.rewardSound == 'device':
            self._rewardSound = True
        elif self.rewardSound is not None:
            self._sound = [self.rewardSoundArray]
        

    def taskFlow(self):
        self.checkParamValues()
        
        # create visual stimulus
        if self.visStimType == 'grating':
            edgeBlurWidth = {'fringeWidth':self.gratingEdgeBlurWidth} if self.gratingEdge=='raisedCos' else None
            visStim = visual.GratingStim(win=self._win,
                                         units='pix',
                                         mask=self.gratingEdge,
                                         maskParams=edgeBlurWidth,
                                         tex=self.gratingType,
                                         pos=(0,0),
                                         size=int(self.gratingSize * self.pixelsPerDeg), 
                                         sf=self.gratingSF / self.pixelsPerDeg)
            
        # convert dB to volume
        if self.soundCalibrationFit is not None:
            self.soundVolume = [self.dBToVol(dB,*self.soundCalibrationFit) for dB in self.soundLevel]
            self.rewardSoundVolume = self.dBToVol(self.rewardSoundLevel,*self.soundCalibrationFit)
            self.incorrectSoundVolume = self.dBToVol(self.incorrectSoundLevel,*self.soundCalibrationFit)

        # sound for reward or incorrect response
        if self.rewardSound is not None and self.rewardSound != 'device':
            self.rewardSoundArray = self.makeSoundArray(soundType=self.rewardSound,
                                                        dur=self.rewardSoundDur,
                                                        vol=self.rewardSoundVolume,
                                                        freq=self.rewardSoundFreq)
        if self.incorrectSound is not None:
            self.incorrectSoundArray = self.makeSoundArray(soundType=self.incorrectSound,
                                                           dur=self.incorrectSoundDur,
                                                           vol=self.incorrectSoundVolume,
                                                           freq=self.incorrectSoundFreq)
        
        # opto params
        if self.optoProb > 0 or len(self.optoNewBlocks) > 0:
            self.getOptoParams()

        # things to keep track of
        self.trialStartFrame = []
        self.trialEndFrame = []
        self.trialPreStimFrames = []
        self.trialStimStartFrame = []
        self.trialStim = []
        self.trialVisStimFrames = []
        self.trialVisStimContrast = []
        self.trialGratingOri = []
        self.trialGratingPhase = []
        self.trialSoundType = []
        self.trialSoundDur = []
        self.trialSoundVolume = []
        self.trialSoundFreq = []
        self.trialSoundAM = []
        self.trialSoundSeed = []
        self.trialSoundArray = []
        self.trialResponse = []
        self.trialResponseFrame = []
        self.trialRewarded = []
        self.trialAutoRewardScheduled = []
        self.trialAutoRewarded = []
        self.trialOptoOnsetFrame = []
        self.trialOptoDur = []
        self.trialOptoVoltage = []
        self.trialGalvoVoltage = []
        self.quiescentViolationFrames = [] # frames where quiescent period was violated
        self.trialRepeat = [False]
        self.trialBlock = []
        blockNumber = 0 # current block
        blockTrials = None # total number of trials to occur in current block
        blockFrames = None # total number of frames to occur in current block
        blockTrialCount = 0 # number of trials completed in current block
        blockFrameCount = 0 # number of frames completed in current block
        blockAutoRewardCount = 0
        missTrialCount = 0
        incorrectRepeatCount = 0
        
        # run loop for each frame presented on the monitor
        while self._continueSession:
            # get rotary encoder and digital input states
            self.getInputData()
            
            # if starting a new trial
            if self._trialFrame == 0:
                preStimFrames = randomExponential(self.preStimFramesFixed,self.preStimFramesVariableMean,self.preStimFramesMax)
                if len(self.trialStartFrame) < 1:
                    preStimFrames += self.postResponseWindowFrames
                self.trialPreStimFrames.append(preStimFrames) # can grow larger than preStimFrames during quiescent period
                
                if self.trialRepeat[-1]:
                    self.trialStim.append(self.trialStim[-1])
                else:
                    if (blockNumber == 0 or 
                        (blockNumber < len(self.blockStim) and
                         ((blockTrialCount == blockTrials or (blockFrames is not None and blockFrameCount >= blockFrames)) or
                           (self.variableBlocks and self.variableBlockThresholdPassed(blockNumber,blockFrameCount))))):
                        # start new block of trials
                        blockNumber += 1
                        blockTrials = None if self.trialsPerBlock is None else self.trialsPerBlock[blockNumber-1]
                        blockFrames = None if self.framesPerBlock is None else self.framesPerBlock[blockNumber-1]
                        blockTrialCount = 0
                        blockFrameCount = 0
                        blockAutoRewardCount = 0
                        missTrialCount = 0
                        incorrectRepeatCount = 0
                        blockStim = self.blockStim[blockNumber-1]
                        stimProb = None if self.blockStimProb is None else self.blockStimProb[blockNumber-1]
                        catchProb = self.blockCatchProb[blockNumber-1]
                        stimSample = []
                        optoVoltage = []
                        galvoVoltage = []

                    visStimFrames = 0
                    visStim.contrast = 0
                    visStim.ori = 0
                    visStim.phase = 0
                    soundType = ''
                    soundDur = 0
                    soundVolume = 0
                    soundFreq = [np.nan]*2
                    soundAM = np.nan
                    soundSeed = random.randrange(2**32)
                    soundArray = np.array([])
                    customContrastVolume = False
                    customOpto = False
                    
                    if blockTrialCount < self.newBlockGoTrials + self.newBlockNogoTrials:
                        if self.newBlockGoTrials > 0:
                            stim = self.blockStimRewarded[blockNumber-1]
                        else:
                            if blockNumber > 1:
                                stim = self.blockStimRewarded[blockNumber-2] # previously rewarded stim
                            else:
                                stim = self.firstBlockNogoStim
                        self.trialStim.append(stim)
                        if blockNumber in self.optoNewBlocks:
                            customOpto = True
                            self.trialOptoOnsetFrame.append(self.optoOnsetFrame[0])
                            self.trialOptoDur.append(self.optoDur[0])
                            i = self.optoNewBlocks.index(blockNumber)
                            self.trialOptoVoltage.append(self.optoVoltage[i])
                            self.trialGalvoVoltage.append(self.galvoVoltage[i])
                    elif self.customSampling:
                        if self.customSampling == 'opto even':
                            if len(stimSample) < 1:
                                stimSample = np.array(blockStim*len(self.optoVoltage)*int(1/self.optoProb) + ['catch']*(len(self.optoVoltage)+1))
                                optoVoltage = np.full(stimSample.size,np.nan)
                                galvoVoltage = np.full((stimSample.size,2),np.nan)
                                n = len(blockStim)
                                for i,(ov,gv) in enumerate(zip(self.optoVoltage,self.galvoVoltage)):
                                    optoVoltage[i*n:i*n+n] = ov
                                    optoVoltage[-i-1] = ov
                                    galvoVoltage[i*n:i*n+n] = gv
                                    galvoVoltage[-i-1] = gv
                                randIndex = np.random.permutation(stimSample.size)
                                stimSample = list(stimSample[randIndex])
                                optoVoltage = list(optoVoltage[randIndex])
                                galvoVoltage = list(galvoVoltage[randIndex])
                            self.trialStim.append(stimSample.pop(0))
                            self.trialOptoVoltage.append(optoVoltage.pop(0))
                            self.trialGalvoVoltage.append(galvoVoltage.pop(0))
                            if np.isnan(self.trialOptoVoltage[-1]):
                                self.trialOptoOnsetFrame.append(np.nan)
                                self.trialOptoDur.append(np.nan)
                            else:
                                self.trialOptoOnsetFrame.append(self.optoOnsetFrame[0])
                                self.trialOptoDur.append(self.optoDur[0])
                            customOpto = True
                        elif self.customSampling == 'multimodal':
                            if len(stimSample) < 1:
                                unimodalStim = [stim for stim in blockStim if '+' not in stim]
                                if blockTrialCount == self.newBlockGoTrials:
                                    stimSample = unimodalStim * 2 + ['catch']
                                else:
                                    stimSample = unimodalStim + blockStim + ['catch']
                                random.shuffle(stimSample)
                            self.trialStim.append(stimSample.pop(0))
                        elif self.customSampling == 'contrast volume':
                            if len(stimSample) < 1:
                                for stim in blockStim:
                                    if 'vis' in stim and 'sound' in stim:
                                        stimSample += list(itertools.product([stim],self.visStimContrast,self.soundVolume))
                                    elif 'vis' in stim:
                                        stimSample += list(itertools.product([stim],self.visStimContrast,[0]))
                                    elif 'sound' in stim:
                                        stimSample += list(itertools.product([stim],[0],self.soundVolume))
                                stimSample += [('catch',0,0)]
                                random.shuffle(stimSample)
                            stim,contrast,soundVolume = stimSample.pop(0)
                            visStim.contrast = contrast
                            self.trialStim.append(stim)
                            customContrastVolume = True
                        else:
                            raise ValueError(self.customSampling + ' is not a recognized cumstom sampling version')
                    elif random.random() < catchProb:
                        self.trialStim.append('catch')
                    elif self.evenSampling:
                        if len(stimSample) < 1:
                            if blockTrialCount == self.newBlockGoTrials and self.minUnimodalTrials > 0:
                                unimodalStim = [stim for stim in blockStim if '+' not in stim]
                                unimodalSample = random.sample(unimodalStim*self.minUnimodalTrials,len(unimodalStim)*self.minUnimodalTrials)
                            else:
                                unimodalSample = []
                            if stimProb is None:
                                # even sampling every len(blockStim)*n trials
                                n = 5
                                stimSample = random.sample(blockStim*n,len(blockStim)*n)
                            else:
                                # proportional sampling every ~100 trials
                                prob = [1/len(blockStim) for _ in len(blockStim)] if stimProb is None else stimProb
                                stimSample = [[stim] * round(p*100) for stim,p in zip(blockStim,prob)]
                                stimSample = [s for stim in stimSample for s in stim]
                                random.shuffle(stimSample)
                            stimSample = unimodalSample + stimSample
                        self.trialStim.append(stimSample.pop(0))
                    else:   
                        self.trialStim.append(np.random.choice(blockStim,p=stimProb))  
                        
                    stimNames = self.trialStim[-1].split('+')
                    visName = [stim for stim in stimNames if 'vis' in stim]
                    visName = visName[0] if len(visName) > 0 else None
                    soundName = [stim for stim in stimNames if 'sound' in stim]
                    soundName = soundName[0] if len(soundName) > 0 else None
                    if visName is not None:
                        visStimFrames = random.choice(self.visStimFrames)
                        if not customContrastVolume:
                            visStim.contrast = max(self.visStimContrast) if blockTrialCount < self.newBlockGoTrials else random.choice(self.visStimContrast)
                        if self.visStimType == 'grating':
                            visStim.ori = random.choice(self.gratingOri[visName])
                            visStim.phase = random.choice(self.gratingPhase)
                    if soundName is not None:
                        soundType = self.soundType[soundName] if isinstance(self.soundType,dict) else self.soundType
                        soundDur = random.choice(self.soundDur)
                        if not customContrastVolume:
                            soundVolume = max(self.soundVolume) if blockTrialCount < self.newBlockGoTrials else random.choice(self.soundVolume)
                        if soundType == 'tone':
                            soundFreq = self.toneFreq[soundName]
                        elif soundType == 'linear sweep':
                            soundFreq = self.linearSweepFreq[soundName]
                        elif soundType == 'log sweep':
                            soundFreq = self.logSweepFreq[soundName]
                        elif soundType == 'noise':
                            soundFreq = self.noiseFiltFreq[soundName]
                        elif soundType == 'AM noise':
                            soundFreq = (2000,20000)
                            soundAM = self.ampModFreq[soundName]
                        soundArray = self.makeSoundArray(soundType,soundDur,soundVolume,soundFreq,soundAM,soundSeed)
                
                optoWaveform = galvoX = galvoY = None
                if customOpto or blockTrialCount >= self.newBlockGoTrials and random.random() < self.optoProb:
                    if not customOpto:
                        self.trialOptoOnsetFrame.append(random.choice(self.optoOnsetFrame))
                        self.trialOptoDur.append(random.choice(self.optoDur))
                        self.trialOptoVoltage.append(random.choice(self.optoVoltage))
                        self.trialGalvoVoltage.append(random.choice(self.galvoVoltage))
                    if not np.isnan(self.trialOptoVoltage[-1]):
                        optoWaveform = self.getOptoPulseWaveform(self.trialOptoVoltage[-1],self.trialOptoDur[-1],self.optoSinFreq,self.optoOnRamp,self.optoOffRamp,self.optoOffsetVoltage)
                        galvoX,galvoY = self.trialGalvoVoltage[-1]
                else:
                    self.trialOptoOnsetFrame.append(np.nan)
                    self.trialOptoDur.append(np.nan)
                    self.trialOptoVoltage.append(np.nan)
                    self.trialGalvoVoltage.append([np.nan]*2)
                    
                self.trialStartFrame.append(self._sessionFrame)
                self.trialBlock.append(blockNumber)
                self.trialVisStimFrames.append(visStimFrames)
                self.trialVisStimContrast.append(visStim.contrast)
                self.trialGratingOri.append(visStim.ori)
                self.trialGratingPhase.append(visStim.phase)
                self.trialSoundType.append(soundType)
                self.trialSoundDur.append(soundDur)
                self.trialSoundVolume.append(soundVolume)
                if soundType == 'tone':
                    self.trialSoundFreq.append([soundFreq,np.nan])
                else:
                    self.trialSoundFreq.append(soundFreq)
                self.trialSoundAM.append(soundAM)
                self.trialSoundSeed.append(soundSeed)
                if self.saveSoundArray:
                    self.trialSoundArray.append(soundArray)
                
                if self.blockStimRewarded[blockNumber-1] in self.trialStim[-1]:
                    isGo = True
                    if blockAutoRewardCount < self.newBlockAutoRewards or missTrialCount == self.autoRewardMissTrials:
                        self.trialAutoRewardScheduled.append(True)
                        autoRewardFrame = self.autoRewardOnsetFrame
                        blockAutoRewardCount += 1
                    else:
                        self.trialAutoRewardScheduled.append(False)
                        autoRewardFrame = None
                    rewardSize = self.solenoidOpenTime if autoRewardFrame is not None or random.random() < self.rewardProbGo else 0
                else:
                    isGo = False
                    if self.trialStim[-1] == 'catch' and random.random() < self.rewardProbCatch:
                        self.trialAutoRewardScheduled.append(True)
                        autoRewardFrame = self.responseWindow[1]
                        rewardSize = self.solenoidOpenTime
                    else:
                        self.trialAutoRewardScheduled.append(False)
                        autoRewardFrame = None
                        rewardSize = 0
                
                optoTriggered = False
                hasResponded = False
                rewardDelivered = False
                autoRewardDelivered = False
                timeoutFrames = 0

            # extend pre stim gray frames if lick occurs during quiescent period
            if not optoTriggered and self._lick and self.trialPreStimFrames[-1] - self.quiescentFrames < self._trialFrame < self.trialPreStimFrames[-1]:
                self.quiescentViolationFrames.append(self._sessionFrame)
                self.trialPreStimFrames[-1] += randomExponential(self.preStimFramesFixed,self.preStimFramesVariableMean,self.preStimFramesMax)
            
            # trigger opto stimulus
            if optoWaveform is not None and self._trialFrame == self.trialPreStimFrames[-1] + self.trialOptoOnsetFrame[-1]:
                self._opto = [optoWaveform,galvoX,galvoY]
                optoTriggered = True
            
            # show/trigger stimulus
            if self._trialFrame == self.trialPreStimFrames[-1]:
                self.trialStimStartFrame.append(self._sessionFrame)
                if soundDur > 0:
                    self._sound = [soundArray]
            if (visStimFrames > 0
                and self.trialPreStimFrames[-1] <= self._trialFrame < self.trialPreStimFrames[-1] + visStimFrames):
                if self.gratingTF > 0:
                    visStim.phase = visStim.phase + self.gratingTF/self.frameRate
                visStim.draw()
            
            # trigger auto reward
            if autoRewardFrame is not None and not rewardDelivered and self._trialFrame == self.trialPreStimFrames[-1] + autoRewardFrame:
                self._reward = rewardSize
                self.setRewardSound()
                self.trialRewarded.append(True)
                self.trialAutoRewarded.append(True)
                rewardDelivered = True
                autoRewardDelivered = True
            
            # check for response within response window
            if (self._lick and not hasResponded 
                and self.trialPreStimFrames[-1] + self.responseWindow[0] <= self._trialFrame < self.trialPreStimFrames[-1] + self.responseWindow[1]):
                self.trialResponse.append(True)
                self.trialResponseFrame.append(self._sessionFrame)
                if isGo:
                    if rewardSize > 0 and not rewardDelivered:
                        self._reward = rewardSize
                        self.setRewardSound()
                        self.trialRewarded.append(True)
                        rewardDelivered = True
                elif self.trialStim[-1] != 'catch':
                    timeoutFrames = self.incorrectTimeoutFrames
                hasResponded = True  
                
            # start timeout stimuli at end of response window
            if timeoutFrames > 0:
                if self._trialFrame == self.trialPreStimFrames[-1] + self.responseWindow[1]:
                    self._win.color = self.incorrectTimeoutColor
                    if self.incorrectSound is not None:
                        self.stopSound()
                        self._sound = [self.incorrectSoundArray]
                elif self._trialFrame == self.trialPreStimFrames[-1] + self.responseWindow[1] + timeoutFrames:
                    self._win.color = self.monBackgroundColor
            
            # end trial after response window plus any post response window frames and timeout
            if self._trialFrame == self.trialPreStimFrames[-1] + self.responseWindow[1] + self.postResponseWindowFrames + timeoutFrames:
                if not hasResponded:
                    self.trialResponse.append(False)
                    self.trialResponseFrame.append(np.nan)

                if not rewardDelivered:
                    self.trialRewarded.append(False)
                    
                if not autoRewardDelivered:
                    self.trialAutoRewarded.append(False)

                if isGo:
                    if hasResponded or rewardDelivered:
                        missTrialCount = 0
                    else:
                        missTrialCount += 1
                    
                self.trialEndFrame.append(self._sessionFrame)
                self._trialFrame = -1
                blockTrialCount += 1
                
                if (not isGo and self.trialStim[-1] != 'catch' and self.trialResponse[-1]  
                    and incorrectRepeatCount < self.incorrectTrialRepeats):
                    # repeat trial after response to unrewarded stimulus
                    incorrectRepeatCount += 1
                    self.trialRepeat.append(True)
                else:
                    incorrectRepeatCount = 0
                    self.trialRepeat.append(False)

                if len(self.trialStartFrame) == self.maxTrials:
                    self._continueSession = False

                self.publishAccumulatorInterface()
            
            blockFrameCount += 1
            if (blockNumber == len(self.blockStim) and 
                (blockTrialCount == blockTrials or (blockFrames is not None and blockFrameCount >= blockFrames))):
                self._continueSession = False

            self.showFrame()



def randomExponential(fixed,variableMean,maxTotal):
    val = fixed + random.expovariate(1/variableMean) if variableMean > 1 else fixed + variableMean
    return int(min(val,maxTotal))



if __name__ == "__main__":
    paramsPath = sys.argv[1]
    with open(paramsPath,'r') as f:
        params = json.load(f)
    task = DynamicRouting1(params)
    task.start(params['subjectName'])