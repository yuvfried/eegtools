import plot
import numpy as np



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


# averaging chronological order: trial-->block-->subject
def subject_erp_block_trial_range(fig, data, sub_id, block, trial, timeline, cmap,
                                   block_end=False, trial_end=False, show_err="blocks"):
    idx = np.argwhere(data['subjects'] == sub_id).flatten()[0]
    group = data['group'][idx]
    block -= 1  # adjust python index
    trial -= 1  # adjust python index

    # multiple blocks and trials
    if not block_end:
        block_end = block+1
    else:
        block_end -= 1
    if not trial_end:
        trial_end = trial+1
    else:
        trial_end -= 1

    # gather data
    sig = data['s2'][idx, :, trial:trial_end, block:block_end]

    # error bars
    if show_err=="blocks":
        err = np.nanstd(sig, axis=2)
    elif show_err=="trials":
        err = np.nanstd(sig, axis=1)
    else:
        err = np.zeros(512)

    # averaging
    if sig.shape[1] > 1:   # multiple trials
        sig = np.nanmean(sig, axis=1)  # averaging over trials
    if sig.shape[1] > 1:   # multiple blocks
        sig = np.nanmean(sig, axis=1)  # averaging over blocks

    sig = sig.reshape(512,)

    gos = plot.go_signal(sig, timeline,
                         error_y=dict(
                             type="data", array=err / 2, visible=True, color=cmap[group]["error"]),
                         name=f'{sub_id} {block} {trial}',
                         line_color=plot.cmap[group]["line"],
                         showlegend=True)
    fig.add_trace(gos)

    fig.show()
