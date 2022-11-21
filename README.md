# q2-PKGNAME

PKGNAME is a plugin to incorporate some functionality from the  [SpiecEasi](https://github.com/zdk123/SpiecEasi) package into the QIIME 2 environment together with additional network visualisation.

## What is it

### QIIME2

<img align="right" src="images/qiime2.png">

[QIIME 2](https://qiime2.org/) is a powerful, extensible, and decentralized microbiome analysis package with a focus on data and analysis transparency. QIIME 2 enables researchers to start an analysis with raw DNA sequence data and finish with publication-quality figures and statistical results.

### SpiecEasi

SpiecEasi (Sparse InversE Covariance estimation for Ecological Association and Statistical Inference) is an [R based](https://www.r-project.org/) package which allows the user to infer microbial ecological networks from compositional datasets typically generated from 16S amplicon sequencing. 

### Plug-in Features

PKGNAME is at the $\alpha$ stage.

<!-- Things not in the plugin / either no included or not completed -->
<!-- qiime spieceasi --citations  -->
<!-- qiime spieceasi --example-data  -->

## Installation

PKGNAME requires a working QIIME 2 environment. The recommended way to [install](https://docs.qiime2.org/2022.8/install/native/) QIIME 2 is through [miniconda](https://docs.conda.io/en/latest/miniconda.html). Miniconda can be conveniently installed using the native package managers of various Linux distributions.  See the instructions for RPM-based and Debian-based distributions [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/rpm-debian.html). Arch Linux users can find miniconda in the [AUR](https://aur.archlinux.org/packages/miniconda3).

Once miniconda has been installed, issue the following commands within the shell
```
conda update conda
conda install wget
```
and install QIIME 2
```
wget https://data.qiime2.org/distro/core/qiime2-2022.8-py38-linux-conda.yml
conda env create -n qiime2-2022.8 --file qiime2-2022.8-py38-linux-conda.yml
```

Test the installation with `qiime --help`. An error free output means successful installation and the QIIME 2 environment can be activated. For example, 

```conda activate qiime2-2022.8```

Install 


## Usage Example
