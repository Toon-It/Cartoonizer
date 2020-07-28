import os
import cv2
import numpy as np
import tensorflow as tf
import network
import guided_filter
from tqdm import tqdm
from flask import Flask, render_template, request

app = Flask(__name__)


def resize_crop(image):
    h, w, c = np.shape(image)
    if min(h, w) > 720:
        if h > w:
            h, w = int(720 * h / w), 720
        else:
            h, w = 720, int(720 * w / h)
    image = cv2.resize(image, (w, h), interpolation=cv2.INTER_AREA)
    h, w = (h // 8) * 8, (w // 8) * 8
    image = image[:h, :w, :]
    return image


def cartoonize(img_name, load_folder, save_folder, model_path):
    input_photo = tf.placeholder(tf.float32, [1, None, None, 3])
    network_out = network.unet_generator(input_photo)
    final_out = guided_filter.guided_filter(input_photo, network_out, r=1, eps=5e-3)

    all_vars = tf.trainable_variables()
    gene_vars = [var for var in all_vars if "generator" in var.name]
    saver = tf.train.Saver(var_list=gene_vars)

    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    sess = tf.Session(config=config)

    sess.run(tf.global_variables_initializer())
    saver.restore(sess, tf.train.latest_checkpoint(model_path))
    name_list = os.listdir(load_folder)
    load_path = os.path.join(load_folder, img_name)
    print(load_path)
    save_path = os.path.join(save_folder, img_name)
    image = cv2.imread(load_path)
    image = resize_crop(image)
    batch_image = image.astype(np.float32) / 127.5 - 1
    batch_image = np.expand_dims(batch_image, axis=0)
    output = sess.run(final_out, feed_dict={input_photo: batch_image})
    output = (np.squeeze(output) + 1) * 127.5
    output = np.clip(output, 0, 255).astype(np.uint8)
    cv2.imwrite(save_path, output)


model_path = "saved_models"
UPLOAD_FOLDER = "static/upload/"
save_folder = "static/cartoonized_images/"
if not os.path.exists(save_folder):
    os.mkdir(save_folder)


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index_toonit.html")

@app.route("/upload", methods=["POST"])
def upload():
    if request.method == "POST":
        image_file = request.files["image"]
        if image_file:
            print(image_file)
            image_location = os.path.join(UPLOAD_FOLDER, image_file.filename)
            color_location = os.path.join(save_folder, image_file.filename)
            image_file.save(image_location)
            img_name = image_file.filename
            cartoonize(img_name, UPLOAD_FOLDER, save_folder, model_path)
            return render_template("result.html", color_loc=img_name)


if __name__ == "__main__":
    app.run(debug=True)
    # img_name = 'Mallu.jpg'
    # cartoonize(img_name, UPLOAD_FOLDER, save_folder, model_path)