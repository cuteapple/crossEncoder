import keras
import numpy as np
import D
from Dataset import ZData as z
import Dataset

from keras.models import Sequential,Model
from keras.layers import Dense,Reshape,UpSampling2D,Conv2D,Activation,Input,Concatenate
from keras_contrib.layers.normalization import InstanceNormalization

def new_G(nclass,nnoise):

	i_c = Input((nclass,),name='class')
	t1 = Dense(nclass,activation='relu')(i_c)
	i_n = Input((nnoise,),name='noise')
	t2 = Dense(nnoise,activation='relu')(i_n)
	i = Concatenate()([t1,t2])

	gen = Sequential(name='gen',
		layers=[
			Dense(128 * 7 * 7,input_shape=(nclass+nnoise,)),
			Activation("relu"),
			InstanceNormalization(),
			Reshape((7, 7, 128)),
			UpSampling2D(),
			Conv2D(128, kernel_size=3, padding="same"),
			Activation("relu"),
			InstanceNormalization(),
			Conv2D(128, kernel_size=3, padding="same"),
			Activation("relu"),
			InstanceNormalization(),
			UpSampling2D(),
			Conv2D(64, kernel_size=3, padding="same"),
			Activation("relu"),
			InstanceNormalization(),
			Conv2D(64, kernel_size=3, padding="same"),
			Activation("relu"),
			InstanceNormalization(),
			Conv2D(1, kernel_size=3, padding="same"),
			Activation("sigmoid")])
	
	return Model([i_c,i_n],gen(i),name='G')

if __name__ == '__main__':
	
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("-e","--epochs", default=100, type=int)
	parser.add_argument("-s","--steps", default=64, type=int)
	parser.add_argument("-b","--batch-size", default=128, type=int)
	parser.add_argument("-p","--path", default="G.h5", type=str)
	parser.add_argument("-dp","--discriminator-path", default="D.h5", type=str)
	args = parser.parse_args()
	print('args :',args)
	
	print('loading D ...')
	d = D.new_D()
	d.load_weights(args.discriminator_path)
	d.trainable = False

	print('loading G ...')
	g = new_G(Dataset.nclass,Dataset.nnoise)
	try: g.load_weights(args.path)
	except: print('failed')
	else: print('success')


	print('linking G & D ...')
	input = [Input((Dataset.nclass,)),Input((Dataset.nnoise,))]
	m = Model(input, d(g(input)))
	m.compile(optimizer='adadelta',loss='mse',metrics=['accuracy'])

	print('training ...')
	#m.fit_generator(z(args.batch_size),
	#	steps_per_epoch = args.steps,
	#	epochs=args.epochs)

	print('saving ...')
	g.save_weights(args.path)