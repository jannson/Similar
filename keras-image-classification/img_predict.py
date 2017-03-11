import os
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
from keras.models import Sequential
from keras.layers import Convolution2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
from scipy.misc import imresize

model = Sequential()
model.add(Convolution2D(32, 3, 3, input_shape=(3, 150, 150)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Convolution2D(32, 3, 3))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Convolution2D(64, 3, 3))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

# the model so far outputs 3D feature maps (height, width, features)
model.add(Flatten())  # this converts our 3D feature maps to 1D feature vectors
model.add(Dense(64))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(1))
model.add(Activation('sigmoid'))

model.compile(loss='binary_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])

model.load_weights('first_try_bk.h5')

basedir = "/opt/ssd1/var/taobao3"
img_width, img_height = 150, 150
img = load_img(os.path.join(basedir, "bingxiang/bingxiang.2.jpg"))
img = imresize(img, size=(img_height, img_width))
test_x = img_to_array(img).reshape(3, img_height, img_width)
print test_x.shape
test_x = test_x.reshape((1,) + test_x.shape)
print test_x.shape
prediction = model.predict(test_x)
print prediction[0][0]
y_classes = model.predict_classes(test_x)
print y_classes
