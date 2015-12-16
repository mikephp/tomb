from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
import ymuser.controls as C
from django.http import JsonResponse

# Create your views here.

import json

wrong_signature = JsonResponse({'code': -1, 'msg': 'wrong signature'})

@csrf_exempt
def token_signin(request):
    body = request.body
    js = json.loads(body)
    if not C.verify_client_auth(js): return wrong_signature
    provider = js['provider']
    client_id = js['client_id']
    token = js['token']
    auth_data = C.request_auth_service(provider, client_id, token)
    user_id = C.get_user_id(auth_data)
    return JsonResponse({'code': 0, 'uid': user_id})

@csrf_exempt
def get_user_info(request):
    body = request.body
    js = json.loads(body)
    if not C.verify_client_auth(js): return wrong_signature
    uid = js['uid']
    info = C.get_user_info(uid)
    info['code'] = 0
    return JsonResponse(info)

@csrf_exempt
def set_user_info(request):
    body = request.body
    js = json.loads(body)
    if not C.verify_client_auth(js): return wrong_signature
    uid = js['uid']
    C.set_user_info(uid, js)
    return JsonResponse({'code': '0'})
