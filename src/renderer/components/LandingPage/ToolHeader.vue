<template>
  <div class="tool-header-content">
    <div id="menuBtn" class="tool-btn" @click="isShowDrawer = true">
      <i class="fa fa-bars"></i>
      <span>菜单</span>
    </div>
    <div class="tool-btn-center-group">
      <el-tooltip content="选择正面图文件夹" placement="bottom-start" :open-delay=700>
        <div class="tool-btn"  @click="SelectDir(1)">
            <i class="fa fa-folder-open"></i>
            <span>正面</span>
        </div>
      </el-tooltip>
      <el-tooltip content="选择侧面图文件夹" placement="bottom-start" :open-delay=700>
        <div class="tool-btn"  @click="SelectDir(2)">
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
          <el-menu-item index="1-1" @click="SelectDir(1)">选择正面图文件夹</el-menu-item>
          <el-menu-item index="1-2" @click="SelectDir(2)">选择侧面图文件夹</el-menu-item>
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
import { Addfont } from '../../../../static/font'
const {dialog} = require('electron').remote
const fs = require('fs')
const parser = require('fast-xml-parser')
const axios = require('axios')
const he = require('he')

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
  methods: {
    /* 功能：选择正侧面图文件夹 */
    SelectDir (flag) {
      let title = flag == 1 ? '选择正面图文件夹' : '选择侧面图文件夹'
      var result = dialog.showOpenDialog({ // 低版本无promise用法
        title: title,
        buttonLabel: '选择文件夹',
        properties: ['openDirectory', 'showHiddenFiles']
      })
      if (result) {
        this.$store.commit('ChangeDirPath', {
          flag: flag,
          path: result[0]
        })
        this.$store.dispatch('LoadDir', {
          flag: flag,
          path: result[0]
        }).then(() => {
          this.$store.dispatch('ChangeCurFilenameToTheFirst', {flag: flag})
        })
      }
    },

    /* 功能：关闭量测图片选择窗口 */
    CloseDialog () {
      this.isShowDialog = false
    },

    /* 功能：将关键点信息以xml格式存入本地文件 */
    WriteToLocalFile (imgList, xmlPath) {
      if (Object.keys(imgList).length != 0){
        let obj = {
          'image-list': imgList
        }
        let j2xml = new parser.j2xParser()
        let xml = j2xml.parse(obj, {})
        fs.writeFile(xmlPath, xml, (err) => {})
      }
    },

    /* 功能：将关键点信息提交至全局变量，并将当前打开图片设置为列表第一项 */
    EditTwoListToGlobal (flag, fileList, resList) {
      this.$store.commit('ChangeResList', {
        flag: flag,
        resList: resList
      })
      this.$store.commit('ChangeFileList', {
        flag: flag,
        fileList: fileList
      })
      this.$store.dispatch('ChangeCurFilenameToTheFirst', {flag: flag})
    },

    /* 功能：将正面图识别结果先进行还原，再提取关键点。
        将关键点信息存入resultList与本地文件，并在fileList中标注是否量测  */
    WriteFrontResult(imgList) {
      let scale = this.$store.state.File.preprocessScale
      let params = this.$store.state.File.params1
      let tempResList = JSON.parse(JSON.stringify(params.resList))  // 创建副本，进行修改
      let tempFileList = JSON.parse(JSON.stringify(params.fileList))  // 创建副本，进行修改
      let tempImgList = {}     // 用于存放保存至本地的正面图数据
      
      imgList.forEach(item => {
        if(item.name[0] == 'f') { // 正面图文件名前带有"f_"的前缀
          let filename = item.name.split('_')[1]
          if (tempResList.hasOwnProperty(filename)) {
            item.name = filename    // 删去标志正侧图的前缀

            // 冠状位参数相关点定义
            let p0 = null
            let p1 = null
            let p2 = null
            let p3 = null
            let p4 = null
            let p5 = null
            let p6 = null
            let p7 = null

            if(item.hasOwnProperty('sacrum')){
              let sXmin = Number.parseInt(item.sacrum.xmin * scale)
              let sYmin = Number.parseInt(item.sacrum.ymin * scale)
              let sXmax = Number.parseInt(item.sacrum.xmax * scale)
              let sYmax = Number.parseInt(item.sacrum.ymax * scale)
              p0 = [sXmin, sYmin]
              p1 = [sXmax, sYmax]
            }

            if(item.hasOwnProperty('cobb1')){
              let cXmin = Number.parseInt(item.cobb1.xmin * scale)
              let cYmin = Number.parseInt(item.cobb1.ymin * scale)
              let cXmax = Number.parseInt(item.cobb1.xmax * scale)
              let cYmax = Number.parseInt(item.cobb1.ymax * scale)
              p2 = [cXmin, cYmin]
              p3 = [cXmax, cYmax]
            }

            if(item.hasOwnProperty('cobb2')){
              let cXmin = Number.parseInt(item.cobb2.xmin * scale)
              let cYmin = Number.parseInt(item.cobb2.ymin * scale)
              let cXmax = Number.parseInt(item.cobb2.xmax * scale)
              let cYmax = Number.parseInt(item.cobb2.ymax * scale)
              p4 = [cXmin, cYmin]
              p5 = [cXmax, cYmax]
            }

            if(item.hasOwnProperty('c7')){
              let cXmin = Number.parseInt(item.c7.xmin * scale)
              let cYmin = Number.parseInt(item.c7.ymin * scale)
              let cXmax = Number.parseInt(item.c7.xmax * scale)
              let cYmax = Number.parseInt(item.c7.ymax * scale)
              p6 = [cXmin, cYmin]
              p7 = [cXmax, cYmax]
            }
            
            
            let frontRes = {
              p0: p0, p1: p1, p2: p2, p3: p3, p4: p4, p5: p5,
              p6: p6, p7: p7
            }

            tempImgList[filename] = frontRes

            tempFileList[filename]['isMeasured'] = true

            tempResList[filename]['isParsed'] = true
            tempResList[filename]['isScaled'] = false
            tempResList[filename].originParseRes.frontRes = frontRes
            tempResList[filename].displayParseRes.frontRes = frontRes
          }
        }
      })

       // 修改两个列表
      this.EditTwoListToGlobal(1, tempFileList, tempResList)
      // 将修改后的以xml格式数据保存本地
      this.WriteToLocalFile(tempImgList, params.resXmlPath)
    },

    /* 功能：将侧面图识别结果先进行还原，再提取关键点。
        将关键点信息存入resultList与本地文件，并在fileList中标注是否量测 */
    WriteSideResult(imgList) {
      let scale = this.$store.state.File.preprocessScale
      let params = this.$store.state.File.params2
      let tempResList = JSON.parse(JSON.stringify(params.resList))  // 创建副本，进行修改
      let tempFileList = JSON.parse(JSON.stringify(params.fileList))  // 创建副本，进行修改
      let tempImgList = {}     // 用于存放保存至本地的侧面图数据
      
      
      imgList.forEach(item => {
        if(item.name[0] == 's') { // 侧面图文件名前带有"s_"的前缀
          let filename = item.name.split('_')[1]
          if (tempResList.hasOwnProperty(filename)) {
            item.name = filename    // 删去标志正侧图的前缀

            // 骨盆参数相关点定义
            let p0 = null
            let p1 = null
            let p2 = null
            let p3 = null
            let p4 = null
            let p5 = null

            // 矢状位参数相关点定义
            let p6 = null
            let p7 = null
            let p8 = null
            let p9 = null

            if(item.hasOwnProperty('sacrum')){
              let sXmin = Number.parseInt(item.sacrum.xmin * scale)
              let sYmin = Number.parseInt(item.sacrum.ymin * scale)
              let sXmax = Number.parseInt(item.sacrum.xmax * scale)
              let sYmax = Number.parseInt(item.sacrum.ymax * scale)
              p0 = [sXmin, sYmin]
              p1 = [sXmax, sYmax]
            }

            if(item.hasOwnProperty('femoralhead1')){
              let f1Xmin = Number.parseInt(item.femoralhead1.xmin * scale)
              let f1Ymin = Number.parseInt(item.femoralhead1.ymin * scale)
              let f1Xmax = Number.parseInt(item.femoralhead1.xmax * scale)
              let f1Ymax = Number.parseInt(item.femoralhead1.ymax * scale)
              if (p0 && p1) 
                p2 = [(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2]
              p3 = [(f1Xmin + f1Xmax) / 2, (f1Ymin + f1Ymax) / 2]
              p5 = p3
              p4 = null
            }
            
            // 当第二个股骨头不存在时，即等同于第一个股骨头
            if(item.hasOwnProperty('femoralhead2')){
              let f2Xmin = Number.parseInt(item.femoralhead2.xmin * scale)
              let f2Ymin = Number.parseInt(item.femoralhead2.ymin * scale)
              let f2Xmax = Number.parseInt(item.femoralhead2.xmax * scale)
              let f2Ymax = Number.parseInt(item.femoralhead2.ymax * scale)
              p4 = [(f2Xmin + f2Xmax) / 2, (f2Ymin + f2Ymax) / 2]
              p5 = [(p3[0] + p4[0]) / 2, (p3[1] + p4[1]) / 2]
            }

            
            if(item.hasOwnProperty('c7')){
              let cXmin = Number.parseInt(item.c7.xmin * scale)
              let cYmin = Number.parseInt(item.c7.ymin * scale)
              let cXmax = Number.parseInt(item.c7.xmax * scale)
              let cYmax = Number.parseInt(item.c7.ymax * scale)
              p6 = [cXmin, cYmin]
              p7 = [cXmax, cYmax]
            }

            if(item.hasOwnProperty('t12')){
              let tXmin = Number.parseInt(item.t12.xmin * scale)
              let tYmin = Number.parseInt(item.t12.ymin * scale)
              let tXmax = Number.parseInt(item.t12.xmax * scale)
              let tYmax = Number.parseInt(item.t12.ymax * scale)
              p8 = [tXmin, tYmin]
              p9 = [tXmax, tYmax]
            }

            let sideRes = {
              p0: p0, p1: p1, p2: p2, p3: p3, p4: p4, p5: p5,
              p6: p6, p7: p7, p8: p8, p9: p9
            }

            tempImgList[filename] = sideRes

            tempFileList[filename]['isMeasured'] = true

            tempResList[filename]['isParsed'] = true
            tempResList[filename]['isScaled'] = false
            tempResList[filename].originParseRes.sideRes = sideRes
            tempResList[filename].displayParseRes.sideRes = sideRes
          }
        }
      })
      
       // 修改两个列表
      this.EditTwoListToGlobal(2, tempFileList, tempResList)
      // 将修改后的以xml格式数据保存本地
      this.WriteToLocalFile(tempImgList, params.resXmlPath)
    },

    /* 功能：通过图片选择窗口回传的图片路径数组，将图片逐个以base64格式读取，
            打包为json上传。（注：正侧图分别设置前缀进行区分，s_  f_） */
    StartMeasure (fileList) {
      
      // 测试代码！！！读取并显示本地保存的测量结果，渲染至页面
      let that = this
      fs.readFile('./tmp/xml/test_result.xml', 'utf-8', (err, res) => {
        let imgList = parser.parse(res)['image-list']['image']
        if (!Array.isArray(imgList)) {
          imgList = [imgList]
        }
        console.log(imgList)

        setTimeout(() => {

          that.WriteSideResult(imgList)
          that.WriteFrontResult(imgList)

          this.$notify.success({
            title: '成功',
            message: '量测已完成，总耗时' + '2分钟',
            duration: 0,
            position: 'bottom-left'
          })
          this.$store.commit('ChangeMeasureState', {isMeasuring: false})
          this.$store.commit('ChangeIsShowResultBoxState', {isShowResultBox: true})
        }, 5000)
      })

      // ！！！！！

      // let that = this
      // let jsonData = []

      // for (let key in fileList.side) {
      //   let data = fs.readFileSync(fileList.side[key])

      //   jsonData.push({
      //     name: 's_' + key,
      //     data: Buffer.from(data).toString('base64')
      //   })
      // }

      // for (let key in fileList.front) {
      //   let data = fs.readFileSync(fileList.front[key])

      //   jsonData.push({
      //     name: 'f_' + key,
      //     data: Buffer.from(data).toString('base64')
      //   })
      // }
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
      //           let data = window.atob(res.data.data) // 将base64字符串转换为utf-8

      //           let imgList = parser.parse(data)['image-list']['image']
      //           if (!Array.isArray(imgList)) {
      //             imgList = [imgList]
      //           }
      //           that.WriteSideResult(imgList)
      //           that.WriteFrontResult(imgList)
                
                
      //           clearInterval(that.measureInterval)
      //           this.$store.commit('ChangeMeasureState', {isMeasuring: false})
      //           this.$store.commit('ChangeIsShowResultBoxState', {isShowResultBox: true})
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
          })
        }
      })
    },

    // ！！！！！！中文乱码！！！！待改
    /* 功能：将量测结果与图片保存为PDF格式文件 */
    Print () {
      try {
        let filename1 = this.$store.state.File.params1.curFilename.split('.')[0]
        let filename2 = this.$store.state.File.params2.curFilename.split('.')[0]
        let canvasData1 = this.$store.state.File.params1.canvasData
        let canvasData2 = this.$store.state.File.params2.canvasData
        if (canvasData1 !== null && canvasData2 !== null) {
          let pdf = new jsPDF()
          // jsPDF存在中文乱码，故需手动导入黑体字体文件
          Addfont(pdf)
          pdf.addFont('simhei', 'simhei', 'normal')
          pdf.setFont('simhei')

          // 待改，尽量写成相对定位
          pdf.addImage(canvasData1, 'JPEG', 20, 15, 249 / 4, 500 / 4)
          pdf.text(filename1, 40, 10)
          pdf.addImage(canvasData2, 'JPEG', 120, 15, 249 / 4, 500 / 4)
          pdf.text(filename2, 140, 10)
          if (this.$store.state.File.curEntireRes !== null) {
            pdf.text('Health Report:', 100, 147)
            let res = this.$store.state.File.curEntireRes
            pdf.text('ss:', 100, 157)
            pdf.text(110, 157, res.pelvis.ss)
            pdf.text('pt:', 100, 167)
            pdf.text(110, 167, res.pelvis.pt)
            pdf.text('pi:', 100, 177)
            pdf.text(110, 177, res.pelvis.pi)

            pdf.text('sva:', 100, 187)
            pdf.text(110, 187, res.sagittal.sva)
            pdf.text('ll:', 100, 197)
            pdf.text(110, 197, res.sagittal.ll)
            pdf.text('cva:', 100, 207)
            pdf.text(110, 207, res.coronal.cva)
            pdf.text('cva:', 100, 217)
            pdf.text(110, 217, res.coronal.cva)

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