import cv2
import numpy as np
from matplotlib import pyplot as plt
from sklearn import datasets, svm, metrics
import pandas as pd
import tensorflow as tf
import os
pd.options.display.float_format = '{:,.2f}'.format



## Creating train and test data
cnt=0
x_train=[]
y_train=[]
for i in range(0,13):
	for j in range(0,70):
		exists = os.path.isfile('dataset/'+str(i)+'/'+str(j)+'.jpg')
		if exists:
				cnt=cnt+1
				gray = cv2.imread('dataset/'+str(i)+'/'+str(j)+'.jpg')
				gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
				gray = cv2.resize(255-gray, (28, 28))
				x_train.append(gray)
				y_train.append(i)

x=np.array(x_train)
y=np.array(y_train)

from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split( x, y, test_size=0.4, random_state=42) ## splitting the data in test and train set

##---------------------------------------------------------------------

## training the data using CNN

x_train = x_train.reshape(x_train.shape[0], 28, 28, 1)
x_test = x_test.reshape(x_test.shape[0], 28, 28, 1)
input_shape = (28, 28, 1)
# Making sure that the values are float so that we can get decimal points after division
x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
# Normalizing the RGB codes by dividing it to the max RGB value.
x_train /= 255
x_test /= 255
print('x_train shape:', x_train.shape)
print('Number of images in x_train', x_train.shape[0])
print('Number of images in x_test', x_test.shape[0])



from keras.models import Sequential  # Importing the required Keras modules containing model and layers
from keras.layers import Dense, Conv2D, Dropout, Flatten, MaxPooling2D

model = Sequential()# Creating a Sequential Model and adding the layers
model.add(Conv2D(28, kernel_size=(3,3), input_shape=input_shape))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Flatten()) # Flattening the 2D arrays for fully connected layers
model.add(Dense(128, activation=tf.nn.relu))
model.add(Dropout(0.2))
model.add(Dense(13,activation=tf.nn.softmax))


model.compile(optimizer='adam',
			  loss='sparse_categorical_crossentropy',
			  metrics=['accuracy'])
model.fit(x=x_train,y=y_train, epochs=50)

##------------------------------------------------------------------------------------------

## Testing the data in test set

cnt=0
acc=0
for i in range(0,10):
	for j in range(1,10):
		exists = os.path.isfile('Dataset/i'+str(i)+str(j)+'.jpg')
		if exists:
				cnt=cnt+1
				gray = cv2.imread('Dataset/i'+str(i)+str(j)+'.jpg', 1)
				gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
				gray = cv2.resize(255-gray, (28, 28))
				flatten = gray.flatten() / 255.0
				#plt.imshow(gray,cmap='Greys')
				#plt.show(10)
				pred = model.predict(flatten.reshape(1, 28, 28, 1))
				#print(pred.argmax())
				if pred.argmax()==i:
					acc=acc+1

print(acc/cnt)

# COMMENTED code for testing on the symbols created which was pretty good in prediction
# gray = cv2.imread('symbols/3.jpg', 1)
# gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
# gray = cv2.resize(255-gray, (28, 28))
# plt.imshow(gray)
# plt.show(10)
# flatten = gray.flatten() / 255.0
# pred = model.predict(flatten.reshape(1, 28, 28, 1))
# if pred.argmax()==10:
# 	print('+')
# elif pred.argmax()==11:
# 	print('/')
# elif pred.argmax()==12:
# 	print('*')
# else:
# 	print(pred.argmax())
#

#---------------------------------------------------------------------------------

## creating contours in orignal image

# code for contours


im = cv2.imread('Img4.jpg') ## image to evaluate
imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
imgray = cv2.blur(imgray,(10,10))


ret,thresh = cv2.threshold(imgray,127,255,cv2.THRESH_BINARY)


class symbols:
  def __init__(myobject,x,y,w,h,Cx,Cy,pred,aspect):
	myobject.y = y
	myobject.x = x
	myobject.w = w
	myobject.h = h
	myobject.Cx = Cx
	myobject.Cy = Cy
	myobject.pred = pred
	myobject.aspect=aspect


_,contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) ## cCreating contours
list=[]
i=0
for cnt in contours:
	x,y,w,h = cv2.boundingRect(cnt)
	if w > 30 and h > 30 or w<30 and h>60 or w>60 and h<30 :
		img=im[y-15:y + h+15, x-15:x + w+15:]
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		gray = cv2.resize(255 - gray, (28, 28))
		flatten = gray.flatten() / 255.0
		pred = model.predict(flatten.reshape(1, 28, 28, 1))
		plt.imshow(img)
		plt.show(10)
		#print(pred.argmax())
		aspect_ratio=w/h
		M = cv2.moments(cnt)
		Cx = M['m10'] / M['m00']
		Cy = M['m01'] / M['m00']
		if pred.argmax()<10:
			s = symbols(x,y,w,h,Cx,Cy,str(pred.argmax()),aspect_ratio)
			print(pred.argmax())
		else:
			if pred.argmax()==10:
				ch='+'
			elif pred.argmax()==11:
				ch='/'
			else:
				ch='*'
			print(ch)
			s= symbols(x,y,w,h,Cx,Cy,str(ch),aspect_ratio)
		if i!=0:
			list.append(s)
		#cv2.imwrite(str(i)+'.png',x)
	i=i+1
x=[ [i.x,i.y,i.w,i.h] for i in list]
print(x)

## Find if one objects is enclosed in other one
def isenclosed(a,b):
	x1=a.x
	y1=a.y
	w1=a.w
	h1=a.h
	x2=b.x
	y2=b.y
	w2=b.w
	h2=b.h
	if x1<x2 and x2+w2<x1+w1 and y1<y2 and y2+h2<y1+h1:
		return 1
	return 0
## -------------------------

## new_list that doesn't take any enclosed one
new_list=[]
for i in list:
	flag=1
	for j in list:
		if i!=j:
			if isenclosed(j,i)==1:
				flag=0
				break
	if flag==1:
		new_list.append(i)

list=new_list
x=[ [i.x,i.y,i.w,i.h] for i in list]
print(x)
# for cnt in contours:
# 	x,y,w,h = cv2.boundingRect(cnt)
# 	#bound the images
# 	cv2.rectangle(im,(x-15,y-15),(x+w+15,y+h+15),(0,255,0),3)

## REmove all images in the symbols folder
d='/home/harshit/PycharmProjects/photomath/symbols'
filesToRemove = [os.path.join(d,f) for f in os.listdir()]
for f in filesToRemove:
	os.path.join("/home/harshit/PycharmProjects/photomath/symbols", f)
## ---------------------------------------------------------------

i=0
for cnt in contours:
	x,y,w,h = cv2.boundingRect(cnt)
	#following if statement is to ignore the noises and save the images which are of normal size(character)
	#In order to write more general code, than specifying the dimensions as 100,
	# number of characters should be divided by word dimension
	if (w>30 and h>30) or (w>100 and h<30):
		#save individual images
		plt.imshow(thresh[y:y+h,x:x+w])
		plt.show(10)
		cv2.imwrite('/home/harshit/PycharmProjects/photomath/symbols/'+str(i)+".jpg",thresh[y-15:y+h+15,x-15:x+w+15])
	i=i+1


## sort the list wrt t the x-coordinates of centroid of symbols
# def simpleExpr(list):
# 	return(sorted(list, key = lambda x: x[1]))
#
#
# sorted=simpleExpr(list)
#
# x=[ i[2] for i in sorted]
# print(x)

def solve(mylist):

	if(len(mylist)==1):
		return str(mylist[0].pred)
	if(len(mylist)==0):
		return ""
	maxi=mylist[0]
	for i in mylist:
		if i.aspect > maxi.aspect:
			maxi=i
	listup=[]
	listdown=[]
	listleft=[]
	listright=[]
	for i in mylist:
		if (i.Cy>maxi.Cy) and (abs(i.Cx-maxi.Cx)<(maxi.w)/2):
			listdown.append(i)
		if (i.Cy<maxi.Cy) and (abs(i.Cx-maxi.Cx)<(maxi.w)/2):
			listup.append(i)
		if (i.Cx-maxi.Cx>(maxi.w)/2):
			listright.append(i)
		if (maxi.Cx-i.Cx>(maxi.w)/2):
			listleft.append(i)
		up = solve(listup)
		down = solve(listdown)
		#print(up)
		#print(maxi.pred)
		if (maxi.pred=="/") and len(down)==0 :
			print(up+"check"+down)
			maxi.pred='-'
		if (len(up) != 0):
			up = "(" + up + ")"
		if (len(down) != 0):
			down = "(" + down + ")"
	return solve(listleft)+up+str(maxi.pred)+down+solve(listright)

print(eval(solve(list)))

