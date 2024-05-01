import xml.etree.ElementTree as ET
try:
    tree = ET.parse('t.xml')
except Exception as e:
    print(e)
