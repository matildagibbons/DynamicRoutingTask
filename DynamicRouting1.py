# -*- coding: utf-8 -*-
"""
Created on Wed Feb 20 15:41:48 2019

@author: SVC_CCG
"""

from __future__ import division
import random
import numpy as np
import psychopy
psychopy.prefs.hardware['audioLib'] = ['PTB'] # import sound after setting audioLib pref
from psychopy import visual, sound  
from TaskControl import TaskControl


class DynamicRouting1(TaskControl):
    
    def __init__(self,rigName,taskVersion=None):
        TaskControl.__init__(self,rigName)
        
        self.maxTrials = None
        self.spacebarRewardsEnabled = False
        
        # block stim is one list per block containing 1 or 2 of 'vis#' or 'sound#'
        # first element rewarded
        self.blockStim = [['vis1']]
        self.trialsPerBlock = None # None or [min,max] trials per block
        self.maxBlocks = 1
        self.newBlockAutoRewards = 5
        
        self.probCatch = 0.15 # fraction of trials with no stimulus and no reward
        
        self.preStimFramesFixed = 180 # min frames between end of previous trial and stimulus onset
        self.preStimFramesVariableMean = 60 # mean of additional preStim frames drawn from exponential distribution
        self.preStimFramesMax = 300 # max total preStim frames
        self.quiescentFrames = 45 # frames before stim onset during which wheel movement delays stim onset
        
        self.responseWindow = [9,45]
        
        self.useIncorrectSound = False # play sound when trial is incorrect
        self.incorrectTrialRepeats = 0 # maximum number of incorrect trial repeats
        self.incorrectTimeoutFrames = 0 # extended gray screen following incorrect trial
        
        # visual stimulus params
        # parameters that can vary across trials are lists
        self.visStimType = 'grating'
        self.visStimFrames = 6 # duration of visual stimulus
        self.visStimContrast = [1]
        self.gratingSize = 25 # degrees
        self.gratingSF = 0.08 # cycles/deg
        self.gratingOri = {'vis1':0,'vis2':90} # clockwise degrees from vertical
        self.gratingType = 'sqr' # 'sqr' or 'sin'
        self.gratingEdge= 'raisedCos' # 'circle' or 'raisedCos'
        self.gratingEdgeBlurWidth = 0.08 # only applies to raisedCos
        
        # auditory stimulus params
        self.soundType = None # 'tone'
        self.soundVolume = 1 # 0-1
        self.soundDur = 0.1 # seconds
        self.toneFreq = {'sound1':5000,'sound2':10000} # Hz
        
        if taskVersion is not None:
            self.setDefaultParams(taskVersion)

    
    def setDefaultParams(self,taskVersion):
        if taskVersion == '1':
            # grating detection
            self.visStimContrast = [0.25,0.5,1]
        
        elif taskVersion == '2':
            # grating detection switch to sound
            self.sefDefaultParams(taskVersion=1)
            self.blockStim = [['vis1'],['sound1','vis1']]
            self.soundType = 'tone'
            self.toneFreq['sound1'] = 8000
            self.trialsPerBlock = [100] * 2
            self.maxBlocks = 2
            
        elif taskVersion == '3':
            # grating ori discrimination
            self.blockStim = [['vis1','vis2']]
            
        elif taskVersion == '4':
            # grating ori discrimination switch
            self.blockStim = [['vis1','vis2'],['vis2','vis1']]
            self.trialsPerBlock = [100] * 2
            self.maxBlocks = 2
    
    
    def checkParamValues(self):
        pass
        

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
        
        # create auditory stimulus
        if self.soundMode == 'internal':
            if self.soundType == 'tone':
                soundStim = sound.Sound(self.toneFreq['sound1'],volume=self.soundVolume,secs=self.soundDur)
        
        # things to keep track of
        self.trialStartFrame = []
        self.trialEndFrame = []
        self.trialPreStimFrames = []
        self.trialStimStartFrame = []
        self.trialStim = []
        self.trialVisStimContrast = []
        self.trialGratingOri = []
        self.trialResponse = []
        self.trialResponseFrame = []
        self.trialRewarded = []
        self.trialAutoRewarded = []
        self.quiescentMoveFrames = [] # frames where quiescent period was violated
        self.trialRepeat = [False]
        self.trialBlock = []
        self.blockStimRewarded = [] # stimulus that is rewarded each block
        blockNumber = 0 # current block
        blockTrials = 0 # total number of trials in current block
        blockTrialCount = 0 # number of trials completed in current block
        blockAutoRewardCount = 0
        incorrectRepeatCount = 0
        
        # run loop for each frame presented on the monitor
        while self._continueSession:
            # get rotary encoder and digital input states
            self.getNidaqData()
            
            # if starting a new trial
            if self._trialFrame == 0:
                preStimFrames = randomExponential(self.preStimFramesFixed,self.preStimFramesVariableMean,self.preStimFramesMax)
                self.trialPreStimFrames.append(preStimFrames) # can grow larger than preStimFrames during quiescent period
                
                if self.trialRepeat[-1]:
                    self.trialStim.append(self.trialStim[-1])
                else:
                    if blockNumber > 0 and random.random() < self.probCatch:
                        self.trialStim.append('catch')
                        visStim.contrast = 0
                    else:
                        if blockNumber == 0 or (blockNumber < self.maxBlocks and blockTrialCount == blockTrials):
                            # start new block of trials
                            blockNumber += 1
                            blockTrials = None if self.trialsPerBlock is None else random.randint(*self.trialsPerBlock)
                            blockTrialCount = 0
                            blockAutoRewardCount = 0
                            blockStim = self.blockStim[(blockNumber-1) % len(self.blockStim)]
                            self.blockStimRewarded.append(blockStim[0])
                        self.trialStim.append(random.choice(blockStim))
                        if 'vis' in self.trialStim[-1]:
                            visStim.contrast = random.choice(self.visStimContrast)
                            if self.visStimType == 'grating':
                                visStim.ori = self.gratingOri[self.trialStim[-1]]
                        else:
                            visStim.contrast = 0
                            if self.soundMode == 'internal':
                                soundStim.setSound(self.toneFreq[self.trialStim[-1]],secs=self.soundDur)
                
                self.trialStartFrame.append(self._sessionFrame)
                self.trialVisStimContrast.append(visStim.contrast)
                if self.visStimType == 'grating':
                    self.trialGratingOri.append(visStim.ori)
                self.trialBlock.append(blockNumber)
                
                if self.trialStim[-1] == self.blockStimRewarded[-1]:
                    if blockAutoRewardCount < self.newBlockAutoRewards:
                        self.trialAutoRewarded.append(True)
                        blockAutoRewardCount += 1
                    else:
                        self.trialAutoRewarded.append(False)
                    rewardSize = self.solenoidOpenTime
                else:
                    self.trialAutoRewarded.append(False)
                    rewardSize = 0
                
                hasResponded = False

            # extend pre stim gray frames if wheel moving during quiescent period
            if self.trialPreStimFrames[-1] - self.quiescentFrames < self._trialFrame < self.trialPreStimFrames[-1]:
                if self._lick:
                    self.quiescentMoveFrames.append(self._sessionFrame)
                    self.trialPreStimFrames[-1] += randomExponential(self.preStimFramesFixed,self.preStimFramesVariableMean,self.preStimFramesMax)
            
            # show/trigger stimulus
            if self._trialFrame == self.trialPreStimFrames[-1]:
                self.trialStimStartFrame.append(self._sessionFrame)
                if 'sound' in self.trialStim[-1]:
                    if self.soundMode == 'external':
                        self._sound = self.trialStim[-1]
                    else:
                        self._sound = soundStim
            if (visStim.contrast > 0
                and self.trialPreStimFrames[-1] <= self._trialFrame < self.trialPreStimFrames[-1] + self.visStimFrames):
                visStim.draw()
            
            # trigger auto reward at beginning of response window
            if self.trialAutoRewarded[-1] and self._trialFrame == self.trialPreStimFrames[-1] + self.responseWindow[0]:
                self._reward = rewardSize
                self.trialRewarded.append(True)
            
            # check for response within response window
            if (self._lick and not hasResponded 
                and self.trialPreStimFrames[-1] + self.responseWindow[0] <= self._trialFrame < self.trialPreStimFrames[-1] + self.responseWindow[1]):
                self.trialResponse.append(True)
                self.trialResponseFrame.append(self._sessionFrame)
                if not (self.trialAutoRewarded[-1] or self.trialStim[-1] == 'catch'):
                    if rewardSize > 0:
                        self.trialRewarded.append(True)
                        self._reward = rewardSize
                    else:
                        self.trialRewarded.append(False)
                        if self.useIncorrectSound:
                            pass # add this later if needed
                hasResponded = True
                
            # end trial after response window
            if self._trialFrame == self.trialPreStimFrames[-1] + self.responseWindow[1]:
                if not hasResponded:
                    self.trialResponse.append(False)
                    self.trialResponseFrame.append(np.nan)
                    self.trialRewarded.append(False)
                elif self.trialStim[-1] == 'catch':
                    self.trialRewarded.append(False)
                    
                self.trialEndFrame.append(self._sessionFrame)
                self._trialFrame = -1
                
                blockTrialCount += 1
                
                if (self.trialStim[-1] != 'catch' and not self.trialRewarded[-1]  
                    and incorrectRepeatCount < self.incorrectTrialRepeats):
                    incorrectRepeatCount += 1
                    self.trialRepeat.append(True)
                else:
                    incorrectRepeatCount = 0
                    self.trialRepeat.append(False)
            
            self.showFrame()
            
            if len(self.trialStartFrame) == self.maxTrials:
                self._continueSession = False



def randomExponential(fixed,variableMean,maxTotal):
    val = fixed + random.expovariate(1/variableMean) if variableMean > 1 else fixed + variableMean
    return int(min(val,maxTotal))


if __name__ == "__main__":
    import sys,json
    paramsPath = sys.argv[1]
    with open(paramsPath,'r') as f:
        params = json.load(f)
    task = DynamicRouting1(params['rigName'],params['taskVersion'])
    task.maxTrials = 10
    task.start(params['subjectName'])