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
      <div class="tool-btn" @click="Print">
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
          <el-menu-item index="1-3" @click="Print">打印（导出为PDF）</el-menu-item>
          <el-menu-item index="1-4">使用说明</el-menu-item>
        </el-submenu>
        <el-submenu index="2">
          <div class="drawer-title-box" slot="title">
            <i class="fa fa-desktop"></i>
            <span>显示</span>
          </div>
          <el-menu-item index="2-1">全屏</el-menu-item>
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
/* 顶部导航栏组件，包含以下部分：
  1. 左侧抽屉导航栏
  2. 图片目录选择、打印及量测按钮
  3. 量测状态栏、取消量测按钮 */

import MeasureDialog from './MeasureDialog'
import {jsPDF} from 'jspdf'
import path from 'path'
import { resolve } from 'url'
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
      isShowDrawer: false, // 是否显示抽屉导航栏
      isShowDialog: false, // 是否显示量测图片选择窗口
      measureInterval: null, // 量测结果查询时间间隔
      measureId: null // 当前量测的Id（用于结果查询）
    }
  },
  computed: {
    isMeasuring () { // 是否正在量测
      return this.$store.state.File.isMeasuring
    }
  },
  mounted () {
    let that = this
    // 测试代码！！！读取并显示本地保存的测量结果，渲染至页面
    fs.readFile('./tmp/xml/result.xml', 'utf-8', (err, res) => {
      let imgList = parser.parse(res)['image-list']['image']
      if (!Array.isArray(imgList)) {
        imgList = [imgList]
      }
      console.log(imgList)
      that.WriteToResultList(2, imgList)
      // that.WriteToResultList(1, imgList) // 正面图待完善
      that.WriteToFileList(1, imgList)
      that.WriteToFileList(2, imgList)
    })
  },
  methods: {
    /* 功能：选择正面图文件夹 */
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
    /* 功能：选择侧面图文件夹 */
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
    /* 功能：关闭量测图片选择窗口 */
    CloseDialog () {
      this.isShowDialog = false
    },
    /* 功能：通过图片选择窗口回传的图片路径数组，将图片逐个以base64格式读取，
            打包为json上传。 */
    StartMeasure (fileDirArr) {
      // let that = this
      // fs.readFile('./tmp/xml/result.xml', 'utf-8', (err, res) => {
      //   let imgList = parser.parse(res)['image-list']['image']
      //   if (!Array.isArray(imgList)) {
      //     imgList = [imgList]
      //   }
      //   console.log(imgList)
      //   that.WriteToResultList(2, imgList)
      //   // that.WriteToResultList(1, imgList) // 正面图待完善
      //   that.WriteToFileList(1, imgList)
      //   that.WriteToFileList(2, imgList)
      // })

      // let that = this
      // let data = window.atob(res.data.data)
      // let imgList = parser.parse(data)['image-list']['image']
      // if (!Array.isArray(imgList)) {
      //   imgList = [imgList]
      // }
      // that.WriteToResultList(2, imgList)
      // // that.WriteToResultList(1, imgList) // 正面图待完善
      // that.WriteToFileList(1, imgList)
      // that.WriteToFileList(2, imgList)

      // let that = this
      // let jsonData = []

      // fileDirArr.forEach(item => {
      //   let data = fs.readFileSync(item)
      //   data = Buffer.from(data).toString('base64')

      //   jsonData.push({
      //     name: item.split('/').pop(),
      //     data: data
      //   })
      // })
      // console.log(jsonData)

      // axios({
      //   method: 'post',
      //   url: 'http://106.75.216.192:12308/image',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'sign': 'spppk'
      //   },
      //   data: jsonData
      // }).then(res => {
      //   if (res.data.error === 0) {
      //     console.log(res.data.data)
      //     let totalTime = 0
      //     let period = 10
      //     that.measureId = res.data.data
      //     that.measureInterval = setInterval(() => {
      //       totalTime += period
      //       axios({
      //         method: 'get',
      //         url: 'http://106.75.216.192:12308/xml?id=' + res.data.data,
      //         headers: {'sign': 'spppk'},
      //         responseType: 'json'
      //       }).then(res => {
      //         console.log(res)
      //         console.log('已耗时' + Math.ceil(totalTime / 60) + '分钟')
      //         if (res.data.error === 0) {
      //           console.log(res.data.data)
      //           let data = window.atob(res.data.data)
      //           let imgList = parser.parse(data)['image-list']['image']
      //           if (!Array.isArray(imgList)) {
      //             imgList = [imgList]
      //           }
      //           that.WriteToResultList(2, imgList)
      //           // that.WriteToResultList(1, imgList) // 正面图待完善
      //           that.WriteToFileList(1, imgList)
      //           that.WriteToFileList(2, imgList)
      //           clearInterval(that.measureInterval)
      //           this.$store.commit('ChangeMeasureState', {isMeasuring: false})
      //           this.$notify.success({
      //             title: '成功',
      //             message: '量测已完成，总耗时' + Math.ceil(totalTime / 60) + '分钟',
      //             duration: 0,
      //             position: 'bottom-left'
      //           })
      //         } else if (res.data.error === '40401') {
      //           // 检测未完成则返回40401错误，继续查找
      //         } else {
      //           throw new Error(1)
      //         }
      //       }).catch(() => {
      //         this.$message.error('量测出错，请稍后重试')
      //         clearInterval(that.measureInterval)
      //         this.$store.commit('ChangeMeasureState', {isMeasuring: false})
      //       })
      //     }, period * 1000)
      //   } else {
      //     throw new Error(1)
      //   }
      // }).catch((e) => {
      //   console.log(e)
      //   this.$message.error('量测出错，请稍后重试')
      //   clearInterval(that.measureInterval)
      //   this.$store.commit('ChangeMeasureState', {isMeasuring: false})
      // })
    },
    /* 功能：将识别结果逐项写入结果列表（用于绘制标注点） */
    WriteToResultList (flag, imgList) {
      let params = flag === 1 ? this.$store.state.File.params1 : this.$store.state.File.params2
      let tempResList = JSON.parse(JSON.stringify(params.resList))
      imgList.forEach(item => {
        if (tempResList.hasOwnProperty(item.name)) {
          tempResList[item.name]['isMeasured'] = true
          tempResList[item.name]['measureRes'] = {
            'sacrum': item.sacrum,
            'femoralhead1': item.femoralhead1,
            'femoralhead2': item.femoralhead2
          }
        }
      })
      this.$store.commit('ChangeResList', {
        flag: flag,
        resList: tempResList
      })
    },
    /* 功能：将识别结果逐项写入文件列表（用于文件列表栏显示） */
    WriteToFileList (flag, imgList) {
      let params = flag === 1 ? this.$store.state.File.params1 : this.$store.state.File.params2
      let tempFileList = JSON.parse(JSON.stringify(params.fileList))
      imgList.forEach(item => {
        if (tempFileList.hasOwnProperty(item.name)) {
          tempFileList[item.name]['isMeasured'] = true
        }
      })
      this.$store.commit('ChangeFileList', {
        flag: flag,
        fileList: tempFileList
      })
    },
    /* 功能：取消量测，停止继续向服务器请求量测结果 */
    CancelMeasure () {
      let that = this
      this.$confirm('此操作将终止量测，是否确定终止?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        clearInterval(that.measureInterval)
        this.$store.commit('ChangeMeasureState', {isMeasuring: false})

        if (that.measureId != null) {
          axios({
            method: 'delete',
            url: 'http://106.75.216.192:12308/cancel?id=' + that.measureId,
            headers: {
              'Content-Type': 'application/json',
              'sign': 'spppk'
            }
          }).then(res => {
            console.log(res)
            that.measureId = null
            clearInterval(cancelInterval)
          })
        }
      })
    },
    /* 功能：将量测结果与图片保存为PDF格式文件 */
    Print () {
      try {
        let filename1 = this.$store.state.File.params1.curFilename.split('.')[0]
        let filename2 = this.$store.state.File.params2.curFilename.split('.')[0]
        let canvasData1 = this.$store.state.File.params1.canvasData
        let canvasData2 = this.$store.state.File.params2.canvasData
        if (canvasData1 !== null && canvasData2 !== null) {
          let pdf = new jsPDF()
          // 待改，尽量写成相对定位
          pdf.addImage(canvasData1, 'JPEG', 20, 15, 249 / 4, 500 / 4)
          pdf.text(filename1, 40, 10)
          pdf.addImage(canvasData2, 'JPEG', 120, 15, 249 / 4, 500 / 4)
          pdf.text(filename2, 140, 10)
          if (this.$store.state.File.curEntireRes !== null) {
            pdf.text('Health Report:', 100, 147)
            let res = this.$store.state.File.curEntireRes
            pdf.text('ss:', 100, 157)
            pdf.text(110, 157, res.ss)
            pdf.text('pt:', 100, 167)
            pdf.text(110, 167, res.pt)
            pdf.text('pi:', 100, 177)
            pdf.text(110, 177, res.pi)
          } else {
            pdf.text('There is No Health Data.', 100, 147)
          }
          let result = dialog.showOpenDialog({
            title: '选择保存路径',
            buttonLabel: '选择路径',
            properties: ['openDirectory', 'showHiddenFiles']
          })
          if (result) {
            let path = result[0] + '/' + filename1 + '_' + filename2 + '.pdf'
            pdf.save(path, {returnPromise: true}).then(this.$message.success('图片结果PDF文件已保存在指定位置'))
          }
        } else {
          throw new Error(1)
        }
      } catch (err) {
        console.log(err)
        this.$message.error('图片打印出错，请稍后重试')
      }
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