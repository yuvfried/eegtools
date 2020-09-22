import plot
import widgets
from ipywidgets import interactive, fixed
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


def group_board(fig, group, trial_start, block_start, trial_end, block_end,
                color, linestyle):
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
    name = f'{group}|{trial_name}|{block_name}'

    rgb = plot.name_to_rgb(color)   # color
    gos = sig.get_gos(name=name,    # title in legend and hovering
                      line_color=plot.read_rgb(rgb),
                      line_dash=linestyle,
                      error_y_color=plot.read_rgb(rgb, error=True),
                      hovertemplate='<b>%{y:.3f}</b>' +     # format of hover
                                    f'<sub>{plot.MICROVOLT_STR}</sub>')

    fig.add_trace(gos)
    fig.show()


def dash_sub():
    fig = plot.init_trial()
    title_text = "Subject Dynamic Within a Given Block-trial Ranges"
    fig.update_layout(title={
        'y': 0.9,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'text': title_text},
        font={'family': 'Arial'},
        legend_title_text='Sub | Trials | Blocks')

    out = interactive(sub_board, {'manual': True},
                                 fig=fixed(fig),
                                 name=widgets.sub_name_dropdown,
                                 trial_start=widgets.trial_start_slider,
                                 block_start=widgets.block_start_slider,
                                 trial_end=widgets.trial_end_slider,
                                 block_end=widgets.block_end_slider)
    return out


def dash_group():
    fig = plot.init_trial()
    title_text = "Group Dynamic Within a Given Block-trial Ranges"
    fig.update_layout(
        title={
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'text': title_text},
        font={'family': 'Arial'},
        legend_title_text='Group|Trials|Blocks',
        hovermode='x unified')

    out = interactive(group_board, {'manual': True, 'manual_name': 'Plot'},
                      fig=fixed(fig),
                      group=widgets.group_name_dropdown,
                      trial_start=widgets.trial_start_slider,
                      block_start=widgets.block_start_slider,
                      trial_end=widgets.trial_end_slider,
                      block_end=widgets.block_end_slider,
                      color=widgets.color,
                      linestyle=widgets.linestyle)
    return out
