## pydepta

pydepta is a Python implementation of Yanhong Zhai and Bing Liu's work on Web Data Extraction Based on Partial Tree Alignment. [1]
The basic idea is to extract the data region with tree match algorithm (see Bing Lius' previous work on MDR [3]) and then build a seed tree on top of records to extract the data fields.

Special thanks to SDE[2] a Java implementation of DEPTA. I basically rewrote it with Python with some improvement.

### Usage

- extract from html page

```
>>> from pydepta import depta
>>> from urllib2 import urlopen
>>> d = depta.Depta()
>>> html = "<html></html>"
>>> regions = d.extract(html)
```

- extract from url

```
>>> from pydepta import depta
>>> d = depta.Depta()
>>> regions = d.extract(url='http://www.amazon.com')
```

- convert region to other format

```
>>> from pydepta import depta
>>> d = depta.Depta()
>>> regions = d.extract(url='http://www.amazon.com')
>>> print regions[0].as_html_table()
>>> print regions[0].as_plain_texts()
```

## Example Output:
![example 1](https://raw.github.com/tpeng/pydepta/master/snapshot1.png)

### Author
pengtaoo AT gmail.com
