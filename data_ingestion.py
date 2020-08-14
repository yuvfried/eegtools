import scipy.io as sio


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
        self.file = sio.loadmat(filename, struct_as_record=False, squeeze_me=True)
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

