## pydepta

pydepta is a Python implementation of Yanhong Zhai and Bing Liu's work on Web Data Extraction Based on Partial Tree Alignment. [1]
The basic idea is to extract the data region with tree match algorithm (see Bing Lius' previous work on MDR [3]) and then build a seed tree on top of records to extract the data fields.

### Usage

- extract from html page

```python
>>> from pydepta import Depta
>>> from urllib2 import urlopen
>>> d = Depta()
>>> html = "<html></html>"
>>> regions = d.extract(html)
```

- extract from url

```python
>>> from pydepta import Depta
>>> d = Depta()
>>> regions = d.extract(url='http://www.iens.nl/restaurant/10545/enschede-rhodos')
```

- infer with seed

```python
>>> from pydepta import Depta
>>> d = Depta()
>>> seed = d.extract(url='http://www.iens.nl/restaurant/10545/enschede-rhodos')[5]
>>> d.infer(seed=seed, url='http://www.iens.nl/restaurant/34397/apeldoorn-de-boschvijver')
>>>
```

## Example Output:
![example 1](https://raw.github.com/tpeng/pydepta/master/snapshot1.png)

### Author
pengtaoo AT gmail.com

### Credit
1. [Web Data Extraction Based on Partial Tree Alignment](http://dl.acm.org/citation.cfm?id=1060761)
2. [SDE](https://github.com/seagatesoft/sde)
3. [Mining Data Records in Web Pages](http://dl.acm.org/citation.cfm?id=956826)