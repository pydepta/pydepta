"""
run DEPTA from command line.
e.g. http://www.iens.nl/restaurant/10545/enschede-rhodos output.html
"""
import sys
from pydepta.depta import Depta

if __name__ == '__main__':
    depta = Depta()
    regions = depta.extract(url=sys.argv[1])
    with open(sys.argv[2], 'w') as f:

        print >> f, '<html><head><title>Extraction Result</title>'
        print >> f, '<style type=\"text/css\">table {border-collapse: collapse;} td {padding: 5px} table, th, td { border: 3px solid black;} </style>'
        print >> f, '</head><body>'

        for i, region in enumerate(regions):
            print >> f, '<h2>Table %s</h2>' %i
            print >> f, region.as_html_table()
        print >> f, '</body></html>'