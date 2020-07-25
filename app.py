import os
import cv2
import numpy as np
import tensorflow as tf
import network
import guided_filter
from tqdm import tqdm
from flask import Flask, render_template, request


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
    save_path = os.path.join(save_folder, img_name)
    image = cv2.imread(load_path)
    image = resize_crop(image)
    batch_image = image.astype(np.float32) / 127.5 - 1
    batch_image = np.expand_dims(batch_image, axis=0)
    output = sess.run(final_out, feed_dict={input_photo: batch_image})
    output = (np.squeeze(output) + 1) * 127.5
    output = np.clip(output, 0, 255).astype(np.uint8)
    cv2.imwrite(save_path, output)


app = Flask(__name__)
model_path = "saved_models"
load_folder = "static/upload/"
img_name = "kurian_mecpodcast.jpg"
save_folder = "static/cartoonized_images/"
if not os.path.exists(save_folder):
    os.mkdir(save_folder)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        image_file = request.files["image"]
        if image_file:
            image_location = os.path.join(load_folder, image_file.filename)
            image_file.save(image_location)
            return render_template("toon_it.html", predictions=1)
    return render_template("toon_it.html", predictions=0)


if __name__ == "__main__":
    # cartoonize(img_name,load_folder, save_folder, model_path)
    app.run(port=1200, debug=True)
