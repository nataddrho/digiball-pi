import pygame
from pygame.locals import *
from math import *


class Ball():

    def __init__(self, screen, yellow_ball=False):
        self._radius = None
        self._center = None
        self._screen = screen

        if (yellow_ball):
            self._ball_image = pygame.image.load("assets/blank_yellow_hires.png")
        else:
            self._ball_image = pygame.image.load("assets/blank_hires.png")
        self._ball_image_scaled = None

    def _draw_circle_alpha(self, surface, color, rect, radius):
        shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
        #pygame.draw.rect(shape_surf, color, shape_surf.get_rect())

        pygame.draw.circle(shape_surf,color,(radius, radius), radius)
        surface.blit(shape_surf, rect)


    def draw(self, center, radius, tip_angle=0, tip_percent=0):
        if radius != self._radius or center!=self._center:
            self._radius = radius
            self._center = center
            pixels = 2*radius
            self._ball_image_scaled = pygame.transform.scale(self._ball_image, (pixels,pixels))

        # Draw ball image
        center_x, center_y = self._center
        pos = (center_x-radius, center_y-radius)
        self._screen.blit(self._ball_image_scaled, pos)

        # Draw ball grid
        color = (0,0,0)
        pygame.draw.circle(self._screen, color, center, radius+25, 25)
        for i in range(1,7):
            pygame.draw.circle(self._screen, color, center, radius*i/10, 1)
        for i in range(0,12):
            x = center[0] + 0.6 * radius * cos(2 * pi * i / 12)
            y = center[1] + 0.6 * radius * sin(2 * pi * i / 12)
            pygame.draw.line(self._screen, color, center,(x,y))


        # Calculate tip outline position
        ball_radius = 1.125
        tip_radius = ball_radius * 11.8 / 57.15
        tip_radius_dime = 0.358
        tip_radius_curvature_ratio = tip_radius_dime / ball_radius

        t = tip_percent
        if t>55:
            t=55
        r1 = ball_radius * t/100
        draw_offset = r1 * tip_radius_curvature_ratio
        px1 = 0
        s1 = r1 + draw_offset
        if (s1-tip_radius) > r1:
            px1 = r1 + tip_radius
        else:
            px1 = s1

        # Draw tip outline
        color = (0, 0, 0)
        ax = sin(pi / 180 * tip_angle)
        ay = -cos(pi / 180 * tip_angle)
        x = center_x + self._radius * ax * px1 / ball_radius
        y = center_y + self._radius * ay * px1 / ball_radius
        tr = self._radius * tip_radius / ball_radius

        #pygame.draw.circle(self._screen, color, (x,y), tr)
        alpha = 128
        pos = (x-tr,y-tr,2*tr,2*tr)
        self._draw_circle_alpha(self._screen, (0, 0, 0, alpha), pos, tr)

        # Draw tip contact point
        color = (0, 255, 255)
        x = center_x + self._radius * ax * r1 / ball_radius
        y = center_y + self._radius * ay * r1 / ball_radius
        tr /= 20
        if tr<3:
            tr = 3
        pygame.draw.circle(self._screen, color, (x, y), tr)


