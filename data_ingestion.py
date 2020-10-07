import scipy.io as sio
import yaml
import numpy as np
import json
import chardet
import re
import os


class MatIngest:
    '''
    Ingestion of Matlab Structure into Python using scipy.io

    ...

    Attributes
    ----------
    filename: str
        path to .mat file
    data_name: str
        the name where the data is (e.g "Data_All")

    Methods
    -------
    create_data_obj
        creates a Python Dict object represents the Matlab Structure
    '''

    def __init__(self, filename, data_name):
        self.file = sio.loadmat(filename,
                                struct_as_record=False, squeeze_me=True)
        self.struct = self.file[data_name]

    def create_data_obj(self):
        """

        :return: a Dict contains Matlab Structure
        """
        struct = self.struct
        d = {}
        for attr in struct._fieldnames:
            d[attr] = getattr(struct, attr)
        # next line defined 2d-array: rows are empty signals and columns are
        # sub_id, trial, block
        d['null'] = np.argwhere(np.all(
            np.isnan(d['s2']), axis=1))
        return d


class EPrime:
    '''
    Parser of txt file represents E-Prime behavioural data (files from
    "2s blocks" folder).

    ...

    Attributes
    ----------
    filename: str
        path to E-Prime txt file consisting behavioural data
    patterns: dict
        nested dict: 2nd level keys are 'meta' and 'data', each of them
        consist regex patterns for extract meta data or RT data (respectively)
        from E-Prime files.
    '''

    def __init__(self, filename, patterns):
        self.filename = filename
        with open(filename, 'rb') as f:
            bin_data = f.read()
            encoding = chardet.detect(bin_data)['encoding']
            self.decoded = bin_data.decode(encoding)
        self.patterns = patterns

    def field_parser(self, field, field_type):
        """

        @param field: one eprime data fields as specified in json config file
        @param field_type: meta or data, see json file
        @return: eprime metadata value for meta field, or eprime trial/block
        values for data fields
        """
        pat = self.patterns[field_type][field]
        if field_type == "meta":
            try:
                out = re.compile(pat).search(self.decoded).group()
            except AttributeError:
                print(f'field: {field} has no match in {self.filename}')
                out = None

        elif field_type == "data":
            out = re.compile(pat).findall(self.decoded)
            if out == []:
                out = None

        else:
            print(f"incorrect field_type: {field_type}" +
                  "allowed are {'meta','data'}")
            out = None

        return out

    def extract_trial_rts(self):
        """
        @return: (340,) np array of RT's
        """

        # ingest data to np array, RT will be float
        rts = np.array(
            self.field_parser('trial_rt', 'data')
        ).astype(float)
        # replace 0 by NaN
        buttons = np.array(
            self.field_parser('trial_response_button', 'data')
        )
        rts[buttons == ''] = np.nan
        # fill anyone who didn't complete all blocks with nan
        if len(rts) != 340:
            rts = np.append(rts, np.repeat(np.nan, 340 - len(rts)))

        return rts


class BehaveIngest:
    '''
    Ingestion of whole txt files in E-Prime data folder ("2s blocks").
    Wrapper for EPrime parser for all txt files in the folder

    ...

    Attributes
    ----------
    path: str
        path to folder
    patterns: dict
        nested dict: 2nd level keys are 'meta' and 'data', each of them
        consist regex patterns for extract meta data or RT data (respectively)
        from E-Prime files.
    '''
    def __init__(self, path, patterns):
        self.path = path
        self.files = []
        for fn in os.listdir(path):
            if fn.endswith('.txt'):
                self.files.append(fn)
        self.patterns = patterns

    def get_subjects(self):
        """

        @return: 1-d np array of subjects in the experiment
        """
        id_lst = []
        for fn in self.files:
            parser = EPrime(filename=os.path.join(self.path,fn),
                            patterns=self.patterns)
            id_lst.append(parser.field_parser("Name", "meta"))
        return np.array(id_lst)

    def get_rts(self):
        """

        @return: np ndarray of shape (num_of subjects,
        num of trials in experiment)
        """
        rt_lst = []
        for fn in self.files:
            parser = EPrime(filename=os.path.join(self.path,fn),
                            patterns=self.patterns)
            rt_lst.append(parser.extract_trial_rts())
        return np.stack(rt_lst)


# # function to get Control/Asd subject's idx
# def get_groups_idx(data, cont_name='Control', asd_name='ASD',
#                    label_name='group'):
#     cont_ind = np.where(data[label_name]==cont_name)[0]
#     asd_ind = np.where(data[label_name]==asd_name)[0]
#     return {cont_name:cont_ind, asd_name:asd_ind}

def convert_subjects(ids, id_map):
    """
Adjust subjects from ids to their id_map mapping,
keep 'not mapped' ids as they are.

    @param ids: subjects to convert
    @param id_map: mapping to other ids list
    @return: converted ids array
    """
    def converter(sub_id):
        if sub_id in id_map:
            return id_map[sub_id]
        else:
            return sub_id
    return np.vectorize(converter)(ids)


def insert_behave_data(data_obj, behave_path, eprime_patterns, id_map):
    eeg_subs = data_obj['subjects']
    behave_ingestor = BehaveIngest(behave_path, eprime_patterns)
    behave_subs = behave_ingestor.get_subjects()
    corrected_behave_subs = convert_subjects(behave_subs, id_map)
    rts = behave_ingestor.get_rts()

    # create data matrix of shape (len(eeg_subs), rts.shape[1])
    data_rts = np.zeros((47,rts.shape[1]))
    for i in range(len(eeg_subs)):
        search = np.argwhere(corrected_behave_subs
                             ==eeg_subs[i]).flatten()  # np array of
        # corresponding index in behavioural data.
        # If found, the index is (1,) np array, If not it's an empty array
        if len(search)>0:   # behavioural data exists
            behave_idx =search[0]
            data_rts[i,:] = rts[behave_idx,:]
        else:   # behavioural data doesn't exist
            data_rts[i,:] = np.nan

    # assign matrix to data object
    data_obj['behave'] = data_rts


with open("CONFIG.yaml", 'r') as f:
    doc = yaml.full_load(f)     # load configuration file
    MAT_FILENAME = doc['mat_filename']
    DATA_ATTR_NAME = doc['data_attr_name']
    BEHAVE_PATH = doc['behave_path']
    ID_MAP = doc['id_map']

    # Configured JSON of E-prime patterns for extraction
    EPRIME_PATTERNS = doc['eprime_patterns']
    with open(EPRIME_PATTERNS, 'r') as jf:
        PATTERNS = json.load(jf)

    # ingest eeg data from MATLAB structure
    mat_data = MatIngest(filename=MAT_FILENAME,
                         data_name=DATA_ATTR_NAME).create_data_obj()

    # Ingest behavioural data from E-Prime output folder
    insert_behave_data(mat_data, BEHAVE_PATH, PATTERNS, ID_MAP)
