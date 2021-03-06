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
from eschalon.savefile import FirstItemLoadException, LoadException

LOG = logging.getLogger(__name__)


class Entity(object):
    """ A class to hold data about a particular entity on a map. """

    def __init__(self, savegame=True):
        """ A fresh object with no data. """

        self.savegame = savegame
        self.entid = -1
        self.x = -1
        self.y = -1
        self.direction = -1
        self.entscript = ''
        self.movement = -1

        self.friendly = -1
        self.frame = -1
        self.health = -1
        self.initial_loc = -1

    def tozero(self, x, y) -> None:
        """ Zeroes out the entity object.  Apart from x and y, which are passed in. """
        self.x = x
        self.y = y
        self.entid = 1
        self.direction = 1
        self.entscript = ''
        if self.savegame:
            self.movement = 1
            self.friendly = 0
            self.frame = 0
            self.health = 0
            self.initial_loc = 0
            self.set_initial(x, y)

        # Call out to superclass zeroing
        self._sub_tozero()

    def _sub_tozero(self):
        """
        Function for superclasses to override with zeroing functions.
        """
        pass

    def replicate(self):
        newentity = Entity.new(self.book, self.savegame)

        # Simple Values
        newentity.savegame = self.savegame
        newentity.entid = self.entid
        newentity.x = self.x
        newentity.y = self.y
        newentity.direction = self.direction
        newentity.entscript = self.entscript
        newentity.friendly = self.friendly
        newentity.frame = self.frame
        newentity.health = self.health
        newentity.initial_loc = self.initial_loc
        newentity.movement = self.movement

        # Call out to superclass replication
        self._sub_replicate(newentity)

        # ... aaand return our new object
        return newentity

    def _sub_replicate(self, newentity):
        """
        Stub for superclasses to override, to replicate specific vars
        """
        pass

    def _convert_savegame(self, savegame):
        """
        Converts ourself to a savegame or global object.  This should be
        overridden by implementing classes if needed.
        """
        self.savegame = savegame
        save_entid = self.entid
        save_direction = self.direction
        save_entscript = self.entscript
        self.tozero(self.x, self.y)
        self.entid = save_entid
        self.direction = save_direction
        self.entscript = save_entscript
        if savegame:
            entity = c.eschalondata.get_entity(self.entid)
            if entity:
                self.friendly = entity.friendly
                self.health = entity.health
                self.movement = entity.movement

    def equals(self, entity):
        """
        Compare ourselves to another entity object.  We're just
        checking if our values are the same, NOT if we're *actually*
        the same object.  Returns true for equality, false for inequality.
        """
        return (self._sub_equals(entity) and
                self.x == entity.x and
                self.y == entity.y and
                self.entid == entity.entid and
                self.direction == entity.direction and
                self.entscript == entity.entscript and
                self.savegame == entity.savegame and
                self.friendly == entity.friendly and
                self.frame == entity.frame and
                self.health == entity.health and
                self.initial_loc == entity.initial_loc and
                self.movement == entity.movement)

    def _sub_equals(self, entity):
        """
        Stub for superclasses to override, to test specific vars
        """
        pass

    def set_initial(self, x, y):
        """
        Set our initial_loc parameter, given actual (x,y) coordinates.
        """
        self.initial_loc = (y * 100) + x

    def display(self, unknowns=False):
        """ Show a textual description of all fields. """

        ret = []

        entity = c.eschalondata.get_entity(self.entid)
        if entity:
            ret.append("\tEntity: %s" % entity.name)
        else:
            ret.append("\tEntity ID: %d" % self.entid)
        ret.append("\tMap Location: (%d, %d)" % (self.x, self.y))
        if self.direction in c.dirtable:
            ret.append("\tFacing %s" % (c.dirtable[self.direction]))
        else:
            ret.append("\tDirection ID: %d" % self.direction)
        ret.append("\tScript: %s" % self.entscript)
        if self.savegame:
            ret.append("\tFriendly: %d" % self.friendly)
            ret.append("\tHealth: %d" % self.health)
            ret.append("\tInitial Tile: %d" % self.initial_loc)
            ret.append("\tMovement Flag: %d" % self.movement)
            if self.book > 1:
                for (i, status) in enumerate(self.statuses):
                    if status != 0:
                        if i in c.statustable:
                            statusstr = c.statustable[i]
                        else:
                            statusstr = 'Unknown Status "%d"' % i
                        ret.append("\t%s: %d" % (statusstr, status))
        else:
            ret.append(
                "\t(No extra attributes - this is the base map definition file)")

        return "\n".join(ret)

    @staticmethod
    def new(book, savegame):
        """
        Static method to initialize the correct object
        """
        if book == 1:
            return B1Entity(savegame)
        elif book == 2:
            return B2Entity(savegame)
        elif book == 3:
            return B3Entity(savegame)


class B1Entity(Entity):
    """
    Entity structure for Book 1
    """

    book = 1
    form_elements = [
        'wall_01_label', 'wall_01',
        'wall_04_label', 'wall_04',
        'exit_north_label', 'exit_north_combo',
        'exit_west_label', 'exit_west_combo',
        'exit_east_label', 'exit_east_combo',
        'exit_south_label', 'exit_south_combo',
        'map_unknownh1_label', 'map_unknownh1',
        'parallax_x_label', 'parallax_x',
        'parallax_y_label', 'parallax_y',
        'clouds_label', 'clouds',
        'mapid_label', 'mapid',
        'unknown5_label', 'unknown5',
        'map_b1_outsideflag_label', 'map_b1_outsideflag',
    ]

    def read(self, df):
        """ Given a file descriptor, read in the entity. """

        # We throw an exception because there seems to be an arbitrary
        # number of entities in the file, and no 'entity count' anywhere.
        # TODO: verify that the count isn't in the main map file.
        if df.eof():
            raise FirstItemLoadException('Reached EOF')

        # ... everything else
        self.entid = df.readuchar()
        self.x = df.readuchar()
        self.y = df.readuchar()
        self.direction = df.readuchar()
        self.entscript = df.readstr().decode('UTF-8')
        if self.savegame:
            self.friendly = df.readuchar()
            self.movement = df.readuchar()
            self.health = df.readint()
            self.frame = df.readuchar()
            self.initial_loc = df.readint()

    def write(self, df):
        """ Write the entity to the file. """

        df.writeuchar(self.entid)
        df.writeuchar(self.x)
        df.writeuchar(self.y)
        df.writeuchar(self.direction)
        df.writestr(self.entscript)
        if self.savegame:
            df.writeuchar(self.friendly)
            df.writeuchar(self.movement)
            df.writeint(self.health)
            df.writeuchar(self.frame)
            df.writeint(self.initial_loc)


class B2Entity(Entity):
    """
    Entity structure for Book 2
    """

    book = 2
    num_statuses = 26
    form_elements = [
        'huge_gfx_button',
        'decalpref_snow', 'decalpref_lava',
        'b2_barrier_label', 'b2_barrier',
        'entrancescript_label', 'entrancescript',
        'returnscript_label', 'returnscript',
        'exitscript_label', 'exitscript',
        'random_sound1_label', 'random_sound1_combo',
        'tile_flag_label', 'tile_flag',
        'tree_set_label', 'tree_set',
        'map_flags_label', 'map_flags_table',
        'random_entity_1_label', 'random_entity_1',
        'random_entity_2_label', 'random_entity_2',
        'parallax1_label', 'parallax_x',
        'parallax2_label', 'parallax_y',
        'objectplace_loot_spin', 'objectplace_loot_label',
        'gtk-biggraphic'
    ]

    def __init__(self, savegame):
        super(B2Entity, self).__init__(savegame)

        # B2-specific vars
        self.statuses = []

    def _sub_tozero(self):
        """
        To-zero for B1 elements
        """
        self.statuses = []
        for i in range(self.num_statuses):
            self.statuses.append(0)

    def _sub_replicate(self, newentity):
        """
        Replication for B2 elements
        """
        newentity.statuses = []
        for status in self.statuses:
            newentity.statuses.append(status)

    def _sub_equals(self, entity):
        """
        Equality function for B2
        """
        if len(self.statuses) != len(entity.statuses):
            return False
        for (mystatus, newstatus) in zip(self.statuses, entity.statuses):
            if mystatus != newstatus:
                return False
        return True

    def read(self, df):
        """ Given a file descriptor, read in the entity. """

        # We throw an exception because there seems to be an arbitrary
        # number of entities in the file, and no 'entity count' anywhere.
        # TODO: verify that the count isn't in the main map file.
        if df.eof():
            raise FirstItemLoadException('Reached EOF')

        # ... everything else
        try:
            self.entid = df.readuchar()
            self.x = df.readuchar()
            self.y = df.readuchar()
            self.direction = df.readuchar()
            self.entscript = df.readstr().decode('UTF-8')
            if self.savegame:
                self.friendly = df.readuchar()
                self.movement = df.readuchar()
                self.health = df.readint()
                self.frame = df.readuchar()
                self.initial_loc = df.readint()
                self.statuses = []
                for i in range(self.num_statuses):
                    self.statuses.append(df.readint())
        except LoadException:
            raise FirstItemLoadException('Reached EOF')

    def write(self, df):
        """ Write the entity to the file. """

        df.writeuchar(self.entid)
        df.writeuchar(self.x)
        df.writeuchar(self.y)
        df.writeuchar(self.direction)
        df.writestr(self.entscript)
        if self.savegame:
            df.writeuchar(self.friendly)
            df.writeuchar(self.movement)
            df.writeint(self.health)
            df.writeuchar(self.frame)
            df.writeint(self.initial_loc)
            for status in self.statuses:
                df.writeint(status)


class B3Entity(B2Entity):
    """
    Entity structure for Book 3
    """

    book = 3
    num_statuses = 30
    form_elements = [
        'huge_gfx_button',
        'decalpref_snow', 'decalpref_lava',
        'b2_barrier_label', 'b2_barrier',
        'entrancescript_label', 'entrancescript',
        'returnscript_label', 'returnscript',
        'exitscript_label', 'exitscript',
        'random_sound1_label', 'random_sound1_combo',
        'random_sound2_label', 'random_sound2_combo',
        'tile_flag_label', 'tile_flag',
        'cartography_label', 'cartography',
        'tree_set_label', 'tree_set',
        'map_flags_label', 'map_flags_table',
        'random_entity_1_label', 'random_entity_1',
        'random_entity_2_label', 'random_entity_2',
        'parallax_x_label', 'parallax_x',
        'parallax_y_label', 'parallax_y',
        'gtk-biggraphic'
    ]

    def __init__(self, savegame):
        super(B3Entity, self).__init__(savegame)
