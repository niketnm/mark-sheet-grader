from PIL import Image
import numpy as np

Y=5
X_OFFSET = 200
DELIMITER_LEN = 6
START_STOP_DELIMITER=7

decoding_dict = {
    8: "A",
    9: "B",
    10: "C",
    11: "D",
    12: "E",
    13: " x"
}


def extract_answers(img, extracted_answer_sheet_path):
    f = open(extracted_answer_sheet_path, 'w')

    ########################## FIRST LINE ###############################
    encoded_info = img[2100:2100+Y, X_OFFSET: img.shape[1]]

    ## remove start and stop delimiter (7+7+7)
    encoded_info = encoded_info[:10, 21:]
    decoder(f, encoded_info, 0)

    ######################### SECOND LINE ###############################
    encoded_info = img[2111:2111+Y, X_OFFSET: img.shape[1]]

    ## remove start and stop delimiter (7+7+7)
    encoded_info = encoded_info[:10, 21:]
    decoder(f, encoded_info, 29)

    ########################## THIRD LINE ###############################
    encoded_info = img[2122:2122+Y, X_OFFSET: img.shape[1]]

    ## remove start and stop delimiter (7+7+7)
    encoded_info = encoded_info[:10, 21:]
    decoder(f, encoded_info, 58)

    f.close()


def decoder(f, encoded_info, question_count = 0, ):
    ## Remove the delimiter that is always there before an answer segment
    encoded_info = encoded_info[:10, DELIMITER_LEN:]

    ## Condition to end a recursive function
    ## Every encoded line has START_STOP_DELIMITER at the start and end of it
    if (is_end_of_encoding(encoded_info)):
        return

    h, length = encoded_info.shape

    question_count = question_count + 1
    f.write(str(question_count) + ' ')

    ## First white box has number of ansers
    answer_count = 0
    for i in range(length):
        if (encoded_info[1, i] == 255 ):
            answer_count = answer_count + 1
        else:
            break

    ## we got the number of answer to look for. Remove that from the encoding
    encoded_info = encoded_info[:10, answer_count:]
    
    for i in range(int(answer_count / 3)):
        encoded_info = encoded_info[:10, DELIMITER_LEN:]
        h, length = encoded_info.shape

        white_pixel_count = 0
        for j in range(length):
            if (encoded_info[1, j] == 255 ):
                white_pixel_count = white_pixel_count + 1
            else:
                f.write(decoding_dict[white_pixel_count])
                encoded_info = encoded_info[:10, white_pixel_count:]
                break
    
    f.write('\n')
    decoder(f, encoded_info, question_count)            


def is_end_of_encoding(encoded_info):
    # Image.fromarray(np.uint8(encoded_info)).save('./patches/'+str(question_count) + '.png')
    h, length = encoded_info.shape

    white_count = 0
    black_count = 0
    for i in range(length):
        if (white_count < 7):
            if (encoded_info[1, i] == 255):
                white_count = white_count + 1
        elif (encoded_info[1, i] == 0):
            black_count = black_count + 1
        elif (white_count == 7 and black_count == 7):
            return True
        else:
            return False
