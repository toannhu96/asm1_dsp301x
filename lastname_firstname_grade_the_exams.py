#!/usr/bin/env python

"""This is assignment 1 of DSP301x_1.2-A_VN. Program help teachers to score exams of students."""

__author__ = "Toàn Nhữ Đình"
__version__ = "1.0"
__email__ = "toanndxm00975@funix.edu.vn"


from typing import Tuple, Dict
import os
import re
import math
import pandas as pd
import numpy as np


script_dir = os.path.dirname(__file__)


def analyze_line(line: str) -> Tuple[bool, Dict[str, list[str]]]:
    """
    Check each data line is valid and return preprocessed data of student answers

    :param str line: a line of text file
    :returns: tuple (result1, result2) 
        - result1 is bool value to check if line is valid or not
        - result2 is dict contains student id and list items of student answers 
    """
    elem = line.split(",")
    if len(elem) != 26:
        print("Invalid line of data: does not contain exactly 26 values:\n" + line)
        return (False, None)
    if not re.match(r"^N[0-9]{8}", elem[0]):
        print("Invalid line of data: N# is invalid\n" + line)
        return (False, None)
    return (True, {"id": elem[0], "answers": elem[1:]})


def calculate_score(answer_keys:list[str], student_answers:list[str]) -> Tuple[int, Dict[str, int]]:
    """
    Calculate total score of student answers

    :param list[str] answer_keys: list items of true result
    :param list[str] student_answers: list items of student answers
    :returns: tuple (result1, result2)
        - result1 is total score of student test
        - result2 is dict contains detail score of each student answer
    """
    total_score = 0
    detail_score = {}
    for idx, student_answer in enumerate(student_answers):
        student_answer = student_answer.strip()
        key = str(idx)
        if not student_answer:
            detail_score[key] = 0
            continue
        if student_answer == answer_keys[idx]:
            detail_score[key] = 4
            total_score += 4
        else:
            detail_score[key] = -1
            total_score -= 1
    return (total_score, detail_score)


def save_result(filename: str, result: dict):
    with open("output/" + filename + "_grades.txt", "w") as f:
        for res in result:
            f.write(res["id"] + "," + str(res["score"]) + "\n")

            
# task 1 -> task 4
def process_exams():
    raw_filename = input("Enter a class file to grade (i.e. class1 for class1.txt): ")
    filename = raw_filename
    if not filename.endswith(".txt"):
        filename += ".txt"
    abs_file_path = os.path.join(script_dir, "data/", filename)

    try:
        f = open(abs_file_path, "r",encoding = "utf-8")
    except:
        print("File cannot be found.")
    else:
        print("Successfully opened " + filename)

        # init report value
        total_valid = 0
        total_invalid = 0
        total_student_high_scores = 0
        total_students = 0
        total_all_scores = 0
        avg_score = None
        highest_score = None
        lowest_score = None
        median_score = None

        # Task 2: preprocess and analyzing
        tests = []
        print("**** ANALYZING ****")
        for line in f:
            analyzed = analyze_line(line.strip())
            if analyzed[0]:
                total_valid += 1
                tests.append(analyzed[1])
            else:
                total_invalid += 1

        # Task 3
        # calculate score
        answer_keys = "B,A,D,D,C,B,D,A,C,C,D,B,A,B,A,C,B,D,A,C,A,A,B,D,D".split(",")
        for test in tests:
            score = calculate_score(answer_keys, test["answers"])
            test["score"] = score[0]
            test["detail_score"] = score[1]
        # report
        total_skip_question = {}
        total_incorrectly_answer = {}
        for test in tests:
            total_students += 1
            total_all_scores += test["score"]
            if test["score"] > 80:
                total_student_high_scores += 1
            if highest_score == None or highest_score < test["score"]: 
                highest_score = test["score"]
            if lowest_score == None or lowest_score > test["score"]:
                lowest_score = test["score"]
            for k, v in test["detail_score"].items():
                if v == 0:
                    total_skip_question[k] = total_skip_question.get(k, 0) + 1
                elif v == -1:
                    total_incorrectly_answer[k] = total_incorrectly_answer.get(k, 0) + 1
        avg_score = round(total_all_scores / total_students, 3)
        sort_scores = sorted(tests, key=lambda x: x["score"], reverse=False) # sort score ascending
        index = math.floor(len(sort_scores) / 2)
        if len(sort_scores) % 2 == 0:
            median_score = round((sort_scores[index]["score"] + sort_scores[index - 1]["score"]) / 2.0, 3)
        else:
            median_score = sort_scores[index]["score"]

        # skip question
        max_skip = 0
        for v in total_skip_question.values():
            if max_skip < v:
                max_skip = v
        most_skip_question_res = []
        for k, v in total_skip_question.items():
            if max_skip == v:
                most_skip_question_res.append("%s - %s - %s" % (str(int(k)+1), str(v), round(v / total_students, 2)))
        
        # incorrectly answer
        max_incorrectly = 0
        for v in total_incorrectly_answer.values():
            if max_incorrectly < v:
                max_incorrectly = v
        most_incorrectly_answer_res = []
        for k, v in total_incorrectly_answer.items():
            if max_incorrectly == v:
                most_incorrectly_answer_res.append("%s - %s - %s" % (str(int(k)+1), str(v), round(v / total_students, 2)))

        print("**** REPORT ****")
        print("Total valid lines of data: " + str(total_valid))
        print("Total invalid lines of data: " + str(total_invalid))
        print("Total student of high scores: " + str(total_student_high_scores))
        print("Mean (average) score: " + str(avg_score))
        print("Highest score: " + str(highest_score))
        print("Lowest score: " + str(lowest_score))
        print("Range of scores: " + str(highest_score - lowest_score))
        print("Median score: " + str(median_score))
        print("Question that most people skip: " + ", ".join(most_skip_question_res))
        print("Question that most people answer incorrectly: " + ", ".join(most_incorrectly_answer_res))

        # Task 4: save result
        save_result(raw_filename, tests)
    finally:
        if f is not None:
            f.close()

            
# task 5: do task 1 -> task 4 with numpy and pandas
def process_exams_with_pd():
    raw_filename = input("Enter a class file to grade (i.e. class1 for class1.txt): ")
    filename = raw_filename
    if not filename.endswith(".txt"):
        filename += ".txt"
    abs_file_path = os.path.join(script_dir, "data/", filename)

    # calculate total lines of file
    with open(abs_file_path, 'r') as f:
        len_csv = sum(1 for line in f)

    try:
        # load file
        df = pd.read_fwf(abs_file_path, header=None)
    except:
        print("File cannot be found.")
    else:
        print("Successfully opened " + filename)
        df = df[0].str.split(',', n=25, expand=True)

        # filter invalid lines in file
        invalid_length_df = df[(df.isna().any(axis=1)) | (df[25].str.split(",").str.len() > 1)]
        for index, row in invalid_length_df.iterrows():
            print("Invalid line of data: does not contain exactly 26 values:")
            print(row.to_frame().T.to_string(header=False))

        invalid_id_df = df[~df[0].str.contains(r"^N[0-9]{8}", regex=True, na=False)]
        for index, row in invalid_id_df.iterrows():
            print("Invalid line of data: N# is invalid")
            print(row.to_frame().T.to_string(header=False))

        valid_df = df[~(df.isin(invalid_length_df[0])) & ~(df.isin(invalid_id_df[0]))].dropna()

        # score exams
        answer_key = "B,A,D,D,C,B,D,A,C,C,D,B,A,B,A,C,B,D,A,C,A,A,B,D,D"
        list_answer_key = answer_key.split(",")
        for idx, answer in enumerate(list_answer_key):
            i = idx + 26
            valid_df[i] = np.where(valid_df[idx+1] == answer, 4, np.where(valid_df[idx+1] == "", 0, -1));      
        valid_df["total_score"] = valid_df.iloc[:, 26:51].sum(axis=1)

        # report
        total_students = valid_df.shape[0]
        print("Total valid lines of data: " + str(len_csv - len(invalid_length_df) - len(invalid_id_df)))
        print("Total invalid lines of data: " + str(len(invalid_length_df) + len(invalid_id_df)))
        print("Total student of high scores: " + str(valid_df[valid_df["total_score"] > 80].shape[0]))
        print("Mean (average) score: " + str(valid_df["total_score"].mean()))
        print("Highest score: " + str(valid_df["total_score"].max()))
        print("Lowest score: " + str(valid_df["total_score"].min()))
        print("Range of scores: " + str(valid_df["total_score"].max() - valid_df["total_score"].min()))
        print("Median score: " + str(valid_df["total_score"].median()))

        lists = np.array(np.where(valid_df.iloc[:, 26:51] == 0, 1, 0)).sum(axis=0)
        most_skip = np.argwhere(lists == np.amax(lists)).flatten().tolist()
        print("Question that most people skip: " + str(["%d - %d - %.2f" % (q+1, lists[q], round(lists[q]/total_students, 2)) for q in most_skip]))

        lists = np.array(np.where(valid_df.iloc[:, 26:51] == -1, 1, 0)).sum(axis=0)
        most_incorrect = np.argwhere(lists == np.amax(lists)).flatten().tolist()
        print("Question that most people answer incorrectly: " + str(["%d - %d - %.2f" % (q+1, lists[q], round(lists[q]/total_students, 2)) for q in most_incorrect]))

        # save result
        valid_df.iloc[:, [0,-1]].to_csv("output/" + raw_filename + "_grades.txt", header=None, index=False, sep=',', encoding='utf-8')
     

if __name__ == "__main__":
    process_exams()
    process_exams_with_pd()
