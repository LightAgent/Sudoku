from time import time
import random


class SolverState:
    def __init__(self,state,time):
        self.state = state
        self.time = time
        
class Solver:
    def __init__(self):
        self.possible_values = {}
        self.domains = {}
        self.initialize_domains()

    def initialize_domains(self):
        for row in range(9):
            for col in range(9):
                if self.board[row][col] != 0:
                    self.domains[(row, col)] = {self.board[row][col]} #Pre-filled cell
                else:
                    self.domains[(row, col)] = set(range(1, 10)) #empty cell

    def apply_arc_consistency(self):
        queue = [(cell, neighbor) for cell in self.domains for neighbor in self.get_neighbors(cell)]
        while queue:
            cell, neighbor = queue.pop(0)
            if self.revise(cell, neighbor):
                if not self.domains[cell]:  # Domain is empty, so this means that teh puzzle is unsolvable
                    return False
                # Add all arcs involving this cell back to the queue
                for neighbor_of_cell in self.get_neighbors(cell):
                    if neighbor_of_cell != neighbor:
                        queue.append((cell, neighbor_of_cell))
        return True

    def solve_arc_consistency(self, board):
        start_time = time()
        if self.__solve_arc_consistency(board):
            return SolverState(True, time() - start_time)
        return SolverState(False, time() - start_time)

    def backtrack_for_arc_consistency(self):
        # Find the cell with the smallest domain (heuristic for efficiency)
        cell = min((cell for cell in self.domains if len(self.domains[cell]) > 1), key=lambda c: len(self.domains[c]))
        for value in self.domains[cell]:
            # Try assigning a value and solve recursively
            original_domains = {key: self.domains[key].copy() for key in self.domains}  # Deep copy of domains
            self.board[cell[0]][cell[1]] = value
            self.domains[cell] = {value}

            if self.apply_arc_consistency() and self.solve_with_arc_consistency():
                return True

            # Revert to the previous state if solving fails
            self.domains = original_domains
            self.board[cell[0]][cell[1]] = 0
        return False

    def solve(self,board) -> SolverState:
        start_time = time()
        self.get_all_possible_values(board)
        
        if not self.is_solvable():
            return SolverState(False,time()-start_time)
        
        result = self.__solve(board,0,0)
        return SolverState(result,time()-start_time)
    
    def is_solvable(self):
        for value in self.possible_values.values():
            if len(value) == 0:
                return False
        return True
    
    def get_all_possible_values(self,board):
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    self.possible_values[(i,j)] = self.get_values_for_cell(board,i,j)
    
    def get_values_for_cell(self,board,row,column):
        return [i for i in range(1,10) if self.is_valid(board,row,column,i)]
    
    def __solve(self,board,row,column):
        if row == 9:
            return True
        elif column == 9:
            return self.__solve(board,row+1,0)
        elif board[row][column] != 0:
            return self.__solve(board,row,column+1)
        else:
            for value in range(1,10):
                if self.is_valid(board,row,column,value):
                    board[row][column] = value
                    if self.__solve(board,row,column+1):
                        return True
                    board[row][column] = 0
            return False
    
    def __solve_arc_consistency(self, board):
        while True:
            if not self.apply_arc_consistency():
                return False

            self.update_on_singleton(board)

            # Check if the puzzle is solved
            if all(len(domain) == 1 for domain in self.domains.values()):
                return True
            
            if not any(len(domain) == 1 for domain in self.domains.values()):
                break
        return self.backtrack_for_arc_consistency()
    
    def is_valid(self,board,row,column,value):
        not_in_row = value not in board[row]
        not_in_column = value not in [board[i][column] for i in range(9)]
        not_in_sub_grid = value not in [board[i][j] for i in range(row//3*3,row//3*3+3) for j in range(column//3*3,column//3*3+3)]
        return not_in_row and not_in_column and not_in_sub_grid
    
    def get_neighbors(self, cell):
        row, col = cell
        neighbors = set()
        for i in range(9):
            neighbors.add((row, i))
            neighbors.add((i, col))
        subgrid_row, subgrid_col = row // 3 * 3, col // 3 * 3
        for i in range(subgrid_row, subgrid_row + 3):
            for j in range(subgrid_col, subgrid_col + 3):
                neighbors.add((i, j))
        neighbors.remove(cell)
        return neighbors
    
    def is_consistent(self, value, neighbor_value):
        return value != neighbor_value
    
    def revise(self, xi, xj):
        revised = False
        for value in self.possible_values[xi]:
            if not any(self.is_consistent(value, neighbor_value) for neighbor_value in self.possible_values[xj]):
                self.possible_values[xi].remove(value)
                revised = True
        return revised
    
    def generate_random_puzzle(self):
        board = [[0 for _ in range(9)] for _ in range(9)]
        for _ in range(random.randint(20, 25)):  # Randomly fill 15 to 25 cells
            row, col = random.randint(0, 8), random.randint(0, 8)
            value = random.randint(1, 9)
            if self.is_valid(board, row, col, value):
                board[row][col] = value
        self.get_all_possible_values(board)
        if not self.is_solvable():
            return self.generate_random_puzzle()  # retry if unsolvable
        return board

    def update_on_singleton(self, board):
        for cell, domain in self.domains.items():
            if len(domain) == 1:
                row, col = cell
                board[row][col] = next(iter(domain))