import pandas as pd
import numpy as np
import os

##################################################################
# UK간 관계는 상속 / 상하위 관계만 고려하여 graph 그림.

class Build_Graph():

    def __init__(self, user_id, last_response='', resource_path='./knowledge_test/resources/', filename = 'UK_relation_table.xlsx'):
        self.num_q = 1
        self.correct_set = []
        self.wrong_set = []
        self.user_id = user_id
        self.new_answer = last_response
        self.resource_path = resource_path
        # pythonanywhere.com에 올릴때 용도.
        # self.resource_path = '/home/hyperstudy/hyperstudy_knowledgelevelanalysis/hyperstudy/resources/'
        os.path.join(resource_path, filename)
        # 데이터 불러오기
        # self.data = pd.read_excel(filename)
        self.data = pd.read_excel(os.path.join(self.resource_path, filename))
        # print("Length of input data :", len(self.data))

        # 'UK이름'과 '연관 UK'에 있는 모든 UK 리스트     ( 해당 단원에서 설명하는 개념이 아닌 기초 개념도 포함. ex. 문자, 식, ... )
        self.uk1 = list(self.data['UK이름'].dropna())
        self.uk2 = list(set(self.data['관련 UK 이름'].dropna()))
        self.UK_all = list(set(self.uk1 + self.uk2))

        self.uk_score_dic = {}  # uk별 스코어를 부여하기 위한 딕셔너리
        for uk in self.UK_all:
            self.uk_score_dic[uk] = []

        # 관계 dictionary
        self.rel_dict = {}

        # dictionary에는 넣은 순서가 유지되지 않기 때문에 source가 되는 UK들을 list로 받고 target이 여러 개인 경우 list의 마지막 UK에 추가해준다. (해당 범위에 해당하는 UK들만)
        self.source_UK_list = []

        # relation dictionary 생성 : rel_dict
        self.data.apply(lambda x: self.relation(x), axis=1)

        # rel_dict를 참고하여 각 개념들의 level을 지정
        self.level_info = self.get_level()

        # rel_dict의 리스트들 순서 재정렬 (level 높은게 먼저 나오게) - 현재는 각 UK(key)마다 연관 UK 리스트(value)들이 각각 낮은 level부터 높은 level 순서로 정렬되어 있음.
        for k in self.rel_dict.keys():
            if type(self.rel_dict[k]) == list:
                self.rel_dict[k].reverse()

        # print("Relation Dictionary :", self.rel_dict)
        # print("Level Dictionary :", self.level_info)

        self.level_infos = []
        for i in range(len(self.level_info)):
            self.level_infos.append(self.level_info[i])
        # print(self.level_infos)

# 엑셀의 표에 나타난 관계를 그대로 dictionary 형태로 옮김
    def relation(self, row):
        # UK 이름이 있는 row이면
        if row['UK이름'] is not np.nan:
            # 관련 UK가 있는 row이면 (첫 관련 UK 일 것이다.)
            if row['관련 UK 이름'] is not None:
                # key : 'UK이름' / value : '관련 UK 이름' 으로 구성된 dictionary element 하나를 추가
                if row['관련 UK 이름'] is np.nan:
                    self.rel_dict[row['UK이름']] = row['관련 UK 이름']
                else:
                    self.rel_dict[row['UK이름']] = [row['관련 UK 이름']]
                self.source_UK_list.append(row['UK이름'])  # 딕셔너리는 키의 순서를 고려하지 않으므로, 리스트로 따로 UK들이 추가된 순서를 보관

            # 관련 UK가 공란이면 Nan이 추가됨

        # UK 이름이 없는 row
        else:
            # 관련 UK는 있는 row이면 (이미 관련 UK가 하나 이상 들어가 있는 상태일 것)
            if row['관련 UK 이름'] is not None:
                # 가장 최근에 추가한 UK에 관련 UK로 추가
                key = self.source_UK_list[-1]
                if self.rel_dict[key] is not None:  # 원래 해당 UK의 관련 UK element가 존재하면,
                    self.rel_dict[key].append(row['관련 UK 이름'])


# Root (level 0)부터 leaf node까지 찾아내려가는 함수
    def get_level(self):
        level = 0
        level_dict = {}
        # 처음 UK 리스트 (root, level=0)
        temp_UK = self.get_root()
        level_dict[level] = temp_UK

        # 풀 서치 시작
        while True:
            # 다음 level 서치
            level = level + 1
            # temp_UK 기반으로 서치하는 그 다음 레벨의 UK들 모으는 리스트
            temp_level = []
            # 현재 level의 UK를 target으로 갖는 source UK들이 그 다음 level이 될 것.
            for k, v in self.rel_dict.items():
                # if v is np.nan:
                #     continue
                # if type(v) == str:
                #     if v in temp_UK:
                #         temp_level.append(k)
                if type(v) == list:
                    for value in v:
                        if value in temp_UK:
                            temp_level.append(k)
                            # rel_dict에서 각 연관 UK 리스트를 레벨 낮은 UK -> 높은 UK 순으로 재정렬. (뒤에서 reverse해서 문제 물어볼 때 레벨 높은 것부터 물어볼 수 있게)
                            self.rel_dict[k].pop(self.rel_dict[k].index(value))
                            self.rel_dict[k].append(value)
                            break;

            # 관계 딕셔너리(rel_dict)에 이전 레벨의 UK를 target으로 하는 관계가 없다면, 이전 레벨 UK들은 다 leaf node일 것. (트리의 끝, loop 종료)
            if temp_level == []:
                break;

            # 뽑아낸 다음 level UK 후보들 중에 이전 level에 이미 level_dict에 포함된 UK들은 level_dict에서 지우고 이번 loop에서 새로 추가해준다.
            # (ex. level 1에서 level_dict에 넣은 '식의 값'이 level 2 서치할 때도 잡혔다. : '식의 값' UK는 level 1 -> level 2 이동)
            remove_list=[]
            for k, v in level_dict.items():
                for value in v:
                    if value in temp_level:
                        remove_list.append(value)
            for key, value in level_dict.items():
                for item in remove_list:
                    if item in value:
                        level_dict[key].pop(level_dict[key].index(item))
            # 이번 level의 리스트를 level_dict에 추가
            level_dict[level] = temp_level
            # 그 다음 서치는 이번 level에서 찾은 temp_level 리스트의 UK들을 바탕으로 그 다음 level 서치함.
            temp_UK = temp_level

        return level_dict


    def get_root(self):
        root_list = []
        val_list = []
        for key, value in self.rel_dict.items():
            # source만 있고 target은 없는 관계 : source가 최상위
            if value is np.nan:
                root_list.append(key)

            # 나머지 중에는 target에만 있고 source에는 없는 UK : 현재 범위 이전에 정의되어 새로 정의되지 않는 개념 (target이 최상위).
            elif type(value) == list:
                for v in value:
                    val_list.append(v)
            else:
                val_list.append(value)
        for i in list(set(val_list)):
            if i not in list(self.rel_dict.keys()):
                if i is not np.nan:
                    root_list.append(i)
        return root_list

###문제를 맞춘 경우 또는 맞췄다고 가정하는 경우 그와 연관된 uk들에게 스코어 1 부여
    def correct_give_score(self, uk):
        if uk not in self.level_infos[0]:
            for item in self.rel_dict[uk]:
                self.uk_score_dic[item].append(1)

###문제를 틀린 경우 그와 연관된 uk들에게 스코어 0 부여
    def wrong_give_score(self, uk):
        if uk not in self.level_infos[0]:
            for item in self.rel_dict[uk]:
                self.uk_score_dic[item].append(0)

###입력받은 uk에 대한 문제를 내고 그에 대한 정오답을 입력받아 그 결과에 따른 알고리즘을 수행함
    def q_interaction(self, uk, list):
        answer = list[self.num_q - 1]
        if answer == 1:   #
            self.num_q += 1
            if uk not in self.correct_set:       #이미 correct_set에 존재하는 경우 넘어가고, wrong_set에 존재하는 경우 wrong_set에서 삭제
                self.correct_set.append(uk)
            if uk in self.wrong_set:
                self.wrong_set.remove(uk)
            self.correct_give_score(uk)     #맞춘 경우의 스코어 부여 함수 호출

        elif answer == 0:     #
            self.num_q += 1
            if uk not in self.wrong_set:
                self.wrong_set.append(uk)
            if uk in self.correct_set:
                self.correct_set.remove(uk)
            self.wrong_give_score(uk)

# ###user_id를 입력받아 현재 형성된 uk 그래프를 바탕으로 순차적으로 문제를 제공하고 그 응답을 통해 user_graph를 형성하는 함수
# def build_user_graph(user_id):
#     num_q = 1   #문제 번호를 위한 인덱스
#     uk_score_dic = {}   #uk별 스코어를 부여하기 위한 딕셔너리
#     for uk in UK_all:
#         uk_score_dic[uk] = []
#     correct_set = []
#     wrong_set = []
#     for i in range(len(level_infos)):    #높은 레벨부터 순차적으로 문제를 제공
#         for item in level_infos[-i-1]:
#             if i != 0:   #리프 레벨이 아닌 경우에는 질문 전에 uk의 스코어를 따져봐야 함
#                 if uk_score_dic[item] != []:    #스코어가 메겨진 uk 일 경우 스코어를 계산
#                     score = uk_score_dic[item].count(1) / len(uk_score_dic[item])
#                     if score > 0.5:     #스코어가 0.5 초과인 경우 문제를 풀도록 하지 않고 맞은 것으로 간주함
#                         uk_score_dic = correct_give_score(item, uk_score_dic)
#                         if item not in correct_set:  # 이미 correct_set에 존재하는 경우 넘어가고, wrong_set에 존재하는 경우 wrong_set에서 삭제
#                             correct_set.append(item)
#                         if item in wrong_set:
#                             wrong_set.remove(item)
#                         continue
#                     else:       #스코어가 0.5 이하인 경우 문제 제공
#                         num_q, correct_set, wrong_set, uk_score_dic = q_interaction(item, num_q, correct_set, wrong_set, uk_score_dic)
#                 else:           #스코어가 메겨지지 않은 uk 일 경우 문제 제공
#                     num_q, correct_set, wrong_set, uk_score_dic = q_interaction(item, num_q, correct_set, wrong_set, uk_score_dic)
#             else:               #리프 레벨인 경우 문제 제공
#                 num_q, correct_set, wrong_set, uk_score_dic = q_interaction(item, num_q, correct_set, wrong_set, uk_score_dic)
#         print(3-i, "레벨", correct_set, wrong_set, uk_score_dic)
#     return user_id, correct_set, wrong_set

    def first_problem(self):
        #("문제 ", self.num_q, " : ", self.level_infos[-1][0])
        return self.level_infos[-1][0]

    def whats_next(self, list):
        self.num_q = 1  # 문제 번호를 위한 인덱스
        #if list가 o와 x를 제외한 다른 문자를 포함한 경우 중지시키고 에러 메시지 호출


        for i in range(len(self.level_infos)):  # 높은 레벨부터 순차적으로 문제를 제공
            for item in self.level_infos[-i - 1]:
                if self.num_q == len(list) + 1:
                    return item
                if i != 0:  # 리프 레벨이 아닌 경우에는 질문 전에 uk의 스코어를 따져봐야 함
                    if self.uk_score_dic[item] != []:  # 스코어가 메겨진 uk 일 경우 스코어를 계산
                        score = self.uk_score_dic[item].count(1) / len(self.uk_score_dic[item])
                        if score > 0.5:  # 스코어가 0.5 초과인 경우 문제를 풀도록 하지 않고 맞은 것으로 간주함
                            self.correct_give_score(item)
                            if item not in self.correct_set:  # 이미 correct_set에 존재하는 경우 넘어가고, wrong_set에 존재하는 경우 wrong_set에서 삭제
                                self.correct_set.append(item)
                            if item in self.wrong_set:
                                self.wrong_set.remove(item)
                            continue
                        else:  # 스코어가 0.5 이하인 경우 문제 제공
                            self.q_interaction(item, list)
                    else:  # 스코어가 메겨지지 않은 uk 일 경우 문제 제공
                        self.q_interaction(item, list)
                else:  # 리프 레벨인 경우 문제 제공
                    self.q_interaction(item, list)
        return self.correct_set, self.wrong_set

# # 데이터 불러오기
# data = pd.read_excel('UK_relation_table.xlsx')
# print("Length of input data :", len(data))
#
# # 'UK이름'과 '연관 UK'에 있는 모든 UK 리스트     ( 해당 단원에서 설명하는 개념이 아닌 기초 개념도 포함. ex. 문자, 식, ... )
# uk1 = list(data['UK이름'].dropna())
# uk2 = list(set(data['관련 UK 이름'].dropna()))
# UK_all = list(set(uk1 + uk2))
#
# # 관계 dictionary
# rel_dict = {}
#
# # dictionary에는 넣은 순서가 유지되지 않기 때문에 source가 되는 UK들을 list로 받고 target이 여러 개인 경우 list의 마지막 UK에 추가해준다. (해당 범위에 해당하는 UK들만)
# source_UK_list = []
#
# # relation dictionary 생성 : rel_dict
# data.apply(lambda x: relation(x, source_UK_list, rel_dict), axis=1)
#
# # rel_dict를 참고하여 각 개념들의 level을 지정
# level_info = get_level(rel_dict)
#
# # rel_dict의 리스트들 순서 재정렬 (level 높은게 먼저 나오게) - 현재는 각 UK(key)마다 연관 UK 리스트(value)들이 각각 낮은 level부터 높은 level 순서로 정렬되어 있음.
# for k in rel_dict.keys():
#     if type(rel_dict[k]) == list:
#         rel_dict[k].reverse()
#
# print("Relation Dictionary :", rel_dict)
# print("Level Dictionary :", level_info)
#
# level_infos = []
# for i in range(len(level_info)):
#     level_infos.append(level_info[i])
# print(level_infos)
#
# user_id, correct_set, wrong_set = build_user_graph(3)
# print(correct_set)
# print(wrong_set)