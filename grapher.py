import base64
import matplotlib
from matplotlib.figure import Figure
import io
import numpy as np
import os
from PIL import Image
import PIL
import datetime


class Graph:
	def __init__(self, data, labels, title, xlabel, ylabel):
		self.title = title
		self.xlabel = xlabel
		self.ylabel = ylabel
		self.data = data
		self.labels = labels
		self.error = None

	def get_base64(self):
		if (self.data):
			fig = Figure(figsize=(6,4.8), dpi=100)
			axis = fig.add_subplot(1,1,1)
			for i in enumerate(self.data):
				index = i[0]
				points = i[1]
				xs = list(points.keys())
				ys = list(points.values())
				if (len(self.labels)>0):
					axis.plot(xs, ys, label=self.labels[index])
				else:
					axis.plot(xs, ys)
				total_dps = len(xs)
				x_ind = np.linspace(0, total_dps-1, 5)
				xticks = []
				ticklabels=[]
				for j in x_ind:
					unix = xs[int(j)]
					xticks += [unix]
					ticklabels += [str(datetime.datetime.fromtimestamp(int(unix)))]
				axis.set_title(self.title)
				axis.set_xlabel(self.xlabel)
				axis.set_ylabel(self.ylabel)
				axis.set_xticks(ticks=xticks)
				axis.set_xticklabels(ticklabels, rotation=30)
				if (len(self.labels)>0):
					axis.legend(loc="upper right", fontsize=8, borderpad=0, labelspacing=0, title_fontsize='small', fancybox=True)
			output = io.BytesIO()
			fig.savefig('figure1.png')
			image = PIL.Image.open('figure1.png')
			image.save(output, format="PNG")
			output.seek(0)
			bytesobject = output.read()
			base = base64.b64encode(bytesobject)
			dec = base.decode('utf-8')
			os.remove('figure1.png')
			return dec
		return False

	def check_data(self):
		if type(self.data) is not list:
			self.error = "Data must be list of dictionaries."
			return False
		elif type(self.data[0]) is not dict:
			self.error = "Data must be list of dictionaries."
			return False
		return True

	def check_info(self, keys):
		args = ['data', 'labels', 'title', 'xlabel', 'ylabel']
		for i in args:
			if i not in keys:
				self.error = "Payload missing arguments. Must have 'data','labels','title','xlabel','ylabel'. "
				return False
		return True



