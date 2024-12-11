# =============================================================================
# import os
# import sys
# import csv
# import shutil
# import openpyxl as xl;
# import pandas as pd
# from datetime import datetime
# from datetime import timezone
#
# import rpy2.robjects as ro
# import rpy2.robjects.pandas2ri as pandas2ri
# =============================================================================


def process_csv_files(folder_path, range_min, range_max):
    """
    Processes .csv files to match the required format for OpenSpecy processing.
    (The required format is two columns named 'wavenumber' and 'intensity')

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
        # For each file in the folder:
        for filename in os.listdir(folder_path):

            # Ensure the file is a .csv
            if filename.endswith('.csv') == False:
                print("Incompatible file format detected. This function only accepts .csv files. Please remove all other file types. Quitting now.")
                sys.exit()

            # Join the individual file with the parent path to get a full path
            file_path = os.path.join(folder_path, filename)

            # Open the .csv file with the csv.reader object
            with open(file_path, 'r', newline='') as csvfile:
                csvreader = csv.reader(csvfile, csv.QUOTE_NONE)

                # Read the .csv into a list
                rows = list(csvreader)

                # Initialize the keep_row list, which will be for rows that
                # contain numeric data
                keep_rows = []

                # For each row:
                for x in len(rows):
                    try:
                        # Check if the data in the first and second columns are
                        # numbers, and if so, keep the row
                        float(rows[x][0])
                        float(rows[x][1])
                        if float(rows[x][0]) >= range_min and float(rows[x][0]) <= range_max:
                            keep_rows.append(rows[x])
                    except:
                        # If the data cannot be converted into a number, skip
                        # the row
                        pass

            # Use the csv.writer object to overwrite the .csv file
            with open(file_path, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)

                # Write the specified column names to the first row
                csvwriter.writerow(['wavenumber', 'intensity'])

                # Write the "floatable" rows to the .csv file
                csvwriter.writerows(keep_rows)

            # The file should now fit the format for OpenSpecy processing
            print(f"Processed file: {filename}")

    except Exception as e:
        print(f'An error occurred: {str(e)}')

    # Compress the folder into a .zip so it can be read in OpenSpecy
    zipped_file_path = shutil.make_archive(folder_path, format='zip', root_dir=folder_path)
    print("Files compressed to",zipped_file_path)

    return zipped_file_path


def reformat_path(path):
    """
    Reformat a raw string file path (path\to\folder) to contain double back-
    slashes (path\\to\\folder), as is required by the R programming language.
    Doesn't do anything if the path uses forward slashes (/)

    Parameters
    ----------
    path : str
        The path to be reformatted.

    Returns
    -------
    reformatted_path : str
        All \ are replaced with \\.

    """

    reformatted_path = path.replace("\\", "\\\\")
    return reformatted_path


def r_script(folder_path):
    """
    Processes spectra through the OpenSpecy R package and returns a dataframe
    with the library matches and other data
    https://github.com/wincowgerDEV/OpenSpecy-package

    Parameters
    ----------
    folder_path : str
        Path to the zipped folder containing the processed .csv files.

    Returns
    -------
    df_top_matches : dataframe
        A Pandas dataframe containing the library match data for the files.

    """

    # Reformat the folder path to have \\ instead of \
    folder_path = reformat_path(folder_path)

    # Send the folder_path Python variable to an R variable
    ro.globalenv['folder_path'] = folder_path

    print("Executing R script...")

    # Call R and execute the following script
    ro.r('''

    library(OpenSpecy)
    library(data.table)

    # Fetch current spectral library from https://osf.io/x7dpz/
    if (FALSE) { # \dontrun{
      check_lib("derivative")
      get_lib("derivative")
    }

    # Load library into global environment
    spec_lib <- load_lib("derivative")

    # Filter the library to only include FTIR spectra
    ftir_lib <- filter_spec(spec_lib, spec_lib$metadata$spectrum_type=="ftir")

    # Read the files in the folder, and conform the range of the spectra to
    # match the range of the library
    files <- read_any(folder_path) |>
      c_spec(range=ftir_lib$wavenumber, res=NULL)

    # 'Monolithic' file processing function, see
    #  https://wincowger.com/OpenSpecy-package/reference/process_spec.html
    files_processed <- process_spec(
      files,
      active = TRUE,
      adj_intens = TRUE,
      adj_intens_args = list(type = "transmittance"),
      conform_spec = FALSE,
      conform_spec_args = list(range = NULL, res = 5, type = "interp"),
      restrict_range = TRUE,
      restrict_range_args = list(min = 650, max = 4000),
      flatten_range = FALSE,
      flatten_range_args = list(min = 2250, max = 2400),
      subtr_baseline = FALSE,
      subtr_baseline_args = list(type = "polynomial", degree = 8, raw = FALSE, baseline =
                                   NULL),
      smooth_intens = TRUE,
      smooth_intens_args = list(polynomial = 3, window = 11, derivative = 1, abs = TRUE),
      make_rel = TRUE,
      make_rel_args = list(na.rm = TRUE)
    )

    # Compare the processed spectra to those in the library and identify the
    # top 5 matches for each spectrum
    top_matches <- match_spec(files_processed, library = ftir_lib, na.rm = T, top_n = 5,
                             add_library_metadata = "sample_name",
                             add_object_metadata = "col_id")

    # Remove all empty columns from the dataframe
    top_matches_trimmed <- top_matches[, !sapply(top_matches, OpenSpecy::is_empty_vector), with = F]

    ''')

    print("Script execution complete.")

    # Send R dataframe to Python dataframe
    pandas2ri.activate()
    df_top_matches = pandas2ri.rpy2py(ro.r['top_matches_trimmed'])

    return df_top_matches


def identical_list_items(lst):
    """
    Checks if all the values in a given list are the same.

    Parameters
    ----------
    lst : list
        A list of values.

    Returns
    -------
    bool
        Returns ::True:: if all the values are the same, ::False:: if not.

    """
    return len(set(lst)) == 1


def plastic_matches_checked(row, index):
    """
    Appends a note to a given list which marks the index of the subsequent
    plastic match.

    Parameters
    ----------
    row : list
        A list containing data for one library match for one file.
    index : int
        The index of the subsequent plastic match.
        (see ::subsequent_matches_checked::)

    Returns
    -------
    row : list
        An updated version of the original ::row:: var. It now contains an
        additional item.

    """

    if index == 1:
        row.append('second match')

    elif index == 2:
        row.append('third match')

    elif index == 3:
        row.append('fourth match')

    elif index == 4:
        row.append('fifth match')

    return row


def nonpolymer_matches_checked(row, nested_list):
    """
    Checks a given dataframe (in the form of a nested list) to determine if all
    matches are empty wells or not.

    Parameters
    ----------
    row : list
        A list containing data for one library match for one file.
    nested_list : list
        A list of lists, where each list in the outer list represents a row.

    Returns
    -------
    row : list
        An updated version of the original ::row:: var. It now contains an
        additional item.

    """

    if 'empty well' in nested_list:
        # Check to see if 'empty well' is the only value in that list
        if identical_list_items(nested_list) == True:
            row.append('all top matches empty wells')
        else:
            row.append('all top matches nonpolymer')
    else:
        row.append('all top matches nonpolymer')

    return row


def subsequent_matches_checked(df, nested_list):
    """
    Checks if the first match (highest r val) for each sample is plastic, and
    if it is not, it checks the subsequent matches for any plastic matches, and
    if there are, it makes a note of its place (1st, 2nd, etc). If there are no
    plastic matches, it will check if all subsequent matches are for an empty
    well and make a note. If that is not the case, it will note that all
    subsequent matches are 'nonpolymer.'

    Parameters
    ----------
    df : df
        A Pandas dataframe.
    nested_list : list
        A list of lists, where each list in the outer list represents a row.

    Returns
    -------
    nested_list : list
        An updated version of the original ::nested_list::. Each inner list is
        now one item longer.

    """

    # Send plastic classification column to list
    polymer = df[df.columns['plastic_or_not']].values.tolist()

    # Proceed if the first match is not plastic
    if polymer[0] == 'not plastic':
        if 'plastic' in polymer:

            # Identify index of first occurrence of 'plastic' and pull the
            # corresponding row to be added to the updated summary sheet
            index = polymer.index('plastic')
            row = df.iloc[index].tolist()

            # Add a note to the row indicating its match # (1st, 2nd, 3rd, etc)
            row = plastic_matches_checked(row, index)

        else:
            # Send the spectrum_identity column to a list
            material = df[df.columns['spectrum_identity']].values.tolist()

            # Send the first row to a list and add a note indicating if all
            # matches are empty wells or simply nonpolymer
            row = df.iloc[0].tolist()
            row = nonpolymer_matches_checked(row, material)

    else:
        # If the first match is polymer, send the first row to a list
        row = df.iloc[0].tolist()
        row.append(' ')

    # Add row to nested_list
    nested_list.append(row)

    return nested_list


def save_df_to_excel(excel_path, df, sheetname):
    """
    Saves a Pandas dataframe to an Excel file. If the Excel file does not yet
    exist, it will create it and save the sheet.

    Parameters
    ----------
    excel_path : str
        The full path to an .xlsx file.
    df : df
        The dataframe to be saved as an Excel sheet.
    sheetname : str
        The name of the Excel sheet.

    Returns
    -------
    None.

    """

    if os.path.exists(excel_path) == False:
        with pd.ExcelWriter(excel_path, engine = 'openpyxl') as writer:
            df.to_excel(writer, sheet_name = sheetname, index=False)

    else:
        with pd.ExcelWriter(excel_path, engine = 'openpyxl', if_sheet_exists = 'replace', mode='a') as writer:
            df.to_excel(writer, sheet_name = sheetname, index = False)



def check_excel_sheet(excel_path, sheetname):
    """
    Checks if an Excel spreadsheet exists within the (already existing) Excel
    workbook and creates one if not. Note that this differs from
    ::save_df_to_excel:: and is used for directly editing cells in an Excel
    spreadsheet.

    Parameters
    ----------
    excel_path : str
        The full path to an already existing .xlsx file.
    sheetname : str
        The name of the Excel sheet.

    Returns
    -------
    ws : openpyxl worksheet object
        An Excel sheet with the desired ::sheetname::.

    """

    # Check if the designated sheetname exists
    if str(sheetname) in excel_path.sheetnames:
        # If the sheetname exists, assign it to ws
        ws = excel_path[str(sheetname)]
    else:
        # If the sheetname does not exist, create it and assign to ws
        ws = excel_path.create_sheet(str(sheetname))

    return ws


def empty_wells_count(df):
    """
    Counts how many times 'empty well' appears in a given dataframe.

    Parameters
    ----------
    df : df
        A Pandas dataframe.

    Returns
    -------
    count : int
        The number of times ::'empty well':: appears in the
        ::'spectrum_identity':: column.

    """

    # Send all rows that contain 'empty well' in the 'spectrum_identity' column
    # to a new dataframe
    df_empty_wells = df[df['spectrum_identity'] == 'empty well']

    # Count the length of the dataframe
    count = len(df_empty_wells)

    return count


def timestamp(version, excel_path):
    """
    Adds a timestamp and version number to the Excel export.

    Parameters
    ----------
    version : str
        The version number of this script.
    excel_path : str
        The full path to an .xlsx file.

    Returns
    -------
    None.

    """

    # Open the Excel workbook
    wb1 = xl.load_workbook(excel_path)

    # Check if 'Notes' sheet exists and create one if not
    notes_sheet = check_excel_sheet(wb1, 'Notes')

    # Pull the current time in UTC (Coordinated Universal Time)
    time_stamp = datetime.now(timezone.utc)

    # Reformat the timestamp to YYYY-MM-DD HH:MM UTC+0000
    formatted_time = time_stamp.strftime('%Y-%m-%d %H:%M %Z%z')

    # Add the version and timestamp to a string and save in cell A4 on the 'Notes' sheet
    time_info = 'This file was processed with OpenSpecy Automation ' + str(version) +' at ' + str(formatted_time)
    notes_sheet['A1'] = time_info

    # Save the Excel workbook
    wb1.save(str(excel_path))


def notes_sheet(excel_path):
    """
    Adds a 'Notes' sheet with the number of nonpolymer matches and empty wells

    Parameters
    ----------
    excel_path : str
        The full path to an .xlsx file.

    Returns
    -------
    None.

    """

    # Open the Excel workbook
    wb1 = xl.load_workbook(excel_path)

    # Check if 'Notes' sheet exists and create one if not
    notes_sheet = check_excel_sheet(wb1, 'Notes')

    # Open the Summary sheet into a pandas dataframe
    xlsx_file = pd.ExcelFile(excel_path)
    df_summary = pd.read_excel(xlsx_file, 'Summary')

    # Send all rows with not plastic matches to a dataframe
    df_not_plastic = df_summary[df_summary['plastic_or_not'] == 'not plastic']

    # Check if the 'not plastic' dataframe is emtpy
    if df_not_plastic.empty:
        print("No nonplastic matches.")

    else:
        # Count how many empty well matches are in the dataframe
        empty_wells = empty_wells_count(df_not_plastic)

        # Open the Updated Summary sheet into a pandas dataframe
        df_updated_summary = pd.read_excel(xlsx_file, 'Updated Summary')

        # Send all rows containing the matching text to a dataframe and count
        # the length of the dataframe
        df_all_empty = df_updated_summary[df_updated_summary['matches_checked'] == 'all top matches empty wells']
        totally_empty_count = len(df_all_empty)

        # Compare the empty well count to the nonpolymer matches count
        empty_matches = (str(empty_wells) + ' out of ' + str(len(df_not_plastic)) + ' nonplastic matches are empty wells.')

        notes_sheet['A3'] = empty_matches

        # Compare the totally empty well count (5/5 empty) to the empty well
        # count (first match empty)
        empty = str(totally_empty_count) + ' out of ' + str(empty_wells) + ' empty well matches have 5/5 top hits for empty wells.'

        notes_sheet['A4'] = empty

        wb1.save(str(excel_path))

        print('Workbook saved to ' + excel_path)

    timestamp('0.9.3', excel_path)


def sort_export(df, excel_path, top_n):
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
        The number of top matches for each file

    Returns
    -------
    None.

    """

    # Sort the dataframe by file name and save to Excel
    df = df.sort_values(by=['file_name.y'], ascending = True)
    save_df_to_excel(excel_path, df, "Info")

    # Copy the following columns into a new dataframe
    df_truncated = df[['file_name.y','spectrum_identity', 'material_class', 'match_val','sn','plastic_or_not']]

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
        subset_df = subset_df.sort_values(by=['match_val'], ascending = False)

        # Check each dataframe for its subsequent matches
        df_updated_summary_list = subsequent_matches_checked(subset_df, df_updated_summary_list)

        # For each subset, replace the rows in the file_name column with '-'
        # (done for legibility purposes)
        for x in range(len(subset_df)):
            if x != 0:
                subset_df.iat[x, 0] = '-'
            row = subset_df.iloc[x]
            row = row.tolist()
            df_full_list.append(row)
            if x == 0:
                # Add the first row of each subset_df to a list
                df_summary_list.append(row)


    # Get column names for list to df conversion
    column_names = list(df_truncated.columns)

    # Add column for the notes added to the updated summary sheet
    updated_column_names = column_names + ['matches_checked']

    # Send each nested list to a dataframe and then save as an Excel sheet in
    # the previously-specified workbook
    list_to_df_to_sheet(df_summary_list, column_names, excel_path, 'Summary')
    list_to_df_to_sheet(df_updated_summary_list, updated_column_names, excel_path, 'Updated Summary')
    list_to_df_to_sheet(df_full_list, column_names, excel_path, 'Subsequent Matches')

    # Add a notes sheet to the Excel workbook
    notes_sheet(excel_path)


def list_to_df_to_sheet(df_lst, columns_list, excel_path, sheet_name):
    """
    Converts a nested list into a Pandas dataframe, which is then saved to an
    Excel worksheet.

    Parameters
    ----------
    excel_path : str
        The full path to an .xlsx file.
    df_lst : list
        The nested list.
    columns_list : list
        The list of column names.
    sheet_name : str
        The name of the Excel sheet.

    Returns
    -------
    None.

    """

    df = pd.DataFrame(df_lst, columns = columns_list)
    save_df_to_excel(excel_path, df, sheet_name)


def openspecy_main(folder_path, file_name, target_directory):
    target_file_path = os.path.join(target_directory, file_name)
    zipped_path = process_csv_files(folder_path, 650, 4000)
    df_top_matches = r_script(zipped_path)
    sort_export(df_top_matches, target_file_path, 5)