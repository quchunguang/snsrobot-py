#!/usr/bin/env python2
# -*- encoding=utf8 -*-
'''
Elo Rating System

Reference
    https://en.wikipedia.org/wiki/Elo_rating_system
'''
import math


def elo_rating(ranka, rankb, scorea, k=16):
    '''
    ranka            - player A's current rank score.
    rankb            - player B's current rank score.
    scorea           - 1 if A win, 0 otherwise.
    k                - The K-factor. k = 16 by default.
    (rankan, rankbn) - return the new rank score for next rating.
    '''
    expecta = 1/(1+math.pow(10, (rankb-ranka)/400))
    rankan = ranka + k*(scorea-expecta)
    rankbn = rankb - k*(scorea-expecta)
    return (rankan, rankbn)


def main():
    '''
    For test only
    '''
    ranka = rankb = 0
    scores = [1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0,
              0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    for i in scores:
        ranka, rankb = elo_rating(ranka, rankb, i)
        print ranka, rankb

if __name__ == '__main__':
    main()
