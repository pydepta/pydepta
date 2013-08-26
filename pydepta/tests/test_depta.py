#coding=utf-8
import unittest
import os
import re
from pydepta.depta import Depta
from pydepta.mdr import element_repr

CASES = [
    ('1.html', 'http://www.iens.nl/restaurant/10545/enschede-rhodos', {
        'records': [[
            u'De laatste recensies|27 juli 2012|8|Eten|6|Service|7|Decor|met een grote groep hier gegeten, op het eten was niets aan te merken, verschillende voorgerechten en ook het hoofdgerecht was door de kok zelf samengesteld op ons verzoek. het duurde allemaal heel erg lang voordat we konden eten. Het was er druk, maar zelfs op het water moesten we lang wachten, dat viel ons erg tegen. prijs kwaliteit was goed.|Gegeten op: 28 juni 2012.|Nuttig|Meld de redactie|rianne|Expertproever',
            u"|30 december 2011|||||||Al sinds de opening, zo'n 25 jaar geleden, komen wij, met heel veel plezier, bij Rhodos. Buiten het feit dat Aslan en Sharly geweldige gastheren zijn, hebben zij ook een geweldige kok. Het eten is dan ook niet te versmaden. Een van onze favorieten: garnalen in roomsaus (voorgerecht) en de overheelijk gegrilde zalm als hoofd gerecht. (eat) De sfeer is er altijd ongedwongen en gezellig. Je voelt je er direct thuis. Als wij buiten de deur ergens willen eten komen wij heel regelmatig uit bij Rhodos. Je kunt de avond heerlijk genieten en je laten verwennen onder het genot van een goed glas wij (wine). Proost!!||Nuttig|Meld de redactie|0096352|Proever in spe",
            u"|28 december 2010|||||||Wederom lekker gegeten bij Aslan en Charly. Geen droge spiezen of koteletjes maar uitstekend gegrild. Het persoonlijke van beide heren is zeer aangenaam. Aanrader!||Nuttig|Meld de redactie|herja|Proever in spe",
            u"|28 augustus 2010|||||||Best wel een prima Griek. Natuurlijk veel te grote porties vlees, maar niet het moddervette spul dat veel andere Grieken je voorzetten. Kwaliteit van de groenten (salades, tomaten) niet slecht, maar ook niet memorabel. Bediening was rommelig.||Nuttig|Meld de redactie||Proever in spe",
            u'|25 november 2007|||||||Afgelopen zaterdag hier gegeten samen met mijn vriend. We zouden in een rookvrije ruimte zitten, maar al snel staken mensen rondom ons een sigaretje op. De halve uitleg die we kregen: "Ja maar als het druk is..." Daarnaast zouden we een uur moeten wachten op een stoofschotel met lam omdat deze op was. Ik heb toen voor een ander gerecht gekozen, waar we ook lang op moesten wachten. Het eten smaakte wel oke, maar meer dan dat kan ik er niet van maken. De rest duurde ook lang: nagerecht, rekening, drinken... Had beter verwacht.||Nuttig|Meld de redactie||Proever in spe',
            ]]
        }),

    ('2.html', 'http://www.diningcity.com/en/zeeland/restaurant_oesterbeurs', {
        'regions': [('<div #review_content .>', 3, 1, 4)],
        'records': [[u'Service|8.0|Atmosphere|6.0|Cuisine|8.0|7.3|Wij hebben een heerlijke avond gehad. En het eten was heel erg lekker. Dus bijzonder genoten. Alleen de drankjes waren vonden wij veel te duur. Bij binnenkomst werd ons gevraagd of we een aperitiefje van het huis wilde.Ja dat wilde wij wel. Het is maar hoe je het bekijkt. Van het huis of toch betalen. Het koste ons 34 euro. 7 glazen wijn 45,75 euro. We waren alles bij elkaar 86.50 kwijt aan drank en water. Ik vind dit eigenlijk wel een domper op deze leuke avond. Je denkt lekker uit eten te gaan, maar dan krijg je rekening en is de drank de helft meer dan je 4 gangen dinee.|georgina de winter, 13 Mar 2013, 12:30',
                    u'Service|7.0|Atmosphere|7.0|Cuisine|8.0|7.3|Het dnig wat jammer was dat ik niet wist dat je van te voren aan moest geven of je een vis of vlees menu wilde. Wat ook jammer was dat je als laatste koffie bestelde dat men niet vroeg of je alleen koffie wilde of koffie compleet. Je kreeg gewoon compleet (zonder te vragen) maar daar moest je dan ook gelijk bijna 7 euro voor betalen. Terwijl je alleen koffie besteld had. Men had dit eerst moeten aangeven!!|12 Mar 2013, 20:41',
                    u'Service|7.0|Atmosphere|8.0|Cuisine|9.0|8.0||11 Mar 2013, 10:58',
                    u'Service|10.0|Atmosphere|10.0|Cuisine|10.0|10.0|In de Oesterbeurs is het genieten in een ontspannen sfeer. Alles is goed uitgebalanceerd. Genoeg zit- en bewegingsruimte bijvoorbeeld. Vaak is dat aan de krappe kant. Bij de Oesterbeurs zitten ook mensen met lange benen ontspannen. De rest? Zie de punten. Dat zegt genoeg! In Yerseke zijn we er trots op!|Andries Jumelet, 11 Mar 2013, 09:38']]
        }),

    ('3.html', 'http://www.iens.nl/restaurant/12229/nijmegen-pasta-e-fagioli', {
        'regions': [('<hr #greyBreak .>', 8, 4, 20)],
        'records': [[u'20 juni 2013|8|Eten|8|Service|8|Decor|Een echte Italiaanse restaurant, waar heerlijke gerechten, bereid met verse ingrediënten. Ik miste traditionele een minestrone, maar tortellini met truffels gecreëerd een perfecte voorgerecht. Pasta e fagioli pasta biedt een zeer goede selectie scherpgeprijsde wijnen. Wij hebben bijna drie uur doorgebracht, genietend van leuke sfeer, Italiaanse muziek en een uitstekende service. Zal terug!|Gegeten op: 1 mei 2013.|Nuttig|Meld de redactie|benny21|Expertproever',
                    u'28 december 2012|9|Eten|10|Service|9|Decor|Heerlijk gegeten. Fijne bediening, niet van die snobs die je wel eens ziet bij chique restaurants. Ook de wijnen zijn geweldig. we zijn meestal 100 euro voor 2 personen kwijt (3 gangen en lekker wijn drinken). En dat is het geld echt waard.|Gegeten op: 13 december 2012.|Nuttig|Meld de redactie|LiekeL|Topproever',
                    u'9 december 2012|10|Eten|10|Service|10|Decor|Lekker authentiek origineel Italiaans eten en drinken. Fantastische Italiaanse wijnen met bijpassende mooie gerechten. Heerlijk brood, prachtige olijfolie, op brandschoon wit damast gedekte tafels, royale tussenruimte, sfeertekening filmdiva Sophia Loren. Super deskundige advisering, uitstekende bediening en prettige ambiance. Vertrouwd en heel goed toeven. Zeer aan te bevelen.|Gegeten op: 8 december 2012.|Nuttig|Meld de redactie|philip.|Proever in spe',
                    u'17 oktober 2012|8|Eten|8|Service|6|Decor|Verrassend lekker gegeten, italiaans en geen pizza gelukkig. Bediening is vriendelijk. Ik vind het eten aan de prijzige kant en vind het jammer dat er geen menu is. De kaart vind ik een beetje onoverzichtelijk, misschien italiaans.|Gegeten op: 13 oktober 2012.|Nuttig|Meld de redactie|ursie1|Proever',
                    u'16 september 2012|7|Eten|6|Service|7|Decor|Pasta e Fagioli heeft in feite twee kleine menukaarten: een met de klassieke Italiaanse gerechten en een met wat modernere gerechten. Maar mixen kan natuurlijk ook en dat doen we dan ook. We beginnen (na voorzien te zijn van wat brood en olie) met een klassieke vitello tonnato. De tonijnsaus is heerlijk zacht van smaak, maar de chef had wel iets royaler mogen zijn met de kappertjes om het iets meer pit te geven. Alles bij elkaar een aardig begin. Het hoofdgerecht komt van de modernere kaart en bestaat uit een flink stuk heerlijk malse parelhoen die nog aan het bot zit. Het korstje had nog net iets knapperige gemogen en iets meer bietensaus ware welkom geweest. We krijgen er wat boontjes en aardappeltje bij. Vooral dat laatste is weinig Italiaans, maar zal wel gezien moeten worden als een toegemoetkoming aan de Nederlandse voorkeuren. Het nagerecht is een chocoladetaartje waarin we tevergeefs een vloeibaar hart hoopten aan te treffen. Het smaakt desondanks wel. De wijnen, uiteraard Italiaans, zijn zeer goed. We zitten in een royale, strak ingerichte serre. De bediening is wat gehaast. Alles bijelkaar een prima maaltijd, zonder dat deze er nu echt uitspringt. En dat laatste is wel wat jammer want de prijs springt er wel wat bovenuit: 100 euro voor een 3-gangenmaaltijd, een 2-gangenmaaltijd, 4 glazen wijn en een koffie is royaal te noemen voor dit niveau.||Nuttig|Meld de redactie||Meesterproever'
                    ]]
        }),

    ('4.html', 'http://www.yp.com.hk/Dining-Entertainment-Shopping-Travel-b/Entertainment-Production-Services/CD-VCD-DVD-Manufacturers/p1/en/', {
        'regions': [('<div #listing_div .>', 0, 1, 13)],
        }),

    ('5.html', 'http://www.eet.nu/enschede/rhodos', {
        'regions': [('<li #feedback has-ratings has-scores .review_604121>', 0, 3, 21)],
        }),
    ]

def normalize_text(text):
    return re.sub(r'\s+', ' ', text.replace(u'\u00a0', ' ')).strip()

class DeptaTest(unittest.TestCase):
    def _get_html(self, fn):
        path = os.path.join(os.path.dirname(__file__), 'htmlpages', fn)
        return open(path, 'rb').read().decode('utf-8')

    def test_depta(self):
        depta = Depta()
        for fn, url, case in CASES:
            body = self._get_html(fn)
            regions = depta.extract(body)
            for k, vs in case.iteritems():
                if k == 'regions':
                    start_elements = [(element_repr(region.parent[region.start]), region.start, region.k, region.covered) for region in regions]
                    for v in vs:
                        self.assertTrue(v in start_elements, '%s region failed' %fn)
                if k == 'records':
                    records_texts = []
                    for region in regions:
                        texts = []
                        for item in region.items:
                            text = u"|".join(normalize_text(field.text) for field in item.fields)
                            texts.append(text)
                        records_texts.append(texts)
                    for v in vs:
                        self.assertTrue(v in records_texts, '%s record failed' %fn)

if __name__ == '__main__':
    unittest.main()

