
class SortieStatus:
    not_takeoff = 'not_takeoff'
    landed = 'landed'
    in_flight = 'in_flight'
    ditched = 'ditched'
    crashed = 'crashed'
    # air_crash = 'air_crash'
    shotdown = 'shotdown'

    def __init__(self, is_airstart=False):
        self.status = self.in_flight if is_airstart else self.not_takeoff

    def __str__(self):
        return self.status

    def __eq__(self, other):
        if isinstance(other, SortieStatus):
            return self.status == other.status
        elif isinstance(other, str):
            return self.status == other
        else:
            return NotImplemented

    @property
    def is_not_takeoff(self):
        return self.status == self.not_takeoff

    @property
    def is_landed(self):
        return self.status == self.landed

    @property
    def is_in_flight(self):
        return self.status == self.in_flight

    @property
    def is_ditched(self):
        return self.status == self.ditched

    @property
    def is_crashed(self):
        return self.status == self.crashed

    @property
    def on_ground(self):
        return self.is_crashed or self.is_ditched or self.is_landed or self.is_not_takeoff

    @property
    def is_shotdown(self):
        return self.status == self.shotdown

    def landing(self):
        if self.is_in_flight:
            self.status = self.landed

    def takeoff(self):
        if not (self.is_shotdown or self.is_crashed):
            self.status = self.in_flight

    def ditch(self):
        if not (self.is_crashed or self.is_shotdown):
            self.status = self.ditched

    def crash(self):
        if not self.is_shotdown:
            self.status = self.crashed

    def down(self):
        self.status = self.shotdown


class LifeStatus:
    unharmed = 'unharmed'
    damaged = 'damaged'
    destroyed = 'destroyed'

    def __init__(self):
        self.status = self.unharmed

    def __str__(self):
        return self.status

    def __eq__(self, other):
        if isinstance(other, LifeStatus):
            return self.status == other.status
        elif isinstance(other, str):
            return self.status == other
        else:
            return NotImplemented

    @property
    def is_unharmed(self):
        return self.status == self.unharmed

    @property
    def is_damaged(self):
        return self.status == self.damaged

    @property
    def is_destroyed(self):
        return self.status == self.destroyed

    def damage(self):
        if self.is_unharmed:
            self.status = self.damaged

    def destroy(self):
        self.status = self.destroyed


class BotLifeStatus(LifeStatus):
    healthy = 'healthy'
    wounded = 'wounded'
    dead = 'dead'

    unharmed = healthy
    damaged = wounded
    destroyed = dead

    def __init__(self):
        super().__init__()
        self.status = self.healthy

    @property
    def is_healthy(self):
        return self.status == self.healthy

    @property
    def is_wounded(self):
        return self.status == self.wounded

    @property
    def is_dead(self):
        return self.status == self.dead
