import os
import cv2
import numpy as np
import tensorflow as tf
import network
import guided_filter
import uuid
from flask import Flask, render_template, request, flash, redirect, session

app = Flask(__name__)
app.secret_key = "super secret key"


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
    print(save_path)
    image = cv2.imread(load_path)
    image = resize_crop(image)
    batch_image = image.astype(np.float32) / 127.5 - 1
    batch_image = np.expand_dims(batch_image, axis=0)
    output = sess.run(final_out, feed_dict={input_photo: batch_image})
    output = (np.squeeze(output) + 1) * 127.5
    output = np.clip(output, 0, 255).astype(np.uint8)
    # adding watermark to image
    # logo = cv2.imread('images/pyimage.png')
    # (wH, wW) = logo.shape[:2]
    # (h, w) = output.shape[:2]

    # # output = np.dstack([output, np.ones((h, w), dtype="uint8") * 255])
    # # overlay = np.zeros((h, w, 3), dtype="uint8")
    # center_y = int(h / 2)
    # center_x = int(w / 2)
    # top_y = center_y - int(wH / 2)
    # left_x = center_x - int(wW / 2)
    # bottom_y = top_y + h
    # right_x = left_x + w

    # roi = output[top_y: bottom_y, left_x: right_x]

    # # overlay[h - wH - 10:h - 10, w - wW - 10:w - 10] = logo
    # # print(overlay.shape)
    # water_output = output.copy()
    # print(water_output.shape)
    # print(roi.shape)
    # result = cv2.addWeighted(roi, 0.25, water_output, 1.0, 0)
    # img[top_y: bottom_y, left_x: right_x] = result

    cv2.imwrite(save_path, output)


# create folder for Uploading and cartoonizing images
model_path = "saved_models"
UPLOAD_FOLDER = "static/upload/"
save_folder = "static/cartoonized_images/"
if not os.path.exists(save_folder):
    os.mkdir(UPLOAD_FOLDER)
    os.mkdir(save_folder)


ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg"])


def allowed_files(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index_toonit.html")


@app.route("/upload", methods=["POST"])
def upload():
    if request.method == "POST":
        # read the POST request input
        if "file" not in request.files:
            flash("No file part")
        image_file = request.files["image"]
        if image_file and allowed_files(image_file.filename):
            print(image_file.filename)
            extension = os.path.splitext(image_file.filename)[1]
            img_name = str(uuid.uuid4()) + extension

            image_file.save(os.path.join(UPLOAD_FOLDER, img_name))
            image_location = os.path.join(UPLOAD_FOLDER, img_name)
            color_location = os.path.join(save_folder, img_name)
            
            # pass hashed values
            cartoonize(img_name, UPLOAD_FOLDER, save_folder, model_path)
            return render_template("result.html", color_loc=img_name)
        else:
            flash("Allowed image types are -> png, jpg, jpeg, gif")
            return redirect(request.url)


if __name__ == "__main__":
    app.run(debug=True)
