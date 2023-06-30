import os, os.path, sys
import glob
from xml.etree import ElementTree



def run(files):
    xml_files = glob.glob(files +"/*.xml")
    xml_element_tree = None
    for xml_file in xml_files:
        data = ElementTree.parse(xml_file).getroot()
        # print (ElementTree.tostring(data))
        for result in data.iter('Header'):
            if xml_element_tree is None:
                xml_element_tree = data 
            else:
                xml_element_tree.extend(result) 
    if xml_element_tree is not None:
        #print (ElementTree.tostring(xml_element_tree))
        f =  open("myxmlfile.xml", "wb")
        f.write(ElementTree.tostring(xml_element_tree))
        f.close()




run(os.getcwd())









