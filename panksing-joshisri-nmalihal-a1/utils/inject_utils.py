import re
import sys
import numpy as np
from PIL import Image


Y=5
X_OFFSET = 200
DELIMITER_LEN = 6
START_STOP_DELIMITER=7

encoding_dict = {
  "A": 8,
  "B": 9,
  "C": 10,
  "D": 11,
  "E": 12,
  "x": 13
}

black_7 = np.zeros((Y, START_STOP_DELIMITER))
white_7 = np.full((Y, START_STOP_DELIMITER), 255)

encoded_start_stop = np.hstack((white_7, black_7))
encoded_start_stop = np.hstack((encoded_start_stop, white_7))

# encoded_start_stop = np.full((Y, START_STOP_DELIMITER), 255)
encoded_delimiter = np.zeros((Y, DELIMITER_LEN))

def read_answers(answers_file):
    ## Initialize the start of encoding
    encoded_ans1 = np.hstack((encoded_start_stop, encoded_delimiter))
    encoded_ans2 = np.hstack((encoded_start_stop, encoded_delimiter))
    encoded_ans3 = np.hstack((encoded_start_stop, encoded_delimiter))

    with open(answers_file) as f:
        lines = f.readlines()
    
    i = 0
    k=0
    for line in lines:
        i = i + 1
        answer_arr = re.findall('([a-zA-Z]+)', line)
        if (i <= 29):
            encoded_ans1 = encode_answer(answer_arr, encoded_ans1)
        elif (i <= 58):
            encoded_ans2 = encode_answer(answer_arr, encoded_ans2)
        elif (i <= 85):
            encoded_ans3 = encode_answer(answer_arr, encoded_ans3)

    encoded_ans1 = np.hstack((encoded_ans1, encoded_start_stop))
    encoded_ans2 = np.hstack((encoded_ans2, encoded_start_stop))
    encoded_ans3 = np.hstack((encoded_ans3, encoded_start_stop))
    return encoded_ans1, encoded_ans2, encoded_ans3


def encode_answer(answers, encoded_ans):
    answer_arr = []
    for ans in answers:
        for c in split(ans):
            answer_arr.append(c)

    answer_count = len(answer_arr)

    encoded_ans_count = np.full((Y, answer_count*3), 255)

    encoded_ans = np.hstack((encoded_ans, encoded_ans_count))
    encoded_ans = np.hstack((encoded_ans, encoded_delimiter))

    for i in range(answer_count):
        answer = answer_arr[i]
        answer_e = np.full((Y, encoding_dict[answer]), 255)

        encoded_ans = np.hstack((encoded_ans, answer_e))
        encoded_ans = np.hstack((encoded_ans, encoded_delimiter))

    return encoded_ans


def inject(img, encoded_ans1, encoded_ans2, encoded_ans3):
    img = img.copy()
    img[2100:2100 + Y, X_OFFSET: X_OFFSET + encoded_ans1.shape[1]] = encoded_ans1
    img[2111:2111 + Y, X_OFFSET: X_OFFSET + encoded_ans2.shape[1]] = encoded_ans2
    img[2122:2122 + Y, X_OFFSET: X_OFFSET + encoded_ans3.shape[1]] = encoded_ans3
    return img


def split(word):
    return [char for char in word]
