import numpy as np


class Component:
    # TODO: account for timeline boundaries corresponding to N1, P2 etc
    def __init__(self, arr, orientation, baseline=0):
        self.sig = arr
        self.orientation = orientation
        self.baseline = baseline

    def rms(self, **kwargs):
        return np.sqrt(np.nanmean((self.sig-self.baseline)**2, **kwargs))

    def peak(self, **kwargs):
        dist = np.abs(self.sig - self.baseline)
        if self.orientation == "N":
            return np.min(dist, **kwargs)
        if self.orientation == "P":
            return np.max(dist, **kwargs)

    def auc(self, **kwargs):
        # TODO: account for timeline copy from notebook
        return np.trapz(y=np.abs(self.sig-self.baseline))



