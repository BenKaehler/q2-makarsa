---
title: 'q2-makarsa : A QIIME 2 plugin for network analysis of microbial data'
tags:
  - Network analysis
  - Community structure
  - Microbial ecology
authors:
  - name: Zakir Hossine
    orcid: 0000-0001-6354-3166
    equal-contrib: true
    affiliation: 1
  - name: Isaac N. Towers
    orcid: 0000-0002-4308-6129
    equal-contrib: true
    affiliation: 1
  - name: Ben Kaehler
    orcid: 0000-0002-5318-9551 
    equal-contrib: true 
    affiliation: 1
affiliations:
  - name: School of Science, UNSW Canberra, Australia
    index: 1
date: April 2023
bibliography: joss.bib
---

# Summary

**q2-makarsa** is a plugin for the QIIME 2 microbiome bioinformatics platform.
The plugin allows the QIIME 2 community to infer and visualise microbial
ecological networks from compositional data. Ecological networks provide a
method for detecting community structure and identifying key species, peptides,
or any biologically meaningful covariates.

# Statement of need

The bacteria, fungi, viruses, and other microbes that inhabit a specific
habitat are known collectively as a microbiome. The microbiomes that occupy the
human body crucially impact human health in positive and negative ways
[@berg2020microbiome]. Microbe-microbe and host-microbe interactions may play a
significant role in many areas; for example, food science
[@singh2017microbiome; @torrazza2011developing; @foodsecurity2017], health
science [@torrazza2011developing; @diease2011] and agricultural production
[@berg2020microbiome]. Understanding the functions, interactions, temporal and
spatial structures, and population dynamics of microbial communities, will lead
to breakthroughs in those areas. To discover the interactions among microbiota
within or between ecosystems, network analysis is an important starting point.
It allows us to investigate questions from the species level to the community
level within a common formal mathematical framework [@Zakir - it looks like you
took this text from https://doi.org/10.1111/brv.12433. Please cite it here].
Here, we present a QIIME 2 plugin [@Bolyen2019] that will help to infer
microbial interactions by using network analysis.

**q2-makarsa** makes available the functionality of SpiecEasi
[@kurtz2015sparse] and FlashWeave [@tackmann2019rapid], two popular tools for
microbial network analysis, within the QIIME 2 microbiome bioinformatics
platform. Among currently available microbial network analysis tools, SpiecEasi
has been comparatively widely adopted by the microbiome research community and
has been cited in almost 1000 scientific publications [@google2023]. SpiecEasi
has been rigorously tested and benchmarked against other methods for microbial
network analysis and has been shown to perform well across a variety of
datasets and scenarios. FlashWeave [@tackmann2019rapid] is another new package
used for microbial network analysis, and it is gaining popularity and
acceptance in the scientific community for its novel algorithm, large-scale
analysis, and multinomics integration properties. Both packages are actively
developed and maintained by dedicated teams of developers, which means that
they are regularly updated and improved with new features and bug fixes.
Overall, SpiecEasi and FlashWeave are powerful tools for analyzing microbial
data and identifying potential interactions between microbial taxa.

The current version of **q2-makarsa** exposes the two methods for network
inference SpiecEasi and FlashWeave by the parameter options `spiec-easi` and
`flashweave` respectively. Specifically, **q2-makarsa** makes available: 

* All of [SpiecEasi's](https://github.com/zdk123/SpiecEasi) features except
  batch-mode execution (thread-level parallelism is supported);
* [FlashWeave's](https://github.com/meringlab/FlashWeave.jl) `learn_network`
  features in their entirety. 

The universal visualisation method is accessed by the option
`visualise-network`. This option combined with QIIME 2 `view` tool allows the
user to understand the inferred ecological network is a variety of ways.

* The network is interactive and its overall size and shape on the screen can
  be manipulated manually within the user's browser.
* A publication ready image of the network can be saved to the local device in
  PNG format.
* Network nodes can be selected and information on which feature (eg. ASVs,
  OTUs, MVs, taxa, peptides)  is represented by the node, statistics, and
  various centrality measures for the node will be displayed.
* Network edges are colour coded for positive (blue) and negative (orange)
  correlations
* Edge thickness is scaled according to statistics appropriate to each method
  with thicker edges indicating stronger connections between features.
* Node size is scaled according user-selected statistics such as centrality
  measures.
* Nodes are colour coded according to user-selected categories such as
  taxonomic classification
* Settings are synchronised across tabs meaning that if you have multiple tabs
  open in the visualisation, any changes you make to the settings (such as the
  scaling of edges or nodes) will be applied to all tabs at once.
* Node attributes can be added via feature metadata (eg. taxonomy, DNA
  sequence, differential abundance scores). If the node attributes are
  taxonomic labels, visualisation offers colourings at any taxonomic level


<!-- In spieceasi, ecological interactions between microbial populations are inferred
by 
- taking advantage of the proportionality invariance of relative abundance data
  and 
- making assumptions about the underlying network structure when the number of
  taxa in the dataset is larger than the number of sampled communities
  [@kurtz2015sparse].

It provides several methods for neighbourhood selection, for example mb,
glasso, slr etc, and uses StARS for model selection. There are several other
parameters that are also used in this plugin, for more details please visit
[SpiecEasi homepage](https://github.com/zdk123/SpiecEasi). 

On the other hand, FlashWeave uses a statistical approach to infer these
relationships based on conditional mutual information tests, which allows it to
handle both linear and non-linear relationships between variables.
Additionally, FlashWeave includes various algorithmic parameters, such as
heterogeneous and sensitive, which can be used to optimize performance and
sensitivity based on the specific properties of the dataset being analyzed.
Finally, FlashWeave is a valuable tool for microbial network analysis because
it allows researchers to identify potentially important relationships between
microbes in complex communities, which can help to better understand the
underlying biology and potentially lead to the development of new therapies or
interventions for various diseases. To learn more about FlashWeave and its user
manual, please visit the project
[homepage](https://github.com/meringlab/FlashWeave.jl).

The name of the visualizer of this plugin is 'visualisation' which takes
generated network as input and visualizes it in a publication-quality figure.
The visualizer provides portable, shareable reports, publication-ready figures,
and integrated decentralized data provenance. In this visualizer, we have
attached some statistical attributes to the network generated from the
spieceasi and flashweave methods to make our network more attractive and
informative. For example, we have added different centrality measurements as
node attributes in the generated network. In this case, we have used
betweenness centrality, degree centrality, closeness centrality, and
eigenvector centrality to measure the centrality properties of nodes, which can
be used in visualisation as the size of the nodes of the generated network. By
doing this we can easily identify which node has the most betweenness value in
that network, in other words, which microbial species is most influential in
that ecological network. We also have added weights of interactions as edges
attribute, although a weighted network is only available for mb and glasso
methods, which will help to identify the pair of microbial taxa which have the
most interactions among any other pair of microbial taxa in that network.
Overall, from visualisation, one can easily identify which species are most
influential in that community and which pair of microbial species have stronger
interactions. In addition, integration as a QIIME 2 plugin, makarsa supports
the use of multiple user interfaces, including a prototype graphical user
interface (q2studio), facilitating its use for non-expert users. The plugin is
freely available under the BSD-3-Clause license at
[](https://github.com/BenKaehler/makarsa).

 DO WE NEED THIS?
The q2-makarsa plugin is written in Python, Julia [@bezanson2017julia], and R,
and employs pandas [@mckinney2011pandas] for data manipulation, networkx
[@hagberg2020networkx] and igraph [@csardi2006igraph] for network generation
and visualization. We also used html [@raggett1999html] and
javaScript[@arnold2005java] in some parts of our programming. The plugin is
compatible with macOS and Linux operating systems. -->

![SpiecEasi pipeline.\label{fig:grl}](flowchart.png){width=40%}   ![SpiecEasi
pipeline.\label{fig:grl}](overview.png){width=40%}

<!-- DO WE NEED THIS?
The standard workflow and an overview of this plugin are shown in
\autoref{fig:grl} [@kurtz2015sparse]. q2-makarsa action accepts inp.file (i.e.,
matrix of feature counts per sample),out.file, method, lambda.min.ratio,
nlambda, rep.num, ncores, thresh, subsample.ratio, seed, sel.criterion,
verbose, pulsar.select, lambda.log, lambda.min and lambda.max as input for
spieceasi method, and input_file,  input_meta, output,heterogeneous, sensitive,
max_k, alpha, conv, feed_forward, max_tests, hps, FDR, n_obs_min, time_limit,
normalize, track_rejections, verbose, transposed, prec, make_sparse, and
update_interval for flashweave method. All of the input parameter has default
values except input.file for spieceasi and input_file for flashweave. . The
visualizer takes network object as input and then visualizes that network.
-->

# Acknowledgements

The authors acknowledge support from University of Dhaka, Bangladesh and UNSW
Canberra, Australia. This work is a partial fulfilment of PhD research at
UNSW Canberra.

# References

