import chardet
import pandas as pd
import os
import re
import json
import numpy as np
import yaml

### GLOBALS ###

with open("CONFIG.yaml", 'r') as f:
    doc = yaml.full_load(f)
    BEHAVE_PATH = doc['behave_path']
    # Configured JSON of E-prime patterns
    EPRIME_PAT_FILENAME = doc['eprime_patterns']
    # ingest patterns map (for json relevant fields visit the source json file)
    with open(EPRIME_PAT_FILENAME, 'r') as jf:
        PATTERNS = json.load(jf)

### helpers

def _read_subject(filename):
    with open(filename, 'rb') as f:
        bin_data = f.read()
        encoding = chardet.detect(bin_data)['encoding']
        decoded = bin_data.decode(encoding)
        return decoded


def _field_parser(data_name, data, field, field_type):
    """

    @param data_name: filename of data, for catching regex failures
    @param data: output of _read_subgect
    @param field: one eprime data fields as specified in json config file
    @param field_type: meta or data, see json file
    @return: eprime metadata value for meta field, or eprime trial/block
    values for data fields
    """
    pat = PATTERNS[field_type][field]
    if field_type == "meta":
        try:
            out = re.compile(pat).search(data).group()
        except AttributeError:
            print(f'field: {field} has no match in {data_name}')
            out = None

    elif field_type == "data":
        out = re.compile(pat).findall(data)
        if out == []:
            out = None

    else:
        print(f"incorrect field_type: {field_type}" +
              "allowed are {'meta','data'}")
        out = None

    return out


def extract_trial_rts(filename):
    """

    @param filename: path to E-Prime .txt file
    @return: tuple of: sub_id (str), (340,) np array of RT's
    """
    data = _read_subject(filename)
    name = _field_parser(data_name=filename, data=data, field='Name',
                         field_type='meta')

    # ingest data to np array, RT will be float
    rts = np.array(
        _field_parser(filename, data, 'trial_rt', 'data')
    ).astype(float)
    # replace 0 by NaN
    buttons = np.array(
        _field_parser(filename, data, 'trial_response_button', 'data')
    )
    rts[buttons==''] = np.nan
    # fill anyone who didn't complete all blocks with nan
    if len(rts) != 340:
        rts = np.append(rts, np.repeat(np.nan, 340 - len(rts)))

    return name, rts


sub_ids = []
lst_of_rts = []
files = os.listdir(BEHAVE_PATH)
for fn in files:
    if fn.endswith('.txt'):
        filename = os.path.join(BEHAVE_PATH,fn)
        name, rts = extract_trial_rts(filename)
        sub_ids.append(name)
        lst_of_rts.append(rts)

subjects = np.array(sub_ids)
data = np.stack(lst_of_rts)
