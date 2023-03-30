"""
与 chat_gpt 交谈
  messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
        {"role": "user", "content": "Where was it played?"}
]
"""
import os
import json
import openai
from GPT.settings import OPEN_AI_API_KEY, LOCAL_PROXY

# openai.proxy = {
#             'http': 'http://' + LOCAL_PROXY,
#             # 'https': 'https://' + LOCAL_PROXY,
#         }

os.environ["http_proxy"] = "http://" + LOCAL_PROXY
os.environ["https_proxy"] = "http://" + LOCAL_PROXY

class ChatWithGPT:
    """
    与 GPT 交谈
    23.03.29, 初步 demo, 目前仅有交谈功能
    将每次交谈的信息追加在 messages_list 中
    ---
    23.03.30, 修改chat 方法，stream=True, 获取实时响应
    不能再返回 current message 和 messages_list，而是返回迭代器
    因此，调用时需要在外部接受 full message 来更新当前对象的 messages_list
    新增 start_chat 方法，用于开启与 chatbot 的聊天，返回完整响应，而不是迭代器
    """
    openai.api_key = OPEN_AI_API_KEY

    openai.proxy = {
        'http': 'http://' + LOCAL_PROXY,
        # 'https': 'https://' + LOCAL_PROXY,
    }

    finish_reason_map = {
        "stop": "chat_gpt 返回完整的模型输出",
        "length": "超出最大长度限制, 输出不完整",
        "content_filter": "内容被过滤, 输出不完整",
        "null": "chat_gpt 仍在响应, 或者不完整",
    }

    def __init__(self, history: list = None):

        self.messages_list = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        if history:
            self.messages_list = history

    def make_messages_list(self, role: str, messages: str):
        """
        生成 messages_list
        :param role: 角色
        :param messages: 新消息内容
        :return: list
        """
        messages = messages.replace('\\', ' ')

        self.messages_list.append({"role": role, "content": messages})

        return self.messages_list

    def start_chat(self, pdf_context: str):
        """
        开启与 chatbot 的聊天
        step 1: 发送开始消息，”'我将发给你一篇文章，请你阅读并围绕这篇文章回答我的问题。接下来我们的对话都是基于这篇文章的内容。'“
        step 2: 发送文章内容
        step 3: 发送问题，”首先，请告诉我这篇文将大概讲了什么？“
        step 4: 获取回答
        :param pdf_context: 文章内容
        :return: chat gpt 回答的文章梗概 和 会话历史
        """
        data = {}

        # 用开始消息初始化 messages_list
        start_message = "我将发给你一篇文章，请你阅读并围绕这篇文章回答我的问题。接下来我们的对话都是基于这篇文章的内容。"
        self.make_messages_list("user", start_message)
        start_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages_list,
            temperature=0,
        )
        start_finish_reason = start_response["choices"][0]["finish_reason"]
        start_reply_content = start_response["choices"][0]["message"]["content"]
        self.make_messages_list("assistant", start_reply_content)
        if start_finish_reason != "stop":
            data['start_finish'] = False
        else:
            data['start_finish'] = True

        # 发送文章内容
        self.make_messages_list("user", pdf_context)
        pdf_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages_list,
            temperature=0,
        )
        pdf_finish_reason = pdf_response["choices"][0]["finish_reason"]
        pdf_reply_content = pdf_response["choices"][0]["message"]["content"]
        self.make_messages_list("assistant", pdf_reply_content)
        if pdf_finish_reason != "stop":
            data['pdf_finish'] = False
        else:
            data['pdf_finish'] = True

        # 发送问题，”首先，请告诉我这篇文将大概讲了什么？“
        question = "首先，请告诉我这篇文将大概讲了什么？"
        self.make_messages_list("user", question)
        question_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages_list,
            temperature=0,
        )
        question_finish_reason = question_response["choices"][0]["finish_reason"]
        question_reply_content = question_response["choices"][0]["message"]["content"]
        self.make_messages_list("assistant", question_reply_content)
        if question_finish_reason != "stop":
            data['question_finish'] = False
        else:
            data['question_finish'] = True

        data['summary'] = question_reply_content
        data['history_list'] = self.messages_list

        return data

    def continue_chat(self, message_content: str):
        """
        与 GPT 交谈
        :param message_content: 交谈内容
        :return: 交谈结果
        """
        # result_data = {}

        # 生成 messages_list
        self.make_messages_list("user", message_content)

        # 使用 messages_list 交谈
        # print(self.messages_list)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages_list,
            temperature=0,
            stream=True,    # 获取实时响应, EventSource
        )

        # reply_content = response["choices"][0]["message"]["content"]
        # finish_reason = response["choices"][0]["finish_reason"]
        # result_data["reply_content"] = reply_content
        # result_data["finish_reason"] = finish_reason_map[finish_reason]

        # 生成 messages_list
        # self.make_messages_list("assistant", reply_content)

        # return result_data, self.messages_list
        return response

    def get_messages_list(self):
        """
        获取 messages_list
        :return: list
        """
        return self.messages_list

    def clear_messages_list(self):
        """
        清空 messages_list
        :return: None
        """
        self.messages_list = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]

        return True


if __name__ == '__main__':
    chat_gpt = ChatWithGPT()
    print(chat_gpt.chat("中国现任的国家元首是谁？"))
    print(chat_gpt.chat("他是哪一年出生的？"))
    print(chat_gpt.chat("他是哪一年上任的？"))
    print('会话历史：', chat_gpt.get_messages_list())
    print(chat_gpt.clear_messages_list())
    print(chat_gpt.get_messages_list())
