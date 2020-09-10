import scipy.io as sio
import yaml
import numpy as np


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
        return d


# function to get Control/Asd subject's idx
def get_groups_idx(data, cont_name='Control', asd_name='ASD',
                   label_name='group'):
    cont_ind = np.where(data[label_name]==cont_name)[0]
    asd_ind = np.where(data[label_name]==asd_name)[0]
    return {cont_name:cont_ind, asd_name:asd_ind}


with open(r"eegtools\CONFIG.yaml", 'r') as f:
    doc = yaml.full_load(f)
    mat_data = MatIngest(filename=doc['mat_filename'],
                     data_name=doc['data_attr_name']).create_data_obj()
    # next line defined 2d-array: rows are empty signals and columns are
    # sub_id, trial, block
    mat_data['null'] = np.argwhere(np.all(np.isnan(mat_data['s2']), axis=1))
