"""
run DEPTA from command line.
e.g. http://www.iens.nl/restaurant/10545/enschede-rhodos output.html
"""
import sys
from pydepta.depta import Depta

if __name__ == '__main__':
    depta = Depta()
    regions = depta.extract(url=sys.argv[1], verbose=True)
    with open(sys.argv[2], 'w') as f:

        print >> f, '<html><head><title>Extraction Result</title>'
        print >> f, '<style type=\"text/css\">table {border-collapse: collapse;} td {padding: 5px} table, th, td { border: 3px solid black;} </style>'
        print >> f, '</head><body>'

        for i, region in enumerate(regions):
            print >> f, '<h2>Table %s</h2>' %i
            print >> f, '<table>'
            items = region.items
            for j, item in enumerate(items):
                print >> f, '<tr>'
                print >> f, '<td>Item %s</td>' %j
                for field in item.fields:
                    print >> f, '<td>%s</td>' %field.text.encode('utf8')
                print >> f, '</tr>'
            print >> f, '</table>'
        print >> f, '</body></html>'