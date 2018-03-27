<style lang="less">
@import '../../styles/common.less';
@import '../Order/components/table.less';
</style>
<template>
<div>
  <Row>
    <Card>
      <Select v-model="select_tab" slot="title" style="width:200px" @on-change="selectChangeOrder">
        <Option value="order" >SQL工单</Option>
        <Option value="sql" >导出工单</Option>
        <Option value="permission" >权限工单</Option>
      </Select>
      <Select v-model="select_user" slot="extra" style="width:200px" @on-change="selectChangeUser">
        <Option v-for="name in users" :value="name" :key="name" >{{ name }}</Option>
      </Select>
      <Row>
        <Col span="24">
        <Table border :columns="columns_title" :data="table_data" stripe size="small"></Table>
        </Col>
      </Row>
      <br>
      <Page :total="page_number" show-elevator @on-change="currentpage" ></Page>
    </Card>
  </Row>
</div>
</template>
<script>
import Cookies from 'js-cookie'
import axios from 'axios'
import util from '../../libs/util'
export default {
  name: 'put',
  data () {
    return {
      page_number: 1,
      cur_page: 1,
      users: [],
      table_data: [],
      select_tab: 'order',
      select_user: '',
      columns_title: []
//      computer_room: util.computer_room,
//      applytable: [],
//      openswitch: false,
//      modaltext: {},
//      editsql: ''
    }
  },
  methods: {
    currentpage (page = 1) {
      this.request_server(page, this.select_tab, this.select_user)
    },
    selectChangeUser (user) {
      this.request_server(1, this.select_tab, user)
    },
    selectChangeOrder (tab) {
      this.request_server(1, tab, this.select_user)
    },
    request_server (page, tab, user) {
      this.update_table_title(tab)
      if (tab === 'order' || tab === 'sql') {
        let type = -1;
        if (tab === 'sql') {
          type = 2
        }
        axios.get(`${util.url}/myorder/?user=${Cookies.get('user')}&page=${page}&filter_name=${user}&type=${type}`)
          .then(res => {
            this.table_data = res.data.data;
            this.table_data.forEach((item) => { (item.backup === 1) ? item.backup = '是' : item.backup = '否' });
            this.page_number = parseInt(res.data.page.alter_number);
            this.users = res.data.users
          })
          .catch(error => {
            util.ajanxerrorcode(this, error)
          })
      } else if (tab === 'permission') {
        this.table_data = []
        axios.get(`${util.url}/userpermission/ordercommit?user=${Cookies.get('user')}&page=${page}&filter_name=${user}`)
          .then(res => {
            this.table_data = res.data.data;
            this.page_number = parseInt(res.data.page.alter_number);
            this.users = res.data.users
          })
          .catch(error => {
            util.ajanxerrorcode(this, error)
          })
      }
    },
    update_table_title (tab) {
      if (tab === 'permission') {
        this.columns_title = [
          {
            title: '工单编号:',
            key: 'id',
            sortable: true
          }, {
            title: '工单说明',
            key: 'text'
          }, {
            title: '提交时间:',
            key: 'datetime',
            sortable: true
          }, {
            title: '用户组',
            key: 'usergroup'
          }, {
            title: '提交人',
            key: 'username',
            sortable: true
          }, {
            title: '状态',
            key: 'status',
            render: (h, params) => {
              const row = params.row;
              let color = '';
              let text = '';
              if (row.status === 0) {
                color = 'red';
                text = '拒绝'
              } else if (row.status === 1) {
                color = 'blue';
                text = '审核中'
              } else if (row.status === 2) {
                color = 'blue';
                text = '执行中'
              } else if (row.status === 3) {
                color = 'green';
                text = '完成'
              }
              return h('Tag', {
                props: {
                  type: 'dot',
                  color: color
                }
              }, text)
            },
            sortable: true,
            filters: [
              {
                label: '完成',
                value: 3
              }, {
                label: '拒绝',
                value: 0
              }, {
                label: '审核中',
                value: 1
              }, {
                label: '执行中',
                value: 2
              }
            ],
            //            filterMultiple: false 禁止多选,
            filterMethod (value, row) {
              if (value === 1) {
                return row.status === 1
              } else if (value === 0) {
                return row.status === 0
              } else if (value === 2) {
                return row.status === 2
              } else if (value === 3) {
                return row.status === 3
              }
            }
          },
          {
            title: '操作',
            key: 'action',
            align: 'center',
            render: (h, params) => {
              return h('div', [
                h('Button', {
                  props: {
                    size: 'small',
                    type: 'text'
                  },
                  on: {
                    click: () => {
                      this.$router.push({
                        name: 'permissiondetail',
                        query: {id: params.row.id}
                      })
                    }
                  }
                }, '详细信息')
              ])
            }
          }
        ]
      } else if (tab === 'order' || tab === 'sql') {
        this.columns_title = [
          {
            title: '工单编号:',
            key: 'work_id',
            sortable: true
          },
          {
            title: '工单说明',
            key: 'text'
          },
          {
            title: '是否备份',
            key: 'backup'
          },
          {
            title: '提交时间:',
            key: 'date',
            sortable: true
          },
          {
            title: '提交人',
            key: 'username',
            sortable: true
          },
          {
            title: '状态',
            key: 'status',
            render: (h, params) => {
              const row = params.row
              let color = ''
              let text = ''
              if (row.status === 2) {
                color = 'blue'
                text = '审核中'
              } else if (row.status === 0) {
                color = 'red'
                text = '拒绝'
              } else if (row.status === 1) {
                color = 'green'
                text = '同意'
              } else {
                color = 'yellow'
                text = '进行中'
              }

              return h('Tag', {
                props: {
                  type: 'dot',
                  color: color
                }
              }, text)
            },
            sortable: true,
            filters: [{
              label: '同意',
              value: 1
            },
              {
                label: '拒绝',
                value: 0
              },
              {
                label: '审核中',
                value: 2
              },
              {
                label: '进行中',
                value: 3
              }
            ],
            //            filterMultiple: false 禁止多选,
            filterMethod (value, row) {
              if (value === 1) {
                return row.status === 1
              } else if (value === 0) {
                return row.status === 0
              } else if (value === 2) {
                return row.status === 2
              } else if (value === 3) {
                return row.status === 3
              }
            }
          }
        ];
        if (tab === 'order') {
            this.columns_title.push({
              title: '操作',
              key: 'action',
              align: 'center',
              render: (h, params) => {
                return h('div', [
                  h('Button', {
                    props: {
                      size: 'small',
                      type: 'text'
                    },
                    on: {
                      click: () => {
                        this.$router.push({
                          name: 'orderlist',
                          query: {workid: params.row.work_id, id: params.row.id, status: params.row.status, type: params.row.type}
                        })
                      }
                    }
                  }, '详细信息')
                ])
              }
            })
        } else {
          this.columns_title.push({
            title: '操作',
            key: 'action',
            align: 'center',
            render: (h, params) => {
              return h('div', [
                h('Button', {
                  props: {
                    size: 'small',
                    type: 'text'
                  },
                  on: {
                    click: () => {
                      this.$router.push({
                        name: 'exportsqldetail',
                        query: {data: params.row}
                      })
                    }
                  }
                }, '详细信息')
              ])
            }
          })
        }
      }
    }
  },
  mounted () {
    this.currentpage();
  }
}
</script>
<!-- remove delete request -->
