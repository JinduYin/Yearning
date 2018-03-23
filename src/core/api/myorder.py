import logging
from libs import baseview, util
from django.db.models import Count
from django.db.models import Q
from core.models import SqlOrder
from django.http import HttpResponse
from rest_framework.response import Response

CUSTOM_ERROR = logging.getLogger('Yearning.core.views')
ADMIN = 'admin'
EXPORT_SQL = '2'


class order(baseview.BaseView):

    '''

    :argument 我的工单展示接口api

    '''

    def get(self, request, args: str=None):
        try:
            username = request.GET.get('user')
            page = request.GET.get('page')
            filter_user = request.GET.get('filter_name')
            order_type = request.GET.get('type')
        except KeyError as e:
            CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
        else:
            try:
                if order_type == EXPORT_SQL:
                    queryset = SqlOrder.objects.filter(type=2)
                else:
                    queryset = SqlOrder.objects.filter(~Q(type=2))
                if username != ADMIN:
                    queryset = queryset.filter(username=username)

                page_number = queryset.aggregate(alter_number=Count('id'))
                start = (int(page) - 1) * 20
                end = int(page) * 20

                # admin 用户查询所有工单 根据用户筛选工单
                # admin用户且filter_user不为空 根据filter_user用户查询
                # 非admin用户，根据username查询
                condition_sql = 'WHERE core_sqlorder.type {} '\
                    .format('= 2' if order_type == EXPORT_SQL else '!=2')
                if username != ADMIN or (username == ADMIN and filter_user):
                    condition_sql += " AND core_sqlorder.username = '{}'"\
                        .format(filter_user if filter_user else username)

                # 获取用户名 去重
                users = []
                if username == ADMIN:
                    users = queryset.values_list('username').distinct()
                    users = [user[0] for user in users if len(user) >= 1]
                else:
                    users.append(username)
                users.insert(0, '')

                info = SqlOrder.objects.raw(
                    "select core_sqlorder.*,core_databaselist.connection_name,\
                    core_databaselist.computer_room from core_sqlorder INNER JOIN \
                    core_databaselist on core_sqlorder.bundle_id = core_databaselist.id \
                    %s ORDER BY core_sqlorder.id DESC " % condition_sql) [start:end]
                data = util.ser(info)
                return Response({'page': page_number, 'data': data, 'users': users})
            except Exception as e:
                CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                return HttpResponse(status=500)
