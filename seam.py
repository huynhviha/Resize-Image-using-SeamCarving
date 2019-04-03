import numpy as np
import cv2
from scipy.misc import toimage
import math
import random
from PIL import Image
	
def energy(img):
	height, width = img.shape[:2]
	energy_img = np.zeros((height, width))
	ver_kernel = np.array([[0, 0, 0], [-1, 0, 1], [0, 0, 0]])
	hor_kernel = np.array([[0, -1, 0], [0, 0, 0], [0, 1, 0]])
	ver_energy = cv2.filter2D(img, 0, ver_kernel)
	hor_energy = cv2.filter2D(img, 0, hor_kernel)
	for i in range(height):
		for j in range(width):
			tmp = np.sqrt(ver_energy[i][j] ** 2 + hor_energy[i][j] ** 2)
			energy_img[i][j] = tmp[0]
	a = toimage(energy_img)
	a.save('d.jpg')
	a = cv2.imread('d.jpg')
	b = a[:, :, 0]
	return b

def vertical_seam(energy):
	height, width = energy.shape[:2]
	dynamic = np.zeros((height, width))
	for x in range(height):
		for y in range(width):
			if x == 0:
				dynamic[x][y] = energy[x][y]
			else:
				if y == 0:
					dynamic[x][y] = min(dynamic[x - 1][y], dynamic[x - 1][y + 1]) + energy[x][y]
				elif y == width - 1:
					dynamic[x][y] = min(dynamic[x - 1][y], dynamic[x - 1][y - 1]) + energy[x][y]
				else:
					dynamic[x][y] = min(dynamic[x - 1][y - 1], dynamic[x - 1][y], dynamic[x - 1][y + 1]) + energy[x][y]
	return dynamic
	
def vertical_trace(dynamic, energy):
	height, width = dynamic.shape[:2]
	min = 1000000
	x = height - 1
	trace = np.zeros((height, width))
	while x >= 0:
		if x == height - 1:
			for y in range(width):
				if dynamic[x][y] < min:
					min = dynamic[x][y]
			tmp_min = min
			mins = []
			for y in range(width):
				if dynamic[x][y] == tmp_min:
					mins.append(y)
			ran = random.randint(0, len(mins) - 1)
			min_x = height - 1
			min_y = mins[ran]
			trace[min_x][min_y] = 1
		else:
			if min_y == 0:
				s = 0
				d = min_y + 2
			elif min == width - 1:
				s = min_y - 1
				d = min_y + 1
			else:
				s = min_y - 1
				d = min_y + 2
			for k in range(s, d):
				if dynamic[x][k] + energy[min_x][min_y] == min:
					min = dynamic[x][k]
					trace[x][k] = 1
					min_x = x
					min_y = k
					break
		x = x - 1
	return trace, tmp_min
	
def remove_vertical_seam(trace, img):
	height, width = img.shape[:2]
	for x in range(height):
		for y in range(width):
			if trace[x][y] == 1:
				for k in range(y, width - 1):
					img[x][k] = img[x][k + 1]
				y = width
	t = img[0: height, 0: width - 1]
	return t
	
def remove_vertical(delta_y, img):
	height, width = img.shape[:2]
	for i in range(delta_y):
		a = energy(img)
		b = vertical_seam(a)
		c, k = vertical_trace(b, a)
		d = remove_vertical_seam(c, img)
		img = d
	return img
	
def add_vertical_seam(trace, img):
	height, width = img.shape[:2]
	tmp = np.zeros((height, 1, 3))
	tmp = img[0: height, width - 1: width]
	img = np.concatenate((img, tmp), axis = 1)
	for x in range(height):
		flag = 0
		for y in range(width):
			if trace[x][y] == 1:
				img[x][y] = img[x][y]
				tmp = y
				y = width
				while(y > tmp):
					img[x][y] = img[x][y - 1]
					y = y - 1
				y = width
	return img

def add_vertical(delta_y, img):
	height, width = img.shape[:2]
	for i in range(delta_y):
		a = energy(img)
		b = vertical_seam(a)
		c, k = vertical_trace(b, a)
		d = add_vertical_seam(c, img)
		img = np.asarray(toimage(d))
	return img
	
def transpose(img):
	height, width = img.shape[:2]
	horizontal_img = np.zeros((width, height, 3))
	for x in range(height):
		for y in range(width):
			horizontal_img[y][x] = img[x][y]
	return np.array(toimage(horizontal_img))
	
def add_horizontal(delta_x, img):
	h = transpose(img)
	tmp = add_vertical(delta_x, h)
	return transpose(tmp)
	
def remove_horizontal(delta_x, img):
	h = transpose(img)
	tmp = remove_vertical(delta_x, h)
	return transpose(tmp)

def main(a, b, img):
	height, width = img.shape[:2]
	a = height + a
	b = width + b
	delta_x = abs(height - a)
	delta_y = abs(width - b)
	if a > height:	
		img = add_horizontal(delta_x, img)
		if b > width:
			img = add_vertical(delta_y, img)
		if b < width:
			img = remove_vertical(delta_y, img)
	elif a < height:
		img = remove_horizontal(delta_x, img)
		if b > width:
			img = add_vertical(delta_y, img)
		if b < width:
			img = remove_vertical(delta_y, img)
	else:
		if b > width:
			img = add_vertical(delta_y, img)
		if b < width:
			img = remove_vertical(delta_y, img)
	return img
	
img = cv2.imread('aa.jpg')
r = main(-40, -40, img)
cv2.imshow('anh goc', img)
cv2.imshow('anh ket qua', r)
cv2.waitKey(0)	