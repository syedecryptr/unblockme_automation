import flask
from flask import request, jsonify
import numpy as np
import ast
import os

app = flask.Flask(__name__)

allBoards = [];
parent = {}
queue = [];


def arrayToBlock(arr, num, blocks):
    res = {};
    for var in range(6):
        for var2 in range(6):
            if(len(res) == num):
                return res
            for key in range(num):
                if(arr[var][var2] == key+1 and not key+1 in res):
                    res[key+1] = [[var, var2], blocks[key+1][1], blocks[key+1][2],blocks[key+1][3]]

def backtrace(start, end):
    path = [end]
    while path[-1] != start:
        path.append(parent[path[-1]])
    path.reverse()
    return path

def alreadyExists(board):
    for var in range(len(allBoards)):
        if (np.array_equal(board, allBoards[var])):
            return True;

    return False

#this return all possible boards after all possbile moves of given block
def allPossibleMoves(number, block, arr):
    # print(number, block, arr)
    allPossibilities = [];
    #if block is horizontal 
    if(block[1] == 'h'):
        #if block size is small:
        if(block[2] == 's'):
            b = np.copy(arr)
            i = block[0][0]
            j = block[0][1]
            ifnew = False
            #check possible to move left

            while(j-1>=0 and b[i][j-1] == 0):
                b[i][j+1] = 0
                b[i][j-1] = number
                j-=1;
                ifnew = True
            if(ifnew and np.array_equal(arr, b)==False):
                allPossibilities.append(b)
            b=np.copy(arr)
            i = block[0][0]
            j = block[0][1]
            ifnew = False
            #check possible to move right

            while(j+2<6 and b[i][j+2] == 0):
                b[i][j] = 0
                b[i][j+2] = number
                j+=1;
                ifnew = True
            if(ifnew and np.array_equal(arr, b)==False):
                allPossibilities.append(b)
        #if block size is large:
        if(block[2] == 'l'):
            b = np.copy(arr)
            i = block[0][0]
            j = block[0][1]
            # print(i,j)
            ifnew = False
            #check possible to move left
            while(j-1>=0 and b[i][j-1] == 0):
                b[i][j+2] = 0
                b[i][j-1] = number
                j-=1;
                ifnew = True
            if(ifnew and np.array_equal(arr, b)==False):
                allPossibilities.append(b)
            b = np.copy(arr)
            i = block[0][0]
            j = block[0][1]
            ifnew = False
            #check possible to move right
            while(j+3<6 and b[i][j+3] == 0):
                b[i][j] = 0
                b[i][j+3] = number
                j+=1;
                ifnew = True
            if(ifnew and np.array_equal(arr, b) ==False):
                allPossibilities.append(b)
    #if block is vertical
    if(block[1] == 'v'):
        #if block size is small:
        if(block[2] == 's'):
            b = np.copy(arr)
            i = block[0][0]
            j = block[0][1]
            ifnew = False
            #check possible to move up
            while(i-1>=0 and b[i-1][j] == 0):
                b[i+1][j] = 0
                b[i-1][j] = number
                i-=1;
                ifnew = True
            if(ifnew and np.array_equal(arr, b)==False):
                allPossibilities.append(b)
            b=np.copy(arr)
            i = block[0][0]
            j = block[0][1]
            ifnew = False
            #check possible to move down
            while(i+2<6 and b[i+2][j] == 0):
                b[i][j] = 0
                b[i+2][j] = number
                i+=1;
                ifnew = True
            if(ifnew and np.array_equal(arr, b)==False):
                allPossibilities.append(b)
        #if block size is large:
        if(block[2] == 'l'):
            b = np.copy(arr)
            i = block[0][0]
            j = block[0][1]
            ifnew = False
            #check possible to move up
            while(i-1>=0 and b[i-1][j] == 0):
                b[i+2][j] = 0
                b[i-1][j] = number
                i-=1;
                ifnew = True
            if(ifnew and np.array_equal(arr, b)==False):
                allPossibilities.append(b)
            b = np.copy(arr)
            i = block[0][0]
            j = block[0][1]
            ifnew = False
            #check possible to move down

            while(i+3<6 and b[i+3][j] == 0):
                b[i][j] = 0
                b[i+3][j] = number
                i+=1;
                ifnew = True
            if(ifnew and np.array_equal(arr, b) ==False):
                allPossibilities.append(b)
    return np.array(allPossibilities)

def solutionFinder(block_number, a, blocks):
    for var in range(block_number-1):
        queue.append([var+1,blocks,a])
    allBoards.append(a)
    while(len(queue)!=0):

        tempNumber = queue.pop(0);
        # print (tempNumber)
        ar = allPossibleMoves(tempNumber[0], tempNumber[1][tempNumber[0]], tempNumber[2]);

        for var in range(len(ar)):

            if(not alreadyExists(ar[var])):
                tempArrayBlock = arrayToBlock(ar[var], block_number-1, blocks)

                allBoards.append(ar[var])
                parent[np.array2string(ar[var])] = np.array2string(tempNumber[2]);
                #end condition
                if(ar[var][2][4] !=0 and ar[var][2][5]!=0 and ar[var][2][5] == ar[var][2][4]):
                    return backtrace(np.array2string(a), np.array2string(ar[var])) 
                for subvar in range(block_number-1):
                    queue.append([subvar+1, tempArrayBlock, ar[var]])

@app.route('/api/v1/solutionFinder', methods=['POST'])
def api_id():
    req_data = request.get_json()

    block_number = req_data['block_number']
    array = np.array(req_data['array'])
    block = ast.literal_eval(req_data['block'])

    # print(type(block))
    # print(type(array))ç
    # print(block_number, array, block)
    print(solutionFinder(block_number, array, block))
    return (jsonify(solutionFinder(block_number, array, block)))
    

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
