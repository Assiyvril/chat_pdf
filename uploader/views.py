# -*- coding: utf-8 -*-
import json
import os

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.http import StreamingHttpResponse, HttpResponse

from GPT.settings import LOCAL_PROXY, OPEN_AI_API_KEY
from chat_history.models import ChatHistory
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
        elif user.is_anonymous:
            return UploadFile.objects.none()
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

        context = file_obj.context.encode('gbk', errors='replace').decode(
            'gbk', errors='replace')

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
        data['info']['history_list'] = start_chat_data.get('history_list',
                                                           None)

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

        file_id = request.data.get('file_id', None)
        if not file_id:
            data['result'] = 'error'
            data['message'] = 'file_id 不能为空'
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        """
        调用 continue_chat 方法, 返回迭代器, 以进行 stream 流式传输
        需要在外部接收 full message， 手动更新 history_list
        """
        ChatGpt = ChatWithGPT(history=history_list)

        def gpt_response():
            """
            生成器, 用于 stream 流式传输
            :return:
            """
            full_message_reply = ''
            response = ChatGpt.continue_chat(message_content=new_question)
            for chunk in response:
                # TODO 暂时不替换空格为 &nbsp;
                chunk_message = chunk.get('choices', [{}])[0].get('delta', {}).get('content', '')
                if chunk_message:
                    content = chunk_message.replace('\n\n', '<br>')
                    print('content', content)
                    full_message_reply += chunk_message

                    yield f'data: {content}\n\n'

            ChatGpt.make_messages_list(
                role='assistant',
                messages=full_message_reply
            )

            new_history_list = ChatGpt.get_history()
            history_obj = ChatHistory.objects.filter(
                pdf_file_id=file_id
            ).order_by('-update_time').first()
            if history_obj:
                history_obj.history_list = new_history_list
                history_obj.save()
                print('update history_list')
            else:
                ChatHistory.objects.create(
                    pdf_file_id=file_id,
                    history_list=new_history_list
                )
                print('create history_list')

        rep = StreamingHttpResponse(gpt_response())
        rep['Access-Control-Allow-Origin'] = '*'
        rep['Content-Type'] = 'text/event-stream'

        return rep

    @action(methods=['get'], detail=False)
    def test_continue(self, request):
        """
        继续与 chatbot 的聊天
        :param request: history_list, new_question, 历史对话列表, 新的问题，必须
        :return: current_answer, new_history_list, 当前的回答, 新的历史对话列表
        """

        data = {}
        history_list = [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "我将发给你一篇文章，请你阅读并围绕这篇文章回答我的问题。接下来我们的对话都是基于这篇文章的内容。"
        },
        {
            "role": "assistant",
            "content": "好的，请把文章发给我。"
        },
        {
            "role": "user",
            "content": "POLYMATIC USER MANUAL\nPM\nVersion 1.1\nAugust 16, 2015\np-o-l-y-m-a-t-i-c\nThe Colina Group\nDepartment of Materials Science and Engineering\nThe Pennsylvania State University\nhttp://www.matse.psu.edu/colinagroup/polymatic\nhttps://nanohub.org/resources/17278\nCopyright 2013, 2015 Lauren J. Abbott\nDistributed under the terms of the GNU General Public LicenseContents\n1 Introduction\n1.1 About Polymatic\n1.2 Included Files\n1.3 Version History\n1.4 GNU Distribution Notice .\n1.5 Citation\n1.6 Publications Using Polymatic\n1.7 Acknowledgments .\n2 Random Packing\n2.1 About\n2.2 Syntax\n2.3 Output\n2.4 Usage\n2.5 Examples\n3 Simulated Polymerization\n3.1 About\n3.2 Polymerization Step\n3.2.1 About\n3.2.2\nSyntax\n3.2.3 Types File\n3.2.4 Input Script\n3.2.5 Output . .\n3.3 Initialization and Finalization\n3.3.1 About\n3.3.2 Syntax\n3.3.3 Output.\n3.4 Polymerization Loop\n3.4.1 About\n3.4.2 Syntax\n3.4.3 Parameters and Input Scripts\n3.4.4 Setup and Output\n3.5 Usage\n3.6 Examples\n1\n3\n3\n3\n4\n5\n5\n5\n7\n9\n9\n10\n10\n11\n13\n15\n15\n17\n17\n17\n18\n19\n25\n26\n26\n26\n27\n27\n27\n28\n28\n30\n32\n34A Data Structures\nA.1 About\nA.2 Molecular System\nA.2.1 Flags.\nA.2.2 Periodic Box.\nA.2.3 Neighbor List\nA.2.4 Molecules\nA.2.5 Atoms\nA.2.6 Bonded Interactions\nA.2.7 Data Types . .\nA.3 Input Script Parameters\nA.3.1 Link Command\nA.3.2 Charge Command.\nA.3.3 Connect Command\nA.3.4 Types Command\nA.3.5 Bond Command.\nA.3.6 Align Command\nB File Conversion\nB.1 About\nB.2 Reading and Writing Files\nB.3 Connectivity Definitions\nB.4 Usage\n2\n39\n39\n39\n40\n40\n41\n41\n42\n43\n44\n47\n47\n48\n48\n49\n49\n50\n51\n51\n51\n52\n531 Introduction\n1.1 About Polymatic\nPolymatic is a code developed in the Colina Group for structure generation\nof amorphous polymers by a simulated polymerization algorithm. Polymatic\ncan be thought of as a wrap-around code that calls a simulation package to\nperform energy minimization and molecular dynamics simulations. In be-\ntween these simulations, the code performs polymerization steps by checking\na set of defined bonding criteria and updating the connectivity information of\nthe system (i.e., bonds, angles, dihedrals, impropers) appropriately to reflect\nthe new bonds being made. Codes are included to perform an initial random\npacking (Chapter 2) and polymerization steps (Chapter 3).\nThe current Polymatic distribution is set up to work with the Large-scale\nAtomic/Molecular Massively Parallel Simulator (LAMMPS). Specifically, it\nis set up to read and write LAMMPS data files with a class I or II force\nfield, including pair, bond, angle, dihedral, and imp"
        },
        {
            "role": "assistant",
            "content": "Based on the article, Polymatic is a code developed by the Colina Group for generating amorphous polymer structures using a simulated polymerization algorithm. The code performs energy minimization and molecular dynamics simulations, and updates the connectivity information of the system based on defined bonding criteria to reflect the new bonds being made during the polymerization steps. The code also includes a feature for performing initial random packing. Polymatic is set up to work with the Large-scale Atomic/Molecular Massively Parallel Simulator (LAMMPS) and is capable of reading and writing LAMMPS data files with a class I or II force field. Additionally, the article provides information on how to use and cite Polymatic, as well as examples and data structures."
        },
        {
            "role": "user",
            "content": "首先，请告诉我这篇文将大概讲了什么？"
        },
        {
            "role": "assistant",
            "content": "这篇文章介绍了一个名为Polymatic的代码，用于通过模拟聚合物化学反应生成无定形聚合物的三维结构模型。文章提供了关于Polymatic的基本介绍、版本历史、使用说明以及数据结构等方面的内容。此外，文章还提供了示例和引用说明。"
        }
    ]

        new_question = request.query_params.get('new_question', '')
        if not new_question:
            data['result'] = 'error'
            data['message'] = 'new_question 不能为空'
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        file_id = request.query_params.get('file_id', None)
        if not file_id:
            data['result'] = 'error'
            data['message'] = 'file_id 不能为空'
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        """
        调用 continue_chat 方法, 返回迭代器, 以进行 stream 流式传输
        需要在外部接收 full message， 手动更新 history_list
        """
        ChatGpt = ChatWithGPT(history=history_list)

        def gpt_response():
            """
            生成器, 用于 stream 流式传输
            :return:
            """
            full_message_reply = ''
            response = ChatGpt.continue_chat(message_content=new_question)
            for chunk in response:
                # TODO 暂时不替换空格为 &nbsp;
                chunk_message = chunk.get('choices', [{}])[0].get('delta',
                                                                  {}).get(
                    'content', '')
                if chunk_message:
                    content = chunk_message.encode('utf-8').decode('utf-8').replace(' ', '&nbsp;').replace('\n\n', ' ')
                    print('content', content)
                    full_message_reply += chunk_message

                    yield f'data: {content}\n\n'
                    # yield json.dumps({'data': f'{content}\n\n'})

            # 更新 history_list
            ChatGpt.make_messages_list(
                role='assistant',
                messages=full_message_reply
            )

            new_history_list = ChatGpt.get_history()
            history_obj = ChatHistory.objects.filter(
                pdf_file_id=file_id
            ).order_by('-update_time').first()
            if history_obj:
                history_obj.history_list = new_history_list
                history_obj.save()
                print('update history_list')
                print('new_history_list', new_history_list)
            else:
                ChatHistory.objects.create(
                    pdf_file_id=file_id,
                    history_list=new_history_list
                )
                print('create history_list')
                print('new_history_list', new_history_list)

        rep = StreamingHttpResponse(gpt_response(), content_type='text/event-stream')
        print(rep.headers)
        # rep['Access-Control-Allow-Origin'] = '*'
        # rep['Content-Type'] = 'text/html; charset=utf-8'
        # rep['Cache-Control'] = 'no-cache'

        return rep



    def my_view(request):
        def content_generator():
            yield 'Content1\n'
            yield 'Content2\n'
            yield 'Content3\n'

        # First, return non-streaming content
        response = HttpResponse('Non-streaming content',
                                content_type='text/plain')

        # Then, return streaming content
        def response_generator():
            for content in content_generator():
                yield content

        streaming_response = StreamingHttpResponse(response_generator(),
                                                   content_type='text/plain')
        streaming_response[
            'Content-Disposition'] = 'attachment; filename="example.txt"'

        # Combine the two responses into one
        combined_response = HttpResponse()
        combined_response.streaming_content = (chunk for chunk in
                                               streaming_response.streaming_content)
        combined_response.write(response.content)
        combined_response['Content-Type'] = response['Content-Type']
        combined_response['Content-Disposition'] = response[
            'Content-Disposition']

        return combined_response