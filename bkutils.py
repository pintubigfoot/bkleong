import csv, io

def loadCsv(debug=False):
  csvfile = file('bkconfig.csv', 'r')
  csvreader = csv.reader(csvfile)

  element = {} # format: { key, [ [type,id,tag], [type,id,tag]... ] }
    
  for i,row in enumerate(csvreader): 
    if debug: print printCsv(row).strip()
    level    = row[0]
    comptype = row[1]
    compname = row[2]

    if   comptype.strip().lower() == 'button':
      tag = '<input type=submit   id="%s" name="%s" value="%s">'%(compname,compname,compname)
    elif comptype.strip().lower() == 'checkbox':
      tag = '<input type=checkbox id="%s" name="%s" value="%s">'%(compname,compname,compname)
      tag+= '<label for="%s">%s</label>'%(compname,compname)
    else: 
      print 'Unsupported %s at line %s'%(compname,i+1)
      continue

    try:
      level = int(level)
      element[level] = element.get(level,[]) + [[comptype, compname, tag]]
    except:
      print 'Unsupported level %s at line %s'%(level,i+1)

  keylevel = element.keys()
  keylevel.sort()
    
  if debug:
    for level in keylevel:
      for comp in element[level]:
        print 'level %s: %s' % (level, comp)

  return keylevel, element

def printCsv(csvdata):
  output = io.BytesIO()
  csvwriter = csv.writer(output)
  csvwriter.writerow(csvdata)
  return output.getvalue()

if __name__=='__main__':
  loadCsv(debug=True)

