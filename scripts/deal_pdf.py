"""
解析pdf文件
使用google vision api 和 google cloud storage api
先将文件上传到 google cloud storage，然后使用 google vision api 解析文件
解析结果保存在 google cloud storage 中
{
    "inputConfig": {
        "gcsSource": {
            "uri": "gs://gpt_demo/cn_c.pdf"
        },
        "mimeType": "application/pdf"
    },
    "responses": [
        {
            "fullTextAnnotation": {
                "pages": [
                    {
                        "property": {
                            "detectedLanguages": [
                                {
                                    "languageCode": "zh",
                                    "confidence": 0.9366392
                                }
                            ]
                        },
                        "width": 595,
                        "height": 841,
                        "blocks": [],
                        "confidence": 0.9858429
                    }
                ],
                "text": "中文测试, 第一页内容"
            }
        }
    ]
        {
            "fullTextAnnotation": {
                "pages": [
                    {
                        "property": {
                            "detectedLanguages": [
                                {
                                    "languageCode": "zh",
                                    "confidence": 0.9366392
                                }
                            ]
                        },
                        "width": 595,
                        "height": 841,
                        "blocks": [],
                        "confidence": 0.9858429
                    }
                ],
                "text": "中文测试，第二页内容"
}
"""

import os
import json
import re
from google.cloud import vision
from google.cloud import storage
from GPT.settings import LOCAL_PROXY, GOOGLE_KEY_FILE

# 代理
os.environ['http_proxy'] = LOCAL_PROXY
os.environ['https_proxy'] = LOCAL_PROXY

# google cloud key
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_KEY_FILE

# 文件类型，'application/pdf' 或 'image/tiff'
mime_type = 'application/pdf'

# 返回的每个 json 文件中包含多少页的内容
batch_size = 100


def analyze_pdf(gcs_source_uri: str, gcs_destination_uri: str):
    """
    解析 pdf 文件
    :param gcs_source_uri: pdf 文件在 Cloud Storage 上的路径
    :param gcs_destination_uri: 输出文件在 Cloud Storage 上的路径
    :return: bool, True 表示成功，False 表示失败
    """

    client = vision.ImageAnnotatorClient()

    # 特征，文本
    feature = vision.Feature(
        type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION
    )

    # 源文件，必须是 Cloud Storage 上的文件
    gcs_source = vision.GcsSource(uri=gcs_source_uri)

    # 输入文件的信息，google.cloud.vision_v1.types.InputConfig 对象
    input_config = vision.InputConfig(
        gcs_source=gcs_source, mime_type=mime_type
    )

    # 输出文件，必须是 Cloud Storage 上的文件，输出的 Google Cloud Storage 位置。
    gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)

    # 输出文件的信息，google.cloud.vision_v1.types.OutputConfig 对象
    output_config = vision.OutputConfig(
        gcs_destination=gcs_destination, batch_size=batch_size)

    # 异步请求类，google.cloud.vision_v1.types.AsyncAnnotateFileRequest 对象
    async_request = vision.AsyncAnnotateFileRequest(
        features=[feature], input_config=input_config,
        output_config=output_config)

    try:
        # 开始异步处理
        operation = client.async_batch_annotate_files(
            requests=[async_request]
        )

        print('正在解析 PDF 文件 请稍后...')
        operation.result(timeout=1000)
        print('解析完成！')
        return True

    except Exception as e:
        print(e)
        return False


def download_gcs_file(gcs_source_uri: str, bucket_name: str):
    """
    下载 Cloud Storage 上的解析结果文件, Json
    :param gcs_source_uri: Cloud Storage 上的路径
    :param bucket_name: Cloud Storage 上的 bucket 名称
    :return: Json 字符串, 若下载失败, 则返回 None
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        json_blob = bucket.blob(gcs_source_uri)
        json_string = json_blob.download_as_string()
        result = json.loads(json_string)
        print('下载成功！')
        return result

    except Exception as e:
        print('下载失败！, 以下是错误信息')
        print(e)
        return None


def get_text_from_json(json_string: str):
    """
    从 json 字符串中提取文本
    :param json_string: json 字符串
    :return: 文本字符串
    """
    try:
        response_list = json_string['responses']
        full_text = ''
        for response in response_list:
            full_text += response['fullTextAnnotation']['text']

        print('提取文本成功！')
        return full_text

    except Exception as e:
        print('提取文本失败！, 以下是错误信息')
        print(e)
        return None


def upload_pdf(bucket_name, source_file_obj, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(source_file_obj)
    print('文件上传成功！')
    return blob.public_url


if __name__ == '__main__':
    r = download_gcs_file('cnc_out/cnc.jsonoutput-1-to-3.json', 'gpt_demo')
    fr = get_text_from_json(r)
    print(fr)

