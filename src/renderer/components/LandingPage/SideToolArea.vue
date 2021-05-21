<template>
  <el-card class="side-tool-area-content">
    <div slot="header">
      <span class="side-tool-area-title">操作面板</span>
    </div>
    <div class="side-tool-area-content">
      <el-button round @click="ShowResultBox">显示结果</el-button>
      <!-- <el-tooltip content="撤销" placement="bottom-start" :open-delay=700 effect="light">
        <div id="undoBtn" class="side-tool-btn">
          <img src="../../assets/btn-icon/undo.svg">
        </div>
      </el-tooltip>
      <el-tooltip content="放大" placement="bottom-start" :open-delay=700 effect="light">
        <div id="zoomInBtn" class="side-tool-btn">
          <img src="../../assets/btn-icon/zoom-in.svg">
        </div>
      </el-tooltip>
      <el-tooltip content="缩小" placement="bottom-start" :open-delay=700 effect="light">
        <div id="zoomOutBtn" class="side-tool-btn">
          <img src="../../assets/btn-icon/zoom-out.svg">
        </div>
      </el-tooltip>
      <el-tooltip content="绘制直线" placement="bottom-start" :open-delay=700 effect="light">
        <div id="drawLineBtn" class="side-tool-btn">
          <img src="../../assets/btn-icon/line.svg">
        </div>
      </el-tooltip>
      <el-tooltip content="绘制曲线" placement="bottom-start" :open-delay=700 effect="light">
        <div id="drawCurvedLineBtn" class="side-tool-btn">
          <img src="../../assets/btn-icon/curved-line.svg">
        </div>
      </el-tooltip>
      <el-tooltip content="绘制矩形" placement="bottom-start" :open-delay=700 effect="light">
        <div id="drawRectangleBtn" class="side-tool-btn">
          <img src="../../assets/btn-icon/rectangle.svg">
        </div>
      </el-tooltip>
      <el-tooltip content="绘制圆" placement="bottom-start" :open-delay=700 effect="light">
        <div id="drawCircleBtn" class="side-tool-btn">
          <img src="../../assets/btn-icon/circle.svg">
        </div>
      </el-tooltip>
      <el-tooltip content="亮度调节" placement="bottom-start" :open-delay=700 effect="light">
        <div id="brightnessAdjustBtn" class="side-tool-btn">
          <img src="../../assets/btn-icon/brightness.svg">
        </div>
      </el-tooltip> -->
    </div>
    <result-box :isShowResultBox="isShowResultBox" @CloseResultBox="CloseResultBox"></result-box>
  </el-card>
</template>

<script>
import ResultBox from './ResultBox.vue'
/*
  侧边操作面板组件，包括各类对图像编辑操作的工具 */
export default {
  components: {
    'result-box': ResultBox
  },
  data() {
    return {
    }
  },
  computed: {
    isShowResultBox () { //是否显示结果面板
      return this.$store.state.File.isShowResultBox
    }
  },
  methods: {
    ShowResultBox () {
      this.$store.commit('ChangeIsShowResultBoxState', {isShowResultBox: true})
    },
    CloseResultBox () {
      this.$store.commit('ChangeIsShowResultBoxState', {isShowResultBox: false})
    }
  }
}
</script>

<style lang="less">
  .side-tool-area-content{
    margin: 8px 4px 8px 8px;
    width: 50%;
  }
  .side-tool-area-title{
    font-size: 1.1rem;
    font-weight: bold;
    color: black;
  }
</style>