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
    """
    openai.api_key = OPEN_AI_API_KEY

    openai.proxy = {
        'http': 'http://' + LOCAL_PROXY,
        # 'https': 'https://' + LOCAL_PROXY,
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

    def chat(self, message_content: str):
        """
        与 GPT 交谈
        :param message_content: 交谈内容
        :return: 交谈结果
        """
        result_data = {}
        finish_reason_map = {
            "stop": "chat_gpt 返回完整的模型输出",
            "length": "超出最大长度限制, 输出不完整",
            "content_filter": "内容被过滤, 输出不完整",
            "null": "chat_gpt 仍在响应, 或者不完整",
        }
        # 生成 messages_list
        self.make_messages_list("user", message_content)

        # 使用 messages_list 交谈
        # print(self.messages_list)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages_list
        )

        reply_content = response["choices"][0]["message"]["content"]
        finish_reason = response["choices"][0]["finish_reason"]
        result_data["reply_content"] = reply_content
        result_data["finish_reason"] = finish_reason_map[finish_reason]

        # 生成 messages_list
        self.make_messages_list("assistant", reply_content)

        return result_data, self.messages_list

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
