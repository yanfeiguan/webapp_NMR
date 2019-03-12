from django.shortcuts import render
from django.http import JsonResponse
import uuid
import redis
import json
redis_client = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)


# Create your views here.

def index(request):
    return render(request, "example/index.html", {})


def longtask(request):
    print("你想让我做一个很长的任务啊")
    task_id = uuid.uuid4().hex
    print("我先创建一个任务id: " + task_id)
    print("把任务详情放进入详情")
    detail_key = "task_detail_{}".format(task_id)
    redis_client.set(detail_key, json.dumps({
        "time": 2,
        "result": 11,
    }))
    print("然后把任务放入任务队列")
    redis_client.rpush("task_queue", task_id)
    return render(request, "example/running.html", {"taskid": task_id})

def check(request):
    task_id = request.GET["taskid"]
    print("我帮你看看任务情况哈", task_id)
    result_key = "task_result_{}".format(task_id)
    result = redis_client.get(result_key)
    if result:
        return JsonResponse({"result": result})
    else:
        return JsonResponse({})
