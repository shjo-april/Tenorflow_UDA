import cv2
import glob
import pickle

import numpy as np

def log_print(string, log_path = './log.txt'):
    print(string)
    
    f = open(log_path, 'a+')
    f.write(string + '\n')
    f.close()
    
def cosine_learning_schedule(st_lr, warmup_lr, end_lr, warmup_iteration, max_iteration, alpha):
    learning_rate_list = []
    decay_iteration = max_iteration - warmup_iteration
    t_warmup_lr = (warmup_lr - st_lr) / warmup_iteration
    
    for t in range(1, warmup_iteration + 1):
        learning_rate_list.append(st_lr + t * t_warmup_lr)
    
    for t in range(1, decay_iteration + 1):
        cosine_decay = 0.5 * (1 + np.cos(np.pi * t / decay_iteration))
        cosine_decay = (1 - alpha) * cosine_decay + alpha
        learning_rate_list.append(cosine_decay * warmup_lr)

    return learning_rate_list

def get_data(file):
    with open(file, 'rb') as fo:
        data = pickle.load(fo, encoding='bytes')
    return data

def one_hot(label, classes):
    v = np.zeros((classes), dtype = np.float32)
    v[label] = 1.
    return v

def get_dataset(dataset_dir, n_label, augment = None):
    train_dic = {}
    test_dataset = []

    n_label_per_class = n_label // 10

    #########################################################
    # train 
    #########################################################
    for file_path in glob.glob(dataset_dir + "data_batch_*"):
        data = get_data(file_path)
        data_length = len(data[b'filenames'])
        
        for i in range(data_length):
            label = int(data[b'labels'][i])
            image_data = data[b'data'][i]

            channel_size = 32 * 32        

            r = image_data[:channel_size]
            g = image_data[channel_size : channel_size * 2]
            b = image_data[channel_size * 2 : ]

            r = r.reshape((32, 32)).astype(np.uint8)
            g = g.reshape((32, 32)).astype(np.uint8)
            b = b.reshape((32, 32)).astype(np.uint8)

            image = cv2.merge((b, g, r))
            
            try:
                train_dic[label].append(image)
            except KeyError:
                train_dic[label] = []
                train_dic[label].append(image)

    #########################################################
    # test 
    #########################################################
    data = get_data(dataset_dir + 'test_batch')
    data_length = len(data[b'filenames'])
    
    for i in range(data_length):
        label = int(data[b'labels'][i])
        image_data = data[b'data'][i]

        channel_size = 32 * 32        
        
        r = image_data[:channel_size]
        g = image_data[channel_size : channel_size * 2]
        b = image_data[channel_size * 2 : ]

        r = r.reshape((32, 32)).astype(np.uint8)
        g = g.reshape((32, 32)).astype(np.uint8)
        b = b.reshape((32, 32)).astype(np.uint8)

        image = cv2.merge((b, g, r))
        test_dataset.append([image, one_hot(label, 10)])

    #########################################################
    # semi supervised learning (labeled / unlabeled) 
    #########################################################
    labeled_data = []
    unlabeled_image_data = []
    
    for class_index in range(10):
        images = np.asarray(train_dic[class_index], dtype = np.uint8)
        
        np.random.shuffle(images)
        
        label = one_hot(class_index, 10)

        for image in images[:n_label_per_class]:
            labeled_data.append([image, label])
        
        for image in images[n_label_per_class:]:
            unlabeled_image_data.append(image)
            # if augment is not None:
            #     u_image = image.copy()
            #     ua_image = augment(image.copy())

            #     unlabeled_image_data.append([u_image, ua_image])
            # else:
            #     unlabeled_image_data.append(image)
    
    return labeled_data, unlabeled_image_data, test_dataset

def get_dataset_fully_supervised(dataset_dir):
    train_dataset = []
    test_dataset = []
    
    #########################################################
    # train 
    #########################################################
    for file_path in glob.glob(dataset_dir + "data_batch_*"):
        data = get_data(file_path)
        data_length = len(data[b'filenames'])
        
        for i in range(data_length):
            label = int(data[b'labels'][i])
            image_data = data[b'data'][i]

            channel_size = 32 * 32        

            r = image_data[:channel_size]
            g = image_data[channel_size : channel_size * 2]
            b = image_data[channel_size * 2 : ]

            r = r.reshape((32, 32)).astype(np.uint8)
            g = g.reshape((32, 32)).astype(np.uint8)
            b = b.reshape((32, 32)).astype(np.uint8)

            image = cv2.merge((b, g, r))
            train_dataset.append([image, one_hot(label, 10)])
    
    #########################################################
    # test 
    #########################################################
    data = get_data(dataset_dir + 'test_batch')
    data_length = len(data[b'filenames'])
    
    for i in range(data_length):
        label = int(data[b'labels'][i])
        image_data = data[b'data'][i]

        channel_size = 32 * 32        

        r = image_data[:channel_size]
        g = image_data[channel_size : channel_size * 2]
        b = image_data[channel_size * 2 : ]

        r = r.reshape((32, 32)).astype(np.uint8)
        g = g.reshape((32, 32)).astype(np.uint8)
        b = b.reshape((32, 32)).astype(np.uint8)

        image = cv2.merge((b, g, r))
        test_dataset.append([image, one_hot(label, 10)])

    return train_dataset, test_dataset
