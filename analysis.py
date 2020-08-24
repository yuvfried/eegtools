import numpy as np
from data_ingestion import mat_data


TIMELINE = mat_data['time']


def adjust_python_idx(idx):
    return idx-1


class Signal:

    def __init__(self, values, timeline=TIMELINE):
        self.values = values
        self.baseline = timeline


class EEGSignal(Signal):

    def __init__(self, name, trial, block, timeline=TIMELINE, data=mat_data):
        self.name = name
        self.sub_id = np.argwhere(data['subjects'] == name).flatten()[0]
        self.trial = adjust_python_idx(trial)
        self.block = adjust_python_idx(block)
        self.values = data['s2'][self.sub_id, :, self.trial, self.block]
        super().__init__(self.values, timeline)


class ERPSignal:

    def __init__(self, name, trials, blocks, timeline=TIMELINE, data=mat_data):
        self.name = name
        self.sub_id = np.argwhere(data['subjects'] == name).flatten()[0]
        self.data = data
        self.timeline = timeline
        self.avg_over = self.__discover_avg_over(trials, blocks)
        self.__set_values()
        self.__signal = None
        self.__noise = None
        # self.desc = f"ERPSignal averaged over {self.avg_over}"

    def set_avg(self, over):
        self.avg_over = over
        self.__set_values()

    def __discover_avg_over(self, trials, blocks):
        if isinstance(self.blocks, int):
            if isinstance(self.trials, int):
                raise TypeError("A stochastic combination of trials and blocks"
                                "was passed. Please use EEGSignal(*args).")
            else:
                return "trial"
        else:
            if isinstance(self.trials, int):
                return "block"
            else:
                return None

    def __set_values(self):
        if self.avg_over == "trial":
            self.block = adjust_python_idx(blocks)
            self.trial_start, self.trial_end = adjust_python_idx(self.trials[0]), adjust_python_idx(self.trials[1])
            self.values = self.data['s2'][sub_id,:, self.trial_start:self.trial_end,self.block]
        if self.avg_over == "block":
            self.block_start, self.block_end = adjust_python_idx(self.blocks[0]), adjust_python_idx(self.blocks[1])
            self.trial = adjust_python_idx(trials)
            self.values = self.data['s2'][sub_id,:, self.trial,self.block_start:self.block_end]
        if self.avg_over is None:
            self.trial_start, self.trial_end = adjust_python_idx(self.trials[0]), adjust_python_idx(self.trials[1])
            self.block_start, self.block_end = adjust_python_idx(self.blocks[0]), adjust_python_idx(self.blocks[1])
            self.values = self.data['s2'][sub_id,:, self.trial_start:self.trial_end, self.block_start:self.block_end]

    def fit(self):
        if self.avg_over is None:
            self.__signal = np.nanmean(self.values, axis=(1,2))
            self.__noise = np.nanstd(self.values, axis=(1,2))
        else:   # trial or block are both will be on axis=1
            self.__signal = np.nanmean(self.values, axis=1)
            self.__noise = np.std(self.values, axis=1)

    def signal(self):
        return Signal(self.__signal, self.timeline)

    def noise(self):
        return self.__noise


class Component:
    def __init__(self, orientation, t1, t2, signal, baseline=0):
        self.orientation = orientation
        self.t1, self.t2 = t1, t2
        boundaries = self.__get_t_idx(signal.timeline, [self.t1, self.t2])
        self.timeline = signal.timeline[boundaries[0]:boundaries[1]]
        self.values = signal.values[boundaries[0]:boundaries[1]]
        self.baseline = baseline

    def __str__(self):
        return f'Component {self.orientation}{self.t1}-{self.t2} post-onset'

    def __get_t_idx(self, timeline, t):
        vf = np.vectorize(lambda t: np.argmin(np.abs(timeline - t)))
        return vf(t)  # idx for corresponding t (same length)

    def summation(self, **kwargs):
        return np.nansum(self.values-self.baseline, **kwargs)

    def abs_summation(self):
        return np.nansum(np.abs(self.values-self.baseline))

    def rms(self, **kwargs):
        return np.sqrt(np.nanmean(self.values-self.baseline, **kwargs))

    def peak(self, **kwargs):
        if self.orientation == "N":
            return np.nanmin(self.values - self.baseline, **kwargs)
        if self.orientation == "P":
            return np.max(self.values - self.baseline, **kwargs)

    def auc(self, absolute_val=False, **kwargs):
        if absolute_val:
            return np.trapz(y=np.abs(self.values-self.baseline), x=self.timeline)
        else:
            return np.trapz(y=self.values-self.baseline, x=self.timeline)


def softmax(x):
    return np.exp(x)/np.nansum(np.exp(x))


# note assumes positive vector (consider N1)?
def zero_one_scaling(x):
    mini = np.nanmin(x)
    maxi = np.nanmax(x)
    return (x-mini)/(maxi-mini)


