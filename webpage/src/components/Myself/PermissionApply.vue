<!--<style lang="less">-->
  <!--@import './own-space.less';-->
<!--</style>-->

<template>
  <div>
    <Card>
      <p slot="title">
        <Icon type="key"></Icon>
        权限申请
      </p>
      <div>
        <Form  :label-width="150" :Input-width="300" label-position="right">
          <FormItem label="用户">
            <Input v-model="userInfo.username" readonly="readonly" style="width: 200px;"></Input>
          </FormItem>
          <FormItem label="权限">
            <Select v-model="userInfo.curGroup" placeholder="请选择" style="width: 200px;">
              <Option v-for="item in userInfo.groupList" :value="item.key" :key="item.key" >{{ item.value }}</Option>
            </Select>
          </FormItem>
          <FormItem label="指定审核人">
            <Select v-model="userInfo.curAuditor" placeholder="请选择" style="width: 200px;" :rules="auditorsValidate">
              <Option v-for="item in userInfo.auditors" :value="item" :key="item" >{{ item }}</Option>
            </Select>
          </FormItem>
          <template>
            <hr style="height:1px;border:none;border-top:1px dashed #dddee1;" />
            <br>
            <FormItem label="DDL权限:">
              <RadioGroup v-model="permission.ddl">
                <Radio label="1">是</Radio>
                <Radio label="0">否</Radio>
              </RadioGroup>
            </FormItem>
            <template v-if="permission.ddl === '1'">
              <FormItem label="连接名:">
                <CheckboxGroup v-model="permission.ddlcon">
                  <Checkbox  v-for="i in this.con" :label="i" :key="i">{{i}}</Checkbox>
                </CheckboxGroup>
              </FormItem>
            </template>
            <hr style="height:1px;border:none;border-top:1px dashed #dddee1;" />
            <br>
            <FormItem label="DML权限:">
              <RadioGroup v-model="permission.dml">
                <Radio label="1">是</Radio>
                <Radio label="0">否</Radio>
              </RadioGroup>
            </FormItem>
            <template v-if="permission.dml === '1'">
              <FormItem label="连接名:">
                <CheckboxGroup v-model="permission.dmlcon">
                  <Checkbox  v-for="i in this.con" :label="i" :key="i">{{i}}</Checkbox>
                </CheckboxGroup>
              </FormItem>
            </template>
            <hr style="height:1px;border:none;border-top:1px dashed #dddee1;" />
            <br>
            <FormItem label="字典权限:">
              <RadioGroup v-model="permission.dic">
                <Radio label="1">是</Radio>
                <Radio label="0">否</Radio>
              </RadioGroup>
            </FormItem>
            <template v-if="permission.dic === '1'">
              <FormItem label="修改权限:">
                <RadioGroup v-model="permission.dicedit">
                  <Radio label="1">是</Radio>
                  <Radio label="0">否</Radio>
                </RadioGroup>
              </FormItem>
              <FormItem label="导出权限:">
                <RadioGroup v-model="permission.dicexport">
                  <Radio label="1">是</Radio>
                  <Radio label="0">否</Radio>
                </RadioGroup>
              </FormItem>
              <FormItem label="连接名:">
                <CheckboxGroup v-model="permission.dicCon">
                  <Checkbox  v-for="i in this.dicadd" :label="i" :key="i">{{i}}</Checkbox>
                </CheckboxGroup>
              </FormItem>
            </template>
            <hr style="height:1px;border:none;border-top:1px dashed #dddee1;" />
            <br>
            <FormItem label="查询权限:">
              <RadioGroup v-model="permission.query">
                <Radio label="1">是</Radio>
                <Radio label="0">否</Radio>
              </RadioGroup>
            </FormItem>
            <template v-if="permission.query === '1'">
              <FormItem label="连接名:">
                <CheckboxGroup v-model="permission.querycon">
                  <Checkbox  v-for="i in this.con" :label="i" :key="i">{{i}}</Checkbox>
                </CheckboxGroup>
              </FormItem>
            </template>
          </template>
          <template v-if="this.userInfo.curGroup === 'admin'">
            <hr style="height:1px;border:none;border-top:1px dashed #dddee1;" />
            <br>
            <FormItem label="用户管理权限:">
              <RadioGroup v-model="permission.user">
                <Radio label="1">是</Radio>
                <Radio label="0">否</Radio>
              </RadioGroup>
            </FormItem>
            <hr style="height:1px;border:none;border-top:1px dashed #dddee1;" />
            <br>
            <FormItem label="数据库管理权限:">
              <RadioGroup v-model="permission.base">
                <Radio label="1">是</Radio>
                <Radio label="0">否</Radio>
              </RadioGroup>
            </FormItem>
          </template>
          <FormItem label="备注">
            <Input v-model="textarea" type="textarea" :autosize="{minRows: 2,maxRows: 5}" style="width: 400px;" placeholder="Enter something..."></Input>
          </FormItem>
        </Form>
        <div slot="footer">
          <Button type="primary" @click="saveInfo">保存</Button>
        </div>
      </div>
    </Card>
  </div>
</template>

<script>
  import Cookies from 'js-cookie'
  import util from '../../libs/util'
  import axios from 'axios'
  export default {
    name: 'permission_apply',
    data () {
      return {
        con: [],
        dicadd: [],
        textarea: '',
        userInfo: {
          username: Cookies.get('user'),
          curGroup: '',
          curAuditor: '',
          auditors: [],
          groupList: [
            {key: 'admin', value: '管理员'},
            {key: 'guest', value: '使用者'}
          ]
        },
        permission: {
          ddl: '0',
          dml: '0',
          dic: '0',
          dicedit: '0',
          dicexport: '0',
          query: '0',
          user: '0',
          base: '0',
          ddlcon: [],
          dmlcon: [],
          diccon: [],
          querycon: [],
          person: []
        },
        auditorsValidate: {
          curAuditor: {
            required: true,
            message: '请输入审核人名',
            trigger: 'blur'
          }
        }
      };
    },
    methods: {
      saveInfo () {
        this.permission.person = [this.userInfo.curAuditor];
        axios.post(util.url + '/userpermission/', {
          'user': this.userInfo.username,
          'group': this.userInfo.curGroup,
          'department': '',
          'permission': JSON.stringify(this.permission),
          'text': this.textarea,
          'auditor': this.userInfo.curAuditor
        })
          .then(res => {
            this.$Notice.success({
              title: '通知',
              desc: res.data
            })
            this.refreshuser()
          })
          .catch(error => {
            util.ajanxerrorcode(this, error)
          })
        this.editInfodModal = false
      }
  },
    mounted () {
      axios.get(`${util.url}/userpermission/order?user=${Cookies.get('user')}`)
        .then(res => {
          this.permission = res.data.permission;
          this.userInfo.username = res.data.username;
          this.userInfo.curGroup = res.data.group;
          this.con = res.data.con;
          this.dicadd = res.data.dicadd;
          this.userInfo.curAuditor = res.data.permission.person[0];
          this.userInfo.auditors = res.data.audituser;
        })
        .catch(error => {
          this.$Notice.error({
            title: '警告',
            desc: error
          })
        })
    }
  };
</script>
