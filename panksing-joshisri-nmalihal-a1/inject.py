import sys
import utils.file_utils as file_utils
import utils.inject_utils as inject_utils


if __name__ == '__main__':
    form_path = sys.argv[1]
    answers_to_inject_file_path = sys.argv[2]
    output_image_file_name = sys.argv[3]

    sheet = file_utils.load_image_gray(form_path)
    
    encoded_ans1, encoded_ans2, encoded_ans3 = inject_utils.read_answers(answers_to_inject_file_path)
    updated_sheet = inject_utils.inject(sheet, encoded_ans1, encoded_ans2, encoded_ans3)

    file_utils.save_as_image(updated_sheet, output_image_file_name)
