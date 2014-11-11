import math
import xml.etree.ElementTree

global xmlFilePath

class MultipathDetector():
    xmlFilePath = "ui.xml"

    @staticmethod
    def computeDistance(coord1, coord2):
        coord1_x, coord1_y = coord1
        coord2_x, coord2_y = coord2

        coord1_x = float(coord1_x)
        coord2_x = float(coord2_x)
        coord1_y = float(coord1_y)
        coord2_y = float(coord1_y)

        distance = math.sqrt(((coord1_x - coord2_x)**2)+((coord1_y - coord2_y)**2))

        if distance <= 0.0:
            print "distance between two coordinates is less than or equal to zero - something is wrong!  (MultipathDetector.distanceForumula)"
            return None
        else:
            return distance

    @staticmethod
    def computeUnitVector(coord1, coord2):
        coord1_x, coord1_y = coord1
        coord2_x, coord2_y = coord2

        distance1_2 = MultipathDetector.computeDistance(coord1, coord2)
        # Note: distanceFormula ensures that no distances <= 0 are returned, thus division here should be safe
        unitVector1_x, unitVector1_y = ((coord1_x - coord2_x) / distance1_2), ((coord1_y - coord2_y) / distance1_2)

        return (unitVector1_x, unitVector1_y)

    @staticmethod
    # TODO:   NOTE!!!  coord2 needs to be the center receiver's coordinates
    def computeDotProduct(coord1, coord2, coord3):
        unitVector1_x, unitVector1_y = MultipathDetector.computeUnitVector(coord1, coord2)
        unitVector2_x, unitVector2_y = MultipathDetector.computeUnitVector(coord2, coord3)

        dotProduct = ((unitVector1_x*unitVector2_x) + (unitVector1_y*unitVector2_y))

        return dotProduct

    @staticmethod
    def computeDotProductTolerance():
        tree = xml.etree.ElementTree.parse(xmlFilePath)
        root = tree.getroot()
        distance = root.get("gps_spacing")
        tolerance = root.get("horizontal")

        # might want to ensure that tolerance is non-zero. Should be done when input by user, but might want to double-check here
        dotProductTolerance = math.acos(math.pi - 2 * math.atan(distance / tolerance))

        return dotProductTolerance

    # returns True if multipathing is detected, otherwise returns False
    @staticmethod
    def multipathDetect(coord1, coord2, coord3):
        tree = xml.etree.ElementTree.parse(xmlFilePath)
        root = tree.getroot()

        dotProductTolerance = MultipathDetector.computeDotProductTolerance()

        gpsDistance = root.get("gps_spacing")
        linearTolerance = root.get("horizontal")

        dist1_2 = MultipathDetector.computeDistance(coord1, coord2)
        dist2_3 = MultipathDetector.computeDistance(coord2, coord3)
        dist1_3 = MultipathDetector.computeDistance(coord1, coord3)

        # initially assume no multipathing
        if dist1_2 < (gpsDistance - linearTolerance):
            return True
        elif dist1_2 > (gpsDistance + linearTolerance):
            return True
        elif dist2_3 < (gpsDistance - linearTolerance):
            return True
        elif dist2_3 > (gpsDistance + linearTolerance):
            return True
        elif dist1_3 < (2*gpsDistance) - linearTolerance:
            return True
        elif dist1_3 > (2*gpsDistance) + linearTolerance:
            return True

        dotProduct = MultipathDetector.computeDotProduct(coord1, coord2, coord3)

        # Note: this first case should NEVER occur - a dot product is bounded between [-1, 1] (inclusive)
        if dotProduct > (1 + MultipathDetector.computeDotProductTolerance()):
            return True
        elif dotProduct < (1 - MultipathDetector.computeDotProductTolerance()):
            return True

        return False




