# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 14:37:16 2022

@author: svc_ccg
"""

import argparse
import itertools
import os
import pathlib
import random
import numpy as np
import pandas as pd
import scipy.optimize
import sklearn.metrics
from  DynamicRoutingAnalysisUtils import getFirstExperimentSession, getSessionsToPass, getSessionData


baseDir = pathlib.Path('//allen/programs/mindscope/workgroups/dynamicrouting')


def getSessionsToFit(mouseId,trainingPhase,sessionIndex):
    drSheets,nsbSheets = [pd.read_excel(os.path.join(baseDir,'DynamicRoutingTask',fileName),sheet_name=None) for fileName in ('DynamicRoutingTraining.xlsx','DynamicRoutingTrainingNSB.xlsx')]
    df = drSheets[str(mouseId)] if str(mouseId) in drSheets else nsbSheets[str(mouseId)]
    preExperimentSessions = np.array(['stage 5' in task for task in df['task version']]) & ~np.array(df['ignore'].astype(bool))
    firstExperimentSession = getFirstExperimentSession(df)
    if firstExperimentSession is not None:
        preExperimentSessions[firstExperimentSession:] = False
    preExperimentSessions = np.where(preExperimentSessions)[0]
    if trainingPhase in ('initial training','after learning'):
        if trainingPhase == 'initial training':
            sessions = preExperimentSessions[:5]
        elif trainingPhase == 'after learning':
            sessionsToPass = getSessionsToPass(mouseId,df,preExperimentSessions,stage=5)
            sessions = preExperimentSessions[sessionsToPass:sessionsToPass+5]
        testSession = sessions[sessionIndex]
        trainSessions = [s for s in sessions if s != testSession]
    else:
        sessions = np.array([trainingPhase in task for task in df['task version']]) & ~np.array(df['ignore'].astype(bool))
        sessions = np.where(sessions)[0]
        testSession = sessions[sessionIndex]
        trainSessions = preExperimentSessions[-4:]
    testData = getSessionData(mouseId,df.loc[testSession,'start time'])
    trainData = [getSessionData(mouseId,startTime) for startTime in df.loc[trainSessions,'start time']]
    return testData,trainData


def calcLogisticProb(q,tau,bias):
    return 1 / (1 + np.exp(-(q - 0.5 + bias) / tau))


def runModel(obj,tauAction,biasAction,visConfidence,audConfidence,alphaContext,alphaAction,alphaHabit,decayContext,
             weightContext=False,weightAction=False,weightHabit=False,attendReward=False,useRPE=False,
             useHistory=True,nReps=1):
    stimNames = ('vis1','vis2','sound1','sound2')
    stimConfidence = [visConfidence,audConfidence]

    pContext = 0.5 + np.zeros((nReps,obj.nTrials,2))
    qContext = np.zeros((nReps,obj.nTrials,2,len(stimNames))) 
    if alphaContext > 0:
        qContext[:,:,0,:2] = [visConfidence,1-visConfidence]
        qContext[:,:,1,-2:] = [audConfidence,1-audConfidence]

    qStim = np.zeros((nReps,obj.nTrials,len(stimNames)))
    if alphaAction > 0:
        qStim[:,:] = [visConfidence,1-visConfidence,audConfidence,1-audConfidence]

    wHabit = np.zeros((nReps,obj.nTrials))
    if not weightHabit and alphaHabit > 0:
        wHabit += 0.5
    qHabit = np.array([visConfidence,1-visConfidence,audConfidence,1-audConfidence])

    expectedValue = np.zeros((nReps,obj.nTrials))

    qTotal = np.zeros((nReps,obj.nTrials))

    pAction = np.zeros((nReps,obj.nTrials))
    
    action = np.zeros((nReps,obj.nTrials),dtype=int)
    
    for i in range(nReps):
        for trial,stim in enumerate(obj.trialStim):
            if stim != 'catch':
                modality = 0 if 'vis' in stim else 1
                pStim = np.zeros(len(stimNames))
                pStim[[stim[:-1] in s for s in stimNames]] = [stimConfidence[modality],1-stimConfidence[modality]] if '1' in stim else [1-stimConfidence[modality],stimConfidence[modality]]

                if weightAction:
                    expectedValue[i,trial] = np.sum(qStim[i,trial] * pStim * np.repeat(pContext[i,trial],2))
                else:
                    valContext = np.sum(qContext[i,trial] * pStim[None,:] * pContext[i,trial][:,None])
                    valStim = np.sum(qStim[i,trial] * pStim)
                    if weightContext:
                        wContext = 1 - 2 * pContext[i,trial].min()
                        expectedValue[i,trial] = wContext * valContext  + (1 - wContext) * valStim 
                    else:   
                        if alphaContext > 0:
                            expectedValue[i,trial] = valContext
                        else:
                            expectedValue[i,trial] = valStim

                if weightHabit:
                    wHabit[i,trial] = 1 - 2 * abs(0.5 - expectedValue[i,trial])

                qTotal[i,trial] = (wHabit[i,trial] * np.sum(qHabit * pStim)) + ((1 - wHabit[i,trial]) * expectedValue[i,trial])           
            
                pAction[i,trial] = calcLogisticProb(qTotal[i,trial],tauAction,biasAction)
                
                if useHistory:
                    action[i,trial] = obj.trialResponse[trial]
                elif random.random() < pAction[i,trial]:
                    action[i,trial] = 1 
            
            if trial+1 < obj.nTrials:
                pContext[i,trial+1] = pContext[i,trial]
                qContext[i,trial+1] = qContext[i,trial]
                qStim[i,trial+1] = qStim[i,trial]
                wHabit[i,trial+1] = wHabit[i,trial]
            
                if action[i,trial] or obj.autoRewarded[trial]:
                    outcome = obj.trialRewarded[trial]
                    predictionError = outcome - expectedValue[i,trial]
                    
                    if alphaContext > 0:
                        if stim != 'catch':
                            if useRPE:
                                contextError = predictionError
                            else:
                                if outcome:
                                    contextError = 1 - pContext[i,trial,modality]
                                else:
                                    contextError = 0 if attendReward else -pContext[i,trial,modality] * pStim[0 if modality==0 else 2]
                            pContext[i,trial+1,modality] += alphaContext * contextError
                            pContext[i,trial+1,modality] = np.clip(pContext[i,trial+1,modality],0,1)
                        if decayContext > 0:
                            iti = (obj.trialStartTimes[trial+1] - obj.trialStartTimes[trial])
                            pContext[i,trial+1,modality] += (1 - np.exp(-iti/decayContext)) * (0.5 - pContext[i,trial+1,modality])
                        pContext[i,trial+1,(1 if modality==0 else 0)] = 1 - pContext[i,trial+1,modality]
                    
                    if alphaAction > 0 and stim != 'catch':
                        if attendReward or weightAction or weightContext or alphaContext == 0:
                            qStim[i,trial+1] += alphaAction * pStim * predictionError
                            qStim[i,trial+1] = np.clip(qStim[i,trial+1],0,1)
                        else:
                            qContext[i,trial+1] += alphaAction * pContext[i,trial][:,None] * pStim[None,:] * predictionError
                            qContext[i,trial+1] = np.clip(qContext[i,trial+1],0,1)

                    if not weightHabit and alphaHabit > 0:
                        wHabit[i,trial+1] += alphaHabit * (abs(predictionError) - wHabit[i,trial])
    
    return pContext, qContext, qStim, wHabit, expectedValue, qTotal, pAction, action


def evalModel(params,*args):
    trainData,fixedValInd,fixedVal,modelTypeDict = args
    if fixedVal is not None:
        params = np.insert(params,(fixedValInd[0] if isinstance(fixedValInd,tuple) else fixedValInd),fixedVal)
    response = np.concatenate([obj.trialResponse for obj in trainData])
    prediction = np.concatenate([runModel(obj,*params,**modelTypeDict)[-2][0] for obj in trainData])
    logLoss = sklearn.metrics.log_loss(response,prediction)
    return logLoss


def fitModel(mouseId,trainingPhase,testData,trainData):
    tauActionBounds = (0.01,1)
    biasActionBounds = (-1,1)
    visConfidenceBounds = (0.5,1)
    audConfidenceBounds = (0.5,1)
    alphaContextBounds = (0,1)
    alphaActionBounds = (0,1)
    decayContextBounds = (1,600) 
    alphaHabitBounds = (0,1)

    bounds = (tauActionBounds,biasActionBounds,visConfidenceBounds,audConfidenceBounds,
              alphaContextBounds,alphaActionBounds,decayContextBounds,alphaHabitBounds)

    fixedValueIndices = (None,1,2,3,(4,6),5,(4,5),6,7,(6,7))
    fixedValues = (None,0,1,1,(0,0),0,(0,0),0,0,(0,0))

    modelTypeParamNames = ('weightContext','weightAction','weightHabit','attendReward','useRPE')
    modelTypeNames,modelTypes = zip(
                                    ('contextQ',(0,0,0,0,0)),
                                    #('contextQRPE',(0,0,0,0,1)),
                                    ('weightContext',(1,0,0,0,0)),
                                    #('weightContextRPE',(1,0,0,0,1)),
                                    ('weightAction',(0,1,0,0,0)),
                                    #('weightActionRPE',(0,1,0,0,1)),
                                    ('weightHabit',(0,0,1,0,0)),
                                    ('attendReward',(0,1,0,1,0)),
                                   )

    for modelTypeName,modelType in zip(modelTypeNames,modelTypes):
        modelTypeParams = {p: bool(m) for p,m in zip(modelTypeParamNames,modelType)}
        fit = scipy.optimize.direct(evalModel,bounds,args=(trainData,None,None,modelTypeParams))
        params = [fit.x]
        logLoss = [fit.fun]
        for fixedValInd,fixedVal in zip(fixedValueIndices,fixedValues):
            if fixedVal is not None:
                bnds = tuple(b for i,b in enumerate(bounds) if (i not in fixedValInd if isinstance(fixedValInd,tuple) else i != fixedValInd))
                fit = scipy.optimize.direct(evalModel,bnds,args=(trainData,fixedValInd,fixedVal,modelTypeParams))
                params.append(np.insert(fit.x,(fixedValInd[0] if isinstance(fixedValInd,tuple) else fixedValInd),fixedVal))
                logLoss.append(fit.fun)

        fileName = str(mouseId)+'_'+testData.startTime+'_'+trainingPhase+'_'+modelTypeName+'.npz'
        filePath = os.path.join(baseDir,'Sam','RLmodel',fileName)
        np.savez(filePath,params=params,logLoss=logLoss,**modelTypeParams) 
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mouseId',type=int)
    parser.add_argument('--sessionIndex',type=int)
    parser.add_argument('--trainingPhase',type=str)
    args = parser.parse_args()
    trainingPhase = args.trainingPhase.replace('_',' ')
    testData,trainData = getSessionsToFit(args.mouseId,trainingPhase,args.sessionIndex)
    fitModel(args.mouseId,trainingPhase,testData,trainData)
