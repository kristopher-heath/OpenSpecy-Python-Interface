# **ATTENTION: THIS PACKAGE IS PRE-RELEASE AND NOT YET USABLE**

## Contents

[OpenSpecy Python Interface](#openspecy-python-interface)

[Setup and Installation](#setup-and-installation)

[Installation Tutorial](#installation-tutorial)

[Usage & Documentation](#usage--documentation)

[Notes](#notes)

[To-Do](#to-do)

[Contributing](#contributing)

[License](#license)

---

# OpenSpecy Python Interface

[OpenSpecy](https://github.com/wincowgerDEV/OpenSpecy-package) is a spectral processing tool for the analysis of Raman and FTIR spectra of environmental plastics. It contains several functions to process and enhance the spectral signals in order to obtain material matches by utilizing an online reference library. It is entirely open-source and free to use, both via an R package available on [CRAN](https://cran.r-project.org/web/packages/OpenSpecy/index.html) as well as a [web version](https://www.openanalysis.org/openspecy/) built with R shiny.

The web version is quite useful, but usage can be hindered by the strength of one's Internet connectivity. Additionally, there is currently no support for downloading a file containing the top *n* matches for all samples in a batch; instead, each file must be individually uploaded and processed, and then the table containing the top *n* matches can be viewed. This greatly restricts processing speed, especially for bulk file uploads. Additionally, the .csv exported by the web version contains many columns of data, and, depending on one's intended use, many may not be immediately necessary for the user.

The OpenSpecy R package, however, can process all top *n* matches consecutively and quickly. The exported data table is still quite large and cumbersome, so for ease and speed of data interpretation, it is necessary to rearrange and exclude several of the columns. R is a great tool for this, but so is Python, which is more user-oriented and beginner-friendly, making it more accessible to less-code-literate people who may have a need for OpenSpecy.

Thus was the beginning of the **OpenSpecy-Python-Interface**, an all-in-one spectral data processing package. It contains several functions to 1) preprocess data to ensure it will be readable by the OpenSpecy R package, 2) call on R to execute a script that uses OpenSpecy, and 3) post-process the data to make a concise, readable Excel sheet containing all the data. It can also be utilized as a comprehensive script that processes your files from start to finish, reducing the need for prior coding knowledge.

---

## Setup and Installation

Note: This is a brief overview of the setup process. For an explicit step-by-step walkthrough, please see the [Installation Tutorial](https://github.com/KrisHeathNREL/OpenSpecy-Python-Interface/blob/main/INSTALLATION_TUTORIAL.md).

**R Installation and Configuration**

* Download and install the most recent version of [R](https://cran.r-project.org/) for your OS
  * Note: R must be installed directly to your device, not inside an environment
* Open up the RGUI
* In the R Console, run the following:

```bash
install.packages('OpenSpecy', repos='http://cran.us.r-project.org')
```

* Once OpenSpecy is installed, run the following code to install the spectral libraries:

```bash
library(OpenSpecy)
get_lib()
```

* Run one last line in the console to get the `R_HOME` variable. Copy and paste it somewhere for later, as it will be necessary to define when using this package.

```bash
R.home()
```

* Exit the RGUI window

---

**Python Installation**

* Create a new environment in Anaconda
* Run the following in the environment terminal:

```bash
pip install openspecy-python-interface
```

* Run Python in the IDE of your choice
* Use the package as outlined below

---

# Installation Tutorial

This is a step-by-step walkthrough for users who aren't as familiar with using R and Python

## R Installation

1. Navigate to [https://cran.r-project.org/](https://cran.r-project.org/) and click the link to download R for your platform.
2. Once you have selected and downloaded your desired version, navigate to the downloaded .exe file and execute it.
3. Follow the on-screen instructions to set up R.
   * If you are using a work computer, make sure to install R in a place that you have read/write privileges. This is necessary for later steps when Python will need to access R libraries

## R Configuration

1. Once installation is complete, open R.
2. In the console, paste and run the following:

```bash
install.packages('OpenSpecy', repos='http://cran.us.r-project.org')
```

![install openspecy in R](instruction_pics/install_openspecy.png "install_openspecy")

3. Once OpenSpecy and its dependencies are installed, run the following code in the console one line at a time:

```bash
library(OpenSpecy)
get_lib()
```

* This will download the 7 spectral libraries that are available in OpenSpecy. These libraries will be kept on your hard drive, so after initial installation, this only needs to be done when the libraries are updated.

![get libraries](instruction_pics/get_lib.png "get_lib")

4. Run this line:

```bash
R.home()
```

* Copy and paste the outputted path somewhere. This will be needed later.

![find R_home var](instruction_pics/r_home.png "r_home")

* Note that in this screenshot, the path is outputted in shorthand. In this case, it corresponds to "C:/Program Files/R/R-4.4.2"

5. Navigate to your `R_HOME` path. Double check that this folder has a 'bin' folder, which contains 'R.exe'
   * If it does not contain the 'bin' folder, look through your other files until you find a bin folder that contains 'R.exe' and copy and paste the file path of the parent directory (the folder that contains the 'bin' folder) somewhere for later

![navigate to the r_home path](instruction_pics/r_home_path.png "r_home_path")

---
![open the bin folder](instruction_pics/r_exe.png "r_exe")

6. Exit out of R. You will be prompted with "Save workspace image?" This is to save any user-defined objects. Because we have not defined anything, it does not matter if you select "yes" or "no"

## Anaconda Installation and Setup

[Anaconda Navigator](https://www.anaconda.com/download) will be used for the purposes of this tutorial.

1. If it is not already installed, download and install Anaconda from [https://www.anaconda.com/download](https://www.anaconda.com/download)
2. Open Anaconda and navigate to the Environments tab on the left side, and then select the Create button from the menu at the bottom of the screen.

![create anaconda environment](instruction_pics/create_env.png "create_env")
3. Name the environment as you choose.

## Python Setup

1. In Anaconda Navigator, click the arrow button next to the environment you created and select "Open Terminal"

![open terminal](instruction_pics/open_terminal.png "open_terminal")

* Note that the environment in this screenshot is the base (root) environment. Please be sure to open the environment you created, not base

2. In the terminal, run the following:

```bash
pip install openspecy-python-interface
```

* This will install this package as well as its dependencies (pandas, openpyxl, and rpy2)

3. Exit out of the terminal

## Python Usage

1. Open a new Python script in your preferred application through Anaconda. Spyder is highly recommended
2. In order for Python to interact with R, it must be able to access the `R_HOME` variable. However, because Python is within a virtual environment, **this variable must manually specified before the package can be imported.**
   * Paste the following code **at the beginning of the script**

```bash
import os
os.environ['R_HOME'] = r"C:\Program Files\R\R-4.4.2"	# Paste your own R_HOME var here
import openspecy-python-interface
```

🎉 Congrats! You have completed setup and installation! 🎉

## Usage & Documentation

**Example:**

```bash
import os
os.environ['R_HOME'] = r"C:\Program Files\R\R-4.4.2"

from openspi.core import openspecy_main

openspecy_main(
    source_folder = r"C:\Users\{user}\Documents\Unprocessed Data\{folder}",
    range_min = 650,
    range_max = 4000,
    export_xlsx = "{filename}.xlsx",
    export_dir = r"C:\Users\{user}\Documents\OpenSpecy Exports")
```

Please see [https://openspecy-python-interface.readthedocs.io/en/latest/](https://openspecy-python-interface.readthedocs.io/en/latest/) for all available functions.


## Notes

This package uses [rpy2](https://rpy2.github.io/) to execute R code through Python. To write your own R script, use the [`rpy2.robjects.r`](https://rpy2.github.io/doc/v3.5.x/html/introduction.html#calling-r-functions) function.

## To-Do

* Add support for settings customizability
  * Selection of OpenSpecy library
  * Full configurability of OpenSpecy's [`process_spec`](https://rawcdn.githack.com/wincowgerDEV/OpenSpecy-package/c253d6c3298c7db56fbfdceee6ff0e654a1431cd/reference/process_spec.html) function

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

---

## License

[MIT](https://choosealicense.com/licenses/mit/)