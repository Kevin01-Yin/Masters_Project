import numpy as np
import keras
from keras.layers import Dense, Dropout, Flatten, InputLayer
from keras.preprocessing.image import ImageDataGenerator
from keras.models import load_model
from keras.models import Sequential
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
import keras.optimizers 
from model_utils import save_training_graph, plot_confusion_matrix, vis_activation
from sklearn.metrics import classification_report, confusion_matrix
from keras.applications.vgg16 import preprocess_input

base_model = load_model('All Layers Trainable/best_weights_model.hdf5')
base_model.layers.pop()

model = Sequential()
model.add(InputLayer((224, 224, 3)))
for layer in base_model.layers:
    model.add(layer)
model.add(Flatten(input_shape=base_model.output_shape[1:]))
#top_model.add(Dense(1024,activation='relu'))
#top_model.add(Dropout(.50))
#model.add(Dense(512,activation='relu'))
model.add(Dropout(.25))

model.add(Dense(2,activation='softmax')) #final layer with softmax activation
print(model.summary())

train_datagen=ImageDataGenerator(
    preprocessing_function=preprocess_input,
    shear_range=0.2,
    zoom_range=0.2,
    rotation_range=20,
    horizontal_flip=True,
    fill_mode='nearest')

valid_datagen=ImageDataGenerator(
        preprocessing_function=preprocess_input)

train_path = 'E:/Master Project/new_xray_datasplit/train' 
valid_path = 'E:/Master Project/new_xray_datasplit/val' 
test_path = 'E:/Master Project/new_xray_datasplit/test' 

train_generator = train_datagen.flow_from_directory(train_path,
                                                 target_size=(224,224),
                                                 color_mode='rgb',
                                                 batch_size=10,
                                                 class_mode='categorical',
                                                 shuffle=True)

valid_gen = valid_datagen.flow_from_directory(valid_path,
                                            target_size=(224,224),
                                            color_mode = "rgb",
                                            class_mode="categorical",
                                            batch_size=10)

test_gen = valid_datagen.flow_from_directory(test_path,
                                            target_size=(224,224),
                                            color_mode = "rgb",
                                            class_mode="categorical",
                                            batch_size=1,
                                            shuffle=False)

# loss function will be categorical cross entropy
# evaluation metric will be accuracy
sgd = keras.optimizers.SGD()
adam = keras.optimizers.Adam(lr=.00001)
model.compile(optimizer=adam,loss='categorical_crossentropy',metrics=['accuracy'])

learning_rate_reduction = ReduceLROnPlateau(monitor='val_acc', 
                                            patience=3, 
                                            verbose=1, 
                                            factor=0.5, 
                                            min_lr=0.00001)

early_stop = keras.callbacks.EarlyStopping(monitor='val_loss',
                              min_delta=0,
                              patience=4,
                              verbose=0, mode='auto')

checkpointer = ModelCheckpoint(filepath="best_weights_model.hdf5", 
                               monitor = 'val_acc',
                               verbose=1, 
                               save_best_only=True)

step_size_train=train_generator.n//train_generator.batch_size
step_size_val=valid_gen.n//valid_gen.batch_size

history = model.fit_generator(generator=train_generator,
                   steps_per_epoch=step_size_train,
                   callbacks=[checkpointer,learning_rate_reduction,early_stop],
                   validation_data=valid_gen,
                   validation_steps=step_size_val,
                   epochs=15)

#model = load_model('best_weights_model.hdf5')
scores = model.evaluate_generator(generator=test_gen,steps=test_gen.n//test_gen.batch_size)
print(str(scores[0]), str(scores[1]))

Y_pred = model.predict_generator(test_gen,test_gen.n//test_gen.batch_size)
y_pred = np.argmax(Y_pred, axis=1)
print('Confusion Matrix')
confusion_mtx=confusion_matrix(test_gen.classes, y_pred)
print(confusion_mtx)
plot_confusion_matrix(confusion_mtx, classes = range(2))

print('Classification Report')
target_names = ['N','P']
print(classification_report(test_gen.classes, y_pred,target_names=target_names))

save_training_graph(history, 'With HAM Weights Training Accuracy')

img_path = 'E:/Master Project/new_xray_datasplit/test/NORMAL/IM-0023-0001.jpeg'
vis_activation(model, img_path)


