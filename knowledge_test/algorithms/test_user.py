from Build_Graph_ver3 import Build_Graph

graph = Build_Graph(3)

graph.first_problem()

answer = []

answer.append(1)

next_prob = graph.whats_next(answer)

print("다음 문제 : ", next_prob)
print("correct : ", graph.correct_set)
print("wrong : ", graph.wrong_set)

answer.append(1)

next_prob = graph.whats_next(answer)

print("다음 문제 : ", next_prob)
print("correct : ", graph.correct_set)
print("wrong : ", graph.wrong_set)

answer.append(0)

next_prob = graph.whats_next(answer)

print("다음 문제 : ", next_prob)
print("correct : ", graph.correct_set)
print("wrong : ", graph.wrong_set)