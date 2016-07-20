#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'hzsunshx'

import cv2

MIN_MATCH_COUNT = 2
DEBUG=True

def _middlePoint(pts):
    DEBUG=False
    def add(p1, p2):
        return (p1[0]+p2[0], p1[1]+p2[1])
    def distance(p1, p2):
        import math
        l2 = (p1[0]-p2[0])*(p1[0]-p2[0]) + (p1[1]-p2[1])*(p1[1]-p2[1])
        return math.sqrt(l2)
    # debug
    for p in pts:
        if DEBUG: print 'Point:', p.pt
    length = len(pts)
    sumx, sumy = reduce(add, [p.pt for p in pts])
    point = sumx/length, sumy/length
    if DEBUG: print 'step1: result=', point

    # filter out ok points
    avg_distance = sum([distance(point, p.pt) for p in pts])/length
    if DEBUG: print 'avg distance=', avg_distance
    good = []
    sumx, sumy = 0.0, 0.0
    for p in pts:
        if DEBUG: print 'point: %s, distance: %.2f' %(p.pt, distance(p.pt, point))
        if distance(p.pt, point) < 1.2*avg_distance:
            good.append(p.pt)
            sumx += p.pt[0]
            sumy += p.pt[1]
        else:
            if DEBUG: print 'not good', p.pt
    if DEBUG: print 'step1: result=', point
    point = map(long, (sumx/len(good), sumy/len(good)))
    if DEBUG: print 'step2: point=', point
    return point

def find_image_position(origin='origin.png', query='query.png', outfile=None):
    img1 = cv2.imread(query, 0) # query image(small)
    img2 = cv2.imread(origin, 0) # train image(big)
    points = locate_image(origin, query, outfile)
    return img2.shape, img1.shape, points

def locate_image(origin='orig.png', query='query.png', outfile=None, threshold=0.3):
    '''
    find all image positions
    @param threshold(float): [0, 1) the bigger the better
    @return points founded
    might raise Exception
    '''
    img1 = cv2.imread(query, 0) # query image(small)
    img2 = cv2.imread(origin, 0) # train image(big)

    # Initiate SIFT detector
    sift = cv2.SIFT()

    try:
        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(img1,None)
        kp2, des2 = sift.detectAndCompute(img2,None)
        if DEBUG: print len(kp1), len(kp2)
    except:
        return []

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)

    # flann
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)

    # store all the good matches as per Lowe's ratio test.
    good = []
    for m,n in matches:
        if m.distance < 0.8*n.distance:
            good.append(m)
    if DEBUG: print len(kp1), len(kp2), 'good cnt:', len(good)

    if len(good)*1.0/len(kp1) < threshold:
        if DEBUG: print "blew threshold: %.2f" %(threshold)
        return []

    #if len(good)*1.0/len(kp1) < 0.3 and 
    if len(good) < MIN_MATCH_COUNT:
        if DEBUG: print "Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT)
        return []

    queryPts = []
    trainPts = []
    for dm in good:
        queryPts.append(kp1[dm.queryIdx])
        trainPts.append(kp2[dm.trainIdx])

    img3 = cv2.drawKeypoints(img1, queryPts)
    cv2.imwrite('image/query.png', img3)

    img3 = cv2.drawKeypoints(img2, trainPts)
    point = _middlePoint(trainPts)
    if DEBUG: print 'position in', point

    if outfile:
        edge = 10
        top_left = (point[0]-edge, point[1]-edge)
        bottom_right = (point[0]+edge, point[1]+edge)
        cv2.rectangle(img3, top_left, bottom_right, 255, 2)
        cv2.imwrite(outfile, img3)
    return [point]

if __name__ == '__main__':
    pts = find_image_position('testdata/mule.png', 'testdata/football.png', 
        outfile='testdata/debug.png')
    print pts
