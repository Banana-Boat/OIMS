<template>
  <el-dialog :visible="isShowDialog"
            @close="Close" @open="Open" width="45%">
    <div slot="title">
      <span style="font-size:1.3rem">选择需要量测的图片</span>
      <i style="margin-left: 2%">(已量测图片已被自动选择)</i>
    </div>
    <div class="dialog-file-list-area-content">
      <el-card class="dialog-file-list-box">
        <div class="file-list-header" slot="header">
          <span class="file-list-title">正面图</span>
          <el-checkbox v-model="isFrontAllSelected" @change="SelectAll(1)">[全选]</el-checkbox>
        </div>
        <el-table ref="frontTable" :data="frontListData" :show-header="false"  max-height="345">
          <el-table-column type="selection">
          </el-table-column>
          <el-table-column prop="filename" align="center">
          </el-table-column>
        </el-table>
      </el-card>
      <el-card class="dialog-file-list-box">
        <div class="file-list-header" slot="header">
          <span class="file-list-title">侧面图</span>
          <el-checkbox v-model="isSideAllSelected" @change="SelectAll(2)">[全选]</el-checkbox>
        </div>
        <el-table ref="sideTable" :data="sideListData" :show-header="false"  max-height="345">
          <el-table-column type="selection">
          </el-table-column>
          <el-table-column prop="filename" align="center">
          </el-table-column>
        </el-table>
      </el-card>
    </div>
    <div slot="footer">
      <div class="progress-btn-box">
        <!-- <div v-if="curPreprocessType != 0" style="width: 100%; padding: 0 1.5rem;">
          <el-progress :percentage="prePercentage"></el-progress>
          <span style="font-size: 0.9rem; margin-right: 0.4rem"><span  v-if="curPreprocessType == 1">正面图</span><span v-else>侧面图</span>预处理...</span>
        </div> -->
        <el-progress v-if="isPreprocessing" style="width:90%;" :percentage="prePercentage"></el-progress>

        <el-button type="primary" @click="Measure" :loading="isPreprocessing" style="margin-right:2%"><span v-if="isPreprocessing">处理中</span><span v-else>量测</span></el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script>
/* 量测图片选择窗口组件，包含以下内容
    1. 正面图选择列表
    2. 侧面图选择列表
    3. 图片预处理进度条、量测按钮 */

const fs = require('fs')
const Jimp = require('jimp')
const imagemin = require("imagemin")
const imageminMozjpeg = require("imagemin-mozjpeg")

export default {
  props: ['isShowDialog'],
  data () {
    return {
      frontListData: [],  // 正面图文件列表
      sideListData: [],
      isFrontAllSelected: false,  // 正面图文件是否全选
      isSideAllSelected: false,
      isPreprocessing: false, // 是否正在进行图片预处理
      curPreprocessType: 0, // 当前预处理的图片类型（0：压缩操作不显示进度条  1：正面  2：侧面）
      preTotalNum: 0, // 待预处理图片总数
      preCurNum: 0, // 当前已进行预处理的图片数
      prePercentage: 0  // 当前预处理百分比
    }
  },
  methods: {
    /* 功能：打开窗口初始化操作 */
    Open () {
      let that = this
      that.isFrontAllSelected = false
      that.isSideAllSelected = false
      that.curPreprocessType = 0
      that.preTotalNum = 0
      that.preCurNum = 0
      that.prePercentage = 0
      that.frontListData = this.GetListData(1)
      that.sideListData = this.GetListData(2)
      that.frontListData.forEach(item => {
        that.$nextTick(() => {
          if (!item.isMeasured) {
            that.$refs.frontTable.toggleRowSelection(item)
          }
        })
      })
      that.sideListData.forEach(item => {
        that.$nextTick(() => {
          if (!item.isMeasured) {
            that.$refs.sideTable.toggleRowSelection(item)
          }
        })
      })
    },
    /* 功能：获取文件列表（是否被量测的数据） */
    GetListData (flag) {
      let resList = flag === 1 ? this.$store.state.File.params1.resList : this.$store.state.File.params2.resList
      let tempListData = []
      for (let key in resList) {
        tempListData.push({
          'filename': key,
          'isMeasured': resList[key].isMeasured
        })
      }
      return tempListData
    },
    /* 功能：全选 */
    SelectAll (flag) {
      if (flag === 1) {
        this.frontListData.forEach(item => {
          this.$refs.frontTable.toggleRowSelection(item, this.isFrontAllSelected)
        })
      } else {
        this.sideListData.forEach(item => {
          this.$refs.sideTable.toggleRowSelection(item, this.isSideAllSelected)
        })
      }
    },
    /* 功能：压缩所有原图并保存在./tmp/img/_compress目录下 */
    Compress (inputDir, outputDir) {
      return new Promise((resolve, reject) => {
        imagemin([inputDir.replace(/\\/g, '/') + '/*.{jpg,png}'], {
          destination: outputDir,
          plugins: [
            imageminMozjpeg({quality: 15})
          ]
        }).then(res => {
          console.log(res)
          console.log('compression finished!' + res.length)
          resolve(true)
        })
      })
    },
    /* 功能: 对已选图片进行缩小5倍的预处理，并保存在./tmp/img/_preprocess目录下 */
    Preprocess (inputDir, outputDir, selectedArr) {
      let that = this
      let targetArr = []  // 选择数组中未被预处理的图片
      let preprocessScale = 1 / this.$store.state.File.preprocessScale

      return new Promise(resolve => {
        fs.readdir(outputDir, (err, existedFiles) => {
          selectedArr.forEach(file => {
            if(existedFiles.indexOf(file) == -1)
              targetArr.push(file)
          })
          that.preTotalNum = targetArr.length
          that.preCurNum = 0
          
          if(targetArr.length != 0){
            fs.readdir(inputDir, (err, files) => {
              files.reduce((prev, cur, index) => {
                return prev.then(res => {
                  return new Promise(resolve => {
                    if (targetArr.indexOf(files[index]) > -1) { 
                      Jimp.read(inputDir + files[index], (err, img) => {
                        if (!err) {
                          // img.crop(0, img.getHeight() / 2, img.getWidth(), img.getHeight() / 2)
                          img.scale(preprocessScale)
                          img.writeAsync(outputDir + files[index]).then(res => {
                            that.preCurNum++
                            that.prePercentage = Number.parseInt((that.preCurNum) / that.preTotalNum * 100)
                            resolve()
                          })
                        }
                      })
                    } else {
                      resolve()
                    }
                  })
                })
              }, Promise.resolve({})).then(() => {
                resolve(true)
              })
            })
          } else{ 
            resolve(true)
          }
        })
      })
    },
    /* 功能：获取被选择的图片，进行压缩、缩小预处理后，将图片路径数组传递至父级组件ToolHeader，进行处理 */
    Measure () {
      let that = this
      that.isPreprocessing = true

      let sideSelectArr = []
      that.$refs.sideTable.selection.forEach(item => {
        sideSelectArr.push(item.filename)
      })
      let frontSelectArr = []
      that.$refs.frontTable.selection.forEach(item => {
        frontSelectArr.push(item.filename)
      })

      let params1 = this.$store.state.File.params1
      let params2 = this.$store.state.File.params2
      let fileList = {
        side: {},
        front: {}
      }

      // !!!测试代码
      that.$store.commit('ChangeMeasureState', {isMeasuring: true})
      that.$refs.frontTable.selection.forEach(item => {
        fileList.front[item.filename.split('/').pop()] = params1.preprocessDirPath + item.filename
      })
      that.$refs.sideTable.selection.forEach(item => {
        fileList.side[item.filename.split('/').pop()] = params2.preprocessDirPath + item.filename
      })

      that.prePercentage = 0

      let i = 0
      let tid
      function Add(){
        clearTimeout(tid)
        that.prePercentage += 10
        i++
        if (i < 10){
          tid = setTimeout(Add, 250)
        } else {
          that.$emit('StartMeasure', fileList)
          that.$notify.info({
            title: '消息',
            message: '正在量测中，请保持网络通畅。预计所需时间为5-10分钟',
            duration: 3500,
            position: 'bottom-left'
          })

          that.isPreprocessing = false
          that.Close()
        }
      }

      tid = setTimeout(Add,200)

      
      // !!!!!!!!!!!!!!!!!!!!
      

      // 效率低下有待改进！！！！！！
      // that.curPreprocessType = 0
      // that.Compress(params1.dirPath, params1.compressDirPath).then((res) => {
      //   if (res) {
      //     that.Compress(params2.dirPath, params2.compressDirPath).then((res) => {
      //       if (res) {
      //         that.curPreprocessType = 1
      //         that.Preprocess(params1.compressDirPath, params1.preprocessDirPath, frontSelectArr).then(res => {
      //           if (res) {
      //             that.curPreprocessType = 2
      //             that.Preprocess(params2.compressDirPath, params2.preprocessDirPath, sideSelectArr).then(res => {
      //               if (res) {
                  
      //                 that.$store.commit('ChangeMeasureState', {isMeasuring: true})
                      
      //                 that.$refs.frontTable.selection.forEach(item => {
      //                   fileList.front[item.filename.split('/').pop()] = params1.preprocessDirPath + item.filename
      //                 })
      //                 that.$refs.sideTable.selection.forEach(item => {
      //                   fileList.side[item.filename.split('/').pop()] = params2.preprocessDirPath + item.filename
      //                 })
                      
      //                 that.$emit('StartMeasure', fileList)

      //                 that.$notify.info({
      //                   title: '消息',
      //                   message: '正在量测中，请保持网络通畅。预计所需时间为5-10分钟',
      //                   duration: 3500,
      //                   position: 'bottom-left'
      //                 })

      //                 that.isPreprocessing = false
      //                 that.Close()
      //               } else {
      //                 that.$message.error('图片预处理出错，请稍后重试')
      //                 that.isPreprocessing = false
      //                 that.Close()
      //               }
      //             })
      //           } else {
      //             that.$message.error('图片预处理出错，请稍后重试')
      //             that.isPreprocessing = false
      //             that.Close()
      //           }
      //         })
      //       } else {
      //         that.$message.error('图片预处理出错，请稍后重试')
      //         that.isPreprocessing = false
      //         that.Close()
      //       }
      //     })
      //   } else {
      //     that.$message.error('图片预处理出错，请稍后重试')
      //     that.isPreprocessing = false
      //     that.Close()
      //   }
      // })
    
    },
    Close () {
      this.$emit('CloseDialog')
    }
  }
}
</script>

<style lang="less">
  .dialog-file-list-area-content{
    display: flex;    
    flex-direction: row;
    justify-content: space-around;
    margin: 8px 4px 8px 4px;
    height: 400px;
  }
  .dialog-file-list-box{
    flex: 1 0 40%;
    margin: 0px 4px 0px 4px;
  }
  .file-list-header{
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
  .file-list-title{
    font-size: 1.1rem;
    font-weight: bold;
    color: black;
  }
  .el-table__body-wrapper::-webkit-scrollbar {
    width: 7px;
    height: 7px;
  }
  .el-table__body-wrapper::-webkit-scrollbar-thumb {
    background-color: #c4c4c4;
    border-radius: 3px;
  }

  .el-progress{
    display: flex;
    align-items: center;
  }

  .progress-btn-box{
    display: flex;
    justify-content: flex-end;
  }
</style>