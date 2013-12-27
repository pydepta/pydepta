========
PyDepta
========

PyDepta is a library to extract structured data from HTML page. It can works in both supervised and unsupervised model.

Under the hold, PyDepta implemented Yanhong Zhai and Bing Liu's work on `Web Data Extraction Based on Partial Tree Alignment`_
to extract data without example data (so called unsupervised learning).
The basic idea is of this algorith is to extract the data region with tree match algorithm (see Bing Lius' previous work on MDR_)
and then build a seed tree on top of records to extract the data fields.

PyDepta can also extract data with example data (so called supervised learning).
It relies on Scrapely_ to extract the structured data after you tell it the data you'd to extract.

Usage
========

1. (Unsupervised) Extract from url
==================================

In this model PyDepta extract the data blindly base on the similarity of subtrees.::

    >>> from pydepta import Depta
    >>> d = Depta()
    >>> url1 = 'http://www.iens.nl/restaurant/12229/nijmegen-pasta-e-fagioli'
    >>> seed = d.extract(url=url1)[8]
    >>> seed.as_plain_texts()[0]

    ['MartenHH', 'Meesterproever', '5 maanden geleden', '7', '10', '1', 'Eten', '6', 'Service', '9', 'Decor', 'Afgelopen zaterdag avond hebben we hier met z\'n zessen heerlijk kunnen dineren. De entourage was erg prettig en de bediening verliep soepel, op een paar vreemde uitschieters na (zie hieronder). Het voorgerecht op basis van aubergine, tomaat en mozarella was lekker. Ook het hoofdgerecht - de kalfsoester met serano ham was goed maar niet perse bijzonder. Er werden ook bijgerechten geserveerd op losse schaaltjes, maar heaas werd er werd niet gevraagd of alles voldoende was. De salade was bv snel op. De porties voldeden overigens prima en zeker na het nagerecht gingen wij zeer voldaan naar huis. \nTot zover de sterke punten. Wat bij een restaurant van dit prijsniveau gewoon niet mag voorkomen zijn de volgende twee zaken. Ten eerste werd ons bij het opdienen van het hoofdgerecht gevraagd wie wat had besteld. Dat hoort echt niet bij een restaurant van deze klasse, en voor mij is dit een echte afkapper. Ten tweede vroegen wij om advies over de wijnkaart. Dat ging helemaal mis. Wij kregen advies van degene die de wijnkaart zou hebben samen gesteld. Echter, toen ik vroeg of de "cannonau di sardegna" bij het menu zou passen werd deze mij zonder verdere motivatie ontraden. Deze zou een zeer vreemde smaak hebben en eigenlijk nergens bij passen. Ook andere adviezen kwamen niet echt uit de verf omdat degene die ons hielp niet echt met ons erover in gesprek leek te willen. Graag wat meer enthousiasme over de eigen wijnkaart - en ook kennis. Dat kan veel beter. Ze had bijvoorbeeld kunnen vragen waarom ik nu juist die ene wijn eruit pikte - het is nl een wijn die ik heel veel drink omdat ik hem erg lekker vind en overal bij vind passen - als het tenminste een goede fles is!', 'Gegeten op 17 augustus 2013', '', '', '', '', '\n                Deel            ', '\n                0 Reacties            ']

The result is a ``Region`` which can convert into plain texts (with ``region.as_plain_texts``) or a HTML table (with ``region.as_html_table``)
or a python dict with (``region_to_dict``)

2. (Supervised) Extract with seed region and data
=================================================

In this model you tell PyDepta the data you expect to scrape from seed region. e.g.
let's say on the seed region you'd like to scrape ``MartenHH`` as name, ``Afgelopen zaterdag avond hebben we...`` as text::


    >>> data = {'name': 'MartenHH', 'text': 'Afgelopen zaterdag avond hebben we'}

then just tell the PyDepta to scrape other similar pages on that site and it will return the results.::


    >>> url2 = 'http://www.iens.nl/restaurant/22513/zwolle-hotel-fidder'
    >>> for item in d.infer(seed, data, url=url2):
    ...     print item
    ...
    {u'text': [u'Heerlijke ontvangst van gastvrije en persoonlijke bediening. Eten is prima. Dit weekend gekozen voor gastronomisch arrangement en is echt goed. Goede keuzes met bijpassende wijnen. Lekker op loopafstand van Zwolle centrum.  Kortom een echte aanrader voor mensen die gastvrijheid en goed eten waarderen! En heb je kritiek of vragen: meldt het gewoon want hier wordt goed op ingespeeld.'], u'name': [u'CamielIens']}
    {u'text': [u"Van de week waren we neer gestreken in een heuse stadstuin, niet ver van onze geliefde Peperbus gelegen namen we plaats op het terras van Fidder's. Het was heerlijk vertoeven in de schaduwrijk tuin, een terras kan je het haast niet noemen. We zaten tussen een moestuin en kruidentuin in en spotte regelmatig de chef die wat kruiden nodig had. De gerechten waren erg lekker en goed verzorgt. Binnenkort kom ik zeker terug om te genieten van hun dineractie."], u'name': [u'Hendrikdeboer']}
    {u'text': [u'We hebben hier echt genoten van heerlijke vers bereide gerechten met een mooi wijnarrangement. Alles was goed op smaak. Mooie stadsreiniging en vriendelijke bediening. \nHier komen we graag terug'], u'name': [u'Vic1980']}
    {u'text': [u'Heerlijk eten, niveau sterrenrestaurant. Rare omgeving: in een nauwe straat ver van het centrum. Veel te langzame bediening, maar wel vriendelijk. We hebben hier een ANWB menu gegeten. Heel mals rundvlees en als voorgerecht forelmousse en als nagerecht broodpudding.'], u'name': [u'Mathilde30']}


Author
======
pengtaoo AT gmail.com

Deployment
===========
http://pydepta-heroku.herokuapp.com/

.. _Web Data Extraction Based on Partial Tree Alignment: http://dl.acm.org/citation.cfm?id=1060761
.. _SDE: https://github.com/seagatesoft/sde
.. _MDR: http://dl.acm.org/citation.cfm?id=956826
.. _Scrapely: https://github.com/scrapy/scrapely