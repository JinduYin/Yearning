<style lang="less">
  @import '../../styles/common.less';
  @import 'components/table.less';
</style>
<template>
  <div>
    <Card>
      <p slot="title" style="height: 45px">
        <Icon type="android-send"></Icon>
        权限工单详细信息
        <br>
        <Button type="text"  @click.native="$router.go(-1)">返回</Button>
      </p>
      <div>
        <Form ref="userForm" :model="userForm" :label-width="200" label-position="right">
          <FormItem label="用户名：" prop="name">
            <div style="display:inline-block;width:300px;">
              <span>{{ userForm.name }}</span>
            </div>
          </FormItem>
          <FormItem label="部门：">
            <span>{{ userForm.department }}</span>
          </FormItem>
          <FormItem label="权限分类：">
            <span>{{ userForm.group }}</span>
          </FormItem>
          <FormItem label="备注">
            <span>{{ userForm.text }}</span>
          </FormItem>
        </Form>
        <hr style="height:1px;border:none;border-top:1px dashed #dddee1;" />
        <br>
        <Form ref="userForm" :model="userForm" :label-width="200" label-position="right">

          <FormItem label="DDL提交权限:">
            <p>{{permission.ddl}}</p>
          </FormItem>
          <FormItem label="可访问的连接名:" v-if="permission.ddl === '是'">
            <p>{{permission.ddlcon}}</p>
          </FormItem>
          <FormItem label="DML提交权限:">
            <p>{{permission.dml}}</p>
          </FormItem>
          <FormItem label="可访问的连接名:" v-if="permission.dml === '是'">
            <p>{{permission.dmlcon}}</p>
          </FormItem>
          <FormItem label="字典查看权限:">
            <p>{{permission.dic}}</p>
          </FormItem>
          <FormItem label="可访问的连接名:" v-if="permission.dic === '是'">
            <p>{{permission.diccon}}</p>
          </FormItem>
          <FormItem label="数据查询权限:">
            <p>{{permission.query}}</p>
          </FormItem>
          <FormItem label="可访问的连接名:" v-if="permission.query === '是'">
            <p>{{permission.querycon}}</p>
          </FormItem>
          <FormItem label="用户管理权限:">
            <p>{{permission.user}}</p>
          </FormItem>
          <FormItem label="数据库管理权限:">
            <p>{{permission.base}}</p>
          </FormItem>
        </Form>
      </div>
    </Card>
  </div>
</template>

<script>
  import Cookies from 'js-cookie'
  import util from '../../libs/util'
  import axios from 'axios'
  const exchangetype = function typeok (vl) {
    if (typeof vl === 'string') {
      if (vl === '1') {
        return '是'
      } else {
        return '否'
      }
    } else if (vl instanceof Array) {
      return vl.join()
    } else {
      return vl.toString()
    }
  }
  export default {
    name: 'permission-detail',
    data () {
      return {
        userForm: {
          name: '',
          group: '',
          department: '',
          permisson: []
        },
        permission: {
          ddl: '',
          ddlcon: ''
        },
        per_id: ''
      };
    },
    methods: {
    },
    mounted () {
      this.per_id = this.$route.query.id;
      axios.get(`${util.url}/userpermission/detail?id=${this.per_id}&user=${Cookies.get('user')}`)
        .then(res => {
          this.userForm = {
            name: res.data.username,
            group: res.data.usergroup,
            department: res.data.department,
            text: res.data.text
          };
          this.permission = res.data.permissions
          for (var key in this.permission) {
            this.permission[key] = exchangetype(this.permission[key])
          }
        })
        .catch(error => {
          util.ajanxerrorcode(this, error)
        });
    }
  };
</script>

