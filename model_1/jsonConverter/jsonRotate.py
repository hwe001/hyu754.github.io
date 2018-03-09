'''
Simple python tutorial
'''
import json

list1 = ['physics','chemistry']; list2 =[1,2,3,4]

del list1[1]
for x in list2:
	print x

#we can also add add lists
list3 = list1+list2;print list3

#import json file
with open('../models/S01_portal_1.json') as json_data:
	d = json.load(json_data)
	print d
