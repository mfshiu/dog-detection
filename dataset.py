import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.utils.data as Data
import torchvision
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader, Dataset
import glob
import numpy as np
import os
import torchvision.transforms as transforms
from PIL import Image
import warnings
warnings.simplefilter("ignore", UserWarning)


img_size = 128
class SiamDataset(Dataset):
    
    def __init__(self, mode = "training", dir = "./"):
        path = dir
        # We import the MNIST dataset that is pre formatted and kept as a csv file 
        # in which each row contains a single image flattened out to 784 pixels
        # so each row contains 784 entries
        # after the import we reshape the image in the format required by pytorch i.e. (C,H,W)
        filenames = []
        labels = []
        img = []
        test_img = []
        teest_labels = []
        self.mode = mode
        
        

        for id in range(1,20):
          temp = []
          test_temp = []
          if id < 10:
            files= glob.glob(os.path.join(path,"dog0"+str(id)+"*/dog*/*.bmp"))
          else:
            files = glob.glob(os.path.join(path,"dog"+str(id)+"*/dog*/*.bmp"))
          for filename in files:
            filenames.append(filename)
            temp.append(filename)
            labels.append(id)
            #print(id, filename)
          if mode == "training":
            temp = temp[:18]
            labels = labels[:18]
            test_temp = temp[18:]
            test_labels = labels[18:]
          
          else:
            temp = temp[18:]
            labels = labels[18:]
          

          #print(id, " length", len(temp))
          img.append(temp)
          test_img.append(test_temp)
        
        self.filenames = filenames
        self.labels = labels
        self.img = img
        self.test_img = test_img
        # training 時做 data augmentation
        self.transform = transforms.Compose([
            
            transforms.ToPILImage(),
            
            transforms.CenterCrop(400),
            transforms.RandomHorizontalFlip(), # 隨機將圖片水平翻轉
            transforms.RandomRotation(30), # 隨機旋轉圖片
            transforms.RandomResizedCrop(img_size, scale=(0.9, 1.0), ratio=(0.95, 1.3333333333333333), interpolation=2),

            transforms.ToTensor(), # 將圖片轉成 Tensor，並把數值 normalize 到 [0,1] (data normalization)
        ])
        self.test_transform = transforms.Compose([
            transforms.ToPILImage(),
            #
            transforms.CenterCrop(400),
            transforms.Compose([transforms.Scale((img_size,img_size))]),
            transforms.ToTensor(), # 將圖片轉成 Tensor，並把數值 normalize 到 [0,1] (data normalization)
        ])
    
    
    def __getitem__(self, idx):
   
        clas = np.random.randint(0,19)
        length = len(self.img[clas])
        im1, im2 = np.random.randint(0,length,2)
        if self.mode =="testing":
          while im1 == im2:
             im2 = np.random.randint(0,length)
        #print(im1, im2)

        
        
        if self.mode =="testing":
          img1 = self.test_transform(np.array(Image.open(self.img[clas][im1]).convert("RGB")))
          img2 = self.test_transform(np.array(Image.open(self.img[clas][im2]).convert("RGB")))
        else:
          img1 = self.transform(np.array(Image.open(self.img[clas][im1]).convert("RGB")))
          img2 = self.transform(np.array(Image.open(self.img[clas][im2]).convert("RGB")))
        
        img1 = torch.Tensor(np.reshape(img1,(3,img_size,img_size)) )
        img2 = torch.Tensor(np.reshape(img2,(3,img_size,img_size)) )
        y1 =torch.Tensor(np.ones(1,dtype=np.float32) )
                   
        
        # I create a negative pair with label of similarity 0
        
        len1 = len(self.img[clas])
        clas2 = np.random.randint(0,19)
        while clas2 == clas:
          clas2 = np.random.randint(0,19)
        
        len2 = len(self.img[clas2])
        
        im3 = np.random.randint(0,len1)
        im4 = np.random.randint(0,len2)
        if self.mode =="testing":
          img3 = self.test_transform(np.array(Image.open(self.img[clas][im1]).convert("RGB")))
          img4 = self.test_transform(np.array(Image.open(self.img[clas2][im4]).convert("RGB")))
        else:
          img3 = self.transform(np.array(Image.open(self.img[clas][im1]).convert("RGB")))
          img4 = self.transform(np.array(Image.open(self.img[clas2][im4]).convert("RGB")))
          
        img3 = torch.Tensor(np.reshape(img3,(3,img_size,img_size)))
        img4 = torch.Tensor(np.reshape(img4,(3,img_size,img_size)))
        y2 = torch.Tensor(np.zeros(1,dtype=np.float32))
        #print(y1, y2)
        return  img1, img2, y1, img3, img4, y2, clas,clas2
            
    def __len__(self):
        
        # here I gave a smaller length than the real dataset's length so that the training can be faster
        if self.mode == "training":
            return 200
        else:
            return 10
