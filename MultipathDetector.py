import math
import xml.etree.ElementTree as ET
import logging 

log = logging.getLogger('log')

xmlFilePath = 'ui.xml'

class MultipathDetector():

    # This function contains a check for mislabeled GPS units - The center unit MUST be labeled #2
    # TODO: we could theoretically add functionality that re-assigns the units to their appropriate positions, but this is lower priority
    @staticmethod
    def checkForMislabeledGPSUnits(gpsDistance, linearTolerance, dist1_2, dist2_3, dist1_3):
        outOfOrderMult = 3
        # CASE 1: Center-unit (#2) is mislabeled as right-unit (#3)
        if (dist1_2 < (2*gpsDistance) + (outOfOrderMult*linearTolerance)) and (dist1_2 > (2*gpsDistance) - (outOfOrderMult*linearTolerance)):
            if (dist1_3 < gpsDistance + (outOfOrderMult*linearTolerance)) and (dist1_3 > gpsDistance - (outOfOrderMult*linearTolerance)):
                log.warn("GPS Units may be mislabeled!!! Make sure the center unit is labeled as #2!")
                return True

        # CASE 2: Center-unit (#2) is mislabeled as left-unit (#1)
        if (dist2_3 < (2*gpsDistance) + (outOfOrderMult*linearTolerance)) and (dist2_3 > (2*gpsDistance) - (outOfOrderMult*linearTolerance)):
            if (dist1_2 < gpsDistance + (outOfOrderMult*linearTolerance)) and (dist1_2 > gpsDistance - (outOfOrderMult*linearTolerance)):
                log.warn("GPS Units may be mislabeled!!! Make sure the center unit is labeled as #2!")
                return True

                
    @staticmethod
    def computeDistance(coord1, coord2):
        coord1_x, coord1_y = coord1
        coord2_x, coord2_y = coord2
        
        coord1_x = float(coord1_x)
        coord2_x = float(coord2_x)
        coord1_y = float(coord1_y)
        coord2_y = float(coord2_y)

        log.info('coord1_x:%s'%(coord1_x))
        log.info('coord2_x:%s'%(coord2_x))
        log.info('coord1_y:%s'%(coord1_y))
        log.info('coord2_y:%s'%(coord2_y))
           
        distance = math.sqrt(((coord1_x - coord2_x)**2)+((coord1_y - coord2_y)**2))

        if distance <= 0.0:
            print "distance between two coordinates is less than or equal to zero - something is wrong!  (MultipathDetector.distanceForumula)"
            log.info('distance between two coordinates is less than or equal to zero - something is wrong!  (MultipathDetector.distanceForumula)')
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
    # NOTE: coord2 needs to be the center receiver's coordinates
    def computeDotProduct(coord1, coord2, coord3):
        unitVector1_x, unitVector1_y = MultipathDetector.computeUnitVector(coord1, coord2)
        unitVector2_x, unitVector2_y = MultipathDetector.computeUnitVector(coord2, coord3)
        dotProduct = ((unitVector1_x*unitVector2_x) + (unitVector1_y*unitVector2_y))
        return dotProduct


    @staticmethod
    def computeDotProductTolerance(distance, tolerance):
        # Check for nonzero tolerance should be done when input by user, in addition to here
        if tolerance == 0:
            log.error("Tolerance value must be nonzero!")

        dotProductTolerance = math.acos(math.pi - 2 * math.atan(float(distance) / float(tolerance)))
        return dotProductTolerance


    @staticmethod
    def outlierCheck(outlierMultiplier, gpsDistance, linearTolerance, dist1_2, dist2_3, dist1_3):
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

    
    @staticmethod
    def linearToleranceCheck(gpsDistance, linearTolerance, dist1_2, dist2_3, dist1_3, verticalTolerance, multipathFlag):
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


    @staticmethod
    def dotProductCheck(dotProduct, dotProductTolerance, multipathFlag):
        log.info('Checking dot product')
        # Note: this first case should NEVER occur - a dot product is bounded between [-1, 1] (inclusive)

        if dotProduct > (1 + dotProductTolerance):
            log.info('dotProduct > (1 + dotProductTolerance)')
            multipathFlag = True
        elif dotProduct < (1 - dotProductTolerance):
            log.info('dotProduct < (1 - dotProductTolerance)')
            multipathFlag = True

        return multipathFlag


    @staticmethod
    def outlierDotProductCheck(dotProduct, dotProductTolerance, outlierMultiplier, outlierFlag):
        if dotProduct > (1 + outlierMultiplier*dotProductTolerance):
            log.info('dotProduct > (1 + outlierMultiplier*dotProductTolerance)')
            outlierFlag = True
        elif dotProduct < (1 - outlierMultiplier*dotProductTolerance):
            log.info('dotProduct < (1 - outlierMultiplier*dotProductTolerance)')
            outlierFlag = True

        return outlierFlag


    # returns a tuple of booleans (Bool_A, Bool_B), where Bool_A is True if multipathing is detected and false otherwise
    # and Bool_B is True if outlier-multipathing is detected (meaning VERY bad multipathing)
    @staticmethod
    def multipathDetect(coord1, coord2, coord3):
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
        
        if MultipathDetector.linearToleranceCheck(gpsDistance, linearTolerance, dist1_2, dist2_3, dist1_3, verticalTolerance, multipathFlag):
            multipathFlag = True
        if MultipathDetector.altitudeCheck(verticalTolerance, coord1[2], coord2[2], coord3[2]):
            multipathFlag = True
        if MultipathDetector.outlierCheck(outlierMultiplier, gpsDistance, linearTolerance, dist1_2, dist2_3, dist1_3):
            outlierFlag = True
            
        # NOTE: at this point in the code, the only way multipathing can occur is by failing the linearTolerance check
        # This means that the gps units could possibly be mislabeled as having the center receiver in the wrong position
        if multipathFlag is True:
            mislabledFlag = MultipathDetector.checkForMislabeledGPSUnits(gpsDistance, linearTolerance, dist1_2, dist2_3, dist1_3)

        if MultipathDetector.outlierDotProductCheck(dotProduct, dotProductTolerance, outlierMultiplier, outlierFlag):
            outlierFlag = True
        if MultipathDetector.dotProductCheck(dotProduct, dotProductTolerance, multipathFlag):
            multipathFlag = True

        return multipathFlag, outlierFlag


    @staticmethod
    def altitudeCheck(verticalTolerance, alt1, alt2, alt3):
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
    
  
    # This will take a queue of (usually 3) sets of tuples, where each set of tuples contains one location-tuple from each receiver
    # Then, we will compute 3 tuples that are the averaged x-, y-, and z-values of each tuple from a given receiver over a 10-epoch sample
    # Finally, we will use those 3 averaged tuples to call multipathDetect
    # The call to multipathQueueHandler must guarantee that the queues are fully populated
    # queue2 will be the center receiver - this is very important!
    @staticmethod
    def multipathQueueHandler(listOfQueues):
        tree = ET.parse(xmlFilePath)

        gpsDistance = float(list(tree.iter('gps_spacing'))[0].text)
        linearTolerance = float(list(tree.iter('horizontal'))[0].text)
        verticalTolerance = float(list(tree.iter('vertical'))[0].text)
        
        if len(listOfQueues) != 3:
            print "ERROR: List of queues contains an incorrect number of queues (exactly 3 needed)"
            log.info('ERROR: List of queues contains an incorrect number of queues (exactly 3 needed)')

        queue1 = listOfQueues[0]
        queue2 = listOfQueues[1]
        queue3 = listOfQueues[2]

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
        dotProductTolerance = MultipathDetector.computeDotProductTolerance(gpsDistance,linearTolerance)
        dotProductAvg = MultipathDetector.computeDotProduct((xCoordAvg_1, yCoordAvg_1), (xCoordAvg_2, yCoordAvg_2), (xCoordAvg_3, yCoordAvg_3))
        dotProductSingle = MultipathDetector.computeDotProduct(queue1[9][:-1], queue2[9][:-1], queue3[9][:-1])
        log.info('Tolerance =%s\t Avg=%s\t Recent=%s' % (dotProductTolerance, dotProductAvg, dotProductSingle))

        avgMultipath = MultipathDetector.multipathDetect((xCoordAvg_1, yCoordAvg_1, zCoordAvg_1), (xCoordAvg_2, yCoordAvg_2, zCoordAvg_2), (xCoordAvg_3, yCoordAvg_3, zCoordAvg_3))


        if multipathCounter >= 3:
            log.info('multipathCounter')
            return True
        elif finalOutlierFlag is True:
            log.info('finalOutlierFlag')
            return True
        else:
            return avgMultipath


