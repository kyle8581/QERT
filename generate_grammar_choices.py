# import spacy
# import pyinflect
import random
import pandas as pd
import nltk

VBP = "VBP"
VBN = "VBN"
VBG = "VBG"
VBD = "VBD"
VBZ = "VBZ"
RBR = "RBR"
RB = "RB"
RBS = "RBS"
NN = "NN"
NNS = "NNS"
JJ = "JJ"
JJS = "JJS"
JJR = "JJR"
TO_VERB = "TO_VERB"

CIRCLED_NUMBER = {1: "①", 2: "②", 3: "③", 4: "④", 5: "⑤"}
determiner_transform_dict = {

    "this": ["these", "that", "those"],
    "these": ["this", "those","that"],
    "those":["that","this","these"],
    "another": ["one"],
    "some":["another"],

    }
pos_transform_dict = {
    VBP: [VBN, VBZ, VBD], 
    VBG : [TO_VERB, VBN],  
    VBN:[TO_VERB, VBG], 
    VBZ:[VBN, VBZ, VBD], 
    RB:[JJ], RBR:[JJR], 
    RBS:[JJS], NN:[NNS], 
    NNS:[NN]
    }

def get_paragraph_from_file(file_name, row_number):
    extension = file_name.split(".")[-1]
    if extension == "csv":
        file_df = pd.read_csv(file_name, encoding="utf-8")
        line = file_df["정답 text"][row_number]
    
    else:
        line = [p for p in open(file_name,"r", encoding="utf-8") ][row_number]
        
    lines = line.split(".")
    return lines

def get_pos_tag_sentences(lines): # lines : paragraph를 문장단위로 나눈 리스트
    pos_tag_sentences = []
    for l in lines:
        tokens = nltk.word_tokenize(l)
        pos_tag_sentences.append(nltk.pos_tag(tokens))
    return pos_tag_sentences

def get_possible_transform(pos_tag_list): # per line
    possible_transform = []
    for tag in pos_tag_list:
        word = tag[0]
        pos = tag[1]
        if pos == VBP:
            pass




        
# 1. 단수동사(VBP) -> 복수동사(VBZ) (현재)
# 2. 복수동사(VBZ) like -> 단수동사 likes
# 3. 수동태 (VBD + VBN) was killed -> 능동태 killed
# 4. 과거분사 (VBN) proven -> 현재분사(VBG) proving
# 5. 현재(VBP, VBZ) eat -> 과거() ate
# 6. 과거 was -> 현재 기본형 is
# 7. 지시어(JJ) this -> 다른 지시어(JJ) those
# 8. 부사(RB) -> 형용사(JJ)


# 그럼 우선 같이 dict 정해 같이 고민하고
# 그다음에 내가 문제 만드는 부분을 할게 여기서 return값을 src하고 target의 list로 만들테니까
# 너는 그거를 선지 만드는 함수에서 선지 generate하는거야 어때
# 너가 함수 만들어보다가 내가 어떤 형식으로 return 줬으면 좋겠느닞 말해주면 그거대로 만들게

# 그 문제 아래에 잇는 선지들은 내가 코드짤때 answers라고 할게

# choices_dict
# type 1)
# {1 : "ate", 2 : "kill",3: good,...}
# type 2)
# {"A": {"answer": "is", "wrong_answer": "was"},...}
def generate_answers(question_type, choices_dict):
    answers_list = []
    if question_type == 1:  # 1,2,3,4,5 중에 틀린거 하나
        for k, v in enumerate(choices_dict.items()):
            answer_str = ""
            answer_str += CIRCLED_NUMBER[v[0]]
            answer_str += " "
            answer_str += v[1]
            answers_list.append(answer_str)
        return answers_list

    else:  # ABC
        answer_ABC_list = [[], [], []]
        num_to_ABC = ["A", "B", "C"]
        tf_values = [[1, 1, 1], [1, 1, 0], [1, 0, 1], [1, 0, 0], [0, 1, 1]]
        random.shuffle(tf_values)
        # print(tf_values)
        for i in range(5):
            for j in range(3):
                if tf_values[i][j]:
                    answer_ABC_list[j].append(
                        choices_dict[num_to_ABC[j]]["answer"])
                else:
                    answer_ABC_list[j].append(
                        choices_dict[num_to_ABC[j]]["wrong_answer"])

        # print(answer_ABC_list)
        for i in range(5):
            answer_str = ""
            answer_str += CIRCLED_NUMBER[len(answers_list)+1]
            answer_str += " "
            answer_str += '{0: <12} ······ {1: ^12} ······ {2: >12}'.format(
                answer_ABC_list[0][i], answer_ABC_list[1][i], answer_ABC_list[2][i])
            answers_list.append(answer_str)
        return answers_list


if __name__ == "__main__":
    choices_dict_type2 = {"A": {"answer": "is", "wrong_answer": "was"}, "B": {
        "answer": "those", "wrong_answer": "this"}, "C": {"answer": "current", "wrong_answer": "currently"}}
    choices_dict_type1 = {1: "apple", 2: "banana",
                          3: "citrus", 4: "durain", 5: "elderberries"}
    answers = generate_answers(1, choices_dict_type1)
    for a in answers:
        print(a)
    answers = generate_answers(2, choices_dict_type2)
    for a in answers:
        print(a)


