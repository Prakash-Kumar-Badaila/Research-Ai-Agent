from django.shortcuts import render
# from .ai_agent import generate_response
from django.views.decorators.csrf import csrf_exempt



# Create your views here.
from django.http import StreamingHttpResponse
import time

@csrf_exempt
def ai_call(request):
    text = "Hello from Django streaming response"
    def generate ():
        for char in text:
            yield char
            time.sleep(0.1)
    return StreamingHttpResponse(generate(),content_type ="text/plain")

# @csrf_exempt
# def ai_call(request):
#     query = request.POST.get('query')

#     return StreamingHttpResponse(generate_response(query), content_type="text/plain")


