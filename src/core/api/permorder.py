import logging
import json
from libs import baseview
from libs import util
from core.task import grained_permissions
from libs.serializers import UserINFO
from rest_framework.response import Response
from django.http import HttpResponse
from django.db.models import Count
from django.db.models import Q
from rest_framework_jwt.settings import api_settings
from core.models import (
    Account,
    grained,
    DatabaseList,
    SqlDictionary,
    PermOrder
)
from libs.util import get_current_datetime
from core.api.myorder import ADMIN

CUSTOM_ERROR = logging.getLogger('Yearning.core.views')

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class UserPermission(baseview.BaseView):
    '''
        Permission order Management interface

        mothod：

        get:

            if args equal to order (/api/v1/userpermission/orderconfirm/order)
            if args equal to ordercommit (/api/v1/userpermission/orderconfirm/ordercommit) get user order information
            if args equal to orderaudit (/api/v1/userpermission/orderconfirm/orderaudit) get user order information
            if args equal to orderexecutor (/api/v1/userpermission/orderconfirm/orderexecutor) get user order information

        put:

            if args equal to orderconfirm (/api/v1/userpermission/orderconfirm) confirm order

            if args equal to orderexecute (/api/v1/userpermission/orderexecute) execute order

        post:

            commit order (/api/v1/userpermission)

    '''

    def get(self, request, args=None):

        """
        args
        :param request:
        :param args:
        :return:
        """
        if args not in ['order', 'ordercommit', 'orderaudit', 'detail']:
            return HttpResponse(status=500)

        if args == 'order':
            user = request.GET.get('user')
            if not user:
                return Response(status=500)

            user_perm = grained.objects.filter(username=user).first()
            user_info = Account.objects.filter(username=user).first()
            audit_user = Account.objects.filter(is_staff=1)\
                .values_list('username', flat=True).distinct()

            db_list = DatabaseList.objects\
                .values_list('connection_name', flat=True)
            dic_list = SqlDictionary.objects\
                .values_list('Name', flat=True).distinct()

            data = dict(
                permission=user_perm.permissions if user_perm else '',
                username=user_info.username if user_info else '',
                group=user_info.group if user_info else '',
                con=list(db_list),
                dicadd=list(dic_list),
                audituser=list(audit_user),
            )

            if data:
                return Response(data)
            else:
                return HttpResponse(content="No Data", status=500)

        data = request.GET.dict()
        page = data.get('page', 1)
        username = data.get('user')
        search = data.get('filter_name')
        start = (int(page) - 1) * 20
        end = int(page) * 20

        if args == 'ordercommit':  # 获取列表
            # 获取用户名 去重
            users = []
            if username == ADMIN:
                users = PermOrder.objects.values_list('username').distinct()
                users = [user[0] for user in users if len(user) >= 1]
            else:
                users.append(username)
            users.insert(0, '')

            page_number = PermOrder.objects.filter(username=username)\
                .aggregate(number=Count('id'))

            condition_sql = ''
            if username != ADMIN or (username == ADMIN and search):
                condition_sql = "WHERE username = '{}'" \
                    .format(search if search else username)

            info = PermOrder.objects.raw(
                " select * from core_permorder {} ORDER BY id desc "
                    .format(condition_sql))[start:end]
            #info = PermOrder.objects.filter(username=username).order_by('-date')[start:end]
            res = util.ser(info)
            return Response({'page': page_number, 'data': res, 'users': users})

        elif args == 'orderaudit':
            queryset = PermOrder.objects.filter(Q(auditor=username) |
                                                Q(executor=username))
            page_number = queryset.aggregate(number=Count('id'))
            info = queryset.order_by('-id')[start:end]
            data = util.ser(info)
            return Response({'page': page_number, 'data': data})
        elif args == 'detail':
            oid = data.get('id', -1)
            info = PermOrder.objects.filter(id=oid)
            res = util.ser(info)
            return Response(res[0] if len(res) > 0 else dict())
        elif args == 'orderexecutor':
            try:
                page = request.GET.get('page')
                username = request.GET.get('user')
            except KeyError as e:
                CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                return HttpResponse(status=500)
            else:
                try:
                    pagenumber = PermOrder.objects.filter(executor=username).aggregate(number=Count('id'))
                    start = (int(page) - 1) * 20
                    end = int(page) * 20
                    info = PermOrder.objects.raw(
                        '''
                        select * from core_permorder where executor = '%s' ORDER BY id desc
                        ''' % username)[start:end]
                    data = util.ser(info)
                    return Response({'page': pagenumber, 'data': data})
                except Exception as e:
                    CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                    return HttpResponse(status=500)

    def post(self, request, args=None):
        try:
            data = dict(
                work_id=util.workId(),
                username=request.data['user'],
                usergroup=request.data['group'],
                department=request.data.get('department', ''),
                status=request.data.get('status', 1),
                permissions=json.loads(request.data['permission']),
                text=request.data['text'],
                auditor=request.data['auditor'],
                date=get_current_datetime(),
            )

        except KeyError as e:
            CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
            return HttpResponse(status=500)
        else:

            try:
                obj = PermOrder.objects.create(**data)
                return Response(dict(
                    msg='%s--工单提供成功!' % data.get('username'),
                    id=obj.id
                ))
            except Exception as e:
                CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                return HttpResponse(status=500)

    def put(self, request, args=None):
        if args == 'orderconfirm':
            data = request.data
            username = data.get('user')
            oid = data.get('id')
            status = data.get('status')

            params = dict(id=oid)
            update_params = dict(status=status)
            if status == 2:
                params['auditor'] = username
                update_params['executor'] = data.get('executor')
            else:
                params['executor'] = username

            # 更新权限表
            is_exists = PermOrder.objects.filter(**params).exists()
            if status == 3 and is_exists:
                # 更新权限表
                tmp = dict(status=2)
                tmp.update(**params)
                perm = PermOrder.objects.filter(**tmp).first()
                account = Account.objects.filter(username=username).first()
                if perm:
                    grained.objects.update_or_create(
                        username=perm.username,
                        defaults={'permissions': perm.permissions},
                    )

                    if perm.usergroup == 'admin' and account.is_staff != 1:
                        account.is_staff = 1
                    elif perm.usergroup == 'guest' and account.is_staff != 0:
                        account.is_staff = 0

                account.save()

            if is_exists:
                PermOrder.objects.filter(id=oid).update(**update_params)
                return Response('%s--工单确认成功!' % username)
            else:
                return HttpResponse(status=500)

        elif args == 'orderexecute':
            try:
                username = request.data['user']
                id = request.data['id']
                status = request.data['status']
            except KeyError as e:
                CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                return HttpResponse(status=500)
            else:
                try:
                    if PermOrder.objects.filter(id=id, status=2, executor=username):
                        perm = PermOrder.objects.get(id=id)
                        grained.objects.update_or_create(username=perm.username,
                                                         defaults={'permissions': perm.permissions},)
                    else:
                        return HttpResponse(status=500)
                    if perm.usergroup == 'admin':
                        Account.objects.filter(username=perm.username).update(
                            group=perm.usergroup,
                            department=perm.department,
                            is_staff=1
                        )
                    elif perm.usergroup == 'guest':
                        Account.objects.filter(username=perm.username).update(
                            group=perm.usergroup,
                            department=perm.department,
                            is_staff=0
                        )
                    PermOrder.objects.filter(id=id).update(status=status)
                    return Response('%s--权限修改成功!' % username)
                except Exception as e:
                    CUSTOM_ERROR.error(f'{e.__class__.__name__}: {e}')
                    return HttpResponse(status=500)