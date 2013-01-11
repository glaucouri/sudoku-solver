# -*- coding: utf-8 -*-
import sys, numpy as np
import itertools, copy
import cProfile

debug=0

C = np.arange(9)

class Sudogame(object):
    def __init__(self, i):
        """
        i è l'input
        """
        self.rawinput = i
        i = i.replace(' ','0')
        i = i.replace('.','0')
        self.game = (np.fromstring(i, dtype=np.uint8)-48).reshape(9,9)
        self.candidates = [[ [] for x in C] for x in C]
        self.supposition = None
    
    def solve(self):
        while np.any(self.game==0):
            self.placed = False
            if debug:
                print 'New turn around'
            for x,y,v in self.walk():
                if not v:
                    candidates = self.get_candidates(x,y)
                    if debug:
                        print '--',x,y,'candidati:', candidates

                    if len(candidates) == 1:
                        self.found(x,y,candidates[0])

            if not self.placed:

                # colonne
                for y in C:
                    prob_candidates = [np.array(self.candidates[ix][iy], 'i') for ix,iy in self.walkx(0,y)  ]

                    candidates = np.concatenate( prob_candidates ) 

                    for p in np.arange(1,10):
                        if p in candidates:
                            if len( np.where( candidates == p )[0] ) == 1:
                                for x in C:
                                    if p in prob_candidates[x]:
                                        self.found(x,y,p)
                    
                # righe 
                for x in C:
                    prob_candidates = [np.array(self.candidates[ix][iy], 'i') for ix,iy in self.walky(x,0)  ]

                    candidates = np.concatenate( prob_candidates ) 

                    for p in np.arange(1,10):
                        if p in candidates:
                            if len( np.where( candidates == p )[0] ) == 1:
                                for y in C:
                                    if p in prob_candidates[y]:
                                        self.found(x,y,p)
                
                # box
                for x,y in ((1,1), (1,4), (1,7),
                            (4,1), (4,4), (4,7),
                            (7,1), (7,4), (7,7)):
                    prob_candidates = [np.array(self.candidates[ix][iy], 'i') for ix,iy in self.walkbox(x,y)  ]

                    candidates = np.concatenate( prob_candidates ) 

                    for p in np.arange(1,10):
                        if p in candidates:
                            if len( np.where( candidates == p )[0] ) == 1:
                                for n, (ix,iy) in enumerate(self.walkbox(x,y)):
                                    if p in prob_candidates[n]:
                                        self.found(ix,iy,p)


            if not self.placed:
                if self.supposition is None:

                    all_suppositions = []

                    for _,x,y in sorted(
                         [(len(self.candidates[x][y]), x,y)  for x in C for y in C if len(self.candidates[x][y])>0]
                               ):
                        for v in self.candidates[x][y]:
                            all_suppositions.append((x,y,v))

                    n_ipo = 0

                    # ipotesi!
                    (x,y,v) = all_suppositions[n_ipo]

                    self.supposition = {'game':self.game.copy(),
                                        'cand':self.candidates[:],
                                        'all_suppositions':all_suppositions,
                                        'n_ipo':n_ipo}

                    if debug:
                        print 'ipotesi',x,y,v

                    self.found(x,y,v)

                else:
                    #import ipdb; ipdb.set_trace()
                    # Non trovato, ipotesi inutile

                    S = self.supposition
                    self.game = S['game']
                    self.candidates = S['cand']

                    S['n_ipo'] += 1

                    (x,y,v) = S['all_suppositions'][S['n_ipo']]

                    if debug:
                        print 'ipotesi',x,y,v
                    
                    #try:
                    self.found(x,y,v)
                    #except:
                    #    import ipdb; ipdb.set_trace()
                    continue

            if not self.placed:
                print 'FALLITO'
                #print self.asstring()
                import ipdb;ipdb.set_trace()
                #raise ValueError
                break

        return 

    def asstring(self):
        return ''.join(map(str,self.game.flatten())).replace('0','.')

    def pprint(self):
        for y in C:
            print self.game[:,y]



    def walk(self):
        #return [(x,y,self.game[x,y]) for _,x,y in sorted([(len(self.candidates[x][y]), x,y)  for x in C for y in C])]
        for x in C:
            for y in C:
                yield x,y, self.game[x,y]

    def walkx(self,_,y):
        """return all coordinates of the row"""
        for x in C:
            yield x,y

    def takex(self,_,y):
        """return all values of the column"""
        return self.game[0:9,y]
    
    def walky(self,x,_):
        for y in C:
            yield x,y
    
    def takey(self,x,_):
        """return all values of the row"""
        return self.game[x,0:9]
    
    def walkbox(self,x,y):
        x = (x/3)*3
        y = (y/3)*3
        for cx in range(x, x+3):
            for cy in range(y, y+3):
                yield cx,cy
    
    def takebox(self,x,y):
        """return all values of the box"""
        x = (x/3)*3
        y = (y/3)*3
        return self.game[ x:x+3, y:y+3 ].flatten()


    def row(self,x):
        q =self.game[x,:]
        return q[q>0]
    
    def col(self,y):
        q=self.game[:,y]
        return q[q>0]
    
    def box(self,x,y):
        x = (x/3)*3
        y = (y/3)*3
        q=self.game[x:x+3,y:y+3]
        return q[q>0]

    def get_candidates(self, x,y):
        if not len(self.candidates[x][y]):
            self.candidates[x][y] = \
                    np.setdiff1d( 
                          np.arange(1,10),
                          np.unique( 
                               np.concatenate( ( self.takex(x,y), 
                                                 self.takey(x,y), 
                                                 self.takebox(x,y)) 
                         ) )
            ).tolist()
        return self.candidates[x][y]

    def found(self,x,y,v):
        self.game[x,y] = v
        self.placed = True
        self.candidates[x][y] = []
        
        for c in C:
            if v in self.candidates[c][y]:
                self.candidates[c][y].remove(v)
            if v in  self.candidates[x][c]:
                self.candidates[x][c].remove(v)

        bx = (x/3)*3
        by = (y/3)*3
        for cx in range(bx, bx+3):
            for cy in range(by, by+3):
                if v in self.candidates[cx][cy]:
                    self.candidates[cx][cy].remove(v)
        if debug:
            print '--',x,y,'found:', v
        

if __name__ == '__main__':
    for line in file('collection.txt').xreadlines():
        line = line.strip()
        print line,
        s = Sudogame(line)
        s.solve()
        #cProfile.run('s.solve()', 'profile.testing')
        print s.asstring()
        #break
