<template>
  <div class="tool-header-content">
    <div id="menuBtn" class="tool-btn" @click="isShowDrawer = true">
      <i class="fa fa-bars"></i>
      <span>菜单</span>
    </div>
    <div class="tool-btn-center-group">
      <el-tooltip content="选择正面图文件夹" placement="bottom-start" :open-delay=700>
        <div class="tool-btn"  @click="SelectFrontDir">
            <i class="fa fa-folder-open"></i>
            <span>正面</span>
        </div>
      </el-tooltip>
      <el-tooltip content="选择侧面图文件夹" placement="bottom-start" :open-delay=700>
        <div class="tool-btn"  @click="SelectSideDir">
          <i class="fa fa-folder-open"></i>
          <span>侧面</span>
        </div>
      </el-tooltip>
      <div class="tool-btn" @click="isShowDialog = true">
        <i class="fa fa-play"></i>
        <span>量测</span>
      </div>
      <div class="tool-btn">
        <i class="fa fa-print"></i>
        <span>打印</span>
      </div>
    </div>
    <div class="measure-state-box" :style="{'visibility':isMeasuring?'visible':'hidden'}">
      <i class="fa fa-spinner fa-spin"></i>
      <span>量测中，请稍后</span>
      <el-button @click="CancelMeasure" type="danger" round size="mini">取消</el-button>
    </div>
    <el-drawer direction="ltr" size="18%" :show-close="false" :visible.sync="isShowDrawer">
      <el-menu :unique-opened=true>
        <el-submenu index="1">
          <div class="drawer-title-box" slot="title">
            <i class="fa fa-clipboard"></i>
            <span>文件</span>
          </div>
          <el-menu-item index="1-1" @click="SelectFrontDir">选择正面图文件夹</el-menu-item>
          <el-menu-item index="1-2" @click="SelectSideDir">选择侧面图文件夹</el-menu-item>
          <el-divider></el-divider>
          <el-menu-item index="1-3">打印（导出为PDF）</el-menu-item>
          <el-menu-item index="1-4">使用说明</el-menu-item>
        </el-submenu>
        <el-submenu index="2">
          <div class="drawer-title-box" slot="title">
            <i class="fa fa-desktop"></i>
            <span>显示</span>
          </div>
          <el-menu-item index="2-1">单栏</el-menu-item>
          <el-menu-item index="2-2">双栏</el-menu-item>
          <el-divider></el-divider>
          <el-menu-item index="2-3">全屏</el-menu-item>
        </el-submenu>
        <el-submenu index="3">
          <div class="drawer-title-box" slot="title">
            <i class="fa fa-camera"></i>
            <span>量测</span>
          </div>
          <el-menu-item index="3-1">正侧脊柱</el-menu-item>
          <el-menu-item index="3-2">...</el-menu-item>
        </el-submenu>
        <el-menu-item index="4" class="drawer-title-box">
          <i class="fa fa-cogs"></i>
          <span slot="title">设置</span>
        </el-menu-item>
      </el-menu>
    </el-drawer>
    <measure-dialog :isShowDialog="isShowDialog" @CloseDialog="CloseDialog"
                    @StartMeasure="StartMeasure">
    </measure-dialog>
  </div>
</template>

<script>
/* eslint-disable */
import MeasureDialog from './MeasureDialog'
const {dialog} = require('electron').remote
const fs = require('fs')
const parser = require('fast-xml-parser')
const axios = require('axios')

export default {
  components: {
    'measure-dialog': MeasureDialog
  },
  data () {
    return {
      isShowDrawer: false,
      isShowDialog: false,
      measureInterval: null
    }
  },
  computed: {
    isMeasuring () {
      return this.$store.state.File.isMeasuring
    }
  },
  methods: {
    SelectFrontDir () {
      var result = dialog.showOpenDialog({ // 低版本无promise用法
        title: '选择正面图文件夹',
        buttonLabel: '选择文件夹',
        properties: ['openDirectory', 'showHiddenFiles']
      })
      if (result) {
        this.$store.commit('ChangeDirPath', {
          flag: 1,
          path: result[0]
        })
        this.$store.dispatch('LoadDir', {
          flag: 1,
          path: result[0]
        })
      }
    },
    SelectSideDir () {
      var result = dialog.showOpenDialog({ // 低版本无promise用法
        title: '选择侧面图文件夹',
        buttonLabel: '选择文件夹',
        properties: ['openDirectory', 'showHiddenFiles']
      })
      if (result) {
        this.$store.commit('ChangeDirPath', {
          flag: 2,
          path: result[0]
        })
        this.$store.dispatch('LoadDir', {
          flag: 2,
          path: result[0]
        })
      }
    },
    CloseDialog () {
      this.isShowDialog = false
    },
    StartMeasure (seletedArr) {
      let that = this
      let jsonData = []
      seletedArr.forEach(item => {
        let data = fs.readFileSync(item)
        data = Buffer.from(data).toString('base64')
        jsonData.push({
          name: item.split('/').pop(),
          data: data
        })
      })
      axios({
        method: 'post',
        url: 'http://api.zerokirin.online/oims/image',
        headers: {
          'Content-Type': 'application/json',
          'sign': 'spppk'
        },
        data: jsonData
      }).then(res => {
        if (res.data.error === 0) {
          // url参数id待改
          let totalTime = 0
          that.measureInterval = setInterval(() => {
            totalTime += 3
            axios({
              method: 'get',
              url: 'http://api.zerokirin.online/oims/xml?id=123',
              headers: {'sign': 'spppk'},
              responseType: 'json'
            }).then(res => {
              if (res.data.error === 0) {
                that.WriteToResultList(2, window.atob(res.data.data))
                // that.WriteToResultList(1, window.atob(res.data.data)) // 正面图待完善
                clearInterval(that.measureInterval)
                this.$store.commit('ChangeMeasureState', {isMeasuring: false})
                this.$notify.success({
                  title: '成功',
                  message: '量测已完成，总耗时' + Math.ceil(totalTime / 60) + '分钟',
                  duration: 3500,
                  position: 'bottom-left'
                })
              } else {
                throw new Error(1)
              }
            }).catch((err) => {
              console.log(err)
              this.$message.error('量测出错，请稍后重试')
              clearInterval(that.measureInterval)
            })
          }, 3000)
        } else {
          throw new Error(1)
        }
      }).catch(() => {
        this.$message.error('量测出错，请稍后重试')
        clearInterval(that.measureInterval)
      })
    },
    WriteToResultList (flag, data) {
      let params = flag === 1 ? this.$store.state.File.params1 : this.$store.state.File.params2
      let tempResList = JSON.parse(JSON.stringify(params.resList))
      let imgList = parser.parse(data)['image-list']['image']
      if (!Array.isArray(imgList)) {
        imgList = [imgList]
      }
      imgList.forEach(item => {
        tempResList[item.name]['isMeasured'] = true
        tempResList[item.name]['measureRes'] = {
          'sacrum': item.sacrum,
          'femoralhead1': item.femoralhead1,
          'femoralhead2': item.femoralhead2
        }
      })
      this.$store.commit('ChangeResList', {
        flag: flag,
        resList: tempResList
      })
    },
    CancelMeasure () {
      let that = this
      this.$confirm('此操作将终止量测，是否确定终止?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        clearInterval(that.measureInterval)
        this.$store.commit('ChangeMeasureState', {isMeasuring: false})
      })
    }
  }
}
</script>

<style lang="less">
  .tool-header-content{
    background: #1a1b21;
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }
  
  // 顶部工具栏
  @tool_header_height: 52px;
  .tool-btn{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: white;
    cursor: pointer;
    height: @tool_header_height;
    width: @tool_header_height + 30;
  }
  .tool-btn:hover{
    background: #5b5c61;
  }
  .tool-btn>i{
    zoom: 1.5;
    margin-bottom: 1px;
  }
  .tool-btn>span{
    font-size: 0.75rem;
    font-weight: lighter;
  }
  .tool-btn-center-group{
    margin-right: 20%;
    display: flex;
  }

  // 抽屉导航栏
  .drawer-title-box>span{
    font-size: 1.1rem;
    font-weight: bold;
  }
  .drawer-title-box>i{
    zoom: 1.2;
    margin-right: 5px;
  }

  // 量测状态栏
  .measure-state-box{
    color: rgb(218, 218, 218);
    font-size: 0.9rem;
    padding-right: 2%;
  }
  .measure-state-box>button{
    padding: 5px 10px !important;
    margin-left: 5px;
  }
</style>