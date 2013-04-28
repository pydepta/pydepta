## pydepta

pydepta is a Python implementation of Yanhong Zhai and Bing Liu's work on Web Data Extraction Based on Partial Tree Alignment. [1]
The basic idea is to extract the data region with tree match algorithm (see Bing Lius' previous work on MDR [3]) and then build a seed tree on top of records to extract the data fields.

Special thanks to SDE[2] a Java implementation of DEPTA. I basically rewrote it with Python with some improvement.

### Usage

- extract from html page

```
>>> import depta
>>> from urllib2 import urlopen
>>> d = depta.Depta()
>>> html = urlopen('http://www.amazon.com').read()
>>> d.extract(html)
```

- extract from url

```
>>> import depta
>>> d = depta.Depta()
>>> d.extract(url='http://www.amazon.com')
```

- extract and annoate the data records with colors

```
>>> import depta
>>> d = depta.Depta()
>>> d.extract(url='http://www.amazon.com', annotate='1.html')
```

- get the data fields

```
>>> import depta
>>> depta = Depta()
>>> items = depta.extract(url=sys.argv[1])
>>> for item in enumerate(items):
        print ' | '.join(map(lambda x: x.text, item.fields))
```

1. [Web Data Extraction Based on Partial Tree Alignment](http://dl.acm.org/citation.cfm?id=1060761)
2. [SDE](https://github.com/seagatesoft/sde)
3. [Mining Data Records in Web Pages](http://dl.acm.org/citation.cfm?id=956826)

### Author
pengtaoo AT gmail.com
