import MultipathDetector
import math
import xml.etree.ElementTree as ET

M = MultipathDetector.MultipathDetector()

print M.computeDotProductTolerance()

print M.multipathDetect((103854.3257,2279680.2842),(103854.8191,2279680.3834),(103855.3392,2279680.4767))