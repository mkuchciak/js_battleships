class Ship:
    def __init__(self, n, l, h):
        self.name = n
        self.length = l
        self.horizontal = h

    def __str__(self):
        return self.name + str(self.length) + str(self.horizontal)
