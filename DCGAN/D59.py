import keras
import numpy as np


class NoizyData:
	'''noizy mnist data'''
	def __init__(self, noise_sigma=1.0, noise_scaler=0.5,noise_area=(7,7), y_scaler=0.3):
		noise_mean = 0.0

		ax = noise_area[0]
		ay = noise_area[1]
		(x,y),(tx,ty) = self.load_mnist()

		
		for i in range(len(x)):
			noise = np.random.normal(noise_mean, noise_sigma, size=(ax,ay,1)) * noise_scaler
			dx = np.random.randint(28 - 1 - ax)
			dy = np.random.randint(28 - 1 - ay)
			x[i, dx:dx + ax, dy:dy + ay] += noise
					
		noisy_x = np.clip(x,0.0,1.0)
		noisy_y = y * y_scaler

		self.x = np.concatenate((x,noisy_x), axis=0)
		self.y = np.concatenate((y,noisy_y), axis=0)
		self.tx = tx
		self.ty = ty

	def train(self):
		return self.x,self.y

	def test(self):
		return self.tx,self.ty

	@staticmethod
	def transform(x):
		return x.astype('float32').reshape(-1,28,28,1) / 255
	
	@staticmethod
	def transform_inv(x):
		return x * 255

	@staticmethod
	def load_mnist():
		from keras.datasets import mnist
		(x_train, y_train), (x_test, y_test) = mnist.load_data()

		target = y_train >= 5
		x_train = x_train[target]
		y_train = y_train[target]

		target = y_test >= 5
		x_test = x_test[target]
		y_test = y_test[target]

		x_train = NoizyData.transform(x_train)
		x_test = NoizyData.transform(x_test)
		y_train = keras.utils.to_categorical(y_train, 10)
		y_test = keras.utils.to_categorical(y_test, 10)
		return (x_train,y_train),(x_test,y_test)

def new_D():
	from keras.models import Sequential
	from keras.layers import Conv2D,Flatten,Dense,Dropout,Input
	model = Sequential(name='mnist_classifier',
		layers=[Conv2D(32, kernel_size=3, strides=1, activation='relu',input_shape=(28,28,1)),
			Conv2D(64, kernel_size=3, strides=2, activation='relu'),
			Dropout(0.5),
			Conv2D(64, kernel_size=3, strides=2, activation='relu'),
			Dropout(0.5),
			Flatten(),
			Dense(128, activation='relu'),
			Dropout(0.5),
			Dense(128, activation='relu'),
			Dropout(0.5),
			Dense(10)])
	model.compile('adadelta', loss='mse', metrics=['accuracy'])
	return model

if __name__ == "__main__":

	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("-e","--epochs", default=200, type=int)
	parser.add_argument("-b","--batch_size", default=128, type=int)
	parser.add_argument("-p","--path", default="D59.h5", type=str)
	parser.add_argument("-ny","--noise_y", default=0.3, type=float)
	parser.add_argument("-nx","--noise_sacler_x", default=0.5, type=float)
	args = parser.parse_args()

	print(f'loading model at {args.path} ...')
	try:
		d = keras.models.load_model(args.path)
	except:
		print('fail, creating new')
		d = new_D()
	else:
		print('success')
	
	print('training ...')
	x,y = NoizyData(y_scaler=args.noise_y, noise_scaler=args.noise_sacler_x).train()
	d.fit(x,y,epochs=args.epochs,batch_size=args.batch_size)

	print('saving ...')
	d.save(args.path)