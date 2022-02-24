import numpy as np
import matplotlib.pyplot as plt 
import matplotlib.image as mpimg
from PIL import Image

def load_image_gray(path):
    im = Image.open(path)
    gray_im = im.convert('L')
    return np.asanyarray(gray_im)

def save_as_image(image_data, output_image_file_name):
    Image.fromarray(np.uint8(image_data)).save(output_image_file_name)
