import pyxel
import pymunk

class CurlingGame:
    def __init__(self):
        self.FPS = 30
        pyxel.init(256, 256, fps=self.FPS)
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)
        self.stones = []
        self.create_stone(128, 200)
        pyxel.run(self.update, self.draw)

    def create_stone(self, x, y):
        body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 10))
        body.position = x, y
        shape = pymunk.Circle(body, 10)
        shape.elasticity = 0.8
        self.space.add(body, shape)
        self.stones.append(shape)

    def update(self):
        self.space.step(1/60.0)
        if pyxel.btnp(pyxel.KEY_SPACE):
            for stone in self.stones:
                stone.body.apply_impulse_at_local_point((0, -500), (0, 0))

    def draw(self):
        pyxel.cls(0)
        for stone in self.stones:
            x, y = stone.body.position
            pyxel.circ(int(x), int(y), 10, 7)
        pyxel.text(10, 10, "Press SPACE to throw stone", 7)

if __name__ == "__main__":
    CurlingGame()