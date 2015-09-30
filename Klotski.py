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
#import random
import Queue
import copy

steps = Queue.Queue()


class Shape(object):
    """docstring for Shape"""
    bottomOffset = [0,0,1,1]
    rightOffset = [0,1,0,1]
    # 1:Dot, 2:Hbar, 3:Vbar, 4:Square
    types = [1,2,3,4]
    def __init__(self, type=1, top=1, left=1):
        if type in self.types:
            self.type = type
            self.top  = top
            self.left = left
        else:
            print "wrong type of shapes"
            sys.exit()

    def bottom(self):
        return self.top+ Shape.bottomOffset[self.type-1]

    def right(self):
        return self.left+ Shape.rightOffset[self.type-1]
        
class State(object):
    row = 5
    col = 4
    size = 20
    seenMask = Set()
    squareindex = -1
    def __init__(self,mask,depth=0):
        if len(mask) == State.size and all((mask[x] in 'VvSsHhDd0') for x in range(20)) and self.parsemask(mask):
            self.depth = depth
            #self.parent = None
            #print len(self.elements)
        else:
            print "wrong size of initial game"
            sys.exit()
    
    ##
    # @brief Construct the current state using mask
    #
    # @param mask
    #
    # @return True if success, false if failed
    def parsemask(self,mask):
        self.elements = list()
        status = [0]*State.size
        for i in range(State.size):
            if status[i] == 0 and mask[i] != '0':
                status[i] = 1
                if mask[i] in 'Dd':
                    self.elements.append(Shape(1,i/4,i%4))
                    
                elif mask[i] in 'Hh' and mask[i+1] in 'Hh':
                    self.elements.append(Shape(2,i/4,i%4))
                    status[i+1] = 1

                elif mask[i] in 'Vv' and mask[i+4] in 'Vv':
                    self.elements.append(Shape(3,i/4,i%4))
                    status[i+4] = 1

                elif mask[i] in 'Ss' and all([mask[j] in 'Ss' for j in [i+1,i+4,i+5]]):
                    self.elements.append(Shape(4,i/4,i%4))
                    State.squareIndex = len(self.elements)-1
                    status[i+1] = 1
                    status[i+4] = 1
                    status[i+5] = 1
                else:
                    return False
        return True

    def setvalue(self,mask,value,x,y):
        mask[x*self.col+y] = value

    def empty(self,mask,x,y):
        if x<0 or x>State.row-1 or y<0 or y>State.col-1:
            return False
        else:
            return mask[x*self.col+y] == '0'

    ##
    # @brief Get the mask of the current state
    #
    # @return mask if legal, False illegal
    def toMask(self):
        mask = ['0' for k in range(20)]
        for i in range(len(self.elements)):
            obj = self.elements[i]
            x = obj.top
            y = obj.left
            if obj.type == 1:
                self.setvalue(mask,'D',x,y)
            elif obj.type == 2:
                self.setvalue(mask,'H',x,y)
                self.setvalue(mask,'H',x,y+1)
            elif obj.type == 3:
                self.setvalue(mask,'V',x,y)
                self.setvalue(mask,'V',x+1,y)
            else:
                self.setvalue(mask,'S',x,y)
                self.setvalue(mask,'S',x,y+1)
                self.setvalue(mask,'S',x+1,y)
                self.setvalue(mask,'S',x+1,y+1)
        return ''.join(mask)

    ##
    # @brief get all of the next legal moves
    #
    # @return the a queue that contains all the next possible moves
    def nextMoves(self):
        mask = self.toMask()
        moves = list()
        for i in range(len(self.elements)):
            obj = self.elements[i]

            #try to move up
            if obj.top > 0 and self.empty(mask,obj.top-1,obj.left) and self.empty(mask,obj.top-1,obj.right()):
                next = copy.deepcopy(self)
                next.elements[i].top -= 1
                next.depth += 1
                _mask = next.toMask()
                if _mask not in State.seenMask:
                    State.seenMask.add(_mask)
                    #next.parent = self
                    moves.append(next)
            #try to move down 
            if obj.bottom() <State.row-1 and self.empty(mask,obj.bottom()+1,obj.left) and self.empty(mask,obj.bottom()+1,obj.right()):
                next = copy.deepcopy(self)
                next.elements[i].top += 1
                next.depth += 1
                _mask = next.toMask()
                if _mask not in State.seenMask:
                    State.seenMask.add(_mask)
                    #next.parent = self
                    moves.append(next)
            #try to move left 
            if obj.left >0 and self.empty(mask,obj.top,obj.left-1) and self.empty(mask,obj.bottom(),obj.left-1):
                next = copy.deepcopy(self)
                next.elements[i].left -= 1
                next.depth += 1
                _mask = next.toMask()
                if _mask not in State.seenMask:
                    State.seenMask.add(_mask)
                    #next.parent = self
                    moves.append(next)
            #try to move right 
            if obj.right() <State.col-1 and self.empty(mask,obj.top,obj.right()+1) and self.empty(mask,obj.bottom(),obj.right()+1):
                next = copy.deepcopy(self)
                next.elements[i].left += 1
                next.depth += 1
                _mask = next.toMask()
                if _mask not in State.seenMask:
                    State.seenMask.add(_mask)
                    #next.parent = self
                    moves.append(next)
        return moves

    def isSolved(self):
        obj = self.elements[State.squareIndex]
        if obj.top == 3 and obj.left == 1:
            return True
        else:
            return False

    def __str__(self):
        _str = list(self.toMask())
        for i in range(State.row):
            _str.insert(i*State.row,'\n')
        _str.append('\n')
        return ''.join(_str)
        
    def __hash__(self):
        return hash(self.toMask())
    
    def __eq__(self,other):
        return isinstance(other, self.__class__) and self.toMask() == other.toMask()

def solve(game):
    steps.put(game)
    State.seenMask.add(game.toMask())
    solution = Queue.LifoQueue()
    while steps.empty() == False:
        currentstep = steps.get()
        print currentstep.depth
        if currentstep.isSolved():
            print "optimal steps:%d" %currentstep.depth
##            while currentstep!= None:
##                solution.put(currentstep)
##                currentstep=currentstep.parent
##            solution.put(currentstep)
        else:
            moves = currentstep.nextMoves()
            #print len(moves)
            for i in range(len(moves)):
                steps.put(moves[i])
            #pdb.set_trace()
    print "Can not find solution"
    return solution

if __name__ == "__main__":
    str = 'VssVVSSVVHHVVDDVD00D'
    #str = 'VSSDVSSDVVVDVVVD0HH0'
    #str = '0ss0dssdhhddddhhddhh'
    #str = 'ssvvssvvvdd0vdd0hhhh'
    #str = '00sshhsshhhhhhhhdddd'
    #vimpdb.set_trace()
    game = State(str,0)
    solution = solve(game)
##    while not solution.empty():
##        cmd = input("print n to continue")
##        if cmd == 'n':
##            print solution.get()
    #print game
    #print game.toMask()
        
