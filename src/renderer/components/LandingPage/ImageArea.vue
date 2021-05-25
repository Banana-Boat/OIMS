<template>
  <div class="image-area-content">
    <div ref="imgBox" @click="SelectImgBox(1)"
        :class="['img-box', selectedBox===1?'img-box-selected':'']">
      <canvas id="frontCanvas"></canvas>
    </div>
    <div @click="SelectImgBox(2)"
        :class="['img-box', selectedBox===2?'img-box-selected':'']">
      <canvas id="sideCanvas"></canvas>
    </div>
  </div>
</template>

<script>
/*
  图像显示组件，包含以下内容：
  1. 正位图显示框
  2. 侧位图显示框 */

import { fabric } from 'fabric'
import { convertToJsonString } from 'fast-xml-parser'

export default {
  data () {
    return {
      frontCanvas: null, // 正位图画布
      sideCanvas: null  // 侧位图画布
    }
  },
  mounted () {
    const that = this
    that.$nextTick(() => {  // 当组件被挂载完毕时
      // 创建fabric画布，并根据页面布局改变画布高度
      this.sideCanvas = new fabric.Canvas('sideCanvas')
      this.frontCanvas = new fabric.Canvas('frontCanvas')
      let imgBoxHeight = this.$refs.imgBox.clientHeight
      this.sideCanvas.setHeight(imgBoxHeight - 5)
      this.frontCanvas.setHeight(imgBoxHeight - 5)

      // 渲染当前打开的图片
      if (this.frontCurFilename) {
        let frontImgInfo = JSON.parse(JSON.stringify(this.$store.state.File.params1.resList[this.frontCurFilename]))
        this.ShowImage(1, this.frontCanvas, frontImgInfo)
      }
      if (this.sideCurFilename) {
        let sideImgInfo = JSON.parse(JSON.stringify(this.$store.state.File.params2.resList[this.sideCurFilename]))
        this.ShowImage(2, this.sideCanvas, sideImgInfo)
      }
    })
  },
  computed: {
    frontCurFilename () { // 当前打开的正面图文件名
      return this.$store.state.File.params1.curFilename
    },
    sideCurFilename () { // 当前打开的侧面图文件名
      return this.$store.state.File.params2.curFilename
    },
    selectedBox () { // 当前选中的图片框，用于指定编辑的图片对象（1：正位图区域，2：侧位图区域）
      return this.$store.state.File.selectedImgBox
    }
  },
  watch: {
    frontCurFilename: {
      immediate: false, // 第一次绑定监听对象时不执行handler
      handler: function (nv, ov) {
        this.$nextTick(() => {
          if (nv) {
            let imgInfo = JSON.parse(JSON.stringify(this.$store.state.File.params1.resList[nv]))
            this.$nextTick(() => {
              this.ShowImage(1, this.frontCanvas, imgInfo)
            })
          } else {
            this.frontCanvas.clear()
          }
        })
      }
    },
    sideCurFilename: {
      immediate: false,
      handler: function (nv, ov) {
        this.$nextTick(() => {
          if (nv) {
            let imgInfo = JSON.parse(JSON.stringify(this.$store.state.File.params2.resList[nv]))
            this.$nextTick(() => {
              this.ShowImage(2, this.sideCanvas, imgInfo)
            })
          } else {
            this.sideCanvas.clear()
          }
        })
      }
    }
  },
  methods: {
    /* 功能：选择正/侧位图显示框 */
    SelectImgBox (flag) {
      this.$store.commit('ChangeSelectedImgBox', {
        flag: flag
      })
    },
    /* 功能：显示图片。包含以下操作：
          1. 图片将以画布背景展现
          2. 调整图片与画布大小
          3. 若有量测数据，则渲染至画布上 */
    ShowImage (flag, canvas, imgInfo) {
      let that = this

      canvas.clear() // 清空画布

      let img = new Image()
      img.src = imgInfo.path
      img.onload = () => {

        // 记录图片宽高，并将在画布中打开
        let ratio = img.height / img.width // 当前打开图像的长宽比
        let displayScale = canvas.height / img.height // 画布与图像之间高度比

        canvas.setWidth(canvas.height / ratio)
        fabric.Image.fromURL(imgInfo.path, function (img, isError) {
          img.set({top: 0, left: 0, scaleX: displayScale, scaleY: displayScale})
          canvas.setBackgroundImage(img, () => {
            canvas.renderAll()
            that.$store.commit('ChangeCanvasData', {flag: flag, canvasData: canvas.toDataURL('image/png')})
          })
        })

        //！！！！！仅绘制骨盆参数，其余参数待添加！！！！！

        // 若图片已被量测，则渲染关键点，并设置关键点位置的监听事件
        if (imgInfo.isParsed && flag == 2) {
          let curFilename = this.$store.state.File.params2.curFilename
          let tempResList = JSON.parse(JSON.stringify(this.$store.state.File.params2.resList))
          let sideRes = imgInfo.displayParseRes.sideRes

          if (!imgInfo.isScaled) {  // 如果量测点没有缩放过, 将坐标点缩放至显示比例，并更新至全局变量
            sideRes = that.OriginToDisplay(imgInfo.displayParseRes.sideRes, displayScale)
            tempResList[curFilename].displayParseRes.sideRes = sideRes
            tempResList[curFilename].isScaled = true

            this.$store.commit('ChangeResList', {
              flag: 2,
              resList: tempResList
            })
          }
          

          // 根据关键点，绘制至画布
          let lineAttr = {  // 绘制直线的属性
            fill: 'blue',
            stroke: 'blue',
            strokeWidth: 1,
            selectable: false,
            evented: false
          }
          let pRadius = 2
          let pFill = 'red'

          if (flag == 2) {
            let p25Line = null
            let p01Line = null
            let p34Line = null
            let p0 = null
            let p1 = null
            let p2 = null
            let p3 = null
            let p4 = null
            let p5 = null

            if(sideRes.p5 && sideRes.p2)
              p25Line = new fabric.Line([sideRes.p2[0], sideRes.p2[1], sideRes.p5[0], sideRes.p5[1]], lineAttr)

            if(sideRes.p1 && sideRes.p0)
              p01Line = new fabric.Line([sideRes.p0[0], sideRes.p0[1], sideRes.p1[0], sideRes.p1[1]], lineAttr)
            
            if(sideRes.p2)
              p2 = new fabric.Circle({left: sideRes.p2[0] - pRadius, top: sideRes.p2[1] - pRadius, radius: pRadius, fill: pFill, selectable: false, evented: false})
            
            if(sideRes.p0)
              p0 = new fabric.Circle({
                left: sideRes.p0[0] - pRadius,
                top: sideRes.p0[1] - pRadius,
                radius: pRadius,
                fill: pFill,
                'self': 'p0',
                'centerP': p2 ? p2 : null,
                'adLine': p01Line ? p01Line : null,
                'centerLine': p25Line ? p25Line : null})
            
            if(sideRes.p1)
              p1 = new fabric.Circle({
                left: sideRes.p1[0] - pRadius,
                top: sideRes.p1[1] - pRadius,
                radius: pRadius,
                fill: pFill,
                'self': 'p1',
                'centerP': p2 ? p2 : null,
                'adLine': p01Line ? p01Line : null,
                'centerLine': p25Line ? p25Line : null})

            if(sideRes.p3)
              p34Line = new fabric.Line([sideRes.p3[0], sideRes.p3[1], sideRes.p3[0], sideRes.p3[1]], lineAttr)
            
            if(sideRes.p5)
              p5 = new fabric.Circle({left: sideRes.p5[0] - pRadius, top: sideRes.p5[1] - pRadius, radius: pRadius, fill: pFill, selectable: false, evented: false})
            
            if(sideRes.p3)
              p3 = new fabric.Circle({
                left: sideRes.p3[0] - pRadius,
                top: sideRes.p3[1] - pRadius,
                radius: pRadius,
                fill: pFill,
                'self': 'p3',
                'centerP': p5 ? p5 : null,
                'adLine': p34Line ? p34Line : null,
                'centerLine': p25Line ? p25Line : null})
            
            if(sideRes.p3)
              p4 = new fabric.Circle({
                left: sideRes.p3[0] - pRadius,
                top: sideRes.p3[1] - pRadius,
                radius: pRadius,
                fill: pFill,
                'self': 'p4',
                'centerP': p5 ? p5 : null,
                'adLine': p34Line ? p34Line : null,
                'centerLine': p25Line ? p25Line : null})

            if(sideRes.p0) p0.hasControls = false
            if(sideRes.p1) p1.hasControls = false
            if(sideRes.p2) p2.hasControls = false
            if(sideRes.p3) p3.hasControls = false
            if(sideRes.p4) p4.hasControls = false
            if(sideRes.p5) p5.hasControls = false

            if (sideRes.p4) {
              p34Line.set({'x2': sideRes.p4[0], 'y2': sideRes.p4[1]})
              p4.set({'left': sideRes.p4[0] - pRadius, 'top': sideRes.p4[1] - pRadius})
            }

            if (p01Line) canvas.add(p01Line)
            if (p34Line) canvas.add(p34Line)
            if (p25Line) canvas.add(p25Line)
            if (p0) canvas.add(p0)
            if (p1) canvas.add(p1)
            if (p2) canvas.add(p2)
            if (p3) canvas.add(p3)
            if (p4) canvas.add(p4)
            if (p5) canvas.add(p5)

            canvas.renderAll()
            that.$store.commit('ChangeCanvasData', {flag: flag, canvasData: canvas.toDataURL('image/png')})
            
            // 监听关键点线的位置变化，并重新绘制。
            
            canvas.on('object:moved', (e) => {
              if (e.target) {
                let p = e.target
                if (['p0', 'p1', 'p3', 'p4'].includes(p.self)) {
                  let curFilename = this.$store.state.File.params2.curFilename
                  let tempResList = JSON.parse(JSON.stringify(this.$store.state.File.params2.resList))
                  let sideRes = tempResList[curFilename].displayParseRes.sideRes
                  
                  switch (p.self) {
                    case 'p0':
                      if(p.adLine){ // 区别四个选择分支
                        p.adLine.set({'x1': p.left + pRadius, 'y1': p.top + pRadius})
                        sideRes.p0 = [p.adLine.x1, p.adLine.y1]
                      }

                      if(p.centerP && p.adLine)
                        p.centerP.set({
                          left: (p.adLine.x1 + p.adLine.x2) / 2 - pRadius,
                          top: (p.adLine.y1 + p.adLine.y2) / 2 - pRadius
                        })

                      if(p.centerLine && p.centerP)
                        p.centerLine.set({'x1': p.centerP.left + pRadius, 'y1': p.centerP.top + pRadius})
                        
                      if(sideRes.p2 && p.centerP) // 区别四个选择分支
                        sideRes.p2 = [p.centerP.left, p.centerP.top]

                      break
                    case 'p1':
                      if(p.adLine){
                        p.adLine.set({'x2': p.left + pRadius, 'y2': p.top + pRadius})
                        sideRes.p1 = [p.adLine.x2, p.adLine.y2]
                      }

                      if(p.centerP && p.adLine)
                        p.centerP.set({
                          left: (p.adLine.x1 + p.adLine.x2) / 2 - pRadius,
                          top: (p.adLine.y1 + p.adLine.y2) / 2 - pRadius
                        })

                      if(p.centerLine && p.centerP)
                        p.centerLine.set({'x1': p.centerP.left + pRadius, 'y1': p.centerP.top + pRadius})
                        
                      if(sideRes.p2 && p.centerP)
                        sideRes.p2 = [p.centerP.left, p.centerP.top]

                      break
                    case 'p3':
                      if(p.adLine){
                        p.adLine.set({'x1': p.left + pRadius, 'y1': p.top + pRadius})
                        sideRes.p3 = [p.adLine.x1, p.adLine.y1]
                      }

                      if(p.centerP && p.adLine){
                        p.centerP.set({
                          left: (p.adLine.x1 + p.adLine.x2) / 2 - pRadius,
                          top: (p.adLine.y1 + p.adLine.y2) / 2 - pRadius
                        })
                      }
                        
                      if(p.centerLine && p.centerP)
                        p.centerLine.set({'x2': p.centerP.left + pRadius, 'y2': p.centerP.top + pRadius})

                      if(sideRes.p5 && p.centerP)
                        sideRes.p5 = [p.centerP.left, p.centerP.top]

                      break
                    case 'p4':
                      if(p.adLine){
                        p.adLine.set({'x2': p.left + pRadius, 'y2': p.top + pRadius})
                        sideRes.p4 = [p.adLine.x2, p.adLine.y2]
                      }

                      if(p.centerP){
                        p.centerP.set({
                          left: (p.adLine.x1 + p.adLine.x2) / 2 - pRadius,
                          top: (p.adLine.y1 + p.adLine.y2) / 2 - pRadius
                        })
                      }

                      if(p.centerLine && p.centerP)
                        p.centerLine.set({'x2': p.centerP.left + pRadius, 'y2': p.centerP.top + pRadius})
                      
                      if(sideRes.p5 && p.centerP)
                        sideRes.p5 = [p.centerP.left, p.centerP.top]

                      break
                  }

                  // 将拖拽后的点存入全局
                  tempResList[curFilename].displayParseRes.sideRes = sideRes
                  that.$store.commit('ChangeResList', {
                    flag: 2,
                    resList: tempResList
                  })
                  // 更新全局变量
                  that.$store.commit('ChangeCanvasData', {flag: flag, canvasData: canvas.toDataURL('image/png')})
                }
              }
            })

            canvas.on('object:moving', (e) => {
              if (e.target) {
                let p = e.target
                if (['p0', 'p1', 'p3', 'p4'].includes(p.self)) {
                  
                  switch (p.self) {
                    case 'p0':
                      if(p.adLine){ // 区别四个选择分支
                        p.adLine.set({'x1': p.left + pRadius, 'y1': p.top + pRadius})
                      }

                      if(p.centerP && p.adLine)
                        p.centerP.set({
                          left: (p.adLine.x1 + p.adLine.x2) / 2 - pRadius,
                          top: (p.adLine.y1 + p.adLine.y2) / 2 - pRadius
                        })

                      if(p.centerLine && p.centerP)
                        p.centerLine.set({'x1': p.centerP.left + pRadius, 'y1': p.centerP.top + pRadius})
                        
                      break
                    case 'p1':
                      if(p.adLine){
                        p.adLine.set({'x2': p.left + pRadius, 'y2': p.top + pRadius})
                      }

                      if(p.centerP && p.adLine)
                        p.centerP.set({
                          left: (p.adLine.x1 + p.adLine.x2) / 2 - pRadius,
                          top: (p.adLine.y1 + p.adLine.y2) / 2 - pRadius
                        })

                      if(p.centerLine && p.centerP)
                        p.centerLine.set({'x1': p.centerP.left + pRadius, 'y1': p.centerP.top + pRadius})
                        
                      break
                    case 'p3':
                      if(p.adLine){
                        p.adLine.set({'x1': p.left + pRadius, 'y1': p.top + pRadius})
                      }

                      if(p.centerP && p.adLine){
                        p.centerP.set({
                          left: (p.adLine.x1 + p.adLine.x2) / 2 - pRadius,
                          top: (p.adLine.y1 + p.adLine.y2) / 2 - pRadius
                        })
                      }
                        
                      if(p.centerLine && p.centerP)
                        p.centerLine.set({'x2': p.centerP.left + pRadius, 'y2': p.centerP.top + pRadius})

                      break
                    case 'p4':
                      if(p.adLine){
                        p.adLine.set({'x2': p.left + pRadius, 'y2': p.top + pRadius})
                      }

                      if(p.centerP){
                        p.centerP.set({
                          left: (p.adLine.x1 + p.adLine.x2) / 2 - pRadius,
                          top: (p.adLine.y1 + p.adLine.y2) / 2 - pRadius
                        })
                      }

                      if(p.centerLine && p.centerP)
                        p.centerLine.set({'x2': p.centerP.left + pRadius, 'y2': p.centerP.top + pRadius})
                    
                      break
                  }
                }
              }
            })
          }

        }
      }
    },
    /* 功能：根据图片缩放比率,将坐标点从原始大小缩放至显示大小 */
    OriginToDisplay(pointList, displayScale) {
      for(let key in pointList) {
        if (pointList[key]) {
          pointList[key][0] *= displayScale
          pointList[key][1] *= displayScale
        }
      }
      return pointList
    },
  }
}
</script>

<style lang="less">
  // 图片框
  .image-area-content{
    display: flex;
    justify-content: space-around;
    height: 100%;
  }
  .img-box{
    height: 100%;
    width: 50%;
    margin: 0 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0px 5px 20px 0px #bababa;
  }
  .img-box::-webkit-scrollbar {
    width: 7px;
    height: 7px;
  }
  .img-box::-webkit-scrollbar-thumb {
    background-color: #c4c4c4;
    border-radius: 3px;
  }
  .img-box-selected {
    box-shadow: 0px 0px 18px 0px #6958c7;
  }
</style>