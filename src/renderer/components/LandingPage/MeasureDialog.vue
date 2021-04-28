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
      <el-button type="primary" @click="Measure" :loading="isPreprocessing" style="margin-right:2%">量测</el-button>
    </div>
  </el-dialog>
</template>

<script>
import { resolve } from 'url'
const compressImages = require('compress-images')
const fs = require('fs')
const Jimp = require('jimp')

export default {
  props: ['isShowDialog'],
  data () {
    return {
      frontListData: [],
      sideListData: [],
      isFrontAllSelected: false,
      isSideAllSelected: false,
      isPreprocessing: false
    }
  },
  methods: {
    Open () {
      let that = this
      that.isFrontAllSelected = false
      that.isSideAllSelected = false
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
    Compress (flag, selectedArr) {
      return new Promise((resolve, reject) => {
        let params = flag === 1 ? this.$store.state.File.params1 : this.$store.state.File.params2
        let dirPath = params.dirPath.replace(/\\/g, '/') + '/*.{jpg,JPG,jpeg,JPEG}'
        let compressDirPath = params.compressDirPath
        compressImages(dirPath, compressDirPath,
          {compress_force: false, statistic: true, autoupdate: true}, false,
          {jpg: {engine: 'mozjpeg', command: ['-quality', '15']}},// 固定为15
          {png: {engine: false, command: false}},
          {svg: {engine: false, command: false}},
          {gif: {engine: false, command: false}},
          (err, completed, statistic) => {
            if (completed) {
              console.log(err)
              console.log(completed)
              resolve(true)
            } else {
              reject(false)
            }
          }
        )
      })
    },
    Preprocess (flag, selectedArr) {
      return new Promise(resolve => {
        let params = flag === 1 ? this.$store.state.File.params1 : this.$store.state.File.params2
        let preprocessDirPath = params.preprocessDirPath
        let compressDirPath = params.compressDirPath
        fs.readdir(compressDirPath, (err, files) => {
          let promiseArray = []
          for (let file of files) {
            if (selectedArr.indexOf(file) > -1) {
              promiseArray.push(new Promise(resolve => {
                Jimp.read(compressDirPath + file, (err, img) => {
                  if (!err) {
                    img.scale(0.2)
                    img.write(preprocessDirPath + file)
                    resolve()
                  }
                })
              }))
            }
          }
          Promise.all(promiseArray).then(res => {
            resolve(true)
          })
        })
      })
    },
    Measure () {
      let that = this
      that.isPreprocessing = true

      let selectedArr = []
      that.$refs.sideTable.selection.forEach(item => {
        selectedArr.push(item.filename)
      })
      that.Compress(2, selectedArr).then((res) => {
        if (res) {
          that.Preprocess(2, selectedArr).then(res => {
            if (res) {
              console.log('sss')
              that.$store.commit('ChangeMeasureState', {isMeasuring: true})
              let fileDirArr = []
              let preprocessDirPath = that.$store.state.File.params2.preprocessDirPath
              that.$refs.sideTable.selection.forEach(item => {
                fileDirArr.push(preprocessDirPath + item.filename)
              })
              console.log(fileDirArr)
              that.$emit('StartMeasure', fileDirArr)
              that.$notify.info({
                title: '消息',
                message: '正在量测中，请保持网络通畅。预计所需时间为5-10分钟',
                duration: 3500,
                position: 'bottom-left'
              })
              
              that.isPreprocessing = false
              that.Close()
            } else {
              that.$message.error('图片预处理出错，请稍后重试')
              that.isPreprocessing = false
              that.Close()
            }
          })
        } else {
          that.$message.error('图片预处理出错，请稍后重试')
          that.isPreprocessing = false
          that.Close()
        }
      })
    
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
</style>