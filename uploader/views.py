# -*- coding: utf-8 -*-
import os

import openai
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from GPT.settings import LOCAL_PROXY, OPEN_AI_API_KEY
from .serializers import UploadFileListSerializer, UploadFileDetailSerializer
from .models import UploadFile
from scripts.chat_gpt import ChatWithGPT

os.environ["http_proxy"] = "http://" + LOCAL_PROXY
os.environ["https_proxy"] = "http://" + LOCAL_PROXY



class UploadFileViewSet(viewsets.ModelViewSet):
    """
    文件上传视图
    """
    queryset = UploadFile.objects.all()
    serializer_class = UploadFileListSerializer

    def get_queryset(self):
        """
        获取当前用户的文件
        管理员可以获取所有文件
        :return:
        """
        user = self.request.user
        if user.is_superuser:
            return UploadFile.objects.all()
        else:
            return UploadFile.objects.filter(owner=user)

    def get_serializer_class(self):
        """
        获取序列化类
        List: UploadFileListSerializer
        Retrieve: UploadFileDetailSerializer
        :return:
        """
        if self.action == 'retrieve':
            return UploadFileDetailSerializer
        else:
            return UploadFileListSerializer

    @action(methods=['get'], detail=False)
    def start_chat(self, request):
        """
        针对某个文档为主题, 开启与 chatbot 的聊天
        :param request:
        :return:
        """

        data = {}
        file_id = request.query_params.get('file_id', None)
        if not file_id:
            data['result'] = 'error'
            data['message'] = 'file_id 不能为空'
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        file_obj = UploadFile.objects.filter(id=file_id).first()
        if not file_obj:
            data['result'] = 'error'
            data['message'] = 'file_id 不存在'
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        context = file_obj.context.encode('gbk', errors='replace').decode('gbk', errors='replace')

        # 截取前 2500 个字符
        context = context[:2500]

        if not context:
            data['result'] = 'error'
            data['message'] = '该文件还未解析'
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        ChatGpt = ChatWithGPT()

        pdf_start_words = '我将发给你一篇文章，请你阅读并围绕这篇文章回答我的问题。接下来我们的对话都是基于这篇文章的内容。'
        ChatGpt.chat(pdf_start_words)
        ChatGpt.chat(context)
        out_line, history_list = ChatGpt.chat('首先，请告诉我这篇文将大概讲了什么？')
        data['result'] = 'success'
        data['message'] = {
            'out_line': out_line,
            'history_list': history_list,
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def continue_chat(self, request):
        """
        继续与 chatbot 的聊天
        :param request:
        :return:
        """
        data = {}
        history_list = request.data.get('history_list', None)
        if not history_list:
            data['result'] = 'error'
            data['message'] = 'history_list 不能为空'
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        new_question = request.data.get('new_question', None)
        if not new_question:
            data['result'] = 'error'
            data['message'] = 'new_question 不能为空'
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        ChatGpt = ChatWithGPT(history_list)
        current_answer, new_history_list = ChatGpt.chat(new_question)
        data['result'] = 'success'
        data['message'] = {
            'current_answer': current_answer,
            'history_list': new_history_list,
        }
        return Response(data, status=status.HTTP_200_OK)
