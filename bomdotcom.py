import re # for regex
import json # for formatting output into json
import sys # for accepting file input at command line

output = {}  # initialize dictionary to track reference designators
count = {}  # initialize dictionary to track material occurences

formats = [ # store list of given line formats in regex
    r'(?P<partNum>.*):(?P<manufacturer>.*):(?P<refDes>.*)',
    r'(?P<manufacturer>.*) -- (?P<partNum>.*):(?P<refDes>.*)',
    r'(?P<refDes>.*);(?P<partNum>.*);(?P<manufacturer>.*)',
]

def parseLine(line):

    line = line.strip('\n')

    # check which format line matches and extract 
    for f in formats:
        extract = re.search(f, line)
        if extract:
            extract = extract.groupdict()
            key = (extract['manufacturer'], extract['partNum'])
            refDes = set(extract['refDes'].split(','))
            return key, refDes
    raise Exception('Material is formatted incorrectly: {0}'.format(line))


def generateOutput(fileline):

    key, refDes = parseLine(fileline) # using tuple of manufacturer and MPN as identifier key

    # using try/except over single condition if/else for better perfomance
    try:
        count[key] += 1
    except:
        count[key] = 1

    try:
        output[key] = output[key] | refDes # combining sets maintains uniqueness
    except:
        output[key] = refDes

def formatJSON():
    # list out output and count dictionaries into json formatted list
    jsonValues = [{"MPN": k[1], "Manufacturer": k[0], "ReferenceDesignators": sorted(v), "NumOccurrences": count[k]} for k, v in output.items()]

    # sort json formatted list by num of occurrences then num of reference designators
    jsonValues = sorted(jsonValues, key=lambda k: (k.get('NumOccurrences'), len(k['ReferenceDesignators'])), reverse=True)

    return jsonValues


if __name__ == '__main__':

    f = open(sys.argv[1], 'r')

    numToDisplay = int(f.readline())  # store num of lines to print at end

    for line in f:
        generateOutput(line)
    
    jsonOutput = formatJSON()

    # use json.dumps() to format function output list into JSON, displaying first <numToDisplay> items
    print(json.dumps(jsonOutput[:numToDisplay], indent=4))

    f.close()