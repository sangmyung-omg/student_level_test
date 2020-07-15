from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .algorithms.Build_Graph_ver3 import Build_Graph
from .models import Problem
import json

def testpage(request):
    if request.method == "GET":
        correct_list = "[]"
        graph = Build_Graph('user')
        first_uk = graph.first_problem()
        problem = Problem.objects.filter(uk_tag = first_uk).first()
        return JsonResponse({'problem': problem.problem, 
                             'answer': problem.answer, 
                             'uk_tag': problem.uk_tag,
                             'pk': problem.pk,
                             'correct_list': correct_list}, json_dumps_params = {'ensure_ascii': True})
    elif request.method == "POST":
        request = json.loads(request.body)
        correct_list = request["correct_list"]
        response = request["answer"]
        
        if response is None:
            return JsonResponse({'problem': 'None'}, json_dumps_params = {'ensure_ascii': True})
        
        if correct_list == '[]':
            correct_list = []
        else:
            correct_list = correct_list.split(",")
            correct_list = list(map(int, correct_list))
        
        problem = Problem.objects.filter(pk = request["pk"]).first()
        
        if response == str(problem.answer):
            correct_list.append(1)
        else:
            correct_list.append(0)
        
        graph = Build_Graph('user')
        next_uk = graph.whats_next(correct_list)
        
        if type(next_uk) is tuple:
            return JsonResponse({'correct_set': next_uk[0], 
                                 'wrong_set': next_uk[1]}, json_dumps_params = {'ensure_ascii': True})
        
        get_object_or_404(Problem, uk_tag = next_uk)
        next_problem = Problem.objects.filter(uk_tag = next_uk).first()
        correct_list = ','.join(list(map(str, correct_list)))
        return JsonResponse({'problem': next_problem.problem,
                             'answer': next_problem.answer,
                             'uk_tag': next_problem.uk_tag,
                             'pk': next_problem.pk,
                             'correct_list': correct_list}, json_dumps_params = {'ensure_ascii': True})
    
    