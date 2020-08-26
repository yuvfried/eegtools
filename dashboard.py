from analysis import EEGSignal, ERPSignal, GroupSignal


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


def group_board(fig, group, trial_start, block_start, trial_end, block_end):
    if (not trial_end) or (trial_start==trial_end):
        trials = trial_start
        trial_name = trial_start
    else:
        trials = (trial_start, trial_end)
        trial_name = f'{trial_start}-{trial_end}'
    if (not block_end) or (block_start==block_end):
        blocks = block_start
        block_name = block_start
    else:
        blocks = (block_start, block_end)
        block_name = f'{block_start}-{block_end}'

    grouped = GroupSignal(group, trials, blocks)
    sig = grouped.fit()
    name = f'{trial_name}|{block_name}'
    gos = sig.get_gos(name=name)
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
