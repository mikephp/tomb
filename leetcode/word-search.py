#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def exist(self, board, word):
        """
        :type board: List[List[str]]
        :type word: str
        :rtype: bool
        """
        def f(i, j):
            traces = []
            visited = set()

            if board[i][j] == word[0]:
                traces.append((i, j, 0, 0))
                visited.add((i, j))

            while traces:
                (i, j, idx, d) = traces.pop()
                if idx == (len(word) - 1):
                    return True

                while True:
                    d += 1
                    ni, nj = i, j
                    if d == 1: # right
                        nj += 1
                    elif d == 2: # down
                        ni += 1
                    elif d == 3: # up
                        ni -= 1
                    elif d == 4:
                        nj -= 1
                    else:
                        visited.remove((i, j))
                        break

                    if ni < 0 or nj < 0 or ni >= len(board) or nj >= len(board[0]) or \
                      (ni, nj) in visited or board[ni][nj] != word[idx+1]:
                        continue
                    else:
                        traces.append((i, j, idx, d))
                        traces.append((ni, nj, idx + 1, 0))
                        visited.add((ni, nj))
                        break

            return False

        for i in range(len(board)):
            for j in range(len(board[0])):
                if f(i, j): return True
        return False

if __name__ == '__main__':
    s = Solution()
    board = [
  ['A','B','C','E'],
  ['S','F','C','S'],
  ['A','D','E','E']
]
    print s.exist(board, 'ABCCED')
