import tensorflow as tf
import cv2
from time import time
from tensorflow import keras
from tensorflow.keras.layers import Dense,Conv2D,Input,Flatten,MaxPooling2D
from tensorflow.keras import callbacks, optimizers,models,regularizers
from tensorflow.keras.preprocessing.image import load_img, ImageDataGenerator
import numpy as np,os,matplotlib.pyplot as plt,re,sys

model_paths=[".model_wts(10-30).hdf5",".model_wts(1-9).hdf5"]
mode=[models.load_model(path_) for path_ in model_paths]
cls_map_1={idx:int(j) for idx, j in enumerate(range(10,31,1))}
cls_map_2={idx:int(j) for idx, j in enumerate(range(1,10,1))}
cls_map=[cls_map_1,cls_map_2]
def img_data(path:str,batch:int,target_size:tuple,label_list:list)->object:
    """Args(
        Path : Image directory path,
        batch : batch_size,
        target_size : (height,width of images),
        label_list : list of class labels
        )\n
        returns a batchwise generator object"""
    gen_object=ImageDataGenerator(rescale=1./255)
    return gen_object.flow_from_directory(path,
                                            target_size=target_size,
                                            batch_size=batch,
                                            class_mode="sparse",
                                            classes=label_list,
                                            shuffle=True,
                                            color_mode='rgba'
                                        )
def train_model(Train_path:str,val_path:str,model_path:str)->None:
    """Args(
        Train_path : Directory path of training image set,
        val_path : Directory path of validation image set,
        model_path : path to saved model after training
        )\n
        Trains a convolutional neural network with regularization for classifying 1 and 2 digit(s) 36*60*4 captcha images,\
        model architecture comprises of 3 Convolutional layers with 3 corresponding pooling layersand 3 fully connected layers with no dropout (regularization was performed using kernel regularizers
        within the Conv layers)
        """

    #Train and validation image tensors
    Train=img_data(path=Train_path,batch=16,target_size=(36,60),label_list=os.listdir(Train_path))
    valid=img_data(path=val_path,batch=16,target_size=(36,60),label_list=os.listdir(val_path))
    
    output_nodes=len(os.listdir(Train_path))
    #stacked convolutional neural networks with pooling layers in between and fully connected layers
    #model.summary() for architecture description
    WEIGHT_DECAY=0.0001
    inputs=Input(shape=(36,60,4))
    x=Conv2D(32,3,activation='relu',kernel_regularizer=regularizers.l2(WEIGHT_DECAY))(inputs)
    pool=MaxPooling2D()(x)
    x=Conv2D(64,3,activation='relu',kernel_regularizer=regularizers.l2(WEIGHT_DECAY*3))(pool)
    pool_2=MaxPooling2D()(x)
    conv_3=Conv2D(128,3,activation='relu',kernel_regularizer=regularizers.l2(WEIGHT_DECAY*3))(pool_2)
    pool_3=MaxPooling2D()(conv_3)
    flat=Flatten()(pool_3)
    full_conn=Dense(512,activation='relu')(flat)
    full_conn_2=Dense(128,activation='relu')(full_conn)
    output=Dense(output_nodes,activation='softmax')(full_conn_2)
    model=keras.Model(inputs=inputs,outputs=output)
    #compiling the model
    #print(model.summary())
    LEARNING_RATE=0.001
    model.compile(
        loss=keras.losses.SparseCategoricalCrossentropy(),
        optimizer=optimizers.Adam(LEARNING_RATE),
        metrics=['accuracy']
    )
    #Save the best model based on minimum loss on the validation_data
    early_stopping=callbacks.EarlyStopping(monitor='val_loss',patience=5,mode='min')
    check_point=callbacks.ModelCheckpoint(model_path, save_best_only=True,monitor='val_accuracy', mode='max')
    model.fit(Train,epochs=10,verbose=1,validation_data=valid,callbacks=[early_stopping,check_point])
    return
def predict_img(x:np.ndarray,model,mapp:dict)->int:
    pred=model.predict(x).argmax()
    return mapp[pred]
def predict_labels(classes:list,model,test_path:str,class_map:dict)->None:
    """Args(
        classes : list of class labels,
        model : trained model weights,
        test_path : Path to test images directory,
        class_map : mapping of model outputs to class labels
        )
        Predicts the image class(digit within the image) using a trained neural network classifier"""
    for label in classes:
        images=os.listdir(test_path+"\\"+label)
        accuracy_score=np.zeros((len(images)))
        for i,image in enumerate(images):
            img_array=plt.imread(test_path+"\\"+label+"\\"+image)
            height, width, channels=img_array.shape
            img_array=img_array.reshape(1,height, width,channels)
            prediction=predict_img(img_array,model=model,mapp=class_map)
            if prediction==int(label):
                accuracy_score[i]=int(label)
            else:
                accuracy_score[i]=prediction
        acc_norm=np.where(accuracy_score==int(label),accuracy_score,0)
        accuracy_score_perc=np.count_nonzero(acc_norm)/acc_norm.shape[0]
        print(f"label ={label}, accuracy_score for class {label} ={accuracy_score_perc}, {accuracy_score}")
    return
def main(Train:bool=False,Test:bool=False,rename:bool=False)->None:
    """Main calling function"""
    #model weights file
    
    #Train set
    Train_1_path="Image_data\\Train\\2_digits"
    Train_2_path="Image_data\\Train\\1_digit"
    Training=[Train_1_path,Train_2_path]
    #Validation set
    valid_1_path="Image_data\\Valid\\2_digits"
    valid_2_path="Image_data\\Valid\\1_digit"
    Validation=[valid_1_path,valid_2_path]
    if Train:
        for i,mode_path in enumerate(model_paths):
            train_model(Training[i],Validation[i],mode_path)
    elif Test:
        #Test set
        test_1_path="Image_data\\Test\\2_digits"
        test_2_path="Image_data\\Test\\1_digit"
        test_set=[test_1_path,test_2_path]
        for i,mode_ in enumerate(mode):
            test=test_set[i]
            classes=os.listdir(test)
            #mapping model output to class labels
            cls_map={idx:int(j) for idx, j in enumerate(classes)}
            predict_labels(classes=classes,model=mode_,test_path=test,class_map=cls_map)
    
    return
if __name__=='__main__':
    main(Test=True)
    