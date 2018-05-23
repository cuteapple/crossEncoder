import keras
import numpy as np


def z(batch_size,length):
	def g():
		answer = np.eye(10)[np.random.choice(10,batch_size)]
		z = np.random.normal(size=(batch_size,length))
		z[:,0:10] = answer
		z[:,10]=0
		answer = z[:,:11]
		return z,answer
	while True:
		yield g()

class ZData:
	''' Data for G '''
	def __init__(self, noise_length=10):
		self.candidate = np.eye(10)

		#shape of z = noise + class
		self.shape = noise_length+10, 
		
		#shape of D(G(z)) = noise + validation + class
		self.shape_dz = 10 + 1,

		self.noise_length = noise_length

	def batch(self,size):
		noise = np.random.normal(size=(size,self.noise_length))
		answer = np.eye(10)[np.random.choice(10,size)]
		
		z = np.zeros()

	def generator(batch_size):


class NoizyData:
	'''noizy mnist data'''
	def __init__(self, noise_sigma=1.0, noise_scaler=0.5,noise_area=(7,7)):
		noise_mean = 0.0

		ax = noise_area[0]
		ay = noise_area[1]
		(x,y),(tx,ty) = self.load_mnist()

		zeros = np.zeros((len(y),11))
		zeros[:,:10]=y
		y = zeros

		
		zeros = np.zeros((len(ty),11))
		zeros[:,:10]=ty
		ty = zeros


		for i in range(len(x)):
			noise = np.random.normal(noise_mean, noise_sigma, size=(ax,ay,1)) * noise_scaler
			dx = np.random.randint(28 - 1 - ax)
			dy = np.random.randint(28 - 1 - ay)
			x[i, dx:dx + ax, dy:dy + ay] += noise
					
		noisy_x = np.clip(x,0.0,1.0)
		
		noisy_y = np.copy(y)
		noisy_y[:,10] = 1


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
		x_train = NoizyData.transform(x_train)
		x_test = NoizyData.transform(x_test)
		y_train = keras.utils.to_categorical(y_train, 10)
		y_test = keras.utils.to_categorical(y_test, 10)
		return (x_train,y_train),(x_test,y_test)
