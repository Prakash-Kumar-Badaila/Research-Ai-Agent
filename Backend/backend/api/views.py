from django.shortcuts import render

# Create your views here.
from django.http import StreamingHttpResponse
import time
def stream_text (request):
    text = "Hello from Django streaming response"
    def generate ():
        for char in text:
            yield char
            time.sleep(0.1)
    return StreamingHttpResponse(generate(),content_type ="text/plain")