<template>
  <div class="image-area-content">
    <div ref="imgBox" @click="SelectImgBox(1)"
        :class="['img-box', selectedBox===1?'img-box-selected':'']">
      <canvas id="canvas1"></canvas>
    </div>
    <div @click="SelectImgBox(2)"
        :class="['img-box', selectedBox===2?'img-box-selected':'']">
      <canvas id="canvas2"></canvas>
    </div>
  </div>
</template>

<script>
import { fabric } from 'fabric'

var canvas1 = null
var canvas2 = null

export default {
  data () {
    return {
    }
  },
  computed: {
    img1Name () {
      return this.$store.state.File.params1.curFilename
    },
    img2Name () {
      return this.$store.state.File.params2.curFilename
    },
    selectedBox () {
      return this.$store.state.File.selectedImgBox
    }
  },
  watch: {
    img1Name (nv, ov) {
      if (nv !== '') {
        let imgInfo = JSON.parse(JSON.stringify(this.$store.state.File.params1.resList[nv]))
        this.ShowImage(1, canvas1, imgInfo)
      } else {
        canvas1.clear()
      }
    },
    img2Name (nv, ov) {
      if (nv !== '') {
        let imgInfo = JSON.parse(JSON.stringify(this.$store.state.File.params2.resList[nv]))
        this.ShowImage(2, canvas2, imgInfo)
      } else {
        canvas2.clear()
      }
    }
  },
  methods: {
    SelectImgBox (flag) {
      this.$store.commit('ChangeSelectedImgBox', {
        flag: flag
      })
    },
    // 将图片设置为背景，并调整图片与画布大小。若有量测数据，则渲染至画布上
    ShowImage (flag, canvas, imgInfo) {
      let that = this
      canvas.clear() // 清空画布
      let img = new Image()
      img.src = imgInfo.path
      img.onload = () => {
        let ratio = img.height / img.width
        let scale = canvas.height / img.height
        let originalHeight = img.height
        canvas.setWidth(canvas.height / ratio)
        fabric.Image.fromURL(imgInfo.path, function (img, isError) {
          img.set({top: 0, left: 0, scaleX: scale, scaleY: scale})
          canvas.setBackgroundImage(img, () => {
            canvas.renderAll()
            that.$store.commit('ChangeCanvasData', {flag: flag, canvasData: canvas.toDataURL('image/png')})
          })
        })
        // 解析数据并绘制图线
        if (imgInfo.isMeasured) {
          let parseRes = {}
          let filename = imgInfo.path.split('\\').pop()
          if (!imgInfo.isParsed) {
            parseRes = that.ParseResult(imgInfo.measureRes, scale, originalHeight)
            let tempResList = JSON.parse(JSON.stringify(that.$store.state.File.params2.resList))
            tempResList[filename].isParsed = true
            tempResList[filename]['parseRes'] = parseRes
            that.$store.commit('ChangeResList', {
              flag: 2,
              resList: tempResList
            })
          } else {
            parseRes = JSON.parse(JSON.stringify(that.$store.state.File.params2.resList[filename].parseRes))
          }
          let lineAttr = {
            fill: 'blue',
            stroke: 'blue',
            strokeWidth: 1,
            selectable: false,
            evented: false
          }
          let pRadius = 2
          let pFill = 'red'
          let p25Line = new fabric.Line([parseRes.p2[0], parseRes.p2[1], parseRes.p5[0], parseRes.p5[1]], lineAttr)
          let p01Line = new fabric.Line([parseRes.p0[0], parseRes.p0[1], parseRes.p1[0], parseRes.p1[1]], lineAttr)
          let p2 = new fabric.Circle({left: parseRes.p2[0] - pRadius, top: parseRes.p2[1] - pRadius, radius: pRadius, fill: pFill, selectable: false, evented: false})
          let p0 = new fabric.Circle({
            left: parseRes.p0[0] - pRadius,
            top: parseRes.p0[1] - pRadius,
            radius: pRadius,
            fill: pFill,
            'self': 'p0',
            'centerP': p2,
            'adLine': p01Line,
            'centerLine': p25Line})
          let p1 = new fabric.Circle({
            left: parseRes.p1[0] - pRadius,
            top: parseRes.p1[1] - pRadius,
            radius: pRadius,
            fill: pFill,
            'self': 'p1',
            'centerP': p2,
            'adLine': p01Line,
            'centerLine': p25Line})
          let p34Line = new fabric.Line([parseRes.p3[0], parseRes.p3[1], parseRes.p3[0], parseRes.p3[1]], lineAttr)
          let p5 = new fabric.Circle({left: parseRes.p5[0] - pRadius, top: parseRes.p5[1] - pRadius, radius: pRadius, fill: pFill, selectable: false, evented: false})
          let p3 = new fabric.Circle({
            left: parseRes.p3[0] - pRadius,
            top: parseRes.p3[1] - pRadius,
            radius: pRadius,
            fill: pFill,
            'self': 'p3',
            'centerP': p5,
            'adLine': p34Line,
            'centerLine': p25Line})
          let p4 = new fabric.Circle({
            left: parseRes.p3[0] - pRadius,
            top: parseRes.p3[1] - pRadius,
            radius: pRadius,
            fill: pFill,
            'self': 'p4',
            'centerP': p5,
            'adLine': p34Line,
            'centerLine': p25Line})
          p0.hasControls = false
          p1.hasControls = false
          p2.hasControls = false
          p3.hasControls = false
          p4.hasControls = false
          p5.hasControls = false
          if (parseRes.p4 != null) {
            p34Line.set({'x2': parseRes.p4[0], 'y2': parseRes.p4[1]})
            p4.set({'left': parseRes.p4[0] - pRadius, 'top': parseRes.p4[1] - pRadius})
          }
          canvas.add(p01Line, p34Line, p25Line, p0, p1, p2, p3, p4, p5)
          canvas.renderAll()
          // 更新全局变量
          that.$store.commit('ChangeCanvasData', {flag: flag, canvasData: canvas.toDataURL('image/png')})
          // 画布监听事件
          canvas.on('object:moving', (e) => {
            if (e.target) {
              let p = e.target
              if (['p0', 'p1', 'p3', 'p4'].includes(p.self)) {
                let curFilename = this.$store.state.File.params2.curFilename
                let tempResList = JSON.parse(JSON.stringify(this.$store.state.File.params2.resList))
                switch (p.self) {
                  case 'p0':
                    p.adLine.set({'x1': p.left + pRadius, 'y1': p.top + pRadius})
                    p.centerP.set({
                      left: (p.adLine.x1 + p.adLine.x2) / 2 - pRadius,
                      top: (p.adLine.y1 + p.adLine.y2) / 2 - pRadius
                    })
                    p.centerLine.set({'x1': p.centerP.left + pRadius, 'y1': p.centerP.top + pRadius})
                    tempResList[curFilename].parseRes.p0 = [p.adLine.x1, p.adLine.y1]
                    tempResList[curFilename].parseRes.p2 = [p.centerP.left, p.centerP.top]
                    break
                  case 'p1':
                    p.adLine.set({'x2': p.left + pRadius, 'y2': p.top + pRadius})
                    p.centerP.set({
                      left: (p.adLine.x1 + p.adLine.x2) / 2 - pRadius,
                      top: (p.adLine.y1 + p.adLine.y2) / 2 - pRadius
                    })
                    p.centerLine.set({'x1': p.centerP.left + pRadius, 'y1': p.centerP.top + pRadius})
                    tempResList[curFilename].parseRes.p1 = [p.adLine.x2, p.adLine.y2]
                    tempResList[curFilename].parseRes.p2 = [p.centerP.left, p.centerP.top]
                    break
                  case 'p3':
                    p.adLine.set({'x1': p.left + pRadius, 'y1': p.top + pRadius})
                    p.centerP.set({
                      left: (p.adLine.x1 + p.adLine.x2) / 2 - pRadius,
                      top: (p.adLine.y1 + p.adLine.y2) / 2 - pRadius
                    })
                    p.centerLine.set({'x2': p.centerP.left + pRadius, 'y2': p.centerP.top + pRadius})
                    tempResList[curFilename].parseRes.p3 = [p.adLine.x1, p.adLine.y1]
                    tempResList[curFilename].parseRes.p5 = [p.centerP.left, p.centerP.top]
                    break
                  case 'p4':
                    p.adLine.set({'x2': p.left + pRadius, 'y2': p.top + pRadius})
                    p.centerP.set({
                      left: (p.adLine.x1 + p.adLine.x2) / 2 - pRadius,
                      top: (p.adLine.y1 + p.adLine.y2) / 2 - pRadius
                    })
                    p.centerLine.set({'x2': p.centerP.left + pRadius, 'y2': p.centerP.top + pRadius})
                    tempResList[curFilename].parseRes.p4 = [p.adLine.x2, p.adLine.y2]
                    tempResList[curFilename].parseRes.p5 = [p.centerP.left, p.centerP.top]
                    break
                }
                that.$store.commit('ChangeResList', {
                  flag: 2,
                  resList: tempResList
                })
                // 更新全局变量
                that.$store.commit('ChangeCanvasData', {flag: flag, canvasData: canvas.toDataURL('image/png')})
              }
            }
          })
        }
      }
    },
    // 解析点坐标
    ParseResult (measureRes, scale, originalHeight) {
      let parseRes = {}
      let sXmin = this.RestoreX(measureRes.sacrum.xmin, scale)
      let sYmin = this.RestoreY(measureRes.sacrum.ymin, scale, originalHeight)
      let sXmax = this.RestoreX(measureRes.sacrum.xmax, scale)
      let sYmax = this.RestoreY(measureRes.sacrum.ymax, scale, originalHeight)
      let f1Xmin = this.RestoreX(measureRes.femoralhead1.xmin, scale)
      let f1Ymin = this.RestoreY(measureRes.femoralhead1.ymin, scale, originalHeight)
      let f1Xmax = this.RestoreX(measureRes.femoralhead1.xmax, scale)
      let f1Ymax = this.RestoreY(measureRes.femoralhead1.ymax, scale, originalHeight)
      let p0 = [sXmin, sYmin]
      let p1 = [sXmax, sYmax]
      let p2 = [(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2]
      let p3 = [(f1Xmin + f1Xmax) / 2, (f1Ymin + f1Ymax) / 2]
      let p5 = p3
      let p4 = null
      // 第二个股骨头可能不存在
      if (measureRes.hasOwnProperty('femoralhead2')) {
        let f2Xmin = this.RestoreX(measureRes.femoralhead2.xmin, scale)
        let f2Ymin = this.RestoreY(measureRes.femoralhead2.ymin, scale, originalHeight)
        let f2Xmax = this.RestoreX(measureRes.femoralhead2.xmax, scale)
        let f2Ymax = this.RestoreY(measureRes.femoralhead2.ymax, scale, originalHeight)
        p4 = [(f2Xmin + f2Xmax) / 2, (f2Ymin + f2Ymax) / 2]
        p5 = [(p3[0] + p4[0]) / 2, (p3[1] + p4[1]) / 2]
      }
      parseRes = {
        'p0': p0,
        'p1': p1,
        'p2': p2,
        'p3': p3,
        'p4': p4,
        'p5': p5
      }
      return parseRes
    },
    // 还原x坐标
    RestoreX (x, scale) {
      let res = Number.parseInt(x) * 5 * scale
      return Number.parseInt(res)
    },
    // 还原y坐标
    RestoreY (y, scale, originalHeight) {
      let res = (Number.parseInt(y) * 5 + originalHeight / 2) * scale
      return Number.parseInt(res)
    }
  },
  mounted () {
    const that = this
    that.$nextTick(() => {
      canvas1 = new fabric.Canvas('canvas1')
      canvas2 = new fabric.Canvas('canvas2')
      let imgBoxHeight = this.$refs.imgBox.clientHeight
      canvas1.setHeight(imgBoxHeight - 5)
      canvas2.setHeight(imgBoxHeight - 5)
    })
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