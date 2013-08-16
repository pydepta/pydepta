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
>>> print regions[0].as_numpy_array()
>>> print regions[0].as_plain_texts()
```


## Example Output:

### <http://www.diningcity.com/en/zeeland/restaurant_oesterbeurs>
<table width="600">
<tbody><tr>
<td>Item 0</td>
<td>Service</td>
<td>8.0</td>
<td>Atmosphere</td>
<td>6.0</td>
<td>Cuisine</td>
<td>8.0</td>
<td>7.3</td>
<td>Wij hebben een heerlijke avond gehad. En het eten was heel erg lekker.
Dus bijzonder genoten.
Alleen de drankjes waren vonden wij veel te duur. Bij binnenkomst werd ons gevraagd of we een aperitiefje van het huis wilde.Ja dat wilde wij wel.
Het is maar hoe je het bekijkt. Van het huis of toch betalen. Het koste ons 34 euro. 7 glazen wijn 45,75 euro. We waren alles bij elkaar 86.50 kwijt aan drank en water. Ik vind dit eigenlijk wel een domper op deze leuke avond.
Je denkt lekker uit eten te gaan, maar dan krijg je rekening en is de drank de helft meer dan je 4 gangen dinee.</td>
<td>georgina de winter, 13 Mar 2013, 12:30</td>
</tr>
<tr>
<td>Item 1</td>
<td>Service</td>
<td>7.0</td>
<td>Atmosphere</td>
<td>7.0</td>
<td>Cuisine</td>
<td>8.0</td>
<td>7.3</td>
<td>Het dnig wat jammer was dat ik niet wist dat je van te voren aan moest geven of je een vis of vlees menu wilde.
Wat ook jammer was dat je als laatste koffie bestelde dat men niet vroeg of je alleen koffie wilde of koffie compleet.
Je kreeg gewoon compleet (zonder te vragen) maar daar moest je dan ook gelijk bijna 7 euro voor betalen. Terwijl je alleen koffie besteld had. Men had dit eerst moeten aangeven!!</td>
<td>12 Mar 2013, 20:41</td>
</tr>
<tr>
<td>Item 2</td>
<td>Service</td>
<td>7.0</td>
<td>Atmosphere</td>
<td>8.0</td>
<td>Cuisine</td>
<td>9.0</td>
<td>8.0</td>
<td>Heerlijk gegeten. Het eten was verrukkelijk en het wijn arrangement ook zeer goed. Volgens mij is de Oesterbeurs toe aan een opwaardering in de restaurantwereld.</td>
<td>11 Mar 2013, 10:58</td>
</tr>
<tr>
<td>Item 3</td>
<td>Service</td>
<td>10.0</td>
<td>Atmosphere</td>
<td>10.0</td>
<td>Cuisine</td>
<td>10.0</td>
<td>10.0</td>
<td>In de Oesterbeurs is het genieten in een ontspannen sfeer. Alles is goed uitgebalanceerd. Genoeg zit- en bewegingsruimte bijvoorbeeld. Vaak is dat aan de krappe kant. Bij de Oesterbeurs zitten ook mensen met lange benen ontspannen.
De rest? Zie de punten. Dat zegt genoeg! In Yerseke zijn we er trots op!</td>
<td>Andries Jumelet, 11 Mar 2013, 09:38</td>
</tr>
</tbody></table>

### <http://www.iens.nl/restaurant/12229/nijmegen-pasta-e-fagioli>

<table width="600">
<tbody><tr>
<td>Item 0</td>
<td>De laatste recensies</td>
<td>27 juli 2012</td>
<td>8</td>
<td>Eten</td>
<td>6</td>
<td>Service</td>
<td>7</td>
<td>Decor</td>
<td>met een grote groep hier gegeten, op het eten was niets aan te merken, verschillende voorgerechten en ook het hoofdgerecht was door de kok zelf samengesteld op ons  verzoek. het duurde allemaal heel erg lang voordat we konden eten. Het was er druk, maar zelfs op het water moesten we lang wachten, dat viel ons erg tegen. prijs kwaliteit was goed.</td>
<td>Gegeten op: 28 juni 2012.</td>
<td>Nuttig</td>
<td>Meld de redactie</td>
<td>rianne</td>
<td>Expertproever</td>
</tr>
<tr>
<td>Item 1</td>
<td></td>
<td>30 december 2011</td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td>Al sinds de opening, zo'n 25 jaar geleden, komen wij, met heel veel plezier,  bij Rhodos. Buiten het feit dat Aslan en Sharly geweldige gastheren zijn, hebben zij ook een geweldige kok. Het eten is dan ook niet te versmaden. Een van onze favorieten: garnalen in roomsaus (voorgerecht) en de overheelijk gegrilde zalm als hoofd gerecht. (eat) De sfeer is er altijd ongedwongen en gezellig. Je voelt je er direct thuis. Als wij buiten de deur ergens willen eten komen wij heel regelmatig uit bij Rhodos. Je kunt de avond heerlijk genieten en je laten verwennen onder het genot van een goed glas wij (wine). Proost!!</td>
<td></td>
<td>Nuttig</td>
<td>Meld de redactie</td>
<td>0096352</td>
<td>Proever in spe</td>
</tr>
<tr>
<td>Item 2</td>
<td></td>
<td>28 december 2010</td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td>Wederom lekker gegeten bij Aslan en Charly.
Geen droge spiezen of koteletjes maar uitstekend gegrild. Het persoonlijke van beide heren is zeer aangenaam. Aanrader!</td>
<td></td>
<td>Nuttig</td>
<td>Meld de redactie</td>
<td>herja</td>
<td>Proever in spe</td>
</tr>
<tr>
<td>Item 3</td>
<td></td>
<td>28 augustus 2010</td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td>Best wel een prima Griek. Natuurlijk veel te grote porties vlees, maar niet het moddervette spul dat veel andere Grieken je voorzetten. Kwaliteit van de groenten (salades, tomaten) niet slecht, maar ook niet memorabel. Bediening was rommelig.</td>
<td></td>
<td>Nuttig</td>
<td>Meld de redactie</td>
<td></td>
<td>Proever in spe</td>
</tr>
<tr>
<td>Item 4</td>
<td></td>
<td>25 november 2007</td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td>Afgelopen zaterdag hier gegeten samen met mijn vriend. We zouden in een rookvrije ruimte zitten, maar al snel staken mensen rondom ons een sigaretje op. De halve uitleg die we kregen: "Ja maar als het druk is..." Daarnaast zouden we een uur moeten wachten op een stoofschotel met lam omdat deze op was. Ik heb toen voor een ander gerecht gekozen, waar we ook lang op moesten wachten. Het eten smaakte wel oke, maar meer dan dat kan ik er niet van maken. De rest duurde ook lang: nagerecht, rekening, drinken...
Had beter verwacht.</td>
<td></td>
<td>Nuttig</td>
<td>Meld de redactie</td>
<td></td>
<td>Proever in spe</td>
</tr>
</tbody></table>

1. [Web Data Extraction Based on Partial Tree Alignment](http://dl.acm.org/citation.cfm?id=1060761)
2. [SDE](https://github.com/seagatesoft/sde)
3. [Mining Data Records in Web Pages](http://dl.acm.org/citation.cfm?id=956826)

### Author
pengtaoo AT gmail.com
