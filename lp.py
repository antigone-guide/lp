#!/usr/bin/env python3

from util import Term
from questions import get_question
from random import choice, randint

X,Y = 79,20
room_locs = [(1,1), (4,9), (6,15), (11,8), (17,5)]
#room_locs = [(11,8), (17,5)]
MAX_LEVEL = 2
HIDE = True


class Room:
    def __init__(self, loc, level):
        self.level = level
        self.x, self.y = x, y = self.loc = loc
        self.tr = (x+3, y)
        self.tl = x, y
        self.br = (x+3, y+3)
        self.bl = (x, y+3)
        self.x2, self.y2 = self.br
        self.v_walls = [(x, y+1), (x, y+2), (x+3, y+1), (x+3, y+2)]
        self.h_walls = [(x+1, y), (x+2, y), (x+1, y+3), (x+2, y+3)]

        self.r_walls = [(x+3, y+1), (x+3, y+2)]
        self.l_walls = [(x, y+1), (x, y+2)]
        self.t_walls = [(x+1, y), (x+2, y)]
        self.b_walls = [(x+1, y+3), (x+2, y+3)]

        self.all = set((X,Y) for Y in range(y, self.y2+1) for X in range(x, self.x2+1))
        self.inside_all = [l for l in list(self.all) if self.loc_inside(l)]
        if randint(1,11)>8:
            l = self.randloc()
            print(l, level[l])
            if not level[l]:
                i = choice(items)()
                level[l] = i
                print('placed item', i)

        if HIDE:
            level.hidden |= self.all

    def __str__(self):
        return f'Room: {self.loc}, {self.br}'

    def randloc(self):
        return choice(list(self.inside_all))

    def empty_randloc(self):
        for _ in range(50):
            l = self.randloc()
            if not self.level[l]:
                return l

    def loc_in(self, loc):
        return self.x <= loc[0] <= self.x2 and self.y <= loc[1] <= self.y2

    def loc_inside(self, loc):
        return self.x < loc[0] < self.x2 and self.y < loc[1] < self.y2

    def add_to_level(self, level):
        level[self.tl] = chars.c_tl
        level[self.tr] = chars.c_tr
        level[self.br] = chars.c_br
        level[self.bl] = chars.c_bl
        for l in self.v_walls:
            level[l] = chars.l_ver
        for l in self.h_walls:
            level[l] = chars.l_hor

    def add_doors(self, level):
        doors = []
        for loc in self.v_walls + self.h_walls:
            if level[loc] == chars.dot:
                level[loc] = chars.door
                doors.append(loc)
        return doors

    def unhide(self, level):
        for l in self.all:
            if l in level.hidden:
                level.hidden.remove(l)

    def relative_pos(self, room):
        """
        assumes x < room.x

        aaa
         bbb

        a
        a b
        a b
          b

        3)
        a
          b

        4)
          b
        a
        """
        ol = overlap(self.x, self.x2, room.x, room.x2)
        if ol:
            return 1, ol
        ol = overlap(self.y, self.y2, room.y, room.y2)
        if ol:
            return 2, ol
        return (3,None) if self.y < room.y else (4,None)

def in_range(loc):
    x,y = loc
    return 0 <= x < X and 0 <= y < Y

def near(loc, xd=None, yd=None):
    x,y = loc
    lst = []
    if xd:
        lst.extend([(x+xd, y), (x, y+yd)])
    else:
        lst = [(x+1,y+1), (x,y+1), (x+1,y), (x-1,y-1), (x-1,y), (x,y-1), (x+1,y-1), (x-1, y+1)]
    return [l for l in lst if in_range(l)]


class Corridor:
    def __init__(self, all):
        self.all = all

    def unhide(self, level):
        for l in self.all:
            if l in level.hidden:
                level.hidden.remove(l)


class chars:
    l_hor = '─'
    l_ver = '│'
    c_tr = '┐'
    c_tl = '┌'
    c_br = '┘'
    c_bl = '└'
    dot = '.'
    door = '+'
    player = '@'

def r():
    return [None]*X

def overlap(a,b,c,d):
    if a>c:
        a,b,c,d = c,d,a,b
    if b>=c:
        return list(range(c+1, b))


class Level:
    def __init__(self, n=0):
        self.n = n
        self.hidden = set()
        self.rooms_by_door = {}
        self.corridors = dict()
        self.b = [r() for _ in range(Y)]
        rooms = self.rooms = [Room(l, self) for l in room_locs]
        for room in rooms:
            room.add_to_level(self)
        for i in range(len(rooms)):
            if i+2 > len(rooms):
                break
            self.make_corridor(rooms[i], rooms[i+1], i==3)
        for room in rooms:
            doors = room.add_doors(self)
            for d in doors:
                self.rooms_by_door[d] = room
        rooms[0].unhide(self)
        self.down_staircase = self.up_staircase = None

    def place_staircase(self, staircase):
        sroom = choice(self.rooms)
        l = sroom.empty_randloc()
        self[l] = staircase()
        if staircase is DownStaircase:
            self.down_staircase = l
        elif staircase is UpStaircase:
            self.up_staircase = l

    def contains(self, loc, val):
        x, y = loc
        return any(isinstance(x, val) for x in self.b[y][x])

    def __getitem__(self, loc):
        x, y = loc
        v = self.b[y][x]
        return v[-1] if v else None

    def __setitem__(self, loc, item):
        x, y = loc
        if not self.b[y][x]:
            self.b[y][x] = [None, item]
        else:
            self.b[y][x].append(item)

    def remove(self, loc, item):
        x, y = loc
        self.b[y][x].remove(item)

    def display(self):
        tostr = lambda x: ' ' if not x else x
        for y in range(Y):
            for x in range(X):
                val = self[(x,y)]
                if val and (x,y) not in self.hidden:
                    print(val, end='')
                else:
                    print(' ', end='')
            print()

    def make_corridor(self, r1, r2, d=False):
        """
        x y
        """
        if r1.x > r2.x:
            r1, r2 = r2, r1

        pos, overlap = r1.relative_pos(r2)
        if pos==1:
            x = choice(overlap)[0]
            self.make_line((x,r1.y2), (x,r2.y))
        elif pos==2:
            y = choice(yr)
            self.make_line((r1.x2,y), (r2.x,y))

        elif pos==3:

            exclude = set()
            for _ in range(2):
                st = choice(list(set(r1.r_walls)-exclude))
                ends = r2.t_walls
                #print("st,ends", st,ends)
                locs = self.burrow(st, ends, xd=1, yd=1)
                if locs:
                    break
                exclude.add(st)

            if not locs:
                exclude = set()
                for _ in range(2):
                    st = choice(list(set(r1.b_walls)-exclude))
                    ends = r2.l_walls
                    #print("st,ends", st,ends)
                    locs = self.burrow(st, ends, xd=1, yd=1)
                    if locs: break
                    exclude.add(st)

            #if not locs:
            #    print(r1)
            #    print(r2)
            assert locs
            #print("locs", locs)
            self.fill_locs(locs)

        elif pos==4:
            exclude = set()
            for _ in range(2):
                st = choice(list(set(r1.r_walls)-exclude))
                ends = r2.b_walls
                #print("st,ends", st,ends)
                locs = self.burrow(st, ends, xd=1, yd=-1)
                if locs:
                    break
                exclude.add(st)

            if not locs:
                exclude = set()
                for _ in range(2):
                    st = choice(list(set(r1.b_walls)-exclude))
                    ends = r2.l_walls
                    print("st,ends", st,ends)
                    locs = self.burrow(st, ends, xd=1, yd=-1)
                    if locs: break
                    exclude.add(st)

            #if not locs:
            #    print(r1)
            #    print(r2)
            assert locs
            #print("locs", locs)
            self.fill_locs(locs)

        corr = Corridor(locs)
        self.corridors[locs[0]] = corr
        self.corridors[locs[-1]] = corr
        if HIDE:
            self.hidden |= set(locs)

    def any_in_rooms(self, locs, rooms, terminate_early=True):
        _in = set()
        for l in locs:
            for r in rooms:
                if r.loc_in(l):
                    if terminate_early:
                        return l
                    _in.add(l)
        #print("_in", _in)
        return _in

    def not_in_rooms(self, locs, rooms):
        _in = self.any_in_rooms(locs, rooms, terminate_early=False)
        return [l for l in locs if l not in _in]

    def make_line(self, l1, l2, char=chars.dot):
        for l in self.make_locs(l1, l2):
            self[l] = char

    def fill_locs(self, locs, char=chars.dot):
        for l in locs:
            self[l] = char

    def make_locs(self, l1, l2):
        x, y = l1
        lst = []
        if x==l2[0]:
            for y in range(l1[1], l2[1]+1):
                lst.append((x,y))
        elif y==l2[1]:
            for x in range(x, l2[0]+1):
                lst.append((x,y))
        return lst

    def burrow(self, start, ends, xd, yd):
        """
        a
         b

         b
        a
        """
        loc = start
        cur = [loc]

        # destination is vertical wall?
        vert = ends[0][0] == ends[1][0]
        horiz = not vert
        #xd = 1 if start[0]<ends[0][0] else -1
        #yd = 1 if start[1]<ends[0][1] else -1
        for _ in range(100):
            nl = near(loc, xd, yd)
            final = list(set(nl) & set(ends))
            #print("final", final)
            if final:
                cur.append(final[0])
                return cur
            locs = self.not_in_rooms(nl, self.rooms)
            #print("nl", nl)
            #print("locs", locs)
            fe, le = ends[0], ends[1]

            if vert and xd==1:
                locs = [l for l in locs if l[0]<fe[0]]
            if horiz and yd==1:
                locs = [l for l in locs if l[1]<fe[1]]
            if horiz and yd==-1:
                locs = [l for l in locs if l[1]>fe[1]]

            if xd==1:
                locs = [l for l in locs if l[0]<=le[0]]
            if yd==1:
                locs = [l for l in locs if l[1]<=le[1]]
            if xd==-1:
                locs = [l for l in locs if l[0]>=fe[0]]
            if yd==-1:
                locs = [l for l in locs if l[1]>=fe[1]]

            if not locs:
                #self.fill_locs(cur, '#')
                #self.display()
                #input('>>')
                return
            loc = choice(locs)
            cur.append(loc)


class Player:
    def __init__(self, loc, level):
        self.loc = loc
        self.level = level
        self.place()
        from collections import defaultdict
        self.inventory = defaultdict(int)

    def place(self):
        self.level[self.loc] = chars.player

    def move(self, dir):
        x,y = self.loc
        if dir=='l': x+=1
        elif dir=='h': x-=1
        elif dir=='j': y+=1
        elif dir=='k': y-=1
        loc = x,y
        level = self.level
        if level[loc] == chars.door:
            if get_question(term):
                print('You got it!')
                level[loc] = chars.dot
                corridor = level.corridors.get(loc)
                room = level.rooms_by_door.get(loc)
                if corridor: corridor.unhide(level)
                if room: room.unhide(level)

            else:
                print('Wrong answer, try again..')
                return
        val = level[loc]

        # can walk inside rooms and in corridors only
        if val == chars.dot or any(r.loc_inside(loc) for r in level.rooms) or isinstance(val, Item):
            level.remove(self.loc, chars.player)
            self.loc = loc
            self.place()
            if isinstance(val, Item):
                self.inventory[val] += 1
                level.remove(self.loc, val)
                print(f'You found an {val}!')


class Item:
    pass

class Agate(Item):
    def __str__(self):
        return '*'

class Aquamarine(Item):
    def __str__(self):
        return '*'

class Calcite(Item):
    def __str__(self):
        return '*'

class DownStaircase:
    def __str__(self):
        return '>'

class UpStaircase:
    def __str__(self):
        return '<'

items = [Agate, Aquamarine, Calcite]

levels = [Level(0), Level(1), Level(2)]
for level in levels[:-1]:
    level.place_staircase(DownStaircase)
for level in levels[1:]:
    level.place_staircase(UpStaircase)
for l in levels:
    print(l.down_staircase, l.up_staircase)

level = levels[0]
r1 = level.rooms[0]
player = Player((r1.x+1, r1.y+1), level)
term = Term()

while 1:
    term.clear()
    level.display()
    inp = term.getch()
    if inp=='q':
        break
    elif inp in 'hjkl':
        player.move(inp)
    elif inp == 'i':
        if not player.inventory:
            print("You don't have anything yet!!")
        for item, count in player.inventory.items():
            print('INVENTORY')
            print(f'{str(item.__class__.__name__):<15}  {count}')
        input('continue >')
    elif inp == '>':
        if level.contains(player.loc, DownStaircase):
            x,y=player.loc
            print(level.b[y][x])
            level.remove(player.loc, chars.player)
            level = levels[level.n+1]
            player.loc = level.up_staircase
            player.level = level
            player.place()
        else:
            print('You are not on a down staircase!')

    elif inp == '<':
        if level.contains(player.loc, UpStaircase):
            level.remove(player.loc, chars.player)
            level = levels[level.n-1]
            player.loc = level.down_staircase
            player.level = level
            player.place()
        else:
            print('You are not on an up staircase!')

