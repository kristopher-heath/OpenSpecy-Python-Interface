import os
import sys
import csv
import shutil

import rpy2.robjects as ro
import rpy2.robjects.pandas2ri as pandas2ri

from .nrel import nrel_delete_sp, nrel_autoname
from .metadata import _xlsx_metadata
from .utils import count_files, reformat_path, save_df_to_excel, matches_checked_sheet, subsequent_matches_checked, list_to_df_to_sheet

def process_csv(file_path, range_min, range_max):
    """
    Processes .csv files to match the required format for OpenSpecy processing.
    (The required format is two columns named ``'wavenumber'`` and ``'intensity'``)


    Parameters
    ----------
    file_path : str
        The complete path to the .csv file to be processed. This function
        only accepts .csv files, and any other file types will cause the
        function to stop.
    range_min : int
        The minimum wavenumber of the desired spectral range. Note that this
        value can be greater than the actual minimum if cropping is desired.
    range_max : int
        The maximum wavenumber of the desired spectral range. Note that this
        value can be less than the actual maximum if cropping is desired.

    Returns
    -------
    file_path : str
        The complete path to the processed .csv file.

    """

    if range_max <= range_min:
        print(
            f"Error. Specified range is incompatible. range_min must be less than range_max.\nCurrent values:\nrange_min: {range_min}\nrange_max: {range_max}"
        )
        sys.exit()
    try:
        # For each file in the folder:
        #for filename in os.listdir(file_path):

        # Ensure the file is a .csv
        if file_path.endswith(".csv") == False:
            print(
                f"Incompatible file format detected: {os.path.basename(file_path)}\nThis function only accepts .csv files. Please remove all other file types. Quitting now."
            )
            sys.exit()

        # Join the individual file with the parent path to get a full path
        #file_path = os.path.join(file_path, filename)

        # Open the .csv file with the csv.reader object
        with open(file_path, "r", newline="") as csvfile:
            csvreader = csv.reader(csvfile, csv.QUOTE_NONE)

            # Read the .csv into a list
            rows = list(csvreader)

            # Initialize the keep_row list, which will be for rows that
            # contain numeric data
            keep_rows = []

            # For each row:
            x = 0
            while x < len(rows):
                try:
                    # Check if the data in the first and second columns are
                    # numbers, and if so, keep the row
                    float(rows[x][0])
                    float(rows[x][1])
                    if (
                        float(rows[x][0]) >= range_min
                        and float(rows[x][0]) <= range_max
                    ):
                        keep_rows.append(rows[x])
                except:
                    # If the data cannot be converted into a number, skip
                    # the row
                    pass
                x += 1

        # Use the csv.writer object to overwrite the .csv file
        with open(file_path, "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)

            # Write the specified column names to the first row
            csvwriter.writerow(["wavenumber", "intensity"])

            # Write the "floatable" rows to the .csv file
            csvwriter.writerows(keep_rows)

        # The file should now fit the format for OpenSpecy processing
        filename = os.path.basename(file_path)

        print(f"Processed file: {filename}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


    return file_path


def process_csv_folder(folder_path, range_min, range_max):
    """
    Processes a batch of .csv files in the given folder by calling
    `process_csv`, then zips the processed files to send to OpenSpecy.


    Parameters
    ----------
    folder_path : str
        The complete path to the folder containing .csv files to be processed.
        This function only accepts .csv files, and any other file types will
        cause the function to stop.
    range_min : int
        The minimum wavenumber of the desired spectral range. Note that this
        value can be greater than the actual minimum if cropping is desired.
    range_max : int
        The maximum wavenumber of the desired spectral range. Note that this
        value can be less than the actual maximum if cropping is desired.

    Returns
    -------
    zipped_file_path : str
        The complete path to a zipped folder containing the processed .csv
        files. This will be located in the same directory as the original
        folder path.

    """

    try:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            process_csv(file_path, range_min, range_max)

    except Exception as e:
        print(f'An error occurred: {str(e)}')

    zipped_file_path = shutil.make_archive(folder_path, format='zip', root_dir=folder_path)
    print("Files compressed to",zipped_file_path)

    return zipped_file_path


def r_script(
        file_path,
        range_min,
        range_max,
        adj_intens: bool = False,
        adj_intens_type: str = 'none',
        subtract_baseline: bool = False,
        top_n: int = 5):
    """
    Processes spectra through the OpenSpecy R package and returns a dataframe
    with the library matches and other data
    https://github.com/wincowgerDEV/OpenSpecy-package

    Parameters
    ----------
    file_path : str
        Path to the zipped folder containing the processed .csv files OR the path to a single .csv file.
    range_min : int
        The minimum wavenumber of the desired spectral range. Note that this
        value can be greater than the actual minimum if cropping is desired.
    range_max : int
        The maximum wavenumber of the desired spectral range. Note that this
        value can be less than the actual maximum if cropping is desired.
    top_n : int
        The top *n* highest matches desired. Recommended values: 1 <= n >= 10
        (Not yet supported)
    adj_intens : bool
        If True, the function will adjust the intensity of the spectra using
        the OpenSpecy package.
    adj_intens_type : str
        The type of intensity adjustment to be made. Options are 'none',
        'transmittance', or 'absorbance'
    subtract_baseline : bool
        If True, the function will subtract the baseline from the spectra using
        IModPolyFit from the OpenSpecy package.
    Returns
    -------
    df_top_matches : dataframe
        A Pandas dataframe containing the library match data for the files.

    """

    # Reformat the folder path to have \\ instead of \
    file_path = reformat_path(file_path)

    # Send the folder_path Python variable to an R variable
    ro.globalenv["file_path"] = file_path
    ro.globalenv["range_min"] = range_min
    ro.globalenv["range_max"] = range_max
    ro.globalenv["py_top_n"] = top_n
    ro.globalenv["py_adj_intens"] = adj_intens
    ro.globalenv["py_adj_intens_type"] = adj_intens_type
    ro.globalenv["py_subtr_baseline"] = subtract_baseline


    print("Executing R script...")

    # Call R and execute the following script
    ro.r(
        """

    library(OpenSpecy)
    library(data.table)
    library(tools)

    # Load library into global environment
    spec_lib <- load_lib("derivative")

    # Filter the library to only include FTIR spectra
    ftir_lib <- filter_spec(spec_lib, spec_lib$metadata$spectrum_type=="ftir")

    # Read the files in the folder, and conform the range of the spectra to
    # match the range of the library
    files <- read_any(file_path)

    if (file_ext(file_path) == 'csv') {
      files <- conform_spec(files, range = ftir_lib$wavenumber, res = NULL)
      }

    if (file_ext(file_path) == 'zip') {
      files <- c_spec(files, range = ftir_lib$wavenumber, res = NULL)
      }

    # 'Monolithic' file processing function, see
    #  https://rawcdn.githack.com/wincowgerDEV/OpenSpecy-package/c253d6c3298c7db56fbfdceee6ff0e654a1431cd/reference/process_spec.html
    files_processed <- process_spec(
      files,
      active = TRUE,
      adj_intens = py_adj_intens,
      adj_intens_args = list(type = py_adj_intens_type),
      conform_spec = FALSE,
      conform_spec_args = list(range = ftir_lib$wavenumber, res = NULL, type = "interp"),
      restrict_range = TRUE,
      restrict_range_args = list(min = range_min, max = range_max),
      flatten_range = FALSE,
      flatten_range_args = list(min = 2200, max = 2420),
      subtr_baseline = py_subtr_baseline,
      subtr_baseline_args = list(type = "polynomial", degree = 8, raw = FALSE, baseline =
                                   NULL),
      smooth_intens = TRUE,
      smooth_intens_args = list(polynomial = 3, window = 11, derivative = 1, abs = TRUE),
      make_rel = TRUE,
      make_rel_args = list(na.rm = TRUE)
    )


    # Compare the processed spectra to those in the library and identify the
    # top 5 matches for each spectrum
    top_matches <- match_spec(files_processed, library = ftir_lib, na.rm = T, top_n = py_top_n,
                             add_library_metadata = "sample_name",
                             add_object_metadata = "col_id")

    # Remove all empty columns from the dataframe
    top_matches_trimmed <- top_matches[, !sapply(top_matches, OpenSpecy::is_empty_vector), with = F]

    """
    )

    print("Script execution complete.")

    # Send R dataframe to Python dataframe
    pandas2ri.activate()
    df_top_matches = pandas2ri.rpy2py(ro.r["top_matches_trimmed"])

    return df_top_matches


def sort_export(df, excel_path, top_n, nrel = False):
    """
    Sorts the dataframe exported from the R script and rearranges it into a
    more presentable format. Exports an Excel file.

    Parameters
    ----------
    df : df
        The dataframe exported from the R script.
    excel_path : str
        The full path to an .xlsx file.
    top_n : int
        The number of top matches for each file. Equal to `top_n` in
        `openspi_main`. Default is 5.
    nrel : Bool
        Adds an extra row regarding first well information to the "Matches
        Checked sheet."


    Returns
    -------
    None.

    """

    # Sort the dataframe by file name and save to Excel
    df = df.sort_values(by=["file_name.y"], ascending=True)
    save_df_to_excel(excel_path, df, "Source Data")

    # Copy the following columns into a new dataframe
    df_truncated = df[
        [
            "file_name.y",
            "spectrum_identity",
            "material_class",
            "match_val",
            "sn",
            "plastic_or_not",
        ]
    ]

    # Initialize lists (these will be nested lists which will be converted to
    # dataframes)
    df_full_list = []
    df_summary_list = []
    df_updated_summary_list = []

    # Cut df into subsets of n (so the df corresponds to the matches for one
    # file at a time)
    for start_row in range(0, len(df_truncated), top_n):
        end_row = start_row + top_n
        subset_df = df_truncated.iloc[start_row:end_row]

        # Sort the df by the 'match_val' column in descending order
        subset_df = subset_df.sort_values(by=["match_val"], ascending=False)

        # Check each dataframe for its subsequent matches
        df_updated_summary_list = subsequent_matches_checked(
            subset_df, df_updated_summary_list
        )

        # For each subset, replace the rows in the file_name column with '-'
        # (done for legibility purposes)
        for x in range(len(subset_df)):
            if x != 0:
                subset_df.iat[x, 0] = "-"
            row = subset_df.iloc[x]
            row = row.tolist()
            df_full_list.append(row)
            if x == 0:
                # Add the first row of each subset_df to a list
                df_summary_list.append(row)

    # Get column names for list to df conversion
    column_names = list(df_truncated.columns)

    # Add column for the notes added to the updated summary sheet
    updated_column_names = column_names + ["matches_checked"]

    # Send each nested list to a dataframe and then save as an Excel sheet in
    # the previously-specified workbook
    list_to_df_to_sheet(df_summary_list, column_names, excel_path, "Summary")
    list_to_df_to_sheet(
        df_updated_summary_list, updated_column_names, excel_path, "Updated Summary"
    )
    list_to_df_to_sheet(df_full_list, column_names, excel_path, "Subsequent Matches")

    # Add a notes sheet to the Excel workbook
    matches_checked_sheet(excel_path, nrel = nrel, n = top_n)



def openspi_main(
        source_path,
        range_min,
        range_max,
        export_xlsx = None,
        export_dir = None,
        nrel_version = False,
        adj_intens = False,
        adj_intens_type = 'none',
        subtr_baseline = False):
    """
    A complete function for spectral pre-processing, processing through the
    OpenSpecy library in R, and configuring/processing the outputted data into
    an Excel spreadsheet.


    Parameters
    ----------
    source_path : str
        The complete path to the folder containing .csv files to be processed OR
        the path to a single .csv file. This function only accepts .csv files,
        and any other file types will cause the function to stop.
    range_min : int
        The minimum wavenumber of the desired spectral range. Note that this
        value can be greater than the actual minimum if cropping is desired.
    range_max : int
        The maximum wavenumber of the desired spectral range. Note that this
        value can be less than the actual maximum if cropping is desired.
    export_xlsx : str
        The desired name of the outputted .xlsx file. If the file name
        does not contain the file extention `.xlsx`, it will be added.
        Optional; if not specified, the outputted file will be named according
        to the source file/folder.
    export_dir : str
        The desired location of the outputted `.xlsx` file. Optional; if not
        specified, the file will be saved in the parent directory of the source
        file/folder.
    nrel_version : bool
        If True, the function will use the NREL version of OpenSpecy, which
        has two differences: 1) all .sp files present in the folder will be
        deleted, and 2) the outputted file will be named in a specific way
        according to the files contained within.
    top_n : int
        The top *n* highest matches desired. Recommended values: 1 <= n >= 10.
        Not yet supported.
    adj_intens : bool
        If True, the function will adjust the intensity of the spectra using
        the OpenSpecy package.
    adj_intens_type : str
        The type of intensity adjustment to be made. Options are 'none',
        'transmittance', or 'absorbance'
    subtr_baseline : bool
        If True, the function will subtract the baseline from the spectra using
        IModPolyFit from the OpenSpecy package.

    Returns
    -------
    None.

    """
    top_n = 5
    # If export_xlsx is specified, check that it includes '.xlsx'
    if not export_xlsx == None:
        if not '.xlsx' in export_xlsx:
            export_xlsx = export_xlsx + '.xlsx'
    else:
        # Check if source_path is a folder or a file, and determine the export
        # name accordingly
        if os.path.isdir(source_path):

            # Generate a name based on the source_path
            if not nrel_version == True:
                export_xlsx = os.path.basename(source_path) + '.xlsx'

            else:
                # If nrel_version is True, use the nrel_autoname function to generate a name
                export_xlsx = nrel_autoname(source_path)

        else:
            # If the source_path is a file, use the file name to generate the export name
            export_xlsx = 'TopMatches' + os.path.basename(source_path).replace('.csv', '.xlsx')

    # If export_dir is specified, check if it exists. If not, create it.
    if not export_dir == None:
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
            print(f"Directory {export_dir} created.")

    # If export_dir is not specified, save the file in the same directory as source_path
    else:
        export_dir = os.path.dirname(source_path)

    target_file_path = os.path.join(export_dir, export_xlsx)


    # Check if the target file already exists. If it does, ask the user if they want to overwrite.
    if os.path.exists(target_file_path):
        print('File already exists. Please specify export_xlsx to change the name.\nIf you proceed, it will be overwritten.\nProceed? [y/n]')
        proceed = str(input())
        if proceed == 'y':
            pass
        elif proceed == 'n':
            sys.exit()
        else:
            print('No valid input detected. Quitting now.')
            sys.exit()

    # Check if the source_path is a folder or a file
    if os.path.isdir(source_path):

        if nrel_version == True:
            nrel_delete_sp(source_path)

        # If the folder contains multiple files, process them all and create a zip folder
        if count_files(source_path) > 1:
            processed_path = process_csv_folder(source_path, range_min, range_max)

        # If the folder contains only one file, determine its path process it.
        elif count_files(source_path) == 1:
            for filename in os.listdir(source_path):
                file_path = os.path.join(source_path, filename)
                processed_path = process_csv(file_path, range_min, range_max)

        # If the folder contains no files, quit.
        elif count_files(source_path) == 0:
            print("No files detected. Quitting now.")
            sys.exit()
    # If the source_path is a file, process it.
    else:
        processed_path = process_csv(source_path, range_min, range_max)

    df_top_matches = r_script(processed_path, range_min, range_max, adj_intens, adj_intens_type, subtr_baseline, top_n)
    sort_export(df_top_matches, target_file_path, 5, nrel = nrel_version)


    _xlsx_metadata(target_file_path)