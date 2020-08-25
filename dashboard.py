import plot
import numpy as np
from analysis import EEGSignal, ERPSignal


def sub_board(fig, name, trial_start, block_start, trial_end, block_end):
    if (not trial_end and not block_end) or \
            (trial_start==trial_end and block_start==block_end): # stochastic cases
        sig = EEGSignal(name, trial=trial_start, block=block_start)
        name = f'{sig.name}|{sig.trial + 1}|{sig.block + 1}'
    else:
        if (block_start==block_end) or (not block_end):
            erp = ERPSignal(name, (trial_start, trial_end), block_start)
            name = f'{erp.name}|{erp.trial_start + 1}-{erp.trial_end + 1}|{erp.block + 1}'
        elif (trial_start==trial_end) or (not trial_end):
            erp = ERPSignal(name, trial_start, (block_start,block_end))
            name = f'{erp.name}|{erp.trial+1}|{erp.block_start+1}-{erp.block_end+1}'
        else:
            erp = ERPSignal(name, (trial_start,trial_end), (block_start,block_end))
            name = f'{erp.name}|{erp.trial_start+1}-{erp.trial_end+1}|{erp.block_start+1}-{erp.block_end+1}'
        sig = erp.fit()

    gos = sig.get_gos(name=name)
    fig.add_trace(gos)
    fig.show()

def group_erp_block_trial_range(fig, group_name, block_range, trial_range, timeline, cmap):
    """
Group ERP Dynamics over a given Range of Blocks and Trials
(averaging order: trial-->block-->subject)
    @param fig: plotly figure
    @param group_name: str {'Control','ASD'}
    @param block_range:
    @param trial_range:
    @param timeline:
    @param cmap:
    """
    idx = get_groups_idx(data)[group_name]
    sig = np.nanmean(data['s2'][idx,  # subjects range
                     :,  # time
                     trial_range[0]:trial_range[1],  # trials
                     block_range[0]:block_range[1]],  # blocks
                     axis=2)  # averaging over trials

    sig = np.nanmean(sig, axis=2)  # averaging over blocks
    sig = np.nanmean(sig, axis=0)  # averaging over subjects

    gos = plot.go_signal(sig, timeline,
                         name=
                         f'{group_name}, {block_range[0] - block_range[1]}, {trial_range[0]}-{trial_range[1]}',
                         line_color=cmap[group_name])
    fig.add_trace(gos)

    fig.show()


# # averaging chronological order: trial-->block-->subject
# def subject_erp_block_trial_range(fig, data, sub_id, block, trial, timeline, cmap,
#                                    block_end=False, trial_end=False, show_err="blocks"):
#     idx = np.argwhere(data['subjects'] == sub_id).flatten()[0]
#     group = data['group'][idx]
#     block -= 1  # adjust python index
#     trial -= 1  # adjust python index
#
#     # multiple blocks and trials
#     if not block_end:
#         block_end = block+1
#     else:
#         block_end -= 1
#     if not trial_end:
#         trial_end = trial+1
#     else:
#         trial_end -= 1
#
#     # gather data
#     sig = data['s2'][idx, :, trial:trial_end, block:block_end]
#
#     # error bars
#     if show_err=="blocks":
#         err = np.nanstd(sig, axis=2)
#     elif show_err=="trials":
#         err = np.nanstd(sig, axis=1)
#     else:
#         err = np.zeros(512)
#
#     # averaging
#     if sig.shape[1] > 1:   # multiple trials
#         sig = np.nanmean(sig, axis=1)  # averaging over trials
#     if sig.shape[1] > 1:   # multiple blocks
#         sig = np.nanmean(sig, axis=1)  # averaging over blocks
#
#     sig = sig.reshape(512,)
#
#     gos = plot.go_signal(sig, timeline,
#                          error_y=dict(
#                              type="data", array=err / 2, visible=True, color=cmap[group]["error"]),
#                          name=f'{sub_id} {block} {trial}',
#                          line_color=plot.cmap[group]["line"],
#                          showlegend=True)
#     fig.add_trace(gos)
#
#     fig.show()
