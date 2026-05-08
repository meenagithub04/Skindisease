import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import DenseNet121
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from sklearn.utils.class_weight import compute_class_weight
import numpy as np
import os
import json

# ---------------- PATHS ----------------
TRAIN_PATH = "dataset/SkinDisease/train"
TEST_PATH = "dataset/SkinDisease/test"
MODEL_DIR = "model"

os.makedirs(MODEL_DIR, exist_ok=True)

# ---------------- SETTINGS ----------------
IMG_SIZE = (224,224)
BATCH_SIZE = 32
EPOCHS = 40

# ---------------- DATA AUGMENTATION ----------------
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=30,
    zoom_range=0.3,
    horizontal_flip=True,
    vertical_flip=True,
    width_shift_range=0.1,
    height_shift_range=0.1,
    brightness_range=[0.7,1.3],
    fill_mode="nearest"
)

test_datagen = ImageDataGenerator(rescale=1./255)

# ---------------- LOAD DATA ----------------
train_data = train_datagen.flow_from_directory(
    TRAIN_PATH,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical"
)

val_data = test_datagen.flow_from_directory(
    TEST_PATH,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical"
)

print("Classes:", train_data.class_indices)

NUM_CLASSES = train_data.num_classes

# ---------------- CLASS WEIGHTS ----------------
labels = train_data.classes

class_weights = compute_class_weight(
    class_weight="balanced",
    classes=np.unique(labels),
    y=labels
)

class_weights = dict(enumerate(class_weights))

# ---------------- BASE MODEL ----------------
base_model = DenseNet121(
    input_shape=(224,224,3),
    include_top=False,
    weights="imagenet"
)

# Freeze most layers
for layer in base_model.layers[:-30]:
    layer.trainable = False

for layer in base_model.layers[-30:]:
    layer.trainable = True

# ---------------- CLASSIFIER ----------------
x = base_model.output
x = layers.GlobalAveragePooling2D()(x)

x = layers.BatchNormalization()(x)

x = layers.Dense(512, activation="relu")(x)
x = layers.Dropout(0.5)(x)

x = layers.Dense(256, activation="relu")(x)
x = layers.Dropout(0.3)(x)

output = layers.Dense(NUM_CLASSES, activation="softmax")(x)

model = models.Model(inputs=base_model.input, outputs=output)

# ---------------- COMPILE ----------------
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# ---------------- CALLBACKS ----------------
early_stop = EarlyStopping(
    monitor="val_loss",
    patience=7,
    restore_best_weights=True
)

reduce_lr = ReduceLROnPlateau(
    monitor="val_loss",
    factor=0.3,
    patience=3,
    verbose=1
)

checkpoint = ModelCheckpoint(
    filepath=os.path.join(MODEL_DIR,"best_skin_model.keras"),
    monitor="val_accuracy",
    save_best_only=True,
    verbose=1
)

# ---------------- TRAIN ----------------
print("🚀 Training Model...")

model.fit(
    train_data,
    validation_data=val_data,
    epochs=EPOCHS,
    callbacks=[early_stop, reduce_lr, checkpoint],
    class_weight=class_weights
)

# ---------------- SAVE MODEL ----------------
model.save(os.path.join(MODEL_DIR,"skin_model.keras"))

labels = train_data.class_indices
labels = {str(v):k for k,v in labels.items()}

with open(os.path.join(MODEL_DIR,"human_labels.json"),"w") as f:
    json.dump(labels,f,indent=4)

print("✅ Training Completed Successfully")