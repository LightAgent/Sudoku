from time import time


class SolverState:
    def __init__(self,state,time):
        self.state = state
        self.time = time
        
class Solver:
    def __init__(self):
        self.possible_values = {}

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
    
    def is_valid(self,board,row,column,value):
        not_in_row = value not in board[row]
        not_in_column = value not in [board[i][column] for i in range(9)]
        not_in_sub_grid = value not in [board[i][j] for i in range(row//3*3,row//3*3+3) for j in range(column//3*3,column//3*3+3)]
        return not_in_row and not_in_column and not_in_sub_grid
