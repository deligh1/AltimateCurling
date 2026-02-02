import pymunk
import pygame
import random

class Game:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width, self.height = width, height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Altimate Curling")
        self.clock = pygame.time.Clock()
        self.scene = None
        self.running = True
    
    def run(self):
        self.scene = TitleScene(self)
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.scene.handle_events(events)
            self.scene.update()
            self.scene.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

    def change_scene(self, scene):
        self.scene = scene

class Scene:
    def __init__(self, game):
        self.game = game

    def handle_events(self, events):
        pass

    def update(self):
        pass

    def draw(self, screen):
        pass

class TitleScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont(None, 74)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.game.change_scene(SelectScene(self.game))

    def draw(self, screen):
        screen.fill((0, 0, 0))
        title_text = self.font.render("Altimate Curling", True, (255, 255, 255))
        prompt_text = self.font.render("Press Enter to Start", True, (255, 255, 255))
        screen.blit(title_text, (self.game.width//2 - title_text.get_width()//2, self.game.height//3))
        screen.blit(prompt_text, (self.game.width//2 - prompt_text.get_width()//2, self.game.height//2))

class SelectScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font("C:/Users/owner/Documents/Noto_Sans_JP/NotoSansJP-VariableFont_wght.ttf", 18)
        p1

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.game.change_scene(CurlingScene(self.game))

    def draw(self, screen):
        screen.fill((50, 50, 150))
        select_text = self.font.render("Select Your Stone", True, (255, 255, 255))
        prompt_text = self.font.render("Press Enter to Continue", True, (255, 255, 255))
        screen.blit(select_text, (self.game.width//2 - select_text.get_width()//2, self.game.height//3))
        screen.blit(prompt_text, (self.game.width//2 - prompt_text.get_width()//2, self.game.height//2))

class Stones:
    RADIUS = 3
    WEIGHT = 1
    FRICTION = 0
    ELASTICITY = 1
    NAME = "Stone"
    IMAGE_NAME = "normal.png"

    def __init__(self, space, player, y, strength, angle, altimate=False):
        self.space = space
        self.player = player
        self.body = pymunk.Body(self.WEIGHT, pymunk.moment_for_circle(self.WEIGHT, 0, self.RADIUS))
        self.body.position = (1, y)
        self.shape = pymunk.Circle(self.body, self.RADIUS)
        self.shape.friction = self.FRICTION
        self.shape.elasticity = self.ELASTICITY
        self.space.add(self.body, self.shape)
        self.body.velocity = (strength * pymunk.Vec2d(3, 0).rotated(-angle))
        self.image_path = f"./img/p{self.player+1}/{self.IMAGE_NAME}"

    def update(self):
        self.body.velocity -= self.body.velocity / self.body.velocity.length * 0.05  # Simulate friction

class NormalStone(Stones):
    NAME = "ノーマルストーン"
    IMAGE_NAME = "normal.png"
    def update(self):
        super().update()
    
class HeavyStone(Stones):
    WEIGHT = 3
    NAME = "ヘビーストーン"
    IMAGE_NAME = "heavy.png"

    def update(self):
        super().update()

class CurlingScene(Scene):
    def __init__(self, game, selected_stone=[[NormalStone] * 8, [NormalStone] * 8]):
        super().__init__(game)
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)
        self.selected_stone = selected_stone
        self.stones = []
        self.turn = 0  # even: player 1, odd: player 2
        self.wall_size = (100, 30)
        self.walls = [
            pymunk.Segment(self.space.static_body, (0, 0), (self.wall_size[0], 0), 1),
            pymunk.Segment(self.space.static_body, (0, self.wall_size[1]), (self.wall_size[0], self.wall_size[1]), 1),
            pymunk.Segment(self.space.static_body, (0, 0), (0, self.wall_size[1]), 1),
            pymunk.Segment(self.space.static_body, (self.wall_size[0], 0), (self.wall_size[0], self.wall_size[1]), 1)
        ]
        for wall in self.walls:
            wall.friction = 0
            wall.elasticity = 1
            self.space.add(wall)
        self.house_position = (self.wall_size[0] - 15, self.wall_size[1] / 2)

        self.waiting_time = 0
        self.operation = {"y":15, "strength":5, "angle":0, "gauge":0}
        self.limit = {"y":(0,30), "strength":(1,10), "angle":(-1.2,1.2)}
        self.state = "operation"  # operation, wait, finish

        self.magnification = 7.0
        self.margin = (80,150)

        self.font = pygame.font.Font("C:/Users/owner/Documents/Noto_Sans_JP/NotoSansJP-VariableFont_wght.ttf", 18)

    def create_stone(self, stone, player, y, strength, angle, altimate=False):
        self.stones.append(stone(self.space, player, y, strength, angle, altimate))

    def judge_winner(self):
        winner = None
        distance = 9999
        for stone in self.stones:
            x, y = stone.body.position
            dist = ((x - self.house_position[0]) ** 2 + (y - self.house_position[1]) ** 2) ** 0.5
            if dist < distance:
                distance = dist
                winner = stone.player
        return winner

    def handle_events(self, events):
        if self.state == "wait":
            pass
        if self.state == "operation":
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.operation["y"] = min(self.operation["y"] - 1, self.limit["y"][1])
                    elif event.key == pygame.K_DOWN:
                        self.operation["y"] = max(self.operation["y"] + 1, self.limit["y"][0])
                    elif event.key == pygame.K_LEFT:
                        self.operation["strength"] = max(self.operation["strength"] - 0.2, self.limit["strength"][0])
                    elif event.key == pygame.K_RIGHT:
                        self.operation["strength"] = min(self.operation["strength"] + 0.2, self.limit["strength"][1])
                    elif event.key == pygame.K_w:
                        self.operation["angle"] = min(self.operation["angle"] + 0.05, self.limit["angle"][1])
                    elif event.key == pygame.K_s:
                        self.operation["angle"] = max(self.operation["angle"] - 0.05, self.limit["angle"][0])
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.operation["strength"] *= self.operation["gauge"] * 0.7 + 0.3
                    self.operation["angle"] += random.choice([1,-1]) * (1-self.operation["gauge"]) * 0.4
                    self.create_stone(self.selected_stone[self.turn % 2][0], self.turn % 2, self.operation["y"], self.operation["strength"], self.operation["angle"])
                    self.state = "wait"
        elif self.state == "finish":
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.game.change_scene(ResultScene(self.game, self.judge_winner()))

    def update(self):
        if self.state != "finish":
            self.space.step(1/60.0)
        for stone in self.stones:
            stone.update()
        
        if self.state == "wait":
            self.waiting_time += 1
            if self.waiting_time > 300:  # Wait for 5 seconds
                self.waiting_time = 0
                self.turn += 1
                if self.turn >= 16:  # Assuming 8 stones per player
                    self.state = "finish"
                else:
                    self.state = "operation"
                    self.operation = {"y":15, "strength":5, "angle":0, "gauge":0}
        
        if self.state == "operation":
            if self.operation["gauge"] < 1.0:
                self.operation["gauge"] += 0.01
                self.operation["gauge"] *= 1.03
            if self.operation["gauge"] > 1.0:
                self.operation["gauge"] = 0

    def draw(self, screen):
        screen.fill((255, 255, 255))
        pygame.draw.rect(screen, (200, 200, 255), (self.margin[0], self.margin[1], self.wall_size[0]*self.magnification, self.wall_size[1]*self.magnification))  # Wall
        pygame.draw.rect(screen, (255, 0, 0), (100, self.game.height - 150, 600, 50))  # Stlength bar
        pygame.draw.rect(screen, (0, 255, 0), (85 + (self.operation["strength"] - self.limit["strength"][0]) / (self.limit["strength"][1] - self.limit["strength"][0]) * 600, self.game.height - 160, 30, 70))  # Strength indicator
        pygame.draw.line(screen, (0, 0, 0), (100, self.margin[1] + self.operation["y"] * self.magnification), (100 + 50 * pygame.math.Vector2(1, 0).rotate_rad(-self.operation["angle"]).x, self.margin[1] + self.operation["y"] * self.magnification + 50 * pygame.math.Vector2(1, 0).rotate_rad(-self.operation["angle"]).y), 3)  # Angle indicator
        pygame.draw.rect(screen, (255, 0, 0), (20, self.margin[1], 40, self.wall_size[1]*self.magnification))  # Y bar
        pygame.draw.rect(screen, (0, 255, 0), (10, self.margin[1] + (self.operation["y"] - self.limit["y"][0]) / (self.limit["y"][1] - self.limit["y"][0]) * self.wall_size[1]*self.magnification - 15, 60, 30))  # Y indicator
        pygame.draw.rect(screen, (255, 0, 0), (100, 70, 600, 50))  # Gauge bar
        pygame.draw.rect(screen, (0, 255, 0), (100, 60, self.operation["gauge"] * 600, 70))  # Gauge indicator
        
        pygame.draw.circle(screen, (255, 200, 200), (int(self.house_position[0] * self.magnification + self.margin[0]), int(self.house_position[1] * self.magnification + self.margin[1])), int(9 * self.magnification))  # House outer
        pygame.draw.circle(screen, (0, 0, 255), (int(self.house_position[0] * self.magnification + self.margin[0]), int(self.house_position[1] * self.magnification + self.margin[1])), int(6 * self.magnification))  # House middle
        pygame.draw.circle(screen, (255, 0, 0), (int(self.house_position[0] * self.magnification + self.margin[0]), int(self.house_position[1] * self.magnification + self.margin[1])), int(3 * self.magnification))  # House inner
        for stone in self.stones:
            x, y = stone.body.position
            color = (255, 0, 0) if stone.player == 0 else (0, 0, 255)
            pygame.draw.circle(screen, color, (int(x * self.magnification + self.margin[0]), int(y * self.magnification + self.margin[1])), int(stone.RADIUS * self.magnification))
        text = ""
        if self.state == "operation":
            text = f"{self.turn % 2 + 1}Pの番です。{self.turn // 2 + 1}ターン目　石の種類：{self.selected_stone[self.turn % 2][0].NAME}"
        elif self.state == "wait":
            text = f"待機中... 残り{(300 - self.waiting_time) // 60}秒"
        elif self.state == "finish":
            text = "ゲーム終了！スペースキーでリザルトへ"
        info_text = self.font.render(text, True, (0, 0, 0))
        screen.blit(info_text, (10, 10))

class ResultScene(Scene):
    def __init__(self, game, winner):
        super().__init__(game)
        self.font = pygame.font.SysFont(None, 74)
        self.winner = winner

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.game.change_scene(TitleScene(self.game))

    def draw(self, screen):
        screen.fill((0, 0, 0))
        result_text = self.font.render(f"Player {self.winner+1} Wins!", True, (255, 255, 255))
        prompt_text = self.font.render("Press Enter to Restart", True, (255, 255, 255))
        screen.blit(result_text, (self.game.width//2 - result_text.get_width()//2, self.game.height//3))
        screen.blit(prompt_text, (self.game.width//2 - prompt_text.get_width()//2, self.game.height//2))


if __name__ == "__main__":
    game = Game()
    game.run()