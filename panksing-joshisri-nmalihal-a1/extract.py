import sys
import utils.file_utils as file_utils
import utils.extract_utils as extract_utils


if __name__ == '__main__':
    answer_sheet_path = sys.argv[1]
    extract_answer_to_path = sys.argv[2]

    sheet = file_utils.load_image_gray(answer_sheet_path)
    sheet = sheet.copy()
    for i in range(sheet.shape[0]):
        for j in range(sheet.shape[1]):
            if (sheet[i,j] < 125):
                sheet[i, j] = int(0)
            else:
                sheet[i, j] = int(255)

    extract_utils.extract_answers(sheet, extract_answer_to_path)
