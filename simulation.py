import os
import sys
import time
import math
import numpy as np
import random
import pygame
from pygame.gfxdraw import pixel
from pygame.locals import *

from utils import grid

BaseGrid = grid.BaseGrid
OptmizedBaseGrid = grid.OptmizedBaseGrid
depth = 32
pattern_path = '/Users/stephanie/PycharmProjects/GameOfLife/utils/patterns/glider.life'


class GameCell:

    def __init__(self,width,height):
        self.size = (width,height)

    @property
    def deadCellColor(self):
        try:
            return self._deadCellColor
        except AttributeError as e:
            pass

        self._deadCellColor = (0,0,0)
        return self._deadCellColor

    @property
    def size(self):
        try:
            return self._size
        except AttributeError as e:
            pass
        self._size = (10,10)
        return self._size

    @size.setter
    def size(self,value):
        self._size = value
        try:
            del(self.surface)
        except AttributeError as e:
            pass

    @property
    def surface(self):
        try:
            return self._surface
        except AttributeError as e:
            pass

        self._surface = pygame.surface.Surface(self.size, depth=depth)

        return self._surface

    def draw(self,age):
        self.surface.fill(self.color(age))
        return self.surface

    def color(self,age):
        """

        :param age: Current generation value
        :return: Cell color
        """
        if age < 1 :
            return (0,0,0)

        if age == 1:
            return (255,255,255)
        elif age in range(2,100):
            return (239, 85, 85)
        elif age in range(100,200):
            return (229, 85, 239)
        elif age in range(200,300):
            return (126, 85, 239)
        elif age in range(300,500):
            return (126, 85, 239)
        else:
            return (85, 239, 172)

        # frequency,width,center = 0.01,127,128
        # colors = []
        #
        # for phase in np.arange(0, 6, 2):
        #     val = int(((math.sin(frequency*age) + phase)*width) + center)
        #     colors.append(255) if val > 255 else colors.append(val)
        #
        #
        #
        # print("Colors :"+str(colors))
        # return tuple(colors)

class SquareGameCell(GameCell):
    def draw(self,age,deadCellColor= None):

        if deadCellColor is None:
            deadCellColor = self.deadCellColor

        if age:
            self.surface.fill(self.color(age))
            pygame.draw.rect(self.surface,deadCellColor,self.surface.get_rect(),1)
        else:
            self.surface.fill(deadCellColor)

        return self.surface

class PyGameGrid(OptmizedBaseGrid):

    def __init__(self,width,height,cellClass=SquareGameCell):
        super(PyGameGrid,self).__init__(width,height)

        self.cell = cellClass(10,10)

        pygame.display.set_caption('Game of Life simulation')

        self.display_height = 100
        self.paused = False
        self.events = {QUIT:self.quit}
        self.controls ={K_ESCAPE:self.quit,
                         K_q:self.quit,
                         K_SPACE: self.togglePaused,
                         K_PAGEUP: self.incrementInterval,
                         K_PAGEDOWN: self.decrementInterval}


    @property
    def screen(self):
        try:
            self._screen
        except AttributeError as e:
            pass

        offset_x,offset_y = self.cell.size

        screen_size = (self.width*offset_x,self.height*offset_y + self.display_height)
        self._screen = pygame.display.set_mode(screen_size,0,depth)
        self._screen.fill(self.background)
        return self._screen

    @property
    def buffer(self):
        try:
            return self._buffer
        except AttributeError as e:
            pass
        self._buffer = self.screen.copy()
        self._buffer.fill(self.background)
        return self._buffer

    @property
    def background(self):
        try:
            return self._background
        except AttributeError as e:
            pass

        self._background = self.cell.deadCellColor
        return self._background

    @property
    def font(self):
        try:
            return self._font
        except AttributeError as e:
            pass

        self._font = pygame.font.Font(pygame.font.get_default_font(),24)
        return self._font

    @property
    def displayRect(self):
        try:
            return self._displayRect
        except AttributeError as e:
            pass

        self._displayRect = self.screen.get_rect()
        self._displayRect.y = self._displayRect.height - self.display_height
        self._displayRect.height = self.display_height
        return self._displayRect

    @property
    def interval(self):
        try:
            return self._interval
        except AttributeError as e:
            pass
        self._interval = 0.01
        return self._interval

    @interval.setter
    def interval(self,value):
        self._interval = float(value)
        if self._interval < 0:
            self._interval = 0.0

    def incrementInterval(self):
        self.interval+=0.01

    def decrementInterval(self):
        self.interval-=0.01

    def togglePaused(self):
        self.paused = not self.paused

    @property
    def generationPerSec(self):
        try:
            return self._generationPerSec
        except AttributeError as e:
            pass
        self._generationPerSec = 0
        return self._generationPerSec

    @generationPerSec.setter
    def generationPerSec(self,value):
        self._generationPerSec = int(value)

    @property
    def status(self):
        try:
            return self.status.format(self=self,
                                       nAlive=len(self.alive),
                                       nTotal=len(self.cells))
        except AttributeError:
            pass

        s = ['Generations: {self.generation:<10}',
             '{self.generationPerSec:>4} G/s',
             'Census: {nAlive}/{nTotal}']

        self._status = ' '.join(s)
        return self.status.format(self=self,
                                   nAlive=len(self.alive),
                                   nTotal=len(self.cells))

    def reset(self):
        super(PyGameGrid,self).reset()

    def quit(self):
        exit()

    def handleInput(self):

        pressed_key = pygame.key.get_pressed()
        for key,action in self.controls.items():
            if pressed_key[key]:
                action()


        """event handling"""
        for event in pygame.event.get():
            event_name = pygame.event.event_name(event.type)
            try:
                self.events[event_name](event)
            except KeyError as e:
                pass

    def drawDisplay(self,surface,color,frame):

        labels = ['Generations:', 'Generations/Sec:',
                  '# Cells Alive:', '# Total Cells:']

        values = ['{self.generation}'.format(self=self),
                  '{self.generationPerSec}'.format(self=self),
                  '{nAlive}'.format(nAlive=len(self.alive)),
                  '{nCells}'.format(nCells=len(self.cells))]


        for i,texts in enumerate(zip(labels,values)):
            label,value = texts
            l = self.font.render(label,True,color)
            r = l.get_rect()
            r.y = frame.y + (i * r.height)
            surface.blit(l,r)

            v = self.font.render(value, True, color)
            r = v.get_rect()
            r.y = frame.y + (i * r.height)
            r.x = 250
            surface.blit(v, r)

    def getRectDimen(self,x,y):
        w,h = self.cell.size
        return ((x*w,y*h),(w,h))

    def draw(self,allCells=False):
        self.buffer.fill(self.background)

        for x,y in self.alive:
            surface = self.cell.draw(self[x,y],self.background)
            self.buffer.blit(surface,self.getRectDimen(x,y))

        self.drawDisplay(self.buffer,(255,255,255),self.displayRect)

        return self.screen.blit(self.buffer,(0,0))

    def saveFrame(self,destdir='images',prefix='generation',ext='bmp'):

        fname = '%s/%s-{:05}.%s' % (destdir,prefix,ext)
        pygame.image.save(self.screen,fname.format(self.generation))

    def run(self,stop=-1,interval=0.01):

        self.interval = interval

        while self.generation != stop:
            self.handleInput()
            t0 = time.time()

            if not self.paused:
                self.advanceGen()

            rect = self.draw(allCells=self.generation==0)

            t1 = time.time()

            if self.paused:
                self.generationPerSec = 0
            else:
                self.generationPerSec = 1/(t1-t0)

            pygame.display.update(rect)

            if self.writeGenerations:
                self.saveFrame(ext='png')

            time.sleep(self.interval)


if __name__ == '__main__':

    """
    GameOfLife.py glider,10,10 pulsar,0,0 lws,0,20
    """

    pygame.init()
    grid = PyGameGrid(100,70,cellClass=SquareGameCell)
    grid.writeGenerations = False

    x,y = 10,10
    pattern_name = 'glider'

    grid.addPattern(pattern_name,x=x,y=y)
    grid.addPattern(pattern_name,x=8,y=20)
    grid.addPattern('pulsar', x=20, y=20)
    grid.addPattern('diehard', x=40, y=90)

    grid.run()


















