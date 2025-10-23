# DEW Benchmark

## Copyright Notice & Dataset Sources

The DEW dataset splits rely on equations, definitions, concepts, and sample exercise problems are collected from the following three reference books:

* Book #1: [Irrigation Guide](https://irrigationtoolbox.com/NEH/Part652_NationalIrrigationGuide/cov_pre.pdf)
    * Authors: USDA (1997)
    * Restrictions: Not Copyrighted/Allowed by the US federal government.
    * Authors's License Statement: Free to use.
* Book #2: [FAO Irrigation Water Management: Irrigation Water Needs](https://www.fao.org/4/s2022e/s2022e00.htm)
    * Authors: FAO (1986)
    * Restrictions: Copyrighted  
    * Authors's License Statement: **“All rights reserved.”**
* Book #3: [Irrigation Systems Management](https://asabe.org/ism)
    * Authors: Eisenhauer et al. (2021)
    * Restrictions: Copyrighted
    * Authors's License Statement: **“This work is licensed under a Creative Commons Attribution 4.0 International License (CC BY-NC-ND).”**


Due to licensing and copyright issues, this repository only reflects information related to Book #1. As of the time of creation of this repository, Books #2 and #3 are still accessible and available online, at their provided link, for the inspection of all.


## Dataset Splits Creation

The DEW-LogiQ split is the continuation of the AgXQA V1 dataset, whose original data sources and creation process (e.g., curation, annotations, etc.)  have been detailed [here](https://huggingface.co/datasets/msu-ceco/agxqa_v1). Compared to AgXQA, DEW-LogiQ is a multiple-choice based QA dataset. It is available [here](). 

The DEW-MathQ split is generated and validated automatically given that it contains symbolic equations. The rest of the document describes its creation process.


### Pre-requisites

* Neo4j Community Edition ([Installation Docs](https://neo4j.com/docs/operations-manual/current/installation/))
* Neo4j Python Driver ([Installation Docs](https://neo4j.com/docs/python-manual/current/install/))


### Folder Structure



