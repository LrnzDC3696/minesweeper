import random

J = X = HEIGHT = 0
I = Y = WIDTH = 1
BOMB_ICON = "💣"
DEFAULT_SQUARE_ICON = "🟩"
RED_FLAG_ICON = "⭕"
QUESTION_MARK_ICON = "❔"
NUMBER_TO_ICON = {x: y for x, y in enumerate("0️⃣ 1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣ 8️⃣".split(" "))}


def check_in_grid(j, i, max_height, max_width, min_height=0, min_width=0):
    return (min_height <= j < max_height) and (min_width <= i < max_width)


def generate_surrounding_locations(j, i, max_height, max_width, min_height=0, min_width=0, except_=None):
    output = set()

    for x, y in {(1, 0), (1, 1), (0, 1), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)}:
        jx = j + x
        iy = i + y

        if not check_in_grid(jx, iy, max_height, max_width, min_height, min_width):
            continue

        output.add((jx, iy))

    if except_ is not None:
        output.difference_update(except_)

    return output


def generate_locations(max_h, max_l, n):
    """Generates n number of random location"""
    output = set()

    while len(output) != n:
        output.add((random.randrange(max_h), random.randrange(max_l)))

    return output


class Mine:
    """Mine"""
    # TODO: (bug) Adjust input from user?
    # TODO: (feature) Add borders? Maybe Fen Notation?

    RED_FLAG = 1
    QUESTION_MARK = 2

    def __init__(self, has_mine=False, value=0, icon=DEFAULT_SQUARE_ICON) -> None:  # TODO: add the bomb icon here
        self.icon = icon  # Red Flag, Question Mark
        self.has_mine = has_mine
        self.value = -1 if has_mine else value
        self._triggered = False
        self._marked = False

    def trigger(self):
        self._triggered = True

        if self.has_mine:
            self.icon = BOMB_ICON
            return False

        else:
            self.icon = NUMBER_TO_ICON[self.value]
            return True

    def mark(self, mark_):  # cannot be marked if triggered
        if self._triggered:
            return False

        red_flag = Mine.RED_FLAG
        question_mark = Mine.QUESTION_MARK

        if mark_ not in (red_flag, question_mark):
            return False

        if mark_ == red_flag:
            self.icon = RED_FLAG_ICON
        elif mark_ == question_mark:
            self.icon = QUESTION_MARK_ICON

        self._marked = True
        return True

    def remove_mark(self):
        self.icon = DEFAULT_SQUARE_ICON
        self._marked = False

    def __str__(self):
        return self.icon


class Minesweeper:
    BEGINNER = {"height": 9, "width": 9, "number_of_mines": 10}
    INTERMEDIATE = {"height": 16, "width": 16, "number_of_mines": 40}
    ADVANCED = {"height": 16, "width": 30, "number_of_mines": 99}

    def __init__(self, height=9, width=9, number_of_mines=10) -> None:
        self.board = None
        self.height = height
        self.width = width
        self.number_of_mines = number_of_mines
        self._setup()
        self._is_game_over = False
        self._are_you_winning_son = False

    def _setup(self):
        # Generate the boards
        self.board = [[None for _ in range(self.width)] for _ in range(self.height)]

        # Put the bombs
        bomb_locations = generate_locations(self.height, self.width, self.number_of_mines)
        self._bomb_locations = bomb_locations

        for i, j in bomb_locations:
            self.board[j][i] = Mine(True)

        # Put the numbered ones
        for i, y in enumerate(self.board):
            for j, x in enumerate(y):
                if self.board[i][j] is not None:
                    continue

                locations_to_check = generate_surrounding_locations(j, i, self.height, self.width)
                self.board[i][j] = Mine(
                    value=len(locations_to_check.intersection(self._bomb_locations))
                )

    @staticmethod
    def take_input(string):
        n = input(string).split(" ")
        return n[:4]

    def _check_if_are_you_winning_son(self):
        for row in self.board:
            for column in row:
                if column.has_mine:
                    continue

                if not column._triggered:
                    return False

        self._are_you_winning_son = True
        self._is_game_over = True
        return True

    def start(self):
        while not self._is_game_over:
            self._show_board()
            ms_input = Minesweeper.take_input("What is your move? [Move: (m, t)] [x: int] [y: int] [Mark: (1, 2)]: ")
            move = ms_input[0]
            x = int(ms_input[1])
            y = int(ms_input[2])
            location = (x, y)

            if move in ("m", "mark"):
                if len(ms_input) < 4:
                    print("Missing arguments retry")
                    continue

                self.mark(location, int(ms_input[3]))

            elif move in ("t", "trigger"):
                if self.trigger(location) is False:
                    self._is_game_over = True
                    self._are_you_winning_son = False
            self._check_if_are_you_winning_son()

        self._show_bombs()
        print("The Game is Over!")
        print(f"You {"Won!" if self._are_you_winning_son else "Lost!"}")

    def _show_bombs(self):
        for i, j in self._bomb_locations:
            self.board[j][i].trigger()
        self._show_board()

    def _show_board(self):
        print(self)

    def _show(self, x, y):
        return self.board[x][y].trigger()

    def _show_surrounding(self, x, y, except_=None):
        self._show(x, y)

        if self.board[x][y].value != 0:
            return

        if except_ is None:
            except_ = {(x, y), }
        elif except_ is not None:
            except_.add((x, y))

        location_surrounding = generate_surrounding_locations(x, y, self.height, self.width, except_=except_)

        for loc_sur in location_surrounding:
            self._show_surrounding(*loc_sur, except_)

    def trigger(self, location):
        lj = location[J]
        li = location[I]

        if self._show(lj, li) is False:  # if the game died
            return False

        # go around and find other things
        self._show_surrounding(lj, li)

        return True

    def mark(self, location, marker):  # 1: Red Flag, 2: Question Mark
        self.board[location[J]][location[I]].mark(marker)

    def __str__(self):
        return "\n".join("".join(str(y) for y in x) for x in self.board)


def main():
    ms = Minesweeper(9, 9, 3)
    ms.start()


if __name__ == "__main__":
    main()
