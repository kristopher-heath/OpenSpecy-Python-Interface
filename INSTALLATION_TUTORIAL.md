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
2. In order for Python to interact with R, it must be able to access the `R_HOME` variable. However, because Python is within a virtual environment, this variable must manually specified before the package can be imported
   * Paste the following code **at the beginning of the script**
```bash
import os
os.environ['R_HOME'] = r"C:\Program Files\R\R-4.4.2"	# Paste your own R_HOME var here
import openspecy-python-interface
```
🎉 Congrats! You have completed setup and installation! 🎉

Please see the Usage section in the README for more information.
