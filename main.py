import pyscreenshot as ImageGrab
import cv2
import numpy as np
import ast
import re
import pyautogui
import time
import json
import requests
a = np.zeros((6, 6))
blocks = {}
allBoards = [];
parent = {}
queue = [];
block_number = 1

def arrayToBlock(arr, num):
    res = {};
    for var in range(6):
        for var2 in range(6):
            if(len(res) == num):
                return res
            for key in range(num):
                if(arr[var][var2] == key+1 and not key+1 in res):
                    res[key+1] = [[var, var2], blocks[key+1][1], blocks[key+1][2],blocks[key+1][3]]

def whichNumberMovedWhere(b1, b2):
	b1=re.sub('\[ +', '[', b1.strip())
	b1=re.sub('[,\s]+', ', ', b1)
	# print(b1)
	b1 = np.array(ast.literal_eval(b1))
	b2=re.sub('\[ +', '[', b2.strip())
	b2=re.sub('[,\s]+', ', ', b2)
	b2 = np.array(ast.literal_eval(b2))

	b1=arrayToBlock(b1, block_number-1)
	b2=arrayToBlock(b2, block_number-1)
	# print(b1)
	
	nmoved = 1
	for var in range(block_number-1):
		if(b1[var+1] != b2[var+1]):
			nmoved = var+1
	if(b1[nmoved][1] == 'h'):
		if(b2[nmoved][0][1] > b1[nmoved][0][1]):
			where = 'r'
		else:
			where = 'l'
	else:
		if(b2[nmoved][0][0] > b1[nmoved][0][0]):
			where = 'd'
		else:
			where = 'u'
	return (nmoved,where,b1[nmoved][3][0], b1[nmoved][3][1])


def mapper(rect, block_number):
	x = rect[0]
	y = rect[1]
	w = rect[2]
	h = rect[3]
	allign = 'h'
	size = 's'
	if(y>-10 and y< 40):
		y_axis = 0
	elif(y > 40 and y < 100):
		y_axis = 1
	elif(y > 100 and y < 160):
		y_axis = 2
	elif(y > 160 and y < 220):
		y_axis = 3
	elif(y > 220 and y < 280):
		y_axis = 4
	else:
		y_axis = 5
	if(x>-10 and x< 40):
		x_axis = 0
	elif(x > 40 and x < 100):
		x_axis = 1
	elif(x > 100 and x < 160):
		x_axis = 2
	elif(x > 160 and x < 220):
		x_axis = 3
	elif(x > 220 and x < 280):
		x_axis = 4
	else:
		x_axis = 5
	if(w > h):

		allign = 'h'

		if(w>170):
			size = 'l'
			a[y_axis][x_axis] = block_number
			a[y_axis][x_axis+1] = block_number
			a[y_axis][x_axis+2] = block_number
		else:
			size = 's'
			a[y_axis][x_axis] = block_number
			a[y_axis][x_axis+1] = block_number
	else:
		allign = 'v'
		if(h>170):
			size = 'l'
			a[y_axis][x_axis] = block_number
			a[y_axis+1][x_axis] = block_number
			a[y_axis+2][x_axis] = block_number
		else:
			size = 's'
			a[y_axis][x_axis] = block_number
			a[y_axis+1][x_axis] = block_number

	blocks[block_number] = [[y_axis, x_axis], allign, size, [x,y]];

def boxes_thresholding(img, b, g, r):
    lower = np.array([0, 0, 0])
    upper = np.array([b,g,r])
    shapeMask = cv2.inRange(img, lower, upper)
    return shapeMask

def callServer(block_number, array, block):
    params = {}
    headers = {
        'Content-Type': 'application/json',
    }
    payload = {
        'block_number': block_number,
        'array': array,
        'block': block
    }
    url = "https://unblockme872.herokuapp.com/api/v1/solutionFinder"
    response = requests.post(url, headers=headers, params=params,
                             data=json.dumps(payload))
    response.raise_for_status()
    print(response.text)
    return response.text

def getStatus():
    url = 'https://unblockme872.herokuapp.com/api/v1/status'
    response = requests.get(url)
    # print(response.text)
    print(".")
    response.raise_for_status()
    # print(response.json())
    return response.json()

if __name__ == '__main__':
	time.sleep(2)
	# to be used later
	# # part of the screen
	img = pyautogui.screenshot(region=(524,304, 390, 390)) # X1,Y1,X2,Y2
	img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
	# cv2.imshow("tttt", img)
	# cv2.waitKey(0)
	# im.show()
	# #-#

	kernel = np.ones((5,5),np.uint8)

	# img=cv2.imread('sample2.png')

	threshold_boxes = boxes_thresholding(img, 0, 124, 226)

	dilated_boxes = cv2.dilate(threshold_boxes,kernel,iterations = 1)

	 # Find contours for detected portion of the image
	cnts, hierarchy = cv2.findContours(dilated_boxes.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	rects = []

	for c in cnts:
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.02 * peri, True)
		x, y, w, h = cv2.boundingRect(approx)
		if h >= 15:
			# if height is enough
			# create rectangle for bounding
			rect = (x, y, w, h)
			rects.append(rect)
			cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 1);
			# cv2.imshow("tttt", img)
			# cv2.waitKey(0)
			mapper(rect, block_number)
			block_number +=1;
	# print(np.array2string(a))
	callServer(block_number, a.tolist(), str(blocks))
	result = getStatus()
	while(result == "{'status':'false'}"):
		# print(result)
		result = getStatus()
		time.sleep(10)
	# for var in range(len(result)):
	# 	print(np.asarray(result[var]))
	# print(a)
	
	for var in range(len(result)-1):
		num, dire, x, y = whichNumberMovedWhere(result[var], result[var+1])
		# print (num, dire)
		x = x+534
		y = y+337
		pyautogui.moveTo(x+20, y+20)
		time.sleep(1)

		if(dire == "l"):
			pyautogui.dragTo(x-400, y+20, button='left') 
		if(dire == "r"):
			pyautogui.dragTo(x+400, y+20, button='left') 
		if(dire == "u"):
			pyautogui.dragTo(x+20, y-400, button='left') 
		if(dire == "d"):
			pyautogui.dragTo(x+20, y+400, button='left') 
