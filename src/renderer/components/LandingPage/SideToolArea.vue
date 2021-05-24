<template>
  <el-card class="side-tool-area-content">
    <div slot="header">
      <span class="side-tool-area-title">操作面板</span>
    </div>
    <div class="tool-box">
      <el-button round @click="ShowResultBox" style="margin:0.6rem 0.8rem 1.2rem 0.8rem"><span v-if="!isShowResultBox">显示结果</span><span v-else>收起浮窗</span></el-button>
      <result-box :isShowResultBox="isShowResultBox" @CloseResultBox="CloseResultBox"></result-box>
      
      <div class="tool-group">
        <i class="tool-icon flaticon-rotate" title="顺时针旋转"></i>
        <i class="tool-icon flaticon-rotate-1" title="逆时针旋转"></i>
        <i class="tool-icon flaticon-vertical" title="垂直翻转"></i>
        <i class="tool-icon flaticon-horizontal" title="水平翻转"></i>
        <i class="tool-icon flaticon-zoom-in" title="放大"></i>
        <i class="tool-icon flaticon-zoom-out" title="缩小"></i>
      </div>
      <div class="tool-group">
        <i class="tool-icon flaticon-undo" title="撤销"></i>
        <i class="tool-icon flaticon-nodes-1" title="绘制线"></i>
        <i class="tool-icon flaticon-selection" title="绘制矩形"></i>
        <i class="tool-icon flaticon-nodes" title="绘制圆"></i>
        <i class="tool-icon flaticon-right" title="绘制箭头"></i>
        <i class="tool-icon flaticon-font" title="添加文字"></i>
        <i class="tool-icon flaticon-eraser" title="清除"></i>
      </div>
      <div class="tool-group">
        <i class="tool-icon flaticon-ruler-1" title="测量两点间距离"></i>
        <i class="tool-icon flaticon-compass" title="测量两线夹角"></i>
        <i class="tool-icon flaticon-triangular-ruler" title="测量三点夹角"></i>
        <i class="tool-icon flaticon-vertical-alignment" title="直方图统计"></i>
      </div>
      
      <div class="tool-group">
        <div class="slider-box">
          <div style="display:flex;"><i class="slider-icon flaticon-daylight"></i>亮度</div>
          <el-slider v-model="brightnessValue" style="padding:0 0.5rem;"></el-slider>
        </div>
        <div class="slider-box">
          <div style="display:flex;"><i class="slider-icon flaticon-brightness-1"></i>对比度</div>
          <el-slider v-model="contrastValue" style="padding:0 0.5rem;"></el-slider>
        </div>
        <div class="slider-box">
          <div style="display:flex;"><i class="slider-icon flaticon-brightness"></i>锐化</div>
          <el-slider v-model="sharpenValue" style="padding:0 0.5rem;"></el-slider>
        </div>
        <div class="slider-box">
          <div style="display:flex;"><i class="slider-icon flaticon-coloring-tool"></i>平滑</div>
          <el-slider v-model="smoothValue" style="padding:0 0.5rem;"></el-slider>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script>
import ResultBox from './ResultBox.vue'
const parser = require('fast-xml-parser')
const fs = require('fs')
const he = require('he')
/*
  侧边操作面板组件，包括各类对图像编辑操作的工具 */
export default {
  components: {
    'result-box': ResultBox
  },
  data() {
    return {
      brightnessValue: 43,
      contrastValue: 67,
      sharpenValue: 22,
      smoothValue: 88
    }
  },
  computed: {
    isShowResultBox () { //是否显示结果面板
      return this.$store.state.File.isShowResultBox
    }
  },
  methods: {
    ShowResultBox () {
      this.$store.commit('ChangeIsShowResultBoxState', {isShowResultBox: !this.isShowResultBox})
    },
    CloseResultBox () {
      this.$store.commit('ChangeIsShowResultBoxState', {isShowResultBox: false})
    },
    // 测试脚本，废弃
    // EditResult() {
    //   let fileList = JSON.parse(JSON.stringify(this.$store.state.File.params2.fileList))
    //   let imgHeightList = {}
    //   for (let key in fileList) {
    //     let img = new Image()
    //     img.src =  fileList[key].path
    //     img.onload = () => {
    //       imgHeightList[key] = img.height / 10
    //     }
    //   }
    //   setTimeout(()=>{
    //     console.log(imgHeightList)
    //     fs.readFile('./tmp/xml/result.xml', 'utf-8', (err, res) => {
    //     let imgList = parser.parse(res)
    //     imgList['image-list']['image'].forEach(item => {
    //       if(item.hasOwnProperty('c7')){
    //           item['c7']['ymin'] += imgHeightList[item.name]
    //           item['c7']['ymax'] += imgHeightList[item.name]
    //       }
    //       if(item.hasOwnProperty('t12')){
    //           item['t12']['ymin'] += imgHeightList[item.name]
    //           item['t12']['ymax'] += imgHeightList[item.name]
    //       }
    //       if(item.hasOwnProperty('femoralhead1')){
    //           item['femoralhead1']['ymin'] += imgHeightList[item.name]
    //           item['femoralhead1']['ymax'] += imgHeightList[item.name]
    //       }
    //       if(item.hasOwnProperty('femoralhead2')){
    //           item['femoralhead2']['ymin'] += imgHeightList[item.name]
    //           item['femoralhead2']['ymax'] += imgHeightList[item.name]
    //       }
    //       if(item.hasOwnProperty('sacrum')){
    //           item['sacrum']['ymin'] += imgHeightList[item.name]
    //           item['sacrum']['ymax'] += imgHeightList[item.name]
    //       }
          
    //       item.name = 's_' + item.name
    //     })
    //     console.log(imgList)
    //     let j2xml = new parser.j2xParser()
    //     let xml = j2xml.parse(imgList, {})
    //     fs.writeFile('./test_result.xml', xml, (err) => {
    //       console.log(err)
    //     })
    //   })
    //   }, 5000)
      
    // }
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
  .tool-box{
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    align-content: center;
  }
  .tool-group{
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
    padding: 0.4rem 0;
    border-top: 1px solid #EBEEF5;
  }

  .tool-icon{
    padding: 1px 4px;
    cursor: pointer;
    font-size: 1.5em;
  }
  .tool-icon:hover{
    background-color: rgb(230, 230, 230);
  }

  .slider-box{
    width: 100%;
    margin-top: 6px;
  }
  .slider-icon{
    zoom: 1.2;
    margin-right: 4px;
  }
</style>