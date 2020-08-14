import plot


# TODO: append data object to this module
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