import argparse
import os
import xml.etree.ElementTree as et
import tensorflow as tf
import numpy as np
from keras.utils.np_utils import to_categorical
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.applications import VGG16
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.preprocessing.image import load_img
from constants import RANDOM_STATE, IMAGE_SIZE, IMAGE_CHANNELS
from network.network_architecture import ClassifyingDetectionNetwork, NETWORKS, LOSS_FUNCTIONS, LOSS_WEIGHTS, \
    BOUNDARY_NETWORK_NAME, CLASSIFICATION_NETWORK_NAME

__root = os.path.abspath('..')

DEFAULT_OUTPUT_LOCATION: str = os.path.join(__root, 'models', 'phase1', 'checkpoint')
DEFAULT_INPUT_LOCATION: str = os.path.join(__root, 'data', 'kaggle', 'andrewmvd')
DEFAULT_EPOCHS: int = 10
DEFAULT_NETWORK: str = 'vgg16'
DEFAULT_DUPLICATE: bool = False

__parser = argparse.ArgumentParser()
__parser.add_argument('--output', default=DEFAULT_OUTPUT_LOCATION, type=str, help='The model output directory')
__parser.add_argument('--input', default=DEFAULT_INPUT_LOCATION, type=str, help='The dataset input directory')
__parser.add_argument('--network', default=DEFAULT_NETWORK, type=str, help='The network architecture to use for bootstrapping')
__parser.add_argument('--epochs', default=DEFAULT_EPOCHS, type=int, help='The number of iterations')
__parser.add_argument('--duplicate', default=DEFAULT_DUPLICATE, type=bool, help='Use duplicate images')

args = __parser.parse_args()

base_directory: str = os.path.abspath(args.input)
image_directory: str = os.path.join(base_directory, 'images')
annotation_directory: str = os.path.join(base_directory, 'annotations')

images = []
labels = []
boundaries = []

for index, file in enumerate(os.listdir(annotation_directory)):
    annotation = et.parse(os.path.join(annotation_directory, file)).getroot()

    filename: str = annotation.find('filename').text
    path: str = os.path.join(image_directory, filename)
    
    width: int = int(annotation.find('size/width').text)
    height: int = int(annotation.find('size/height').text)

    image = img_to_array(load_img(path, target_size=(IMAGE_SIZE, IMAGE_SIZE, IMAGE_CHANNELS))) / 255.0

    scaled_width: float = float(IMAGE_SIZE / width)
    scaled_height: float = float(IMAGE_SIZE / height)

    for boundary in annotation.iter('object'):
        label: str = boundary.find('name').text

        xmin = float(boundary.find('bndbox/xmin').text)
        ymin = float(boundary.find('bndbox/ymin').text)
        xmax = float(boundary.find('bndbox/xmax').text)
        ymax = float(boundary.find('bndbox/ymax').text)

        # scaling, normalisation, sigmoid & image duplication

        # point = (original * scale) / new
        scaled_xmin = (xmin * scaled_width) / IMAGE_SIZE
        scaled_ymin = (ymin * scaled_height) / IMAGE_SIZE
        scaled_xmax = (xmax * scaled_width) / IMAGE_SIZE
        scaled_ymax = (ymax * scaled_height) / IMAGE_SIZE

        coordinates = (scaled_xmin, scaled_ymin, scaled_xmax, scaled_ymax)

        images.append(image)
        labels.append(label)
        boundaries.append(coordinates)

        if not args.duplicate:
            break

images = np.asarray(images)
labels = np.asarray(labels)
boundaries = np.asarray(boundaries)
classes, totals = np.unique(labels, return_counts=True)

encoder = LabelEncoder()
labels = encoder.fit_transform(labels)
labels = to_categorical(labels)

# TODO: store as HD5 object..?

print(f'Images: {len(images)}, Labels: {len(labels)}, Boundaries: {len(boundaries)}, Classes: {dict(zip(classes, totals))}')
print(labels[0:3])
print(boundaries[0:3])

splits = train_test_split(images, labels, boundaries, test_size=0.2, random_state=RANDOM_STATE)

(train_images, test_images) = splits[0:2]
(train_labels, test_labels) = splits[2:4]
(train_boundaries, test_boundaries) = splits[4:6]

train_targets = {
    BOUNDARY_NETWORK_NAME: train_boundaries,
    CLASSIFICATION_NETWORK_NAME: train_labels
}

test_targets = {
    BOUNDARY_NETWORK_NAME: test_boundaries,
    CLASSIFICATION_NETWORK_NAME: test_labels
}

# TODO: validation

# TODO: after data preparation
architecture = ClassifyingDetectionNetwork(base=NETWORKS.get(args.network, VGG16), classes=len(classes))
model = architecture.compile(loss=LOSS_FUNCTIONS, weights=LOSS_WEIGHTS)
model.summary()

checkpoint = tf.keras.callbacks.ModelCheckpoint(
    filepath=args.output,
    monitor='val_loss',
    mode='auto',
    save_weights_only=False,
    save_best_only=True,
    verbose=1
)

history = model.fit(
    train_images,
    train_targets,
    validation_data=(test_images, test_targets),
    epochs=args.epochs,
    callbacks=[checkpoint],
    verbose=1
)
