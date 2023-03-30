# -*- coding: utf-8 -*-
import os

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.http import StreamingHttpResponse

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

    @action(methods=['post'], detail=False)
    def start_chat(self, request):
        """
        针对某个文档为主题, 开启与 chatbot 的聊天
        :param request:
        :return:
        """

        data = {
            'info': {}
        }
        file_id = request.data.get('file_id')
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

        # 截取前 2500 个字符 TODO: 粗糙的截取方式, 后续需要优化
        context = context[:2500]

        if not context:
            data['result'] = 'error'
            data['message'] = '该文件还未解析'
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        data['message'] = ''
        ChatGpt = ChatWithGPT()
        start_chat_data = ChatGpt.start_chat(pdf_context=context)
        # 判断是否开启会话成功
        start_finish = start_chat_data.get('start_finish', None)
        if not start_finish:
            data['result'] = 'error'
            data['message'] += '与 chatgpt 的聊天开启失败 请重试或者联系管理员'

        pdf_finish = start_chat_data.get('pdf_finish', None)
        if not pdf_finish:
            data['result'] = 'error'
            data['message'] += '向 chatgpt 传递 pdf 文件未收到正确回应 请重试或者联系管理员'

        question_finish = start_chat_data.get('question_finish', None)
        if not question_finish:
            data['result'] = 'error'
            data['message'] += '向 chatgpt 请求文章梗概未收到正确回应 请重试或者联系管理员'

        data['info']['summary'] = start_chat_data.get('summary', None)
        data['info']['history_list'] = start_chat_data.get('history_list', None)

        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def continue_chat(self, request):
        """
        继续与 chatbot 的聊天
        :param request: history_list, new_question, 历史对话列表, 新的问题，必须
        :return: current_answer, new_history_list, 当前的回答, 新的历史对话列表
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

        """
        调用 continue_chat 方法, 返回迭代器, 以进行 stream 流式传输
        需要在外部接收 full message， 手动更新 history_list
        """
        ChatGpt = ChatWithGPT(history=history_list)
        chunks_list = []
        messages_list = []

        gpt_response = ChatGpt.continue_chat(message_content=new_question)
        for chunk in gpt_response:
            chunks_list.append(chunk)
            chunk_message = chunk.get('choices', [{}])[0].get('delta', None)
            messages_list.append(chunk_message)
            print('chunk_message: ', chunk_message)

        full_reply_content = ''.join(
            m.get('content', '') for m in messages_list
        )
        print('full_reply_content: ', full_reply_content)

        return Response(full_reply_content, status=status.HTTP_200_OK)
        # resp = StreamingHttpResponse(
        #     gpt_response, content_type='text/event-stream'
        # )
        # resp['Cache-Control'] = 'no-cache'
        # # resp['Connection'] = 'keep-alive'
        # resp['Content-Encoding'] = 'gzip'
        # return resp
