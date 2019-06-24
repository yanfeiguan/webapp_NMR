#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Xiang Wang @ 2019-03-12 20:39:30


from django.urls import path
from . import views

app_name = "djangoexample"

urlpatterns = [
    path(r'index/', views.index, name="index"),
    path(r'longtask/', views.longtask, name="longtask"),
    path(r'check/', views.check, name="check"),
]
