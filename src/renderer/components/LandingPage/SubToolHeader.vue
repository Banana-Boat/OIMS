<template>
  <div class="sub-tool-header-content">
    <el-tooltip content="撤销" placement="bottom-start" :open-delay=700 effect="light">
      <div id="undoBtn" class="sub-tool-btn">
        <img src="../../assets/btn-icon/undo.svg">
      </div>
    </el-tooltip>
    <el-tooltip content="放大" placement="bottom-start" :open-delay=700 effect="light">
      <div id="zoomInBtn" class="sub-tool-btn">
        <img src="../../assets/btn-icon/zoom-in.svg">
      </div>
    </el-tooltip>
    <el-tooltip content="缩小" placement="bottom-start" :open-delay=700 effect="light">
      <div id="zoomOutBtn" class="sub-tool-btn">
        <img src="../../assets/btn-icon/zoom-out.svg">
      </div>
    </el-tooltip>
    <el-tooltip content="绘制直线" placement="bottom-start" :open-delay=700 effect="light">
      <div id="drawLineBtn" class="sub-tool-btn" @click="Test">
        <img src="../../assets/btn-icon/line.svg">
      </div>
    </el-tooltip>
    <el-tooltip content="绘制曲线" placement="bottom-start" :open-delay=700 effect="light">
      <div id="drawCurvedLineBtn" class="sub-tool-btn">
        <img src="../../assets/btn-icon/curved-line.svg">
      </div>
    </el-tooltip>
    <el-tooltip content="绘制矩形" placement="bottom-start" :open-delay=700 effect="light">
      <div id="drawRectangleBtn" class="sub-tool-btn" @click="PaintRect">
        <img src="../../assets/btn-icon/rectangle.svg">
      </div>
    </el-tooltip>
    <el-tooltip content="绘制圆" placement="bottom-start" :open-delay=700 effect="light">
      <div id="drawCircleBtn" class="sub-tool-btn">
        <img src="../../assets/btn-icon/circle.svg">
      </div>
    </el-tooltip>
    <el-tooltip content="亮度调节" placement="bottom-start" :open-delay=700 effect="light">
      <div id="brightnessAdjustBtn" class="sub-tool-btn">
        <img src="../../assets/btn-icon/brightness.svg">
      </div>
    </el-tooltip>
  </div>
</template>

<script>

/*
  次级顶部工具栏组件，包括各类对图像编辑操作的工具 */
export default {
  methods:{
    Test(){
      //alert("ok")
      let flag = this.$store.state.File.selectedImgBox
      let params = flag==1? this.$store.state.File.params1 : this.$store.state.File.params2
      let curFilename = params.curFilename
      let tempList = params.testList
      if (tempList[curFilename].x1 == null){
        tempList[curFilename]={
        'x1':100,
        'y1':100,
        'x2':200,
        'y2':200
        }
      }
      else{
        tempList[curFilename]={
        'x1':null,
        'y1':null,
        'x2':null,
        'y2':null
        }
      }
      
      //alert(curFilename)
      this.$store.commit('ChangTest', {
          flag: flag,
          //testx: 300,
          //texty: 100,
          curFilename: curFilename,
          testList: tempList
      })
    },
    PaintRect(){
      let flag = this.$store.state.File.selectedImgBox
      let params = flag==1? this.$store.state.File.params1 : this.$store.state.File.params2
      let curFilename = params.curFilename
      let rectList = params.rectList

      if (rectList[curFilename].width == null){
        rectList[curFilename]={
          'width': 100, 
          'height': 100, 
          'left': 100, 
          'top': 100, 
          'angle': 0
        }
      }
      else{
        rectList[curFilename]={
          'width': null, 
          'height': null, 
          'left': null, 
          'top': null, 
          'angle': null
        }
      }
      this.$store.commit('ChangRect', {
          flag: flag,
          curFilename: curFilename,
          rectList: rectList
      })
    }
  }
}

</script>

<style lang="less">
  .sub-tool-header-content{
    width: 100%;
    height: 100%;
    background: #e5e7e8;
    display: flex;
    align-items: center;
    box-shadow: 0px 5px 10px 0px #bababa;
    justify-content:flex-end;
    padding: 0px 3%;
  }
  // 二级顶部工具栏
  @sub_tool_header_height: 36px;
  .sub-tool-header{
    flex: 0 0 @sub_tool_header_height;
    background: #e5e7e8;
    display: flex;
    align-items: center;
    box-shadow: 0px 5px 10px 0px #bababa;
  }
  .sub-tool-btn{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #535353;
    cursor: pointer;
    height: @sub_tool_header_height - 2;
    width: @sub_tool_header_height + 10;
  }
  .sub-tool-btn:hover{
    background: #c4c5c5;
  }
  .sub-tool-btn>i{
    zoom: 1.3;
  }
  .sub-tool-btn>img{
    height: @sub_tool_header_height - 10;
  }
</style>