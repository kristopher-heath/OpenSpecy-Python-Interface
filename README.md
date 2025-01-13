## **ATTENTION: THIS PACKAGE IS PRE-RELEASE AND NOT YET USABLE**
---
# OpenSpecy Python Interface

[OpenSpecy](https://github.com/wincowgerDEV/OpenSpecy-package) is a spectral processing tool for the analysis of Raman and FTIR spectra of environmental plastics. It contains several functions to process and enhance the spectral signals in order to obtain material matches by utilizing an online reference library. It is entirely open-source and free to use, both via an R package available on [CRAN](https://cran.r-project.org/web/packages/OpenSpecy/index.html) as well as a [web version](https://www.openanalysis.org/openspecy/) built with R shiny.

The web version is quite useful, but usage can be hindered by the strength of one's Internet connectivity. Additionally, there is currently no support for downloading a file containing the top *n* matches for all samples in a batch; instead, each file must be individually uploaded and processed, and then the table containing the top *n* matches can be viewed. This greatly restricts processing speed, especially for bulk file uploads. Additionally, the .csv exported by the web version contains many columns of data, and, depending on one's intended use, many may not be immediately necessary for the user. 

The OpenSpecy R package, however, can process all top *n* matches consecutively and quickly. The exported data table is still quite large and cumbersome, so for ease and speed of data interpretation, it is necessary to rearrange and exclude several of the columns. R is a great tool for this, but so is Python, which is more user-oriented and beginner-friendly, making it more accessible to less-code-literate people who may have a need for OpenSpecy.

Thus was the beginning of the **OpenSpecy-Python-Interface**, an all-in-one spectral data processing package. It contains several functions to 1) preprocess data to ensure it will be readable by the OpenSpecy R package, 2) call on R to execute a script that uses OpenSpecy, and 3) post-process the data to make a concise, readable Excel sheet containing all the data. It can also be utilized as a comprehensive script that processes your files from start to finish, reducing the need for prior coding knowledge.

---
## Setup and Installation
Note: This is a brief overview of the setup process. For a step-by-step walkthrough, please see the [Installation Tutorial](INSTALLATION_TUTORIAL.md).

**R Installation and Configuration**
* Download and install the most recent version of [R](https://cran.r-project.org/) for your OS
  - Note: R must be installed directly to your device, not inside an environment
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
* Use the package as outlined

---
## Notes
---
## Usage

```python
import openspecy-python-interface as osi
from osi import main


```
---
## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

---
## License

[MIT](https://choosealicense.com/licenses/mit/)
