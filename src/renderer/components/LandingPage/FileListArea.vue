<template>
  <div class="file-list-area-content" ref="areaHeight">
    <el-card class="file-list-box">
      <div class="file-list-header" slot="header">
        <span class="file-list-title">正面图</span>
        <i ref="frontRefreshBtn" @click="Refresh(1)"
          :class="['fa', 'fa-refresh', 'file-list-refresh', isFrontRefreshing?'fa-spin':'']"></i>
      </div>
      <el-table ref="table1" :data="frontListData" :show-header="false" :max-height="tableHeight" @row-click="SelectFrontFile"
              style="cursor: pointer;" tooltip-effect="light"
              :row-style="{height: '20px'}" :cell-style="{padding: '5px'}"
              :highlight-current-row="true">
        <el-table-column min-width="70" :show-overflow-tooltip="true">
          <template slot-scope="scope">
            <el-tooltip :content="scope.row.path" placement="top-start" :open-delay=1000 effect="light">
              <span>{{ scope.row.filename }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="oper" min-width="30" align="right">
          <template slot-scope="scope">
            <i class="fa fa-check measured-icon" v-if="scope.row.isMeasured"></i>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <el-card class="file-list-box">
      <div class="file-list-header" slot="header">
        <span class="file-list-title">侧面图</span>
        <i ref="sideRefreshBtn" @click="RefreshSideFile"
          :class="['fa', 'fa-refresh', 'file-list-refresh', isSideRefreshing?'fa-spin':'']"></i>
      </div>
      <el-table ref="table2" :data="sideListData" :show-header="false" :max-height="tableHeight" @row-click="SelectSideFile"
                style="cursor: pointer;" tooltip-effect="light"
                :row-style="{height: '20px'}" :cell-style="{padding: '5px'}"
                :highlight-current-row="true">
        <el-table-column min-width="65" :show-overflow-tooltip="true">
          <template slot-scope="scope">
            <el-tooltip :content="scope.row.path" placement="top-start" :open-delay=1000 effect="light">
              <span>{{ scope.row.filename }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column min-width="35" align="right">
          <template slot-scope="scope">
            <i class="fa fa-check measured-icon" v-if="scope.row.isMeasured"></i>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { resolve } from 'url'
/* 
  文件列表栏组件 */
  
const parser = require('fast-xml-parser')
const fs = require('fs')

export default {
  data () {
    return {
      frontListData: [],  // 正面图数组
      sideListData: [],
      isFrontRefreshing: false, // 正面图是否被刷新
      isSideRefreshing: false,
      tableHeight: 0
    }
  },
  created() {
    this.$store.dispatch('ChangeCurFilenameToTheFirst', {flag: 1})
    this.$store.dispatch('ChangeCurFilenameToTheFirst', {flag: 2})
  },
  mounted() {
    this.$nextTick(() => {
      // 计算表格高度
      this.tableHeight = this.$refs.areaHeight.clientHeight / 2 - 100
    })
  },
  computed: {
    frontFileList () {
      return this.$store.state.File.params1.fileList
    },
    sideFileList () {
      return this.$store.state.File.params2.fileList
    }
  },
  watch: {
    /* 功能: 监听正面图文件列表的变化 */
    frontFileList: {
      immediate: true,
      handler: function(nv, ov) {
        this.frontListData = this.GetListData(nv)
        this.$nextTick(() => { // 设置表格中当前选中行
          if (this.frontListData.length > 0) {
            this.$refs.table1.setCurrentRow(this.frontListData[0])
          }
        })
      }
    },
    /* 功能: 监听侧面图文件列表的变化 */
    sideFileList: {
      immediate: true,
      handler: function(nv, ov){
        this.sideListData = this.GetListData(nv)
        this.$nextTick(() => { // 设置表格中当前选中行
          if (this.sideListData.length > 0) {
            this.$refs.table2.setCurrentRow(this.sideListData[0])
          }
        })
      }
    },
  },
  methods: {
    /* 功能：将fileList整理为表格所需格式 */
    GetListData (fileList) {
      let listData = []
      for (let key in fileList) {
        listData.push({
          'filename': key,
          'path': fileList[key].path,
          'isMeasured': fileList[key].isMeasured
        })
      }
      return listData
    },
    /* 功能：点击选择正面图列表项 */
    SelectFrontFile (row) {
      this.$store.commit('ChangeCurFilename', {
        flag: 1,
        curFilename: row.filename
      })
    },
    SelectSideFile (row) {
      this.$store.commit('ChangeCurFilename', {
        flag: 2,
        curFilename: row.filename
      })
    },
    /* 功能：刷新正侧面图文件列表 */
    Refresh (flag) {
      let that = this
      let params = flag == 1 ? this.$store.state.File.params1 : this.$store.state.File.params2

      // 读文件为异步进行，须将结果数据更改至全局后，才可通知画布与结果窗更改
      that.$store.dispatch('LoadDir', {
        flag: flag,
        path: params.dirPath
      }).then(() => {
        that.LoadLocalResultFile(flag).then(() => {
          this.$store.dispatch('ChangeCurFilenameToTheFirst', {flag: flag})
        })
      })

      if (flag == 1) {
        that.isFrontRefreshing = true
        let clock = setInterval(() => {
          that.isFrontRefreshing = false
          clearInterval(clock)
        }, 1000)
      } else {
        that.isSideRefreshing = true
        let clock = setInterval(() => {
          that.isSideRefreshing = false
          clearInterval(clock)
        }, 1000)
      }
    },
    /* 加载本地量测数据 */
    LoadLocalResultFile (flag) {
      let params = flag === 1 ? this.$store.state.File.params1 : this.$store.state.File.params2
      let tempResList = JSON.parse(JSON.stringify(params.resList))
      let tempFileList = JSON.parse(JSON.stringify(params.fileList))

      return new Promise(resolve => {

        if (Object.keys(tempFileList).length !== 0) {
          fs.readFile(params.resXmlPath, 'utf-8', (err, res) => {
            if (!err) {
              let imgList = parser.parse(res)

              for (let filename in imgList['image-list']) {
                let item = imgList['image-list'][filename]

                if (flag == 1) {
                  tempResList[filename].originParseRes.frontRes = item
                  tempResList[filename].displayParseRes.frontRes = item
                } else {
                  tempResList[filename].originParseRes.sideRes = item
                  tempResList[filename].displayParseRes.sideRes = item
                }
                
                tempFileList[filename]['isMeasured'] = true
                tempResList[filename]['isParsed'] = true
                tempResList[filename]['isScaled'] = false
                
              }

              // 修改两个列表
              this.$store.commit('ChangeResList', {
                flag: flag,
                resList: tempResList
              })
              this.$store.commit('ChangeFileList', {
                flag: flag,
                fileList: tempFileList
              })

              resolve()
            }
          })

        } else {
          resolve()
        }
      })
      
    }
  }
}
</script>

<style lang="less">
  .success-row {
    background: #f0f9eb;
  }
  // 文件列表栏
  .file-list-area-content{
    display: flex;    
    flex-direction: column;
    width: 50%;
    justify-content: space-between;
    margin: 8px 8px 8px 4px;
  }
  .file-list-box{
    height: 49%;
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
  .file-list-refresh{
    color: #515151;
    cursor: pointer;
  }
  .file-list-refresh:hover{
    color: #808080;
  }
  .el-table__body-wrapper::-webkit-scrollbar {
    width: 7px;
    height: 7px;
  }
  .el-table__body-wrapper::-webkit-scrollbar-thumb {
    background-color: #c4c4c4;
    border-radius: 3px;
  }
  .measured-icon{
    zoom: 1.4;
    color: rgb(59, 196, 81);
  }
</style>