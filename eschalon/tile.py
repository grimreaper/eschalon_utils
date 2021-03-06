#!/usr/bin/python
# vim: set expandtab tabstop=4 shiftwidth=4:
#
# Eschalon Savefile Editor
# Copyright (C) 2008-2017 CJ Kucera, Elliot Kendall, Eitan Adler
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
import logging

from eschalon.constants import constants as c

LOG = logging.getLogger(__name__)


class Tile(object):
    """ A class to hold data about a particular tile on a map. """

    def __init__(self, x, y):
        """ A fresh object with no data. """

        self.x = x
        self.y = y

        self.wall = 0
        self.floorimg = 0
        self.decalimg = 0
        self.wallimg = 0
        self.walldecalimg = 0
        self.tilecontentid = 0

        self.tilecontents = []
        self.entity = None
        self.savegame = False

    def _convert_savegame(self, savegame):
        """
        Converts ourselves to a savegame or global file.  This could
        be extended by implementing classes  if needed.
        """
        for tilecontent in self.tilecontents:
            tilecontent._convert_savegame(savegame)
        self.savegame = savegame

    def replicate(self):
        newtile = Tile.new(self.book, self.x, self.y)
        newtile.savegame = self.savegame

        # Simple Values
        newtile.wall = self.wall
        newtile.floorimg = self.floorimg
        newtile.decalimg = self.decalimg
        newtile.wallimg = self.wallimg
        newtile.walldecalimg = self.walldecalimg
        newtile.tilecontentid = self.tilecontentid

        # Arrays
        for tilecontent in self.tilecontents:
            newtile.tilecontents.append(tilecontent.replicate())

        # Objects
        if (self.entity is not None):
            newtile.entity = self.entity.replicate()

        # Call out to superclass replication
        self._sub_replicate(newtile)

        # ... aaand return our new object
        return newtile

    def _sub_replicate(self, newentity):
        """
        Stub for superclasses to override, to replicate specific vars
        """
        pass

    def equals(self, tile):
        """
        Compare ourselves to another tile object.  We're just
        checking if our values are the same, NOT if we're *actually*
        the same object.  Returns true for equality, false for inequality.
        """
        return (self._sub_equals(tile) and
                self.x == tile.x and
                self.y == tile.y and
                self.wall == tile.wall and
                self.floorimg == tile.floorimg and
                self.decalimg == tile.decalimg and
                self.wallimg == tile.wallimg and
                self.walldecalimg == tile.walldecalimg and
                self.tilecontentid == tile.tilecontentid and
                self.entity_equals(tile.entity) and
                self.tilecontents_equal(tile.tilecontents))

    def _sub_equals(self, entity):
        """
        Stub for superclasses to override, to test specific vars
        """
        pass

    def entity_equals(self, entity):
        """
        Compare the contents of our entity to the contents of the
        given entity.
        """
        if (self.entity is None):
            return (entity is None)
        else:
            if (entity is None):
                return False
            else:
                return self.entity.equals(entity)

    def tilecontents_equal(self, tilecontents):
        """
        Compare the contents of our tilecontents to the contents of the
        given tilecontents.
        """
        if (len(self.tilecontents) != len(tilecontents)):
            return False
        for (mytilecontent, comptilecontent) in zip(self.tilecontents, tilecontents):
            if (not mytilecontent.equals(comptilecontent)):
                return False
        return True

    def hasdata(self):
        """ Do we have something other than zeroes? """
        return (self._sub_hasdata() or
                self.wall != 0 or self.floorimg != 0 or
                self.decalimg != 0 or self.wallimg != 0 or
                self.walldecalimg != 0 or self.tilecontentid != 0)

    def _sub_hasdata(self):
        """ Stub for superclasses to define. """
        pass

    def addtilecontent(self, tilecontent):
        """
        Add a tilecontent to our tilecontent list.  Just an internal construct which isn't actually
        stored on disk.
        """
        self.tilecontents.append(tilecontent)

    def deltilecontent(self, tilecontent):
        """
        Remove a tilecontent.
        """
        self.tilecontents.remove(tilecontent)

    def addentity(self, entity):
        """
        Add an entity to our entity list.  Just an internal construct which isn't actually
        stored on disk.
        """
        self.entity = entity

    def delentity(self):
        """
        Remove our entity.  No matter if we don't have one.
        """
        self.entity = None

    def display(self, unknowns=False):
        """ Show a textual description of all fields. """

        ret = []
        ret.append("    Wall Flag: %d" % self.wall)
        ret.append("    Floor Image: %d" % self.floorimg)
        ret.append("    Decal Image: %d" % self.decalimg)
        ret.append("    Wall Image: %d" % self.wallimg)
        ret.append("    Wall Decal Image: %d" % self.walldecalimg)
        if (self.tilecontentid in c.tilecontenttypetable):
            ret.append("    Object Type: %s" %
                       c.tilecontenttypetable[self.tilecontentid])
        else:
            ret.append("    Object Type: %d" % self.tilecontentid)
        if (unknowns):
            if self.book == 1:
                ret.append("    Unknown 5: %d" % self.unknown5)
            else:
                ret.append("    Tile flag: %d" % self.tile_flag)
                if self.book == 3:
                    ret.append("    Cartography: %d" % self.cartography)

        # Display any entities we may have
        if (self.entity is not None):
            ret.append('')
            ret.append("  Associated Entity:")
            ret.append(self.entity.display(unknowns))
            ret.append('')

        # Display any tilecontents we may have
        for tilecontent in self.tilecontents:
            ret.append('')
            ret.append("  Associated Object:")
            ret.append(tilecontent.display(unknowns))
        ret.append('')

        # Return
        return "\n".join(ret)

    @staticmethod
    def new(book, x, y):
        """
        Static method to initialize the correct object
        """
        if book == 1:
            return B1Tile(x, y)
        elif book == 2:
            return B2Tile(x, y)
        elif book == 3:
            return B3Tile(x, y)


class B1Tile(Tile):
    """
    Tile structure for Book 1
    """

    book = 1

    def __init__(self, x, y):
        super(B1Tile, self).__init__(x, y)

        # Book 1 specific vars
        self.unknown5 = 0
        # This var is *probably* actually part of the wall ID, like in book 2

    def read(self, df):
        """ Given a file descriptor, read in the tile. """

        self.wall = df.readuchar()
        self.floorimg = df.readuchar()
        self.decalimg = df.readuchar()
        self.wallimg = df.readuchar()
        self.unknown5 = df.readuchar()
        self.walldecalimg = df.readuchar()
        self.tilecontentid = df.readuchar()

    def write(self, df):
        """ Write the tile to the file. """

        df.writeuchar(self.wall)
        df.writeuchar(self.floorimg)
        df.writeuchar(self.decalimg)
        df.writeuchar(self.wallimg)
        df.writeuchar(self.unknown5)
        df.writeuchar(self.walldecalimg)
        df.writeuchar(self.tilecontentid)

    def _sub_replicate(self, newtile):
        """
        Replication for B1 elements
        """
        newtile.unknown5 = self.unknown5

    def _sub_equals(self, tile):
        """
        Equality function for B1
        """
        return (tile.unknown5 == self.unknown5)

    def _sub_hasdata(self):
        """
        Do we have data in our B1-specific elements?
        """
        return (self.unknown5 != 0)


class B2Tile(Tile):
    """
    Tile structure for Book 2
    """

    book = 2

    def __init__(self, x, y):
        super(B2Tile, self).__init__(x, y)

        # Book 2 specific vars
        self.tile_flag = 0

    def read(self, df):
        """ Given a file descriptor, read in the tile. """

        self.wall = df.readuchar()
        self.floorimg = df.readuchar()
        self.decalimg = df.readuchar()
        self.wallimg = df.readshort()
        self.walldecalimg = df.readuchar()
        self.tilecontentid = df.readuchar()
        if self.savegame:
            self.tile_flag = df.readint()

    def write(self, df):
        """ Write the tile to the file. """

        df.writeuchar(self.wall)
        df.writeuchar(self.floorimg)
        df.writeuchar(self.decalimg)
        df.writeshort(self.wallimg)
        df.writeuchar(self.walldecalimg)
        df.writeuchar(self.tilecontentid)
        if self.savegame:
            df.writeint(self.tile_flag)

    def _sub_replicate(self, newtile):
        """
        Replication for B2 elements
        """
        newtile.tile_flag = self.tile_flag

    def _sub_equals(self, tile):
        """
        Equality function for B2
        """
        return (tile.tile_flag == self.tile_flag)

    def _sub_hasdata(self):
        """
        Do we have data in our B2-specific elements?
        """
        return (self.tile_flag != 0)

    def _convert_savegame(self, savegame):
        """
        Converts ourself to a savegame or global file.
        """
        super(B2Tile, self)._convert_savegame(savegame)
        self.tile_flag = 0


class B3Tile(B2Tile):
    """
    Tile structure for Book 3
    """

    book = 3

    def __init__(self, x, y):
        super(B3Tile, self).__init__(x, y)

        # Book 3 specific vars
        self.cartography = 0

    def read(self, df):
        """ Given a file descriptor, read in the tile. """

        self.wall = df.readuchar()
        self.floorimg = df.readuchar()
        self.decalimg = df.readuchar()
        self.wallimg = df.readshort()
        self.walldecalimg = df.readuchar()
        self.tilecontentid = df.readuchar()
        if self.savegame:
            self.tile_flag = df.readint()
            self.cartography = df.readint()

    def write(self, df):
        """ Write the tile to the file. """

        df.writeuchar(self.wall)
        df.writeuchar(self.floorimg)
        df.writeuchar(self.decalimg)
        df.writeshort(self.wallimg)
        df.writeuchar(self.walldecalimg)
        df.writeuchar(self.tilecontentid)
        if self.savegame:
            df.writeint(self.tile_flag)
            df.writeint(self.cartography)

    def _sub_replicate(self, newtile):
        """
        Replication for B3 elements
        """
        super(B3Tile, self)._sub_replicate(newtile)
        newtile.cartography = self.cartography

    def _sub_equals(self, tile):
        """
        Equality function for B3
        """
        return (tile.cartography == self.cartography and super(B3Tile, self)._sub_equals(tile))

    def _sub_hasdata(self):
        """
        Do we have data in our B3-specific elements?
        """
        return (self.cartography != 0 or super(B3Tile, self)._sub_hasdata())

    def _convert_savegame(self, savegame):
        """
        Converts ourself to a savegame or global file.
        """
        super(B3Tile, self)._convert_savegame(savegame)
        self.cartography = 0
