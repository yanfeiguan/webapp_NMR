#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Xiang Wang @ 2019-03-12 20:57:56


import json
import redis
import time


redis_client = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)

print("这个是需要一直运行的程序, 作用就是从task_queque获取任务,然后执行")

def handle_task_id(task_id):
    task_detail_key = "task_detail_{}".format(task_id)
    detail = redis_client.get("task_detail_{}".format(task_id))
    print("任务详情", detail)
    data = json.loads(detail)
    need_sleep = int(data.get("time", "0"))
    time.sleep(need_sleep)
    result = data.get("result", "没有结果")
    task_result_key = "task_result_{}".format(task_id)
    print("把结果存入redis")
    redis_client.set(task_result_key, result)


while True:
    result = redis_client.blpop("task_queue", 3)
    print(result)
    if result:
        _, task_id = result
        print("有任务来啦, 任务id: ", task_id, time.time())
        try:
            handle_task_id(task_id)
            print("任务处理结束@", time.time())
        except Exception as e:
            print("报错警告")
            print(e)
    else:
        print("没有任务,请允许我休息0.3秒")
        time.sleep(0.3)
