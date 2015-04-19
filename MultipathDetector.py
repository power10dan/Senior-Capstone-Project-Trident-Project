import math
import xml.etree.ElementTree as ET
import logging 

log = logging.getLogger('log')

xmlFilePath = 'ui.xml'

class MultipathDetector():

    # Global variable representing the ordering of the GPS units
    # 0 --> Ordering is good (it is acceptable for the left and right units to be mislabeled, so long as the center unit is labeled as such)
    # 1 --> Center unit (#2) is confused for the left unit (#1)
    # 2 --> Center unit (#2) is confused for right unit (#3)
    goodGPSOrdering_Flag = 0
    goodGPSOrdering_Counter1 = 0  # counts the number of times units #2 and #3 (center and right) are detected as swapped
    goodGPSOrdering_Counter2 = 0  # counts the number of times units #2 and #1 (center and left) are detected as swapped
    mislabeledFlag = 0  # indicates that the center unit has been (officially) confused with one of the other units


    # This function contains a check for mislabeled GPS units - The center unit MUST be labeled #2
    # TODO: we could theoretically add functionality that re-assigns the units to their appropriate positions, but this is lower priority
    @staticmethod
    def checkForMislabeledGPSUnits(gpsDistance, linearTolerance, dist1_2, dist2_3, dist1_3):
        try:
            outOfOrderMult = 3

            # CASE 1: Center-unit (#2) is mislabeled as right-unit (#3)
            if (dist1_2 < (2*gpsDistance) + (outOfOrderMult*linearTolerance)) and (dist1_2 > (2*gpsDistance) - (outOfOrderMult*linearTolerance)):
                if (dist1_3 < gpsDistance + (outOfOrderMult*linearTolerance)) and (dist1_3 > gpsDistance - (outOfOrderMult*linearTolerance)):
                    log.warn("GPS Units may be mislabeled!!! Make sure the center unit is labeled as #2!")
                    self.goodGPSOrdering_Flag = 2
                    self.goodGPSOrdering_Counter1 += 1
                    if self.goodGPSOrdering_Counter1 >= 10:
                        self.mislabeledFlag = 1  # 1 indicates center unit is mislabeled as right unit
                    return 2
            # CASE 2: Center-unit (#2) is mislabeled as left-unit (#1)
            elif (dist2_3 < (2*gpsDistance) + (outOfOrderMult*linearTolerance)) and (dist2_3 > (2*gpsDistance) - (outOfOrderMult*linearTolerance)):
                if (dist1_2 < gpsDistance + (outOfOrderMult*linearTolerance)) and (dist1_2 > gpsDistance - (outOfOrderMult*linearTolerance)):
                    log.warn("GPS Units may be mislabeled!!! Make sure the center unit is labeled as #2!")
                    self.goodGPSOrdering_Flag = 1
                    self.goodGPSOrdering_Counter2 += 1
                    if self.goodGPSOrdering_Counter2 >= 10:
                        self.mislabeledFlag = 2  # 2 indicates center unit is mislabeled as left unit
                    return 1
            else:
                return 0
        except:
            log.error("Error in MultipathDetector.checkForMislabeledGPSUnits")


    @staticmethod
    def computeDistance(coord1, coord2):
        try:
            coord1_x, coord1_y = coord1
            coord2_x, coord2_y = coord2

            coord1_x = float(coord1_x)
            coord2_x = float(coord2_x)
            coord1_y = float(coord1_y)
            coord2_y = float(coord2_y)

            log.info('coord1_x:%s' % (coord1_x))
            log.info('coord2_x:%s' % (coord2_x))
            log.info('coord1_y:%s' % (coord1_y))
            log.info('coord2_y:%s' % (coord2_y))

            distance = math.sqrt(((coord1_x - coord2_x)**2)+((coord1_y - coord2_y)**2))

            if distance <= 0.0:
                print "distance between two coordinates is less than or equal to zero - something is wrong!  (MultipathDetector.distanceForumula)"
                log.info('distance between two coordinates is less than or equal to zero - something is wrong!  (MultipathDetector.distanceForumula)')
                return None
            else:
                return distance
        except:
            log.error("Error in MultipathDetector.computeDistance")


    @staticmethod
    def computeUnitVector(coord1, coord2):
        try:
            coord1_x, coord1_y = coord1
            coord2_x, coord2_y = coord2

            distance1_2 = MultipathDetector.computeDistance(coord1, coord2)
            # Note: distanceFormula ensures that no distances <= 0 are returned, thus division here should be safe
            unitVector1_x, unitVector1_y = ((coord1_x - coord2_x) / distance1_2), ((coord1_y - coord2_y) / distance1_2)

            return (unitVector1_x, unitVector1_y)
        except:
            log.error("Error in MultipathDetector.computeUnitVector")


    @staticmethod
    # NOTE: coord2 needs to be the center receiver's coordinates
    def computeDotProduct(coord1, coord2, coord3):
        try:
            unitVector1_x, unitVector1_y = MultipathDetector.computeUnitVector(coord1, coord2)
            unitVector2_x, unitVector2_y = MultipathDetector.computeUnitVector(coord2, coord3)
            dotProduct = ((unitVector1_x*unitVector2_x) + (unitVector1_y*unitVector2_y))
            return dotProduct
        except:
            log.error("Error in MultipathDetector.computeDotProduct")


    @staticmethod
    def computeDotProductTolerance(distance, tolerance):
        # Check for nonzero tolerance should be done when input by user, in addition to here
        try:
            if tolerance == 0:
                log.error("Tolerance value must be nonzero!")

            dotProductTolerance = math.acos(math.pi - 2 * math.atan(float(distance) / float(tolerance)))
            return dotProductTolerance
        except:
            log.error("Error in computeDotProductTolerance")


    @staticmethod
    def outlierCheck(outlierMultiplier, gpsDistance, linearTolerance, dist1_2, dist2_3, dist1_3):
        try:
            log.info('Checking outlier')
            outlierFlag = False

            if dist1_2 < (gpsDistance - outlierMultiplier*linearTolerance):
                log.info('dist1_2 < (gpsDistance - outlierMultiplier*linearTolerance)')
                outlierFlag = True
            elif dist1_2 > (gpsDistance + outlierMultiplier*linearTolerance):
                log.info('dist1_2 > (gpsDistance + outlierMultiplier*linearTolerance)')
                outlierFlag = True
            elif dist2_3 < (gpsDistance - outlierMultiplier*linearTolerance):
                log.info('dist2_3 < (gpsDistance - outlierMultiplier*linearTolerance)')
                outlierFlag = True
            elif dist2_3 > (gpsDistance + outlierMultiplier*linearTolerance):
                log.info('dist2_3 > (gpsDistance + outlierMultiplier*linearTolerance)')
                outlierFlag = True
            elif dist1_3 < (2*gpsDistance) - outlierMultiplier*linearTolerance:
                log.info('dist1_3 < (2*gpsDistance) - outlierMultiplier*linearTolerance')
                outlierFlag = True
            elif dist1_3 > (2*gpsDistance) + outlierMultiplier*linearTolerance:
                log.info('dist1_3 < (2*gpsDistance) - outlierMultiplier*linearTolerance')
                outlierFlag = True

            return outlierFlag
        except:
            log.error("Error in MultipathDetector.outlierCheck")


    @staticmethod
    def linearToleranceCheck(gpsDistance, linearTolerance, dist1_2, dist2_3, dist1_3, multipathFlag):
        try:
            log.info('Checking linear tolerance')

            if dist1_2 < (gpsDistance - linearTolerance):
                log.info('dist1_2 < (gpsDistance - linearTolerance)')
                multipathFlag = True
            elif dist1_2 > (gpsDistance + linearTolerance):
                log.info('dist1_2 > (gpsDistance + linearTolerance)')
                multipathFlag = True
            elif dist2_3 < (gpsDistance - linearTolerance):
                log.info('dist2_3 < (gpsDistance - linearTolerance)')
                multipathFlag = True
            elif dist2_3 > (gpsDistance + linearTolerance):
                log.info('dist2_3 > (gpsDistance + linearTolerance)')
                multipathFlag = True
            elif dist1_3 < (2*gpsDistance) - linearTolerance:
                log.info('dist1_3 < (2*gpsDistance) - linearTolerance')
                multipathFlag = True
            elif dist1_3 > (2*gpsDistance) + linearTolerance:
                log.info('dist1_3 > (2*gpsDistance) + linearTolerance')
                multipathFlag = True

            return multipathFlag
        except:
            log.error("Error in MultipathDetector.linearToleranceCheck")


    @staticmethod
    def dotProductCheck(dotProduct, dotProductTolerance, multipathFlag):
        try:
            log.info('Checking dot product')
            # Note: this first case should NEVER occur - a dot product is bounded between [-1, 1] (inclusive)

            if dotProduct > (1 + dotProductTolerance):
                log.info('dotProduct > (1 + dotProductTolerance)')
                multipathFlag = True
            elif dotProduct < (1 - dotProductTolerance):
                log.info('dotProduct < (1 - dotProductTolerance)')
                multipathFlag = True

            return multipathFlag
        except:
            log.error("Error in MultipathDetector.dotProductCheck")


    @staticmethod
    def outlierDotProductCheck(dotProduct, dotProductTolerance, outlierMultiplier, outlierFlag):
        try:
            if dotProduct > (1 + outlierMultiplier*dotProductTolerance):
                log.info('dotProduct > (1 + outlierMultiplier*dotProductTolerance)')
                outlierFlag = True
            elif dotProduct < (1 - outlierMultiplier*dotProductTolerance):
                log.info('dotProduct < (1 - outlierMultiplier*dotProductTolerance)')
                outlierFlag = True

            return outlierFlag
        except:
            log.error("Error in MultipathDetector.outlierDotProductCheck")


    # returns a tuple of booleans (Bool_A, Bool_B), where Bool_A is True if multipathing is detected and false otherwise
    # and Bool_B is True if outlier-multipathing is detected (meaning VERY bad multipathing)
    @staticmethod
    def multipathDetect(coord1, coord2, coord3):
        try:
            tree = ET.parse(xmlFilePath)

            gpsDistance = float(list(tree.iter('gps_spacing'))[0].text)
            linearTolerance = float(list(tree.iter('horizontal'))[0].text)
            verticalTolerance = float(list(tree.iter('vertical'))[0].text)

            dotProductTolerance = MultipathDetector.computeDotProductTolerance(gpsDistance, linearTolerance)

            log.info('MultipathDetect Algorithm:')
            log.info('Compute Distance:')
            log.info('GPS 1 and 2')
            dist1_2 = MultipathDetector.computeDistance(coord1[:-1], coord2[:-1])
            log.info('GPS 2 and 3')
            dist2_3 = MultipathDetector.computeDistance(coord2[:-1], coord3[:-1])
            log.info('GPS 1 and 3')
            dist1_3 = MultipathDetector.computeDistance(coord1[:-1], coord3[:-1])
            dotProduct = MultipathDetector.computeDotProduct(coord1[:-1], coord2[:-1], coord3[:-1])

            log.info('GPS Spacing: %s' % gpsDistance)
            log.info('Horizontal Tolerance: %s' % linearTolerance)
            log.info('Vertical Tolerance: %s' % verticalTolerance)
            log.info('Distance 1 and 2: %s' % dist1_2)
            log.info('Distance 2 and 3: %s' % dist2_3)
            log.info('Distance 1 and 3: %s' % dist1_3)
            log.info('Dot product: %s' % dotProduct)
            log.info('Dot product tolerance: %s' % dotProductTolerance)

            outlierMultiplier = 3
            multipathFlag = False
            outlierFlag = False

            if MultipathDetector.linearToleranceCheck(gpsDistance, linearTolerance, dist1_2, dist2_3, dist1_3, multipathFlag):
                multipathFlag = True
            if MultipathDetector.altitudeCheck(verticalTolerance, coord1[2], coord2[2], coord3[2]):
                multipathFlag = True
            if MultipathDetector.outlierCheck(outlierMultiplier, gpsDistance, linearTolerance, dist1_2, dist2_3, dist1_3):
                outlierFlag = True

            # NOTE: at this point in the code, the only way multipathing can occur is by failing the linearTolerance check
            # This means that the gps units could possibly be mislabeled as having the center receiver in the wrong position
            if multipathFlag is True:
                # global mislabledFlag
                self.mislabledFlag = MultipathDetector.checkForMislabeledGPSUnits(gpsDistance, linearTolerance, dist1_2, dist2_3, dist1_3)

            if MultipathDetector.outlierDotProductCheck(dotProduct, dotProductTolerance, outlierMultiplier, outlierFlag):
                outlierFlag = True
            if MultipathDetector.dotProductCheck(dotProduct, dotProductTolerance, multipathFlag):
                multipathFlag = True

            return multipathFlag, outlierFlag
        except:
            log.error("Error in MultipathDetector.multipathDetect")


    @staticmethod
    def altitudeCheck(verticalTolerance, alt1, alt2, alt3):
        try:
            log.info('Altitude Check Debugging Mode')
            altMultipath = False
            alt1 = float(alt1)
            alt2 = float(alt2)
            alt3 = float(alt3)
            if abs(alt1 - alt2) > verticalTolerance:
                log.info('abs(alt1 - alt2) > verticalTolerance')
                altMultipath = True
            elif abs(alt2 - alt3) > verticalTolerance:
                log.info('abs(alt2 - alt3) > verticalTolerance')
                altMultipath = True
            elif abs(alt1 - alt3) > verticalTolerance:
                log.info('abs(alt1 - alt3) > verticalTolerance')
                altMultipath = True
            return altMultipath
        except:
            log.error("Error in MultipathDetector.altitudeCheck")


    # This will take a queue of (usually 3) sets of tuples, where each set of tuples contains one location-tuple from each receiver
    # Then, we will compute 3 tuples that are the averaged x-, y-, and z-values of each tuple from a given receiver over a 10-epoch sample
    # Finally, we will use those 3 averaged tuples to call multipathDetect
    # The call to multipathQueueHandler must guarantee that the queues are fully populated
    # queue2 will be the center receiver - this is very important!
    @staticmethod
    def multipathQueueHandler(listOfQueues):
        try:
            if self.mislabeledFlag != 0:
                return self.mislabeledFlag

            tree = ET.parse(xmlFilePath)

            gpsDistance = float(list(tree.iter('gps_spacing'))[0].text)
            linearTolerance = float(list(tree.iter('horizontal'))[0].text)

            if len(listOfQueues) != 3:
                print "ERROR: List of queues contains an incorrect number of queues (exactly 3 needed)"
                log.info('ERROR: List of queues contains an incorrect number of queues (exactly 3 needed)')


            # # This else-if block reorders the input queues if they were detected as being incorrectly labeled
            # global goodGPSOrdering_Flag
            # if goodGPSOrdering_Flag == 0:
            #     queue1 = listOfQueues[0]
            #     queue2 = listOfQueues[1]
            #     queue3 = listOfQueues[2]
            # elif goodGPSOrdering_Flag == 1:
            #     log.info("Left and Center units detected as swapped - switching them to correct order!")
            #     queue1 = listOfQueues[2]
            #     queue2 = listOfQueues[1]
            #     queue3 = listOfQueues[3]
            # elif goodGPSOrdering_Flag == 2:
            #     log.info("Right and Center units detected as swapped - switching them to correct order!")
            #     queue1 = listOfQueues[1]
            #     queue2 = listOfQueues[3]
            #     queue3 = listOfQueues[2]
            # else:
            #     log.error("goodGPSOrdering_Flag is not an expected value (1, 2, or 3)")
            #     print "goodGPSOrdering_Flag is not an expected value (1, 2, or 3)"
            #     queue1 = None
            #     queue2 = None
            #     queue3 = None
            #     assert(goodGPSOrdering_Flag >= 0)
            #     assert(goodGPSOrdering_Flag <= 3)

            if len(queue1) != len(queue2) or len(queue1) != len(queue3) or len(queue2) != len(queue3):
                print "ERROR: Queues are not of equal length"
                log.info('ERROR: Queues are not of equal length')
                assert(len(queue1) == len(queue2))
                assert(len(queue2) == len(queue3))

            if len(queue1) != 10:
                print "ERROR: Queues are not of length 10"
                log.info('ERROR: Queues are not of length 10')
                assert(len(queue1) == 10)

            xCoordAvg_1 = 0
            xCoordAvg_2 = 0
            xCoordAvg_3 = 0
            yCoordAvg_1 = 0
            yCoordAvg_2 = 0
            yCoordAvg_3 = 0
            zCoordAvg_1 = 0
            zCoordAvg_2 = 0
            zCoordAvg_3 = 0

            multipathCounter = 0
            finalOutlierFlag = False

            # determines multipathing for each element of the queues
            for i in range(len(queue1)):
                (multipathFlag, outlierFlag) = MultipathDetector.multipathDetect(queue1[i], queue2[i], queue3[i])
                if multipathFlag is True:
                    multipathCounter += 1
                if outlierFlag is True:
                    finalOutlierFlag = True
                else:
                    finalOutlierFlag = False

                xCoord1, yCoord1, zCoord1 = queue1[i]
                xCoord2, yCoord2, zCoord2 = queue2[i]
                xCoord3, yCoord3, zCoord3 = queue3[i]

                xCoordAvg_1 = xCoordAvg_1 + float(xCoord1)
                xCoordAvg_2 = xCoordAvg_2 + float(xCoord2)
                xCoordAvg_3 = xCoordAvg_3 + float(xCoord3)

                yCoordAvg_1 = yCoordAvg_1 + float(yCoord1)
                yCoordAvg_2 = yCoordAvg_2 + float(yCoord2)
                yCoordAvg_3 = yCoordAvg_3 + float(yCoord3)

                zCoordAvg_1 = zCoordAvg_1 + float(zCoord1)
                zCoordAvg_2 = zCoordAvg_2 + float(zCoord2)
                zCoordAvg_3 = zCoordAvg_3 + float(zCoord3)

            xCoordAvg_1 = xCoordAvg_1 / len(queue1)
            xCoordAvg_2 = xCoordAvg_2 / len(queue2)
            xCoordAvg_3 = xCoordAvg_3 / len(queue3)

            yCoordAvg_1 = yCoordAvg_1 / len(queue1)
            yCoordAvg_2 = yCoordAvg_2 / len(queue2)
            yCoordAvg_3 = yCoordAvg_3 / len(queue3)

            zCoordAvg_1 = zCoordAvg_1 / len(queue1)
            zCoordAvg_2 = zCoordAvg_2 / len(queue2)
            zCoordAvg_3 = zCoordAvg_3 / len(queue3)

            # prints the dot product tolerance, the average dot product of the queue, and the most recent data points' dot product
            # for testing purposes
            dotProductTolerance = MultipathDetector.computeDotProductTolerance(gpsDistance, linearTolerance)
            dotProductAvg = MultipathDetector.computeDotProduct((xCoordAvg_1, yCoordAvg_1), (xCoordAvg_2, yCoordAvg_2), (xCoordAvg_3, yCoordAvg_3))
            dotProductSingle = MultipathDetector.computeDotProduct(queue1[9][:-1], queue2[9][:-1], queue3[9][:-1])
            log.info('Tolerance =%s\t Avg=%s\t Recent=%s' % (dotProductTolerance, dotProductAvg, dotProductSingle))

            # computes multipathing for the averaged values in the queues
            avgMultipath = MultipathDetector.multipathDetect((xCoordAvg_1, yCoordAvg_1, zCoordAvg_1), (xCoordAvg_2, yCoordAvg_2, zCoordAvg_2), (xCoordAvg_3, yCoordAvg_3, zCoordAvg_3))

            if multipathCounter >= 3:
                # more than 3 elements of the queue contain multipathing 
                log.info('multipathCounter')
                return True
            elif finalOutlierFlag is True:
                log.info('finalOutlierFlag')
                return True
            else:
                return avgMultipath
        except:
            log.error("Error in MultipathDetector.multipathQueueHandler")

