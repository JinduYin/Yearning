<style lang="less">
  @import '../../styles/common.less';
  @import 'components/table.less';
</style>
<template>
  <div>
    <Card>
      <p slot="title" style="height: 45px">
        <Icon type="android-send"></Icon>
        导出SQL工单详细信息
        <br>
        <Button type="text"  @click.native="$router.go(-1)">返回</Button>
      </p>
      <div>
        <Form ref="orderInfo" :model="orderInfo" :label-width="200" label-position="right">
          <FormItem label="工单号：">
            <div style="display:inline-block;width:300px;">
              <span>{{ orderInfo.work_id }}</span>
            </div>
          </FormItem>
          <FormItem label="用户名：">
            <span>{{ orderInfo.username }}</span>
          </FormItem>
          <FormItem label="提交时间：">
            <span>{{ orderInfo.date }}</span>
          </FormItem>
          <FormItem label="数据库">
            <span>{{ orderInfo.basename }}</span>
          </FormItem>
        </Form>
        <hr style="height:1px;border:none;border-top:1px dashed #dddee1;" />
        <br>
        <Form ref="orderInfo" :model="orderInfo" :label-width="200" label-position="right">
          <FormItem label="执行时间:">
            <p>{{ recordInfo.date }}</p>
          </FormItem>
          <FormItem label="SQL语句:">
            <p>{{ recordInfo.sql }}</p>
          </FormItem>
          <FormItem label="影响行数:">
            <p>{{ recordInfo.affectrow }}</p>
          </FormItem>
          <FormItem label="执行耗时:">
            <p>{{ recordInfo.execute_time }}</p>
          </FormItem>
          <FormItem label="文件名:">
            <p>{{ recordInfo.file_name }}</p>
          </FormItem>
          <FormItem label="状态:">
            <p>{{ recordInfo.state }}</p>
          </FormItem>
          <FormItem label="错误:">
            <p>{{ recordInfo.error }}</p>
          </FormItem>
        </Form>
      </div>
      <Button icon="ios-cloud-download-outline" type="success" @click="download_file()" style="margin-left: 3%; width: 150px">下载</Button>
    </Card>
  </div>
</template>

<script>
//  import Cookies from 'js-cookie'
  import util from '../../libs/util'
  import axios from 'axios'
  export default {
    name: 'permission-detail',
    data () {
      return {
        orderInfo: {
          work_id: '',
          username: '',
          date: '',
          basename: ''
        },
        recordInfo: {
          date: '',
          sql: '',
          affectrow: '',
          execute_time: '',
          file_name: '',
          state: '',
          error: ''
        },
        data: ''
      };
    },
    methods: {
      download_file () {
        document.location.href = 'http://127.0.0.1:8000/api/v1/export/?file_name=201803231550099207_2018-03-23_17-26-48.xls';
      }
    },
    mounted () {
      this.data = this.$route.query.data;
      this.orderInfo = this.$route.query.data;
      axios.get(`${util.url}/detail?id=${this.data.id}&workid=${this.data.work_id}&status=1`)
        .then(res => {
          if (res.data.data.length >= 1) {
            this.recordInfo = res.data.data[0]
          }
        })
        .catch(error => {
          util.ajanxerrorcode(this, error)
        });
    }
  };
</script>

