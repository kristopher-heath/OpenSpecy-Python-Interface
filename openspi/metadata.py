import os
import openpyxl

def _xlsx_metadata(xlsx_file):
    """
    Adds the OpenSpecy-Python-Interface version number as metadata stored in
    Excel's `subject` and `keywords` attributes.

    Parameters
    ----------
    xlsx_file : str
        The full file path of the .xlsx file to be tagged.

    Returns
    -------
    None.

    """

    # Pull version num from __version__.py
    from openspi.__version__ import __version__

    # Create version tag str
    version_tag = "OpenSPI v" + __version__

    # Load the workbook
    wb = openpyxl.load_workbook(xlsx_file)

    # Access the workbook properties
    props = wb.properties

    # Check workbook properties, if missing version tag, add it
    if props.subject != version_tag or props.keywords != version_tag:
        props.subject = version_tag
        props.keywords = version_tag

    # Save the workbook
    wb.save(xlsx_file)