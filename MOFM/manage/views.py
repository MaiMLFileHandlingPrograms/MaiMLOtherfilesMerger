###################################
##  views class
###################################
import os
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings




###############################################
##    class for URI  main menu
##     URL/top/  -->  top.html
###############################################
class MainMenu():
    ## メニュー画面を表示
    def displayTop(request):
        return render(request, 'top.html')
