import os
import sys
import csv
import shutil

import rpy2.robjects as ro
import rpy2.robjects.pandas2ri as pandas2ri

from .openspecy_utils import reformat_path, save_df_to_excel, subsequent_matches_checked, list_to_df_to_sheet, notes_sheet

def process_csv_files(folder_path, range_min, range_max):
    """
    Processes .csv files to match the required format for OpenSpecy processing.
    (The required format is two columns named ``'wavenumber'`` and ``'intensity'``)


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
            if filename.endswith(".csv") == False:
                print(
                    "Incompatible file format detected. This function only accepts .csv files. Please remove all other file types. Quitting now."
                )
                sys.exit()

            # Join the individual file with the parent path to get a full path
            file_path = os.path.join(folder_path, filename)

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
            print(f"Processed file: {filename}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    # Compress the folder into a .zip so it can be read in OpenSpecy
    zipped_file_path = shutil.make_archive(
        folder_path, format="zip", root_dir=folder_path
    )
    print("Files compressed to", zipped_file_path)

    return zipped_file_path


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
    ro.globalenv["folder_path"] = folder_path

    print("Executing R script...")

    # Call R and execute the following script
    ro.r(
        """

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
    #  https://rawcdn.githack.com/wincowgerDEV/OpenSpecy-package/c253d6c3298c7db56fbfdceee6ff0e654a1431cd/reference/process_spec.html
    files_processed <- process_spec(
      files,
      active = TRUE,
      adj_intens = FALSE,
      adj_intens_args = list(type = "none"),
      conform_spec = FALSE,
      conform_spec_args = list(range = NULL, res = 5, type = "interp"),
      restrict_range = FALSE,
      restrict_range_args = list(min = 0, max = 6000),
      flatten_range = FALSE,
      flatten_range_args = list(min = 2200, max = 2420),
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

    """
    )

    print("Script execution complete.")

    # Send R dataframe to Python dataframe
    pandas2ri.activate()
    df_top_matches = pandas2ri.rpy2py(ro.r["top_matches_trimmed"])

    return df_top_matches


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
    df = df.sort_values(by=["file_name.y"], ascending=True)
    save_df_to_excel(excel_path, df, "Info")

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
    notes_sheet(excel_path)


def openspecy_main(folder_path, file_name, target_directory):
    target_file_path = os.path.join(target_directory, file_name)
    zipped_path = process_csv_files(folder_path, 650, 4000)
    df_top_matches = r_script(zipped_path)
    sort_export(df_top_matches, target_file_path, 5)