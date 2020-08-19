import numpy as np


def softmax(x):
    return np.exp(x)/np.nansum(np.exp(x))


def zero_one_scaling(x):
    mini = np.nanmin(x)
    maxi = np.nanmax(x)
    return (x-mini)/(maxi-mini)


class Component:
    def __init__(self, orientation, t1, t2, baseline=0):
        self.t1, self.t2 = t1, t2
        self.orientation = orientation
        self.baseline = baseline
        self.sig = None  # will be declared by using 'fit'
        self.timeline = None

    def __str__(self):
        return f'{self.orientation} Component {self.t1}-{self.t2} post onset'

    def isfit(self):
        if self.sig is None:
            return False
        else:
            return True

    # t is a 2d-vector
    def __get_t_idx(self, timeline, t):
        vf = np.vectorize(lambda t: np.argmin(np.abs(timeline - t)))
        return vf(t)  # idx for corresponding t (same length)

    def fit(self, sig, timeline):
        start_idx, stop_idx = self.__get_t_idx(timeline, [self.t1, self.t2])
        self.timeline = timeline[start_idx:stop_idx]
        self.sig = sig[start_idx:stop_idx]

    def summation(self, **kwargs):
        return np.nansum(self.sig-self.baseline, **kwargs)

    def abs_summation(self):
        return np.nansum(np.abs(self.sig-self.baseline))

    def rms(self, **kwargs):
        return np.sqrt(np.nanmean(self.sig-self.baseline, **kwargs))

    def peak(self, **kwargs):
        if self.orientation == "N":
            return np.nanmin(self.sig - self.baseline, **kwargs)
        if self.orientation == "P":
            return np.max(self.sig - self.baseline, **kwargs)

    def auc(self, absolute_val=False, **kwargs):
        if absolute_val:
            return np.trapz(y=np.abs(self.sig-self.baseline), x=self.timeline)
        else:
            return np.trapz(y=self.sig-self.baseline, x=self.timeline)



