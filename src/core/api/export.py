#!/usr/bin/env python
# encoding: utf-8

"""
------------------------------------------------------------------------------
File Name    :  export.py
Description  :  

Author: Yin
Create Time: 2018-03-24 12:33
Version:    1.0
------------------------------------------------------------------------------
"""

__author__ = 'YIN'


import logging
from rest_framework.response import Response
from django.http import HttpResponse
from django.http import StreamingHttpResponse, FileResponse
from libs import baseview
from libs import util

CONF = util.conf_path()
FILE_PATH = CONF.path
CUSTOM_ERROR = logging.getLogger('Yearning.core.views')


class ExportSql(baseview.BaseView):
    """
    导出sql生成的excel文件
    """

    def get(self, request, args: str = None):
        data = request.GET.dict()
        file_name = data.get('file_name')

        path = FILE_PATH
        path = path + '/' if path[-1] != '/' else path
        path = path + file_name

        return Response(dict(url=path))

        # 不用Django下载支持
        # def read_file(name, chunk_size=512):
        #     with open(name, encoding='ISO-8859-1') as f:
        #         while True:
        #             c = f.read(chunk_size)
        #             if c:
        #                 yield c
        #             else:
        #                 break
        #
        # response = StreamingHttpResponse(read_file(path))
        # response['Content-Type'] = 'application/octet-stream'
        # response['Content-Disposition'] = 'attachment;filename="{}"'.format(
        #     file_name)
        #
        # return response







