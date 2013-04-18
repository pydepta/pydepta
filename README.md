## pydepta

pydepta is a Python implementation of Yanhong Zhai and Bing Liu's work on Web Data Extraction Based on Partial Tree Alignment. [1]
The basic idea is to extract the data region with tree match algorithm (see Bing Lius' previous work on MDR [3]) and then build a seed tree on top of records to extract the data fields.

Special thanks to SDE[2] a Java implementation of DEPTA. I basically rewrote it with Python with some improvement.

### Usage

simply run the depta.py with url you want to extract. Also there will be a output.html generated which annonated the data
records with colors.

1. [Web Data Extraction Based on Partial Tree Alignment](http://dl.acm.org/citation.cfm?id=1060761)
2. [SDE](https://github.com/seagatesoft/sde)
3. [Mining Data Records in Web Pages](http://dl.acm.org/citation.cfm?id=956826)

tpeng <pengtaoo@gmail.com>
