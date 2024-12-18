from time import time
from dokusan import generators

class SolverState:
    def __init__(self, state, duration):
        self.state = state
        self.time = duration


class Solver:
    def __init__(self):
        self.possible_values = {}

    def solve(self, board):
        start_time = time()
        self.get_all_possible_values(board)

        if not self.is_solvable(board):
            return SolverState(False, time() - start_time)

        # Appling AC-3 to reduce domains
        self.ac3()

        # Backtrack to find a solution
        result = self.__solve(board, 0, 0)
        return SolverState(result, time() - start_time)

    def is_solvable(self,board):
        for value in self.possible_values.values():
            if len(value) == 0:
                return False
            
        # for i in range(9):
        #     for j in range(9):
        #         if board[i][j] != 0:
        #             if not self.is_valid(board,i,j,board[i][j]):
        #                 return False
        print("Returned True")
        return True

    def get_all_possible_values(self, board):
        self.possible_values = {}
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    self.possible_values[(i, j)] = self.get_values_for_cell(board, i, j)

    def get_values_for_cell(self, board, row, column):
        return [i for i in range(1, 10) if self.is_valid(board, row, column, i)]

    def get_neighbors(self, cell):
        row, col = cell
        neighbors = set()

        neighbors.update((row, j) for j in range(9) if j != col)
        neighbors.update((i, col) for i in range(9) if i != row)

        start_row, start_col = (row // 3) * 3, (col // 3) * 3
        neighbors.update(
            (i, j)
            for i in range(start_row, start_row + 3)
            for j in range(start_col, start_col + 3)
            if (i, j) != (row, col)
        )

        return {neighbor for neighbor in neighbors if neighbor in self.possible_values}

    def ac3(self):
        queue = [(xi, xj) for xi in self.possible_values for xj in self.get_neighbors(xi)]

        while queue:
            xi, xj = queue.pop(0)
            if self.revise(xi, xj):
                if len(self.possible_values[xi]) == 0:
                    return False
                # Adds all the one-way arcs 
                for xk in self.get_neighbors(xi) - {xj}:
                    queue.append((xk, xi))
        return True

    def revise(self, xi, xj):
        revised = False
        for value in set(self.possible_values[xi]):
            if not any(self.is_consistent(value, other) for other in self.possible_values[xj]):
                self.possible_values[xi].remove(value)
                revised = True
        return revised

    def is_consistent(self, value, other):
        return value != other

    def __solve(self, board, row, column):
        if row == 9:
            return True
        elif column == 9:
            return self.__solve(board, row + 1, 0)
        elif board[row][column] != 0:
            return self.__solve(board, row, column + 1)
        else:
            cell = (row, column)
            for value in self.possible_values.get(cell, range(1, 10)):
                if self.is_valid(board, row, column, value):
                    board[row][column] = value
                    if self.__solve(board, row, column + 1):
                        return True
                    board[row][column] = 0
                    # print(f"Backtracking at: {row},{column} failed value => {value}")
            return False

    def is_valid(self, board, row, column, value):
        not_in_row = value not in board[row]
        not_in_column = value not in [board[i][column] for i in range(9)]
        not_in_sub_grid = value not in [
            board[i][j]
            for i in range(row // 3 * 3, row // 3 * 3 + 3)
            for j in range(column // 3 * 3, column // 3 * 3 + 3)
        ]
        return not_in_row and not_in_column and not_in_sub_grid
        
    def generate_random_board(self):
        sudoku = generators.random_sudoku(avg_rank=300)
        board = [[0 for _ in range(9)] for _ in range(9)]
        for cell in sudoku.cells():
            board[cell.position.row][cell.position.column] = 0 if cell.value == None else cell.value
            # self.update_gui_board(cell.position.row,cell.position.column,board[cell.position.row][cell.position.column])
        print(board)
        return board
