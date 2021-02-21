<template>
  <div class="file-list-area-content">
    <el-card class="file-list-box">
      <div class="file-list-header" slot="header">
        <span class="file-list-title">正面图</span>
        <i ref="frontRefreshBtn" @click="RefreshFrontFile"
          :class="['fa', 'fa-refresh', 'file-list-refresh', isFrontRefreshing?'fa-spin':'']"></i>
      </div>
      <el-table ref="table1" :data="FrontListData" :show-header="false" max-height="260" @row-click="SelectFrontFile"
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
        <el-table-column prop="oper" min-width="30" align="right" fixed="right">
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
      <el-table ref="table2" :data="SideListData" :show-header="false" max-height="260" @row-click="SelectSideFile"
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
        <el-table-column min-width="35" align="right" fixed="right">
          <template slot-scope="scope">
            <i class="fa fa-check measured-icon" v-if="scope.row.isMeasured"></i>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
export default {
  data () {
    return {
      isFrontRefreshing: false,
      isSideRefreshing: false
    }
  },
  computed: {
    FrontListData () {
      let fileList = this.$store.state.File.params1.fileList
      let listData = []
      for (let key in fileList) {
        listData.push({
          'filename': key,
          'path': fileList[key].path,
          'isMeasured': fileList[key].isMeasured
        })
      }
      this.$nextTick(() => { // 设置表格中当前选中行
        if (this.FrontListData.length > 0) {
          this.$refs.table1.setCurrentRow(this.FrontListData[0])
        }
      })
      return listData
    },
    SideListData () {
      var fileList = this.$store.state.File.params2.fileList
      var listData = []
      for (let key in fileList) {
        listData.push({
          'filename': key,
          'path': fileList[key].path,
          'isMeasured': fileList[key].isMeasured
        })
      }
      this.$nextTick(() => {
        if (this.SideListData.length > 0) {
          this.$refs.table2.setCurrentRow(this.SideListData[0])
        }
      })
      return listData
    }
  },
  methods: {
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
    RefreshFrontFile () {
      let that = this
      that.$store.dispatch('LoadDir', {
        flag: 1,
        path: that.$store.state.File.params1.dirPath
      })
      that.isFrontRefreshing = true
      let clock = setInterval(() => {
        that.isFrontRefreshing = false
        clearInterval(clock)
      }, 1000)
    },
    RefreshSideFile () {
      let that = this
      that.$store.dispatch('LoadDir', {
        flag: 2,
        path: that.$store.state.File.params2.dirPath
      })
      that.isSideRefreshing = true
      let clock = setInterval(() => {
        that.isSideRefreshing = false
        clearInterval(clock)
      }, 1000)
    }
  }
}
</script>

<style lang="less">
  .success-row {
    background: #f0f9eb;
  }
  // 文件列表栏
  @file_list_area_height_ratio: 45%;
  .file-list-area-content{
    display: flex;    
    flex-direction: row;
    justify-content: space-around;
    margin: 8px 4px 8px 4px;
    height: @file_list_area_height_ratio;
  }
  .file-list-box{
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