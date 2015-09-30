# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 16:33:31 2015

@author: slong
"""
import sys
#import pdb
#import vimpdb
from sets import Set
#import numpy as np
import random
import Queue
import copy

steps = Queue.Queue()


class Dot(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y
    def moveUp(self):
        self.x = self.x-1
    def moveDown(self):
        self.x = self.x+1
    def moveRight(self):
        self.y = self.y+1
    def moveLeft(self):
        self.y = self.y-1
    def getDots(self):
        tmp = list()
        tmp.append(self)
        return tmp

class Hbar(object):
    def __init__(self,dot1,dot2):
        self.elements = list()
        if isinstance(dot1,Dot) and isinstance(dot2,Dot) and abs(dot1.y-dot2.y) == 1 and dot1.x == dot2.x:
            self.elements.append(dot1)
            self.elements.append(dot2)
        else:
            print "Wrong Hbar initilize"
            sys.exit()
          
    def moveDown(self):
        for dot in self.elements:
            dot.moveDown()
  
    def moveUp(self):
        for dot in self.elements:
            dot.moveUp()
      
    def moveRight(self):
        for dot in self.elements:
            dot.moveRight()
    
    def moveLeft(self):
        for dot in self.elements:
            dot.moveLeft()
    
    def getDots(self):
        return self.elements

class Vbar(object):
    def __init__(self,dot1,dot2):
        self.elements = list()
        if isinstance(dot1,Dot) and isinstance(dot2,Dot) and abs(dot1.x-dot2.x) == 1 and dot1.y == dot2.y:
            self.elements.append(dot1)
            self.elements.append(dot2)
        else:
            print "Wrong Vbar initilize"
            sys.exit()
        
    def moveDown(self):
        for dot in self.elements:
            dot.moveDown()
    
    def moveUp(self):
        for dot in self.elements:
            dot.moveUp()
        
    def moveRight(self):
        for dot in self.elements:
            dot.moveRight()
        
    def moveLeft(self):
        for dot in self.elements:
            dot.moveLeft()
    
    def getDots(self):
        return self.elements

class Square(object):
    def __init__(self,vbar1,vbar2):
        self.elements = list()
        if isinstance(vbar1,Vbar) and isinstance(vbar2,Vbar) and abs(vbar1.elements[0].y-vbar2.elements[0].y) == 1:
            self.elements.append(vbar1)
            self.elements.append(vbar2)
            
    def moveDown(self):
        for vbar in self.elements:
            vbar.moveDown()
    
    def moveUp(self):
        for vbar in self.elements:
            vbar.moveUp()
        
    def moveRight(self):
        for vbar in self.elements:
            vbar.moveRight()
        
    def moveLeft(self):
        for vbar in self.elements:
            vbar.moveLeft()
    
    def getDots(self):
        return self.elements[0].elements + self.elements[1].elements

class Gamestate(object):
    seenMask = Set()
    def __init__(self,mask,depth):
        if len(mask) == 20 and all((mask[x] in 'VvSsHhDd0') for x in range(20)):
            if self.parsemask(mask) == False:
                print "Wrong initial game"
                sys.exit()
            else:
                self.mask = mask
                self.depth = depth
                print len(self.elements)
        else:
            print "wrong size of initial game"
            sys.exit()
    
    ##
    # @brief Get the mask of the current state
    #
    # @return mask if legal, False illegal

    def toMask(self):
        mask = ['0' for k in range(20)]
        for i in range(len(self.elements)):
            obj = self.elements[i]
            listdots = obj.getDots()
            for j in range(len(listdots)):
                x = listdots[j].x
                y = listdots[j].y
                if mask[x*4+y] != '0':
                    return False
                elif isinstance(obj, Dot):
                    mask[x*4+y] = 'D'
                elif isinstance(obj,Vbar):
                    mask[x*4+y] = 'V'
                elif isinstance(obj,Hbar):
                    mask[x*4+y] = 'H'
                else:
                    mask[x*4+y] = 'S'
        return ''.join(mask)
    
    ##
    # @brief Construct the current state using mask
    #
    # @param mask
    #
    # @return True if success, false if failed
    def parsemask(self,mask):
        self.elements = list()
        status = [0]*20
        for i in range(20):
            if status[i] == 0 and mask[i] != '0':
                status[i] = 1
                if mask[i] in 'Dd':
                    self.elements.append(Dot(i/4,i%4))
                    
                elif mask[i] in 'Vv' and mask[i+4] in 'Vv':
                    self.elements.append(Vbar(Dot(i/4,i%4),Dot(i/4+1,i%4)))
                    status[i+4] = 1
                        
                elif mask[i] in 'Hh' and mask[i+1] in 'Hh':
                    self.elements.append(Hbar(Dot(i/4,i%4),Dot(i/4,i%4+1)))
                    status[i+1] = 1
                    
                elif mask[i] in 'Ss' and all([mask[j] in 'Ss' for j in [i+1,i+4,i+5]]):
                    self.elements.append(Square(Vbar(Dot(i/4,i%4),Dot(i/4+1,i%4)),Vbar(Dot((i+1)/4,(i+1)%4),Dot((i+1)/4+1,(i+1)%4))))
                    status[i+1] = 1
                    status[i+4] = 1
                    status[i+5] = 1
                else:
                    return False
        return True
    

    ##
    # @brief locate the index of element in current elements list that on (x,y)
    #
    # @param x
    # @param y
    #
    # @return index of element if found, else -1 
    def locateElement(self,x,y):
        # check boundary
        if x<0 or x>5 or y<0 or y>4:
            return -1
        for i in range(len(self.elements)):
            obj  = self.elements[i]
            listdots = obj.getDots()
            for  j in range(len(listdots)):
                obj2 = listdots[j]
                if obj2.x == x and obj2.y == y:
                    return i
        return -1


    ##
    # @brief get all of the next legal moves
    #
    # @return the a queue that contains all the next possible moves
    def nextMoves(self):
        emptyspaces = [(i,j) for j in range(4) for i in range(5) if self.mask[i*4+j] == '0']
        #pdb.set_trace()
        searchdir = [1,2,3,4]
        moves = list()
        for i in range(len(emptyspaces)):
            emptyx = emptyspaces[i][0]
            emptyy = emptyspaces[i][1]
            
            #do a random permutation to the searchdir to increase the speed
            randi = random.randint(0,3)
            randj = random.randint(0,3)
            tmp = searchdir[i]
            searchdir[randi] = searchdir[randj]
            searchdir[randj] = tmp
            
            for j in range(len(searchdir)):
                dir = searchdir[j]
                next = copy.deepcopy(self)
                if dir == 1:
                    # look for the element on top of the empty spaces
                    indice = self.locateElement(emptyx-1,emptyy)
                    #obj = self.elements[indice]
                    if indice != -1:
                        next.elements[indice].moveDown()
                        next.mask = next.toMask()
                        next.depth = self.depth + 1
                        if (next.mask != False) and (next.mask not in Gamestate.seenMask):
                            moves.append(next)
                            Gamestate.seenMask.add(next.mask)

                elif dir == 2:
                    # look for the element below the empty spaces
                    indice = self.locateElement(emptyx+1,emptyy)
                    #obj = self.elements[indice]
                    if indice != -1:
                        next.elements[indice].moveUp()
                        next.mask = next.toMask()
                        next.depth = self.depth + 1
                        if (next.mask != False) and (next.mask not in Gamestate.seenMask):
                            moves.append(next)
                            Gamestate.seenMask.add(next.mask)

                elif dir == 3:
                    # look for the element on the left of the empty spaces
                    indice = self.locateElement(emptyx,emptyy-1)
                    #obj = self.elements[indice]
                    if indice != -1:
                        next.elements[indice].moveRight()
                        next.mask = next.toMask()
                        next.depth = self.depth + 1
                        if (next.mask != False) and (next.mask not in Gamestate.seenMask):
                            moves.append(next)
                            Gamestate.seenMask.add(next.mask)
                else:
                    # look for the element on the right of the empty spaces
                    indice = self.locateElement(emptyx,emptyy+1)
                    #obj = self.elements[indice]
                    if indice != -1:
                        next.elements[indice].moveLeft()
                        next.mask = next.toMask()
                        next.depth = self.depth + 1
                        if (next.mask != False) and (next.mask not in Gamestate.seenMask):
                            moves.append(next)
                            Gamestate.seenMask.add(next.mask)

        return moves

    def isSolved(self):
        indice = [13,14,17,18]
        return all([self.mask[i] in 'Ss' for i in indice])
        
    def __hash__(self):
        return hash(''.join(self.mask))
    
    def __eq__(self,other):
        return isinstance(other, self.__class__) and self.mask == other.mask


def solve(game):
    steps.put(game)
    Gamestate.seenMask.add(game.toMask())
    while steps.empty() == False:
        currentstep = steps.get()
        if currentstep.isSolved():
            print "optimal steps:%d" %currentstep.depth
            return True
        else:
            moves = currentstep.nextMoves()
            for i in range(len(moves)):
                steps.put(moves[i])
            #pdb.set_trace()
    return False

if __name__ == "__main__":
    #str = 'VssVVSSVVHHVVDDVD00D'
    #str = 'VSSDVSSDVVVDVVVD0HH0'
    #str = '0ss0dssdhhddddhhddhh'
    str = 'ssvvssvvvdd0vdd0hhhh'
    #d = Dot(3,5)
    #vimpdb.set_trace()
    game = Gamestate(str,0)
    #print game.toMask()
    res = solve(game)

    #print steps.qsize()
    print res
    #c = list()
    #c.append(Dot(3,4))
    #c.append(Dot(2,5))
    #c.append(Vbar(Dot(2,3),Dot(3,3)))
    #d=copy.deepcopy(c)
    #d[0].x = 5
    #print c[0].x
