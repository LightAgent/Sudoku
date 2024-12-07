from time import time


class SolverState:
    def __init__(self,state,time):
        self.state = state
        self.time = time
        
class Solver:
    def solve(self,board) -> SolverState:
        start_time = time()
        result = self.__solve(board,0,0)
        return SolverState(result,time()-start_time)
    
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
