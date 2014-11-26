import math
import xml.etree.ElementTree as ET

xmlFilePath = 'ui.xml'

class MultipathDetector():
    

    @staticmethod
    def parseTupleFile():
        filePath = "cartesianTupleFile.txt"
        fileObject = open(filePath, 'r')

        fileObject.seek(2, 0)


        fileObject.close()



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
        tree = ET.parse(xmlFilePath)
        distance = float(list(tree.iter('gps_spacing'))[0].text)
        tolerance = float(list(tree.iter('horizontal'))[0].text)

        # might want to ensure that tolerance is non-zero. Should be done when input by user, but might want to double-check here
        dotProductTolerance = math.acos(math.pi - 2 * math.atan(float(distance) / float(tolerance)))

        return dotProductTolerance

    # returns a tuple of booleans (Bool_A, Bool_B), where Bool_A is True if multipathing is detected and false otherwise
    # and Bool_B is True if outlier-multipathing is detected (meaning VERY bad multipathing)
    @staticmethod
    def multipathDetect(coord1, coord2, coord3):
        tree = ET.parse(xmlFilePath)

        dotProductTolerance = MultipathDetector.computeDotProductTolerance()

        gpsDistance = float(list(tree.iter('gps_spacing'))[0].text)
        linearTolerance = float(list(tree.iter('horizontal'))[0].text)

        dist1_2 = MultipathDetector.computeDistance(coord1, coord2)
        dist2_3 = MultipathDetector.computeDistance(coord2, coord3)
        dist1_3 = MultipathDetector.computeDistance(coord1, coord3)
        dotProduct = MultipathDetector.computeDotProduct(coord1, coord2, coord3)

        outlierMultiplier = 3
        outlierFlag = False
        multipathFlag = False


        if dist1_2 < (gpsDistance - outlierMultiplier*linearTolerance):
            outlierFlag = True
        elif dist1_2 > (gpsDistance + outlierMultiplier*linearTolerance):
            outlierFlag = True
        elif dist2_3 < (gpsDistance - outlierMultiplier*linearTolerance):
            outlierFlag = True
        elif dist2_3 > (gpsDistance + outlierMultiplier*linearTolerance):
            outlierFlag = True
        elif dist1_3 < (2*gpsDistance) - outlierMultiplier*linearTolerance:
            outlierFlag = True
        elif dist1_3 > (2*gpsDistance) + outlierMultiplier*linearTolerance:
            outlierFlag = True


        # initially assume no multipathing
        if dist1_2 < (gpsDistance - linearTolerance):
            multipathFlag = True
        elif dist1_2 > (gpsDistance + linearTolerance):
            multipathFlag = True
        elif dist2_3 < (gpsDistance - linearTolerance):
            multipathFlag = True
        elif dist2_3 > (gpsDistance + linearTolerance):
            multipathFlag = True
        elif dist1_3 < (2*gpsDistance) - linearTolerance:
            multipathFlag = True
        elif dist1_3 > (2*gpsDistance) + linearTolerance:
            multipathFlag = True


        if dotProduct > (1 + outlierMultiplier*MultipathDetector.computeDotProductTolerance()):
            outlierFlag = True
        elif dotProduct < (1 - outlierMultiplier*MultipathDetector.computeDotProductTolerance()):
            outlierFlag = True

        # Note: this first case should NEVER occur - a dot product is bounded between [-1, 1] (inclusive)
        if dotProduct > (1 + MultipathDetector.computeDotProductTolerance()):
            multipathFlag = True
        elif dotProduct < (1 - MultipathDetector.computeDotProductTolerance()):
            multipathFlag = True

        return (multipathFlag, outlierFlag)

    # This will take a queue of sets of tuples, where each set of tuples is one tuple from each receiver
    # Then, we will compute 3 tuples that are the averaged x- and y-values of each tuple from a given receiver
    # Finally, we will use those 3 averaged tuples to call multipathDetect

    # The call to multipathQueueHandler must guarantee that the queues are fully populated
    # queue2 will be the center receiver
    @staticmethod
    def multipathQueueHandler(listOfQueues):
        if len(listOfQueues) != 3:
            print "ERROR: List of queues contains an incorrect number of queues (exactly 3 needed)"

        queue1 = listOfQueues[0]
        queue2 = listOfQueues[1]
        queue3 = listOfQueues[2]

        if len(queue1) != len(queue2) or len(queue1) != len(queue3) or len(queue2) != len(queue3):
            print "ERROR: Queues are not of equal length"

        if len(queue1) != 10:
            print "ERROR: Queues are not of length 10"

        xCoordAvg_1 = 0
        xCoordAvg_2 = 0
        xCoordAvg_3 = 0
        yCoordAvg_1 = 0
        yCoordAvg_2 = 0
        yCoordAvg_3 = 0


        multipathCounter = 0
        for i in range(len(queue1)):
            (multipathFlag, outlierFlag) = MultipathDetector.multipathDetect(queue1[i], queue2[i], queue3[i])
            if multipathFlag == True:
                multipathCounter = multipathCounter + 1
            if outlierFlag == True:
                finalOutlierFlag = True
            else:
                finalOutlierFlag = False
                
            xCoord1, yCoord1 = queue1[i]
            xCoord2, yCoord2 = queue2[i]
            xCoord3, yCoord3 = queue3[i]

            xCoordAvg_1 = xCoordAvg_1 + xCoord1
            xCoordAvg_2 = xCoordAvg_2 + xCoord2
            xCoordAvg_3 = xCoordAvg_3 + xCoord3

            yCoordAvg_1 = yCoordAvg_1 + yCoord1
            yCoordAvg_2 = yCoordAvg_2 + yCoord2
            yCoordAvg_3 = yCoordAvg_3 + yCoord3

        xCoordAvg_1 = xCoordAvg_1 / len(queue1)
        xCoordAvg_2 = xCoordAvg_2 / len(queue2)
        xCoordAvg_3 = xCoordAvg_3 / len(queue3)

        yCoordAvg_1 = yCoordAvg_1 / len(queue1)
        yCoordAvg_2 = yCoordAvg_2 / len(queue2)
        yCoordAvg_3 = yCoordAvg_3 / len(queue3)


        # prints the dot product tolerance, the average dot product of the queue, and the most recent data points' dot product
        # for testing purposes
        dotProductTolerance = MultipathDetector.computeDotProductTolerance()
        dotProductAvg = MultipathDetector.computeDotProduct((xCoordAvg_1, yCoordAvg_1), (xCoordAvg_2, yCoordAvg_2), (xCoordAvg_3, yCoordAvg_3))
        dotProductSingle = MultipathDetector.computeDotProduct(queue1[9], queue2[9], queue3[9])
        print "Tolerance =", dotProductTolerance, "\t Avg=", dotProductAvg, "\t Recent=", dotProductSingle


        avgMultipath = MultipathDetector.multipathDetect((xCoordAvg_1, yCoordAvg_1), (xCoordAvg_2, yCoordAvg_2), (xCoordAvg_3, yCoordAvg_3))

        if multipathCounter >= 3:
            return True
        elif finalOutlierFlag == True:
            return True
        else:
            return avgMultipath
