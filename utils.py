#INVALID = 'N/A'

def appendColumns(columns):
    columnList = []
    for c in columns:
        columnList.append(c)
    return columnList

def isValid(item):
    return (item != 'N/A' and (not (not item))) #Do not contain invalid and is not empty

def getValue(function, attribute, conn):

    CURSOR_VALUE = conn.cursor()

    if (function == 'MIN'):
        function = "MAX(MIN("+attribute+"), 0)"
    else:
        function = "MAX("+attribute+")"
    query = "SELECT "+function+" FROM movies WHERE "+attribute+" != 'N/A'"
    #print query
    CURSOR_VALUE.execute(query)
    return CURSOR_VALUE.fetchone()[0]

def loadMinMaxValues(conn, COLUMNS):    
    for c in COLUMNS:
        MIN.append(float(getValue('MIN', c, conn)))
        MAX.append(float(getValue('MAX', c, conn)))
