<style lang="less">
  @import '../../styles/common.less';
  @import '../Order/components/table.less';
</style>

<template>
  <div>
    <Row>
      <Col span="4">
      <Card>
        <p slot="title">
          <Icon type="ios-redo"></Icon>
          选择数据库
        </p>
        <div class="edittable-test-con">
          <div id="showImage" class="margin-bottom-10">

            <Form ref="formItem" :model="formItem" :rules="ruleValidate" :label-width="80">
              <FormItem label="连接名:" prop="connection_name">
                <Select v-model="formItem.connection_name" @on-change="DataBaseName" filterable>
                  <Option v-for="i in datalist.connection_name_list" :value="i" :key="i">{{ i }}</Option>
                </Select>
              </FormItem>

              <FormItem label="库名:" prop="basename">
                <Select v-model="formItem.basename" @on-change="chooseLibrary"  filterable >
                  <Option v-for="item in datalist.basenamelist" :value="item" :key="item">{{ item }}</Option>
                </Select>
              </FormItem>
            </Form>
            <Alert style="height: 145px">
              SQL查询注意事项:
              <template slot="desc">
                <p>1.选择对应的数据库</p>
                <p>2.输入相应select语句</p>
                <p>注意:只支持select语句,其他语句统统不可达!</p>
              </template>
            </Alert>
          </div>
        </div>
      </Card>
      </Col>
      <Col span="20" class="padding-left-10">
      <Card>
        <p slot="title">
          <Icon type="ios-crop-strong"></Icon>
          填写sql语句
        </p>
        <editor v-model="sql" @init="editorInit"></editor>
        <br>
        <br>
        <Button type="error" icon="trash-a" @click.native="ClearForm()">清除</Button>
        <Button type="info" icon="paintbucket" @click.native="beautify()">美化</Button>
        <Button type="success" icon="android-refresh" @click.native="CheckSql()">检测</Button>
        <Button type="primary" icon="ios-redo":disabled="this.disabled_commit" @click.native="submitOrder()">提交工单</Button>
        <br>
        <br>
        <Alert v-model="check_error_msg" v-if="check_error_msg" style="width: 400px" type="error">{{ check_error_msg }}</Alert>
      </Card>
      </Col>
    </Row>

    <Modal v-model="modal_commit" @on-ok="commitorder" :ok-text="'提交工单'" width="800">
      <Row>
        <Card>
          <div class="step-header-con">
            <h3 style="margin-left: 35%">SQL平台审核工单</h3>
          </div>
          <p class="step-content"></p>
          <Form class="step-form" :label-width="100">
            <FormItem label="用户名:">
              <p>{{username}}</p>
            </FormItem>
            <FormItem label="数据库库名:">
              <p>{{formItem.basename}}</p>
            </FormItem>
            <FormItem label="执行SQL:">
              <p>{{sql}}</p>
            </FormItem>
            <FormItem label="工单提交说明:" required>
              <Input v-model="formItem.text" placeholder="最多不超过20个字"></Input>
            </FormItem>
            <FormItem label="指定审核人:" required>
              <Select v-model="formItem.assigned" filterable transfer>
                <Option v-for="i in assigned" :value="i" :key="i">{{i}}</Option>
              </Select>
            </FormItem>
            <FormItem label="确认提交：" required>
              <Checkbox v-model="pass">确认</Checkbox>
            </FormItem>
          </Form>
        </Card>
      </Row>
    </Modal>

  </div>
</template>
<script>
  import Cookies from 'js-cookie'
  import ICol from '../../../node_modules/iview/src/components/grid/col.vue'
  import axios from 'axios'
  import util from '../../libs/util'
//  import Csv from '../../../node_modules/iview/src/utils/csv'
//  import ExportCsv from '../../../node_modules/iview/src/components/table/export-csv';
  export default {
  components: {
      ICol,
      editor: require('../../libs/editor')
    },
    name: 'SearchSQL',
    data () {
      return {
        validate_gen: true,
        formItem: {
          connection_name: '',
          basename: '',
          text: '',
          assigned: '',
          backup: '0'
        },
        Testresults: [],
        item: {},
        datalist: {
          connection_name_list: [],
          basenamelist: [],
          sqllist: [],
          computer_roomlist: util.computer_room
        },
        ruleValidate: {
          connection_name: [{
            required: true,
            message: '连接名不得为空',
            trigger: 'change'
          }],
          basename: [{
            required: true,
            message: '数据库名不得为空',
            trigger: 'change'
          }]
        },
        id: null,
        total: 0,
        allsearchdata: [],
        limitPrompt: '',
        limitStyle: {
          color: 'red',
          fontSize: '13px'
        },
        disabled_commit: true,
        modal_commit: false,
        check_error_msg: '',
        username: Cookies.get('user'),
        assigned: [],
        pass: false,
        sql: ''
      }
    },
    methods: {
      editorInit: function () {
        require('brace/mode/mysql')
        require('brace/theme/xcode')
      },
      beautify () {
        axios.put(`${util.url}/sqlsyntax/beautify`, {
          'data': this.sql
        })
          .then(res => {
            this.sql = res.data
          })
          .catch(error => {
            this.$Notice.error({
              title: '警告',
              desc: error
            })
          })
      },
      splice_arr (page) {
        this.Testresults = this.allsearchdata.slice(page * 10 - 10, page * 10)
      },
      Connection_Name (val) {
        this.datalist.connection_name_list = []
        this.datalist.basenamelist = []
        this.formItem.connection_name = ''
        this.formItem.basename = ''
        if (val) {
          this.ScreenConnection(val)
        }
      },
      ScreenConnection (val) {
        this.datalist.connection_name_list = this.item.filter(item => {
          if (item.computer_room === val) {
            return item
          }
        })
      },
      DataBaseName (index) {
        if (index) {
          this.id = this.item.filter(item => {
            if (item.connection_name === index) {
              return item
            }
          })
          axios.put(`${util.url}/workorder/basename`, {
            'id': this.id[0].id
          })
            .then(res => {
              this.datalist.basenamelist = res.data
            })
            .catch(() => {
              this.$Notice.error({
                title: '警告',
                desc: '无法连接数据库!请检查网络'
              })
            })
        }
      },
      ClearForm () {
        this.sql = ''
        this.Testresults = []
        this.$refs.totol.currentPage = 1
        this.total = 0
      },
      CheckSql () {
        let address = {
          'id': this.id[0].id,
          'basename': this.formItem.basename
        }
        axios.post(`${util.url}/search`, {
          'sql': this.sql,
          'address': JSON.stringify(address)
        })
          .then(res => {
            if (res.data['error']) {
              this.check_error_msg = res.data['error'];
              this.disabled_commit = true
              this.$Notice.error({
                title: '错误',
                desc: res.data['error']
              })
            } else {
              this.disabled_commit = false
              this.check_error_msg = '';
            }
          })
          .catch(error => {
            util.ajanxerrorcode(this, error)
          })
      },
      submitOrder () {
        this.modal_commit = true
        console.log(this.formItem)
        console.log(this.datalist)
      },
      commitorder () {
        if (this.sql === [] || this.formItem.basename === '' || this.assigned === '' || this.formItem.text === '' || this.formItem.assigned === '') {
          this.$Notice.error({
            title: '警告',
            desc: '工单数据缺失,请检查工单信息是否缺失!'
          })
        } else {
          if (this.pass === true) {
            axios.post(`${util.url}/sqlsyntax/`, {
              'data': JSON.stringify(this.formItem),
              'sql': JSON.stringify([this.sql]),
              'user': Cookies.get('user'),
              'type': 2,
              'id': this.id[0].id
            })
              .then(res => {
                this.$Notice.success({
                  title: '通知',
                  desc: res.data
                })
                this.$router.push({
                  name: 'myorder'
                })
              }).catch(error => {
              util.ajanxerrorcode(this, error)
            })
          } else {
            this.$Notice.warning({
              title: '注意',
              desc: '提交工单需点击确认按钮'
            })
          }
        }
      },
      chooseLibrary () {

      }
    },
    mounted () {
      axios.put(`${util.url}/workorder/connection`, {'permissions_type': 'query'})
        .then(res => {
          this.item = res.data['connection']
          this.assigned = res.data['assigend']
          this.datalist.connection_name_list = res.data.database;
        })
        .catch(error => {
          util.ajanxerrorcode(this, error)
        });
    }
  }
</script>
