import os.path
import tensorflow as tf
from keras_preprocessing.image import ImageDataGenerator
from tensorflow import keras

RANDOM_STATE: int = 694_201_337
ACTIVATION_FN: str = 'relu'
OUTPUT_FN: str = 'sigmoid'  # softmax
LOSS_FN: str = 'binary_crossentropy'  # sparse_categorical_crossentropy
CLASSES: int = 1
CLASS_MODE: str = 'binary'


class MaskDetectorProvider:
    @staticmethod
    def version() -> str:
        return f'Mask detector: TensorFlow - {tf.__version__}, Keras: {keras.__version__}, GPU(s): {tf.config.list_physical_devices("GPU")}'


def create_model(size: int, channels: int):
    model = tf.keras.models.Sequential([
        # CONV-POOL
        tf.keras.layers.Conv2D(64, (3, 3), activation=ACTIVATION_FN, input_shape=(size, size, channels)),
        tf.keras.layers.MaxPool2D((2, 2)),
        # CONV-POOL
        tf.keras.layers.Conv2D(64, (3, 3), activation=ACTIVATION_FN),
        tf.keras.layers.MaxPool2D((2, 2)),
        # CONV-POOL
        tf.keras.layers.Conv2D(128, (3, 3), activation=ACTIVATION_FN),
        tf.keras.layers.MaxPool2D((2, 2)),
        # CONV-POOL
        tf.keras.layers.Conv2D(128, (3, 3), activation=ACTIVATION_FN),
        tf.keras.layers.MaxPool2D((2, 2)),
        # DROPOUT
        tf.keras.layers.Dropout(rate=0.5, seed=RANDOM_STATE),
        # FC
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(512, activation=ACTIVATION_FN),
        tf.keras.layers.Dense(CLASSES, activation=OUTPUT_FN)
    ])
    return model


def prepare(model):
    model.compile(
        optimizer='adam',
        loss=LOSS_FN,
        metrics=['accuracy']
    )
    model.summary()
    return model


training_provider = ImageDataGenerator(
    rescale=1./255,
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)
testing_provider = ImageDataGenerator(rescale=1./255)


def training_generator(directory: str, size: int, channels: int):
    color_mode: str = 'grayscale' if channels == 1 else 'rgb'
    return testing_provider.flow_from_directory(
        directory=directory,
        color_mode=color_mode,
        target_size=(size, size),
        seed=RANDOM_STATE,
        class_mode=CLASS_MODE
    )


def testing_generator(directory: str, size: int, channels: int):
    color_mode: str = 'grayscale' if channels == 1 else 'rgb'
    return testing_provider.flow_from_directory(
        directory=directory,
        color_mode=color_mode,
        target_size=(size, size),
        seed=RANDOM_STATE,
        class_mode=CLASS_MODE
    )


def build(path: str, size: int, channels: int, training, validation=None):
    model = tf.keras.models.load_model(path)

    if model is not None:
        return prepare(model)

    checkpoint = tf.keras.callbacks.ModelCheckpoint(
        filepath=path,
        monitor='val_loss',
        mode='auto',
        save_weights_only=False,
        save_best_only=True,
        verbose=1
    )

    model = prepare(create_model(size, channels))

    model.fit(
        training,
        validation_data=validation,
        epochs=10,
        validation_steps=10,
        verbose=2,
        callbacks=[checkpoint]
    )

    return model
