import time

from django.shortcuts import render


# Create your views here.

import json
from obs import ObsClient
import os

from django.http import JsonResponse

from voice.models import Voicefile
from voice_share.models import Article
# 这个 ArticleListSerializer 暂时还没有
from voice_share.serializers import ArticleListSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import render
from django.http import HttpResponse
from .models import Article
from django.http import Http404
from rest_framework import mixins
from rest_framework import generics


from voice_share.models import Article
from voice_share.serializers import ArticleDetailSerializer



@api_view(['GET'])
def article_list(request):
    if request.method == 'GET':
        articles = Article.objects.all()
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)


class ArticleDetail(APIView):
    """文章详情视图"""

    def get_object(self, pk):
        """获取单个文章对象"""
        try:
            # pk 即主键，默认状态下就是 id
            return Article.objects.get(pk=pk)
        except:
            raise Http404

    def get(self, request, pk):
        article = self.get_object(pk)   
        serializer_context = {
            'request': request,
        }
        serializer = ArticleDetailSerializer(article,  context=serializer_context)
        # 返回 Json 数据

        return Response(serializer.data)

    def put(self, request, pk):
        article = self.get_object(pk)
        serializer_context = {
            'request': request,
        }
        serializer = ArticleDetailSerializer(article, data=request.data, context=serializer_context)
        # 验证提交的数据是否合法
        # 不合法则返回400
        if serializer.is_valid():
            # 序列化器将持有的数据反序列化后，
            # 保存到数据库中
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        article = self.get_object(pk)
        article.delete()
        # 删除成功后返回204
        return Response({'msg': '删除成功'}, status=status.HTTP_204_NO_CONTENT)


class VoiceShare(APIView):

    def post(self, request):
        article = Article()
        user = request.user
        article.user = user
        # article.title = request.POST.get('title')
        # article.text = request.POST.get('text')
        # json 格式
        json_data = json.loads(request.body)

        article.title = json_data['title']
        article.text = json_data['text']
        voice_name = json_data['voice_name']


        # voice_name = request.POST.get('voice_name')

        try:
            Voice = Voicefile.objects.get(user=user, name=voice_name)
            print(Voice)
        except OSError as e:
            print(e)
        
        
        #获取暂存音频的url
        old_obs_url = Voice.url
        #得到文件后缀
        ext = old_obs_url.split('.')[-1]
        # print(ext)

        # obsClient = ObsClient(
        #     access_key_id='ILH9LF6DUM0V7TACBI7P',  # 刚刚下载csv文件里面的Access Key Id PX91I6UXKYUFOTKE8BFK

        #     # 刚刚下载csv文件里面的Secret Access Key XoA4NB2b56ehNbaPkM31mCB5B6DlbK9TisA3mxG5
        #     secret_access_key='94SpA5u79LsnXOajCBR52NfWn2K1bUakYGwcqMdt',
            	
        #     # https://obs.cn-north-4.myhuaweicloud.com
        #     server='https://obs.cn-southwest-2.myhuaweicloud.com'  # 这里的访问域名就是我们在桶的基本信息那里记下的东西
        # )
        obsClient = ObsClient(
            access_key_id='PX91I6UXKYUFOTKE8BFK',  # 刚刚下载csv文件里面的Access Key Id 

            # 刚刚下载csv文件里面的Secret Access Key 
            secret_access_key='XoA4NB2b56ehNbaPkM31mCB5B6DlbK9TisA3mxG5',
            	
            # 
            server='https://obs.cn-north-4.myhuaweicloud.com'  # 这里的访问域名就是我们在桶的基本信息那里记下的东西
        )



        ctime = str(int(time.time()))
        temp_path = f'./temp/'
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)
        #暂存音频下载到本地
        try:
            # http://crowdofvoice.obs.cn-north-4.myhuaweicloud.com/
            resp = obsClient.getObject(bucketName="crowdofvoice",
                                             objectKey=old_obs_url.split("http://obs.crowdofvoice.top/")[1],
                                             downloadPath=temp_path + old_obs_url.split("http://obs.crowdofvoice.top/")[1])
            if resp.status < 300:
                print('requestId:', resp.requestId)
                print('url:', resp.body.url)
            else:
                print('errorCode:', resp.errorCode)
                print('errorMessage:', resp.errorMessage)
        except:
            import traceback
            print(traceback.format_exc())

        key_path = 'shared_wav/' + request.user.username + '/' + ctime + '.' + ext
        print(key_path)
        #暂存到本地的音频上传到永久obs桶
        resp_new = obsClient.putFile(bucketName = "crowdofvoice", objectKey = key_path, file_path = temp_path + old_obs_url.split("http://obs.crowdofvoice.top/")[1])
        if resp_new.status < 300:
            # 输出请求Id
            print('requestId:', resp_new.requestId)
        else:
            # 输出错误码
            print('errorCode:', resp_new.errorCode)
            # 输出错误信息
            print('errorMessage:', resp_new.errorMessage)

        # 关闭obsClient
        obsClient.close()


        #删除本地的暂存音频
        try:
            os.remove(temp_path + old_obs_url.split("http://obs.crowdofvoice.top/")[1])
        except FileNotFoundError as e:
            print(f'File not found: {e.filename}')

        article.shared_voice_url = 'http://obs.crowdofvoice.top/' + key_path
        article.save()
        return Response({
            'status': 201,
            'msg': '发布成功',
            "data": 'http://obs.crowdofvoice.top/' + key_path
        })