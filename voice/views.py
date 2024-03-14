# -*- coding: utf-8 -*-
import time
from django.shortcuts import render
from .models import *
from rest_framework.response import Response
#from .serializers import *
from rest_framework.views import APIView
#from lib import CorsHeaders 
from django.core.exceptions import ObjectDoesNotExist
import argparse
from obs import ObsClient
from argparse import RawTextHelpFormatter
# pylint: disable=redefined-outer-name, unused-argument
from pathlib import Path
import sys
from TTS1 import settings
#sys.path.append("/home/ubuntu/home/TTS")
from TTS.utils.synthesizer import Synthesizer
# Create your views here.
# import rest_framework_jwt.views
from rest_framework_jwt.views import ObtainJSONWebToken
from rest_framework_jwt.settings import api_settings
from .serializers import *
from django.http import QueryDict
import requests
from django.contrib.auth.hashers import make_password
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ViewSet
import json

tts_path = "./yourtts-pth-0515/model_file.pth"
tts_config_path = "./yourtts-pth-0515/config.json"
# 新版TTS要改成
# tts_path = ""
model_dir = "./yourtts-pth-0515"

speakers_file_path = None
language_ids_file_path = None
vocoder_path = None
vocoder_config_path = None
encoder_path = None
encoder_config_path = None
vc_path = None
vc_config_path = None
use_cuda = None
synthesizer = Synthesizer(
    tts_path,
    # model_dir,
    tts_config_path,
    # speakers_file_path,
    # language_ids_file_path,
    # vocoder_path,
    # vocoder_config_path,
    # encoder_path,
    # encoder_config_path,
    # vc_path,
    # vc_config_path,
    # use_cuda,
)


class OpenId:
    def __init__(self, jscode):
        self.url = 'https://api.weixin.qq.com/sns/jscode2session'
        self.app_id = 'wx338ae279b3379d6c'
        self.app_secret = 'f84b3d18e9676b608e7fd9e80e4d9c86'
        self.jscode = jscode

    def get_openid(self):
        url = self.url + "?appid=" + self.app_id + "&secret=" + self.app_secret + "&js_code=" + self.jscode + "&grant_type=authorization_code"
        res = requests.get(url)
        print(url)
        openid = res.json()['openid']
        session_key = res.json()['session_key']
        print(openid)
        return openid, session_key
    
def createUser(openid):
    list = QueryDict(mutable=True)
    list["username"] = openid
    password1 = openid
    list["phone"] = 12345
    list["password"] = password1
    list["repassword"] = password1
    #print(list)
    serializer = RegisterSerializers(data=list)
    serializer.is_valid(raise_exception=True)
    password = serializer.validated_data['password']
    password = make_password(password=password1)
    serializer.validated_data['password'] = password
    user = serializer.save()
    return openid,openid

class Login(ObtainJSONWebToken):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        print("Trying to login")
        code = request.data['code']
        print(code)
        try:
            openid, session_key = OpenId(code).get_openid()
            user = User.objects.filter(username=openid)

            if user.exists():
                print("find a user")
                user = User.objects.get(username=openid)
                username = openid
                password = openid
            else:
                print("no user has been found, creating now")
                username,password = createUser(openid)
            data1 = {
                'username':username,
                'password':password
            }
            jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER
            serializer = self.get_serializer(data=data1)
            serializer.is_valid(raise_exception=True)
            print("序列化对象：", serializer.validated_data)
            user1 = serializer.object.get('user')
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user1, request)
            serializer = UserSerializers(instance=user1, many=False)
            # print(serializer.data)
            a = serializer.data
            a.update(response_data)
            print(a)
            res = {
                "status": 0,
                "msg": 200,
                "data": a
            }
            print(res)
            return Response(res)
        except BaseException as e:
            print(e)
            print(e.__class__)

class UserViewSet(CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializers
    permission_classes = []
    authentication_classes=[]
    # @CorsHeaders.Headers
    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data['password']
        password = make_password(password=password)
        serializer.validated_data['password'] = password

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

class VoiceGenerateView(APIView):
    #authentication_classes = []
    #permission_classes = []
    #@CorsHeaders.Headers
    def post(self,request):
        voice = Voicefile()

        json_data = json.loads(request.body)
        # print(json_data)
        name = json_data['name']
        fileid = json_data['usersound_id']
        text = json_data['text']
        print(name,fileid,text)
        # name = request.POST.get('name')
        voice.name = name
        voice.user = request.user
        # fileid = request.POST.get('usersound_id')
        voicefile = UserSound.objects.get(id=fileid).sound_file
        filename = str(voicefile)
        # text = request.POST.get('text')

        ext = ''
        if voicefile:
            # 获取后缀名
            ext = filename.split('.')[-1]
            # 如果上传图片的后缀名不在配置的后缀名里返回格式不允许
            if ext not in settings.ALLOWED_VOICE_TYPE:
                return Response({
                    "status": 205,
                    "msg": "格式不允许",
                    "data": ''
                })
            else:
                path = f'./files/'
                try:
                    os.makedirs(path)
                except OSError as e:
                    print(e)
                # 这个地方要考虑到上传的name数据里也许没有后缀名的情况
                try:
                    file = open(os.path.join(path,name+'.'+ext), 'wb')
                except OSError as e:
                    print(e)

                print(os.path.join(path,name+'.'+ext))
                for chunk in voicefile.chunks():
                    try:
                    
                        file.write(chunk)
                    except OSError as e:
                        print(e)
                # for chunk in voicefile.chunks():
                #     file.write(chunk)
                
                file.close()
                path = path + name+'.'+ext
        
        if tts_path is not None:
            wav = synthesizer.tts(
                text,
                speaker_wav=path,
            )
        
        out_path = f"./wave/{filename}"
        print(" > Saving output to {}".format(out_path))
        synthesizer.save_wav(wav, out_path)
        ctime=str(int(time.time()))
        start = datetime.datetime.now()
        print(start)
        # obsClient = ObsClient(
        #                 access_key_id='ILH9LF6DUM0V7TACBI7P',  # 刚刚下载csv文件里面的Access Key Id
        #                 # 刚刚下载csv文件里面的Secret Access Key
        #                 secret_access_key='94SpA5u79LsnXOajCBR52NfWn2K1bUakYGwcqMdt',
        #                 server='https://obs.cn-southwest-2.myhuaweicloud.com'  # 这里的访问域名就是我们在桶的基本信息那里记下的东西
        #             )
        obsClient = ObsClient(
            access_key_id='PX91I6UXKYUFOTKE8BFK',  # 刚刚下载csv文件里面的Access Key Id 

            # 刚刚下载csv文件里面的Secret Access Key 
            secret_access_key='XoA4NB2b56ehNbaPkM31mCB5B6DlbK9TisA3mxG5',
            	
            # 
            server='https://obs.cn-north-4.myhuaweicloud.com'  # 这里的访问域名就是我们在桶的基本信息那里记下的东西
        )




        # 使用访问OBS
        # 调用putFile接口上传对象到桶内
        print(datetime)
        resp = obsClient.putFile('crowdofvoice', 'wav/'+request.user.username+'/'+ctime+'.'+ext, file_path=out_path)
        path = 'http://obs.crowdofvoice.top/' + 'wav/' +request.user.username+'/'+ctime+'.'+ext
        print(path)
        print(resp.status)
        if resp.status < 300:
            # 输出请求Id
            print('requestId:', resp.requestId)
        else:
            # 输出错误码
            print('errorCode:', resp.errorCode)
            # 输出错误信息
            print('errorMessage:', resp.errorMessage)
        # 关闭obsClient
        obsClient.close()
        end = datetime.datetime.now()
        print(end - start)  # 打印出使用的总时间
        voice.url = path
        print(voice)
        voice.save()
        return Response({
            'status': 201,
            'msg': '添加成功',
            "data": path
        })
class PersonalVoiceView(APIView):
    #authentication_classes = []
    #permission_classes = []
    def get(self, request):
        userid = request.user.id
        Voice = Voicefile.objects.filter(user=userid)
        serializer = VoiceSerializers(instance=Voice, many=True)
        res = {
            "status": 0,
            "msg": 200,
            "data": {"items": serializer.data}
        }
        return Response(res)
class PubVoiceView(APIView):
    #authentication_classes = []
    #permission_classes = []
    def get(self, request):
        Voice = Voicefile.objects.all()
        serializer = VoiceSerializers(instance=Voice, many=True)
        res = {
            "status": 0,
            "msg": 200,
            "data": {"items": serializer.data}
        }
        return Response(res)


class Usersound(ViewSet):

    def get(self, request):  ##查询用户音色

        Sound = UserSound.objects.filter(user=request.user)
        serializer = UsersoundSerializers(instance=Sound, many=True)

        return Response({
            "status": 0,
            "msg": 200,
            "data": {"items": serializer.data}
        })

    def upload(self, request):  ####post
        if request.method == 'POST' and request.FILES.getlist('sound'):
            # 获得后缀名
            ext = request.FILES['sound'].name.split('.')[-1]
            # 直接对文件重命名
            request.FILES['sound'].name = str(request.user.username) + str(int(time.time())) + '.' + ext

            user = request.user

            if user == "None":
                return Response({
                    "status": 0,
                    "msg": "don't have this person",
                    "data": "",
                })
            if not user.VIP:
                saved_audio_count = UserSound.objects.filter(user_id=user.id).count()
                if saved_audio_count >= 3:
                    return Response({
                        "status": 0,
                        "msg": "You have reached the maximum limit of saved audio files.",
                        "data": "",
                    })

            sounds = request.FILES.getlist('sound')
            name = request.POST.get("name")
            description = request.POST.get("description")

            print(sounds)
            for sound_file in sounds:

                user_sound = UserSound(user=user, sound_file=sound_file)
                print(user_sound.id)
                user_sound.save()

                text = " 欢迎使用众生语音个性化合成系统。"
                filename = str(user_sound.sound_file)
                
                path = "./media/" + filename
                print(path)
                if tts_path is not None:
                    wav = synthesizer.tts(
                        text,
                        speaker_wav=path,
                    )
                out_path = f"./wave/{filename}"
                print(" > Saving output to {}".format(out_path))
                synthesizer.save_wav(wav, out_path)

                # obsClient = ObsClient(
                #     access_key_id='ILH9LF6DUM0V7TACBI7P',  # 刚刚下载csv文件里面的Access Key Id
                #     # 刚刚下载csv文件里面的Secret Access Key
                #     secret_access_key='94SpA5u79LsnXOajCBR52NfWn2K1bUakYGwcqMdt',
                #     server='https://obs.cn-southwest-2.myhuaweicloud.com'  # 这里的访问域名就是我们在桶的基本信息那里记下的东西
                # )
                obsClient = ObsClient(
                    access_key_id='PX91I6UXKYUFOTKE8BFK',  # 刚刚下载csv文件里面的Access Key Id 

                    # 刚刚下载csv文件里面的Secret Access Key 
                    secret_access_key='XoA4NB2b56ehNbaPkM31mCB5B6DlbK9TisA3mxG5',
                        
                    # 
                    server='https://obs.cn-north-4.myhuaweicloud.com'  # 这里的访问域名就是我们在桶的基本信息那里记下的东西
                )

                # 使用访问OBS
                # 调用putFile接口上传对象到桶内
                print(datetime)
                resp = obsClient.putFile('crowdofvoice', 'wav/' + filename, file_path=out_path)
                path = 'http://obs.crowdofvoice.top/' + 'wav/' + filename
                print(path)
                print(resp.status)
                if resp.status < 300:
                    # 输出请求Id
                    print('requestId:', resp.requestId)
                else:
                    # 输出错误码
                    print('errorCode:', resp.errorCode)
                    # 输出错误信息
                    print('errorMessage:', resp.errorMessage)
                # 关闭obsClient
                obsClient.close()
                tim = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                UserSound.objects.filter(id=user_sound.id).update(path=path)
                UserSound.objects.filter(id=user_sound.id).update(time=tim)
                UserSound.objects.filter(id=user_sound.id).update(name=name)
                UserSound.objects.filter(id=user_sound.id).update(description=description)

            return Response({
                "status": 0,
                "msg": "upload successful",
                "data": {"name":name,
                        "description":description,
                         "time":tim,
                         "phone":user.phone,
                         "VIP":user.VIP,
                         "filename":filename,
                         "path":path,
                        },
            })
        return Response({
            "status": 0,
            "msg": "file wrong",
            "data": "",
        })

    def delete_data(self, request):

        nid = request.POST.get("nid")
        file_model = UserSound.objects.get(id=nid)
        file_model.delete()  # 删除MySQL表中的数据，将触发信号删除文件
        return Response({
            "status": 200,
            "msg": "delete successful",
            "data": "",
        })

    def user_description(self, request):  # put改原音频名称

        description = request.POST.get("description")
        name = request.POST.get("name")

        nid = request.POST.get("nid")

        UserSound.objects.filter(id=nid).update(description=description)
        UserSound.objects.filter(id=nid).update(name=name)

        Sound = UserSound.objects.filter(id = nid)
        serializer = UsersoundSerializers(instance=Sound, many=True)

        return Response({
            "status": 0,
            "msg": 200,
            "data": {"items": serializer.data}
        })
