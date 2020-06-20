import os
from PIL import Image
import secrets
from stack import app


# post image resizing and optimization
def post_img(form_image):
    random_hex = secrets.token_hex(4)
    _, f_ext = os.path.splitext(form_image.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/posts', picture_fn)

    output_size = (400, 400)
    i = Image.open(form_image)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn
