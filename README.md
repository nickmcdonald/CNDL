# CNDL

Development environment is only set up for windows at the moment.

## Setting up dev Environment
### Dependancies
- Anaconda
- Git

``` bash
git clone https://github.com/nickmcdonald/CNDL.git
conda env create
conda activate cndl
```

For development testing you can run CNDL with
``` bash
python cndl.py
```

## Building
## Dependancies
- WiX Toolset - https://wixtoolset.org/releases/
- 7zip - https://www.7-zip.org/

You will need to add WiX and 7zip to PATH

To build the executable and installers use
``` bash
build [version number]
```
The results will be in the dist directory
