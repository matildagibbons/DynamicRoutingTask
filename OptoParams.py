import os
import numpy as np
import scipy.stats
from scipy.interpolate import interpn, LinearNDInterpolator


baseDir = r'\\allen\programs\mindscope\workgroups\dynamicrouting\DynamicRoutingTask\OptoGui'


def txtToDict(f):
    with open(f,'r') as r:
        cols = zip(*[line.strip('\n').split('\t') for line in r.readlines()]) 
    return {d[0]: [float(s) for s in d[1:]] for d in cols}


def getBregmaGalvoCalibrationData(rigName):
    f = os.path.join(baseDir,rigName + '_bregma_galvo.txt')
    return txtToDict(f)
  
  
def bregmaToGalvo(calibrationData,bregmaX,bregmaY):
    px = np.unique(calibrationData['bregmaX'])
    py = np.unique(calibrationData['bregmaY'])
    vx = np.zeros((len(px),len(py)))
    vy = vx.copy()
    for x,y,zx,zy in zip(calibrationData['bregmaX'],calibrationData['bregmaY'],calibrationData['galvoX'],calibrationData['galvoY']):
      i = np.where(px==x)[0][0]
      j = np.where(py==y)[0][0]
      vx[i,j] = zx
      vy[i,j] = zy
    galvoX,galvoY = [interpn((px,py),v,(bregmaX,bregmaY))[0] for v in (vx,vy)]
    return galvoX, galvoY


def galvoToBregma(calibrationData,galvoX,galvoY):
    points = np.stack((calibrationData['galvoX'],calibrationData['galvoY']),axis=1)
    bregmaX,bregmaY = [float(LinearNDInterpolator(points,calibrationData[b])(galvoX,galvoY)) for b in ('bregmaX','bregmaY')]
    return bregmaX, bregmaY


def getOptoPowerCalibrationData(rigName,devName):
    f = os.path.join(baseDir,rigName + '_' + devName + '_power.txt')
    d = txtToDict(f)
    slope,intercept = scipy.stats.linregress(d['input (V)'],d['power (mW)'])[:2]
    d['slope'] = slope
    d['intercept'] = intercept
    return d


def powerToVolts(calibrationData,power):
    return (power - calibrationData['intercept']) / calibrationData['slope']


def voltsToPower(calibrationData,volts):
    return volts * calibrationData['slope'] + calibrationData['intercept']



optoParams = {
              'test': {
                       'V1': {'power': 1, 'bregma': (-3,-3)},
                       'ACC': {'power': 1, 'bregma': (-0.5,1)},
                       'mFC': {'power': 1, 'bregma': (-0.5,2.5)},
                       'lFC': {'power': 1, 'bregma': (-2,2.5)},
			          },
              
              '643280': {
                         'V1': {'power': 5, 'bregma': (-3.5,-4.1)},
                         'ACC': {'power': 5, 'bregma': (-0.75,1)},
                         'mFC': {'power': 5, 'bregma': (-0.8,2.5)},
                         'lFC': {'power': 5, 'bregma': (-2,2.5)},
                        },
              }
