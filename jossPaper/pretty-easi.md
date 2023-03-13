---
title: 'q2-makarsa : A qiime2 plugin for network analysis of microbial data'
tags:
  - Network analysis
  - Community structure
  - Microbial ecology
authors:
  - name: Zakir Hossine
    orcid: 0000-0001-6354-3166
    equal-contrib: true
    affiliation: 1
  - name: Ben Kaehler
    orcid: 0000-0002-5318-9551 
    equal-contrib: true 
    affiliation: 1
  - name: Isaac N. Towers
    orcid: 0000-0002-4308-6129
    equal-contrib: true
    affiliation: 1
affiliations:
  - name: School of Science, UNSW Canberra, Australia
    index: 1
date: March 2023
bibliography: joss.bib
---

# Summary

**q2-makarsa** is a plugin for the QIIME 2 microbiome bioinformatics platform. The plugin allows the QIIME 2 community to infer microbial ecological networks from community composition data from which we can identify central species and their influences on the species that have interactions with that central species. 

# Statement of need

A microbiome is an inevitable part of life and it can have both positive and negative impacts on human health even though we ignore its presence [@berg2020microbiome]. Interactions of the microbiome with itself and with its host may play a significant role in many areas; for example, food science [@singh2017microbiome; @torrazza2011developing], health science [@torrazza2011developing] and agricultural production [@suman2022microbiome]. If it is possible to reveal the functions, interactions, temporal and spatial structures, and population dynamics of microbial communities, it will not only be a scientific discovery, but it will also contribute to human health, biotechnological development, agriculture, and environmental protection. To discover the interactions among microbiota within or between ecosystems, network analysis is an important starting point. It allows us to investigate questions from the species level to the community level within a common formal mathematical framework. Here, we present a qiime2 plugin that will help to infer microbial interactions by using network analysis.

**q2-makarsa** performs network analysis of microbiome data. It has two methods for network generation and one visualizer to visualize the generated network.  The name of available methods in q2-makarsa are spieceasi and flashweave, which call SpiecEasi and FlashWeave respectively to generate an ecological network for given compositional data. The name of the visualizer of this plugin is 'visualization' which takes generated network as input and visualizes it in a publication-quality figure.


In spieceasi,ecological interactions between microbial populations are infered by 

- taking advantage of the proportionality invariance of relative abundance data and 
- making assumptions about the underlying network structure when the number of taxa in the dataset is larger than the number of sampled communities [@kurtz2015sparse].

It provides several methods for neighbourhood selection, for example mb, glasso, slr etc, and uses StARS for model selection. There are several other parameters that are also used in this plugin, for more details please visit [](https://github.com/zdk123/SpiecEasi). 
On the otherhand, in flashweave, interactions between microbes are predicted by statistical co-occurrence or co-abundance. To learn more about FlashWeave and its user manual, please visit [](https://github.com/meringlab/FlashWeave.jl).

The visualizar provide portable, shareable reports, publication-ready figures, and integrated decentralized data provenance. In addition,integration as a QIIME 2 plugin, makarsa supports the use of multiple user interfaces, including a prototype graphical user interface (q2studio), facilitating its use for non-expert users. The plugin is freely available under the BSD-3-Clause license at [](https://github.com/BenKaehler/makarsa).

The q2-makarsa plugin is written in Python, Julia, and R, and employs pandas [@mckinney2011pandas] for data manipulation, networkx [@hagberg2020networkx] and igraph [@csardi2006igraph] for network generation and visualization. We also used html [@raggett1999html] and javaScript[@arnold2005java] in some parts of our programming. The plugin is compatible with macOS and Linux operating systems.

![SpiecEasi pipeline.\label{fig:grl}](spieceasi.png){width=40%}

The standard workflow for SpiecEasi, which is called in q2-makarsa for network generation, is shown in \autoref{fig:grl} [@kurtz2015sparse]. q2-makarsa action accepts inp.file (i.e., matrix of feature counts per sample),out.file, method, lambda.min.ratio, nlambda, rep.num, ncores, thresh, subsample.ratio, seed, sel.criterion, verbose, pulsar.select, lambda.log, lambda.min and lambda.max as input for spieceasi method, and input_file,  input_meta, output, minclustersize, maxclustersize, pcadimension, nthreads, seed, alpha, nruns, subsampleratio, numclusters, maxoverlap and verbose for flashweave method. All of the input parameter has default values except input.file for spieceasi and input_file for flashweave. We have attached some statistical attributes to the network generated from spieceasi method. Here, we have used degree centrality, betweenness centrality, closeness centrality, eigenvector centrality, and associativity as node attributes. we also used weight to edges, although a weighted network is only available for mb and glasso methods. This plugin has one visualizer, which takes network object as input and then visualizes that network.

# Acknowledgements

The authors acknowledge support from University of Dhaka, Bangladesh and UNSW Canberra, Australia. This work is a partial fullfillment of PhD research at UNSW Canberra.
# References
