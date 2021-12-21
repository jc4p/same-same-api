from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
import tensorflow as tf
from random import choice
import io
import glob
import requests

def load_image(image_path, image_size=(256, 256), preserve_aspect_ratio=True):
  """Loads and preprocesses images."""
  # Load and convert to float32 numpy array, add batch dimension, and normalize to range [0, 1].
  img = tf.io.decode_image(
      tf.io.read_file(image_path),
      channels=3, dtype=tf.float32)[tf.newaxis, ...]
  img = tf.image.resize(img, image_size, preserve_aspect_ratio=True)
  return img

app = FastAPI()

@app.get("/")
def read_root():
    return "Hello"

@app.post("/style/")
async def create_upload_file(file: UploadFile = File(...)):
    upload_image_body = await file.read()

    upload_image = tf.io.decode_image(upload_image_body, channels=3, dtype=tf.float32)[tf.newaxis, ...]
    upload_image = tf.image.resize(upload_image, (512, 512))

    style_options = glob.glob('./styles/*.jpg')
    style_image = load_image(choice(style_options))

    json_data = {
        'inputs': {
            'placeholder': upload_image.numpy().tolist(),
            'placeholder_1': style_image.numpy().tolist()
        }
    }

    endpoint = "http://localhost:8501/v1/models/styler:predict"
    response = requests.post(endpoint, json=json_data)

    output = response.json()['outputs'][0]

    output_image = tf.keras.utils.array_to_img(output)

    buf = io.BytesIO()
    output_image.save(buf, format='JPEG', quality=90)
    buf.seek(0)

    return StreamingResponse(buf, media_type='image/jpeg')
