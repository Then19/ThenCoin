from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
import asyncio
from threading import Thread
from random import randint, choice
from pydantic import BaseModel


class Move(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class Point(BaseModel):
    x: int
    y: int

    def move_point(self, side: Move):
        if side == Move.UP:
            self.x -= 1
        elif side == Move.DOWN:
            self.x += 1
        elif side == Move.LEFT:
            self.y -= 1
        else:
            self.y += 1

    def check_borders(self, x: int, y: int) -> bool:
        if 0 > self.x or self.x > x - 1:
            return False
        if 0 > self.y or self.y > y - 1:
            return False
        return True

    def get_tuple(self) -> tuple:
        return tuple([self.x, self.y])


class Player:
    def __init__(self, user_id: UUID, side: Move):
        self.user_id = user_id
        self.moves: list[Move] = [side, side]
        self.snake_coords: list[Point] = self.__generate_start_coords(side)

    def set_move(self, side: Move):
        if self.moves[-1] != side:
            self.moves = [self.moves[-1], side]

    @staticmethod
    def __generate_start_coords(side: Move) -> list[Point]:
        if side == Move.UP:
            return [Point.construct(x=i, y=36) for i in range(30, 35)]
        elif side == Move.DOWN:
            return [Point.construct(x=i, y=3) for i in range(9, 4, -1)]
        elif side == Move.LEFT:
            return [Point.construct(x=3, y=i) for i in range(30, 35)]
        elif side == Move.RIGHT:
            return [Point.construct(x=36, y=i) for i in range(9, 4, -1)]

    def __try_step(self, move: Move):
        coord_head: Point = self.snake_coords[0].copy()
        coord_head.move_point(move)
        return coord_head

    @staticmethod
    def __check_borders(coord: Point, borders: Optional[list[Point]] = None) -> bool:
        if not coord.check_borders(40, 40):
            return False

        if not borders:
            return True

        return True

    def next_step(self, borders: Optional[list[Point]] = None) -> bool:
        step = self.__try_step(self.moves[-1])

        if step == self.snake_coords[1]:
            step = self.__try_step(self.moves[0])

        if not self.__check_borders(step, borders):
            return False

        self.snake_coords.insert(0, step)
        del self.snake_coords[-1]

        return True

    def add_length(self, size: int):
        for _ in range(size):
            self.snake_coords.insert(-1, self.snake_coords[-1].copy())


class SnakeGame:
    def __init__(self, game_id: UUID, players: list[UUID]):
        self.game_id = game_id

        self.players: dict[UUID, Player] = \
            {n: Player(n, p) for n, p in zip(players, [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT])}

        self.borders: list[Point] = []

        self.bonuses: dict[tuple, int] = {}

    def __lose_game(self, user_id: UUID):
        del self.players[user_id]

    def get_game_data(self):
        return {
            'game': self.game_id,
            'status': len(self.players),
            'snakes': {n: [g.get_tuple() for g in i.snake_coords] for n, i in self.players.items()},
            'borders': [i.get_tuple for i in self.borders],
            'points': self.bonuses
        }

    def points_control(self):
        if (count_points := len(self.bonuses)) < (must_points := len(self.players) * 3):
            for _ in range(must_points - count_points):
                self.bonuses[(randint(0, 39), randint(0, 39))] = choice([1, 2, 5])

    def __get_hard_points(self) -> list[Point]:
        temp: list[Point] = []
        for i in self.players.values():
            temp.extend(i.snake_coords[1:])
        return temp

    def __check_cross(self):
        close_points: list[Point] = self.__get_hard_points()
        losers = []

        for i in self.players.values():
            if i.snake_coords[0] in close_points:
                losers.append(i.user_id)

        for i in losers:
            self.__lose_game(i)

    def __players_step(self):
        losers = []
        for p in self.players.values():
            if not p.next_step(self.borders):
                losers.append(p.user_id)

            if (p_p := p.snake_coords[0].get_tuple()) in self.bonuses:
                p.add_length(self.bonuses[p_p])
                del self.bonuses[p_p]

        self.__check_cross()
        
        for i in losers:
            self.__lose_game(i)

    def next_tick(self):
        self.__players_step()
        self.points_control()


test_player = uuid4()
game = SnakeGame(game_id=uuid4(), players=[test_player, uuid4(), uuid4()])


async def render_board():
    status = True

    while status:
        board = [["_" for i in range(40)] for j in range(40)]
        game_data = game.get_game_data()
        status = game_data['status']

        simbols = iter("#%$+")

        snake_simbols = {i: next(simbols) for i in game_data['snakes'].keys()}

        for c, p in game_data['points'].items():
            board[c[0]][c[1]] = {5: '@', 2: '&', 1: '*'}.get(p)

        for x, y in game_data['borders']:
            board[x][y] = ' '

        for n, c in game_data['snakes'].items():
            for x, y in c:
                board[x][y] = snake_simbols[n]

        for i in board:
            print(''.join(i))
        print(game.next_tick())
        await asyncio.sleep(0.1)


def mover():
    while True:
        s_move = input()
        if s_move == 'w':
            game.players[test_player].set_move(Move.UP)
        elif s_move == 's':
            game.players[test_player].set_move(Move.DOWN)
        elif s_move == 'a':
            game.players[test_player].set_move(Move.LEFT)
        elif s_move == 'd':
            game.players[test_player].set_move(Move.RIGHT)


if __name__ == "__main__":
    Thread(target=mover).start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(render_board())
