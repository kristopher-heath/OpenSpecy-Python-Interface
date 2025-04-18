import os
from datetime import datetime

def nrel_delete_sp(folder_path):
    '''
    Deletes .sp files. Specific use: folder contains both .sp and .csv files
    for each spectrum. OpenSpecy does not accept .sp files, so they must be
    removed from the folder. Note that these files were backed up elsewhere
    before deletion.

    Parameters
    ----------
    folder_path : str
        The complete path to the folder containing .csv files to be processed.

    Returns
    -------
    None.

    '''
    for filename in os.listdir(folder_path):
        source_file = os.path.join(folder_path, filename)

        if source_file.endswith('.sp'):
            os.remove(source_file)


def nrel_autoname(folder_path):

    '''
    Creates an export name according to specific naming conventions used in the
    WaterPACT project at NREL.

    Parameters
    ----------
    folder_path : str
        The complete path to the folder containing .csv files to be processed.

    Returns
    -------
    file_name : str
        A file name based on the name of the first file in the folder.

    '''
    time_stamp = datetime.now()
    date = time_stamp.strftime('%Y%m%d')

    file_list = os.listdir(folder_path)
    filename = file_list[0]


    name = os.path.splitext(filename)[0]

    index = name.find('_')
    if index != -1:
        string_1 = name[index + 1:]

    r_index = string_1.rfind('_')
    string_2 = string_1[:r_index]


    file_name = 'TopMatches_' + string_2 + '_' + date + '.xlsx'

    return file_name