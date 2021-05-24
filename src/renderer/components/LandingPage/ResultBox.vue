<template>
  <div v-draggable class="result-box" v-if="isShowResultBox">
    <div class="header-box">
      <span class="header-text">量测结果</span>
      <i class="fa fa-close close-icon" @click="CloseResultBox"></i>
    </div>
    <div class="content-box">

      <div>
        <div class="front-content-box"  v-if="isFrontMeasured">
          <div class="content-group">
            <span class="content-group-title">冠状位参数</span>
            <span><span style="font-weight:bold;">cva</span> : {{result.coronal.cva}}</span>
            <span><span style="font-weight:bold;">cobb</span> : {{result.coronal.cobb}}</span>
          </div>
        </div>

        <div class="side-content-box"  v-if="isSideMeasured">
          <div class="content-group">
            <span class="content-group-title">矢状位参数</span>
            <span><span style="font-weight:bold;">sva</span> : {{result.sagittal.sva}}</span>
            <span><span style="font-weight:bold;">ll</span> : {{result.sagittal.ll}}</span>
          </div>
          <div class="content-group">
            <span class="content-group-title">骨盆参数</span>
            <span><span style="font-weight:bold;">ss</span> : {{result.pelvis.ss}}</span>
            <span><span style="font-weight:bold;">pt</span> : {{result.pelvis.pt}}</span>
            <span><span style="font-weight:bold;">pi</span> : {{result.pelvis.pi}}</span>
          </div>
        </div>
      </div>

      <div class="standard-link">
        <el-link type="primary" @click="ShowStandard">分型标准</el-link>
      </div>
      <el-dialog :visible="isShowStandardDialog" @close="CloseStandardDialog" width="40%" :append-to-body="true">
        <div slot="title">
          <span style="font-size:1.3rem">分型标准</span>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import { Draggable } from 'draggable-vue-directive'

export default {
  directives: {
      Draggable,
  },
  props: ['isShowResultBox'],
  data () {
    return {
      result: { // 计算结果对象（包括骨盆、矢状位、冠状位三类参数）
        pelvis: {
          ss: '',
          pt: '',
          pi: ''
        },
        sagittal: {
          sva: '',
          ll: ''
        },
        coronal: {
          cva: '',
          cobb: ''
        }
      },
      isFrontMeasured: false, // 正面图是否被量测的标志位
      isSideMeasured: false, // 侧面图是否被量测的标志位
      isShowStandardDialog: false // 是否显示分型标准的弹窗
    }
  },
  computed: {
    frontCurFilename () {
      return this.$store.state.File.params1.curFilename
    },
    sideCurFilename () {
      return this.$store.state.File.params2.curFilename
    },
  },
  watch: {
    frontCurFilename: {
      immediate: true,
      handler: function(nv, ov) {
        let curFilename = nv
        this.Refresh(1, curFilename)
      }
    },
    sideCurFilename: {
      immediate: true,
      handler: function(nv, ov) {
        let curFilename = nv
        this.Refresh(2, curFilename)
      }
    }
  },
  methods: {
    /* 功能：刷新页面结果面板信息 */
    Refresh (flag, curFilename) {
      let params = flag === 1 ? this.$store.state.File.params1 : this.$store.state.File.params2
      let curEntireRes = JSON.parse(JSON.stringify(this.$store.state.File.curEntireRes))
      let isMeasured = false
      let measureRes = {}
      
      if (params.resList[curFilename]) {
        isMeasured = JSON.parse(JSON.stringify(params.resList[curFilename].isMeasured))
        measureRes = JSON.parse(JSON.stringify(params.resList[curFilename].measureRes))
      }

      if (flag == 1) {
        if (isMeasured) {
          let coronalResult = this.CalCoronalResult(measureRes)
          this.result.coronal = coronalResult
        }
        this.isFrontMeasured = isMeasured
        
      } else {
        if (isMeasured) {
          let pelvisResult = this.CalPelvisResult(measureRes)
          let sagittalResult = this.CalSagittalResult(measureRes)
          this.result.pelvis = pelvisResult
          this.result.sagittal = sagittalResult
        }
        this.isSideMeasured = isMeasured
      }

      if (isMeasured) {
        this.$store.commit('ChangeCurEntireRes', {
          curEntireRes: JSON.parse(JSON.stringify(this.result))
        })
      } 
      
    },
    /* 功能：计算冠状位参数(cva, cobb)，注：医学图像分辨率固定为96 */
    CalCoronalResult (measureRes) {
      let cva = null
      let cobb = null

      if (measureRes.c7 && measureRes.sacrum) {
        let c7_middle_x = (measureRes.c7.xmin + measureRes.c7.xmax) / 2
        let sacrum_left_x = measureRes.sacrum.xmin
        cva = ((Math.abs(c7_middle_x - sacrum_left_x)) / 96 * 25.4)
      }

      if (measureRes.cobb1 && measureRes.cobb2) {
        let upper_angle = (Math.atan((measureRes.cobb1.ymax - measureRes.cobb1.ymin) / (measureRes.cobb1.xmax - measureRes.cobb1.xmin)))
                          * 180 / Math.PI
        let lower_angle = (Math.atan((measureRes.cobb2.ymax - measureRes.cobb2.ymin) / (measureRes.cobb2.xmax - measureRes.cobb2.xmin)))
                          * 180 / Math.PI
        cobb = upper_angle + lower_angle
      }

      return {
        cva: cva ? cva.toFixed(2) + 'mm' : '识别区域缺失，请手动量测',
        cobb: cobb ? cobb.toFixed(2) + '°' : '识别区域缺失，请手动量测'
      }
    },

    /* 功能：计算矢状位参数(sva, ll)，注：医学图像分辨率固定为96 */
    CalSagittalResult (measureRes) {
      let sva = null
      let ll = null

      if (measureRes.c7 && measureRes.sacrum) {
        let c7_middle_x = (measureRes.c7.xmin + measureRes.c7.xmax) / 2
        let sacrum_left_x = measureRes.sacrum.xmin
        sva = ((Math.abs(c7_middle_x - sacrum_left_x)) / 96 * 25.4)
      }

      if (measureRes.t12 && measureRes.sacrum) {
        let upper_angle = (Math.atan((measureRes.t12.ymax - measureRes.t12.ymin) / (measureRes.t12.xmax - measureRes.t12.xmin)))
                          * 180 / Math.PI
        let lower_angle = (Math.atan((measureRes.sacrum.ymax - measureRes.sacrum.ymin) / (measureRes.sacrum.xmax - measureRes.sacrum.xmin)))
                          * 180 / Math.PI
        ll = upper_angle + lower_angle
      }

      return {
        sva: sva ? sva.toFixed(2) + 'mm' : '识别区域缺失，请手动量测',
        ll: ll ? ll.toFixed(2) + '°' : '识别区域缺失，请手动量测'
      }
    },
    
    /* 功能：计算骨盆相关参数(ss, pt, pi) */
    CalPelvisResult (measureRes) {
      let p0 = null
      let p1 = null
      let p2 = null
      let p3 = null
      let p4 = null
      let p5 = null

      let ss = null
      let pt = null
      let pi = null

      if (measureRes.sacrum) {
        let sXmin = Number.parseInt(measureRes.sacrum.xmin)
        let sYmin = Number.parseInt(measureRes.sacrum.ymin)
        let sXmax = Number.parseInt(measureRes.sacrum.xmax)
        let sYmax = Number.parseInt(measureRes.sacrum.ymax)
        p0 = [sXmin, sYmin]
        p1 = [sXmax, sYmax]
      }
      
      if (measureRes.femoralhead1) {
        let f1Xmin = Number.parseInt(measureRes.femoralhead1.xmin)
        let f1Ymin = Number.parseInt(measureRes.femoralhead1.ymin)
        let f1Xmax = Number.parseInt(measureRes.femoralhead1.xmax)
        let f1Ymax = Number.parseInt(measureRes.femoralhead1.ymax)
        if (p0 && p1) 
          p2 = [(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2]
        p3 = [(f1Xmin + f1Xmax) / 2, (f1Ymin + f1Ymax) / 2]
        p5 = p3
        p4 = null
      }
      // 当第二个股骨头不存在时，即等同于第一个股骨头
      if (measureRes.femoralhead2) {
        let f2Xmin = Number.parseInt(measureRes.femoralhead2.xmin)
        let f2Ymin = Number.parseInt(measureRes.femoralhead2.ymin)
        let f2Xmax = Number.parseInt(measureRes.femoralhead2.xmax)
        let f2Ymax = Number.parseInt(measureRes.femoralhead2.ymax)
        p4 = [(f2Xmin + f2Xmax) / 2, (f2Ymin + f2Ymax) / 2]
        p5 = [(p3[0] + p4[0]) / 2, (p3[1] + p4[1]) / 2]
      }

      if(p1 && p0)
        ss = Math.atan((p1[1] - p0[1]) / (p1[0] - p0[0])) * 180 / Math.PI
      
      if(p5 && p2)
        pt = 90.0 - (Math.atan((p2[1] - p5[1]) / (p2[0] - p5[0])) * 180 / Math.PI)
      
      if(p1 && p0 && p5 && p2)
        pi = ss + pt

      return {
        ss: ss ? ss.toFixed(2) + '°' : '识别区域缺失，请手动量测',
        pt: pt ? pt.toFixed(2) + '°' : '识别区域缺失，请手动量测',
        pi: pi ? pi.toFixed(2) + '°' : '识别区域缺失，请手动量测'
      }
    },
    /* 功能：关闭结果显示窗 */
    CloseResultBox () {
      this.$emit('CloseResultBox')
    },
    /* 功能：显示分型标准弹窗 */
    ShowStandard () {
      this.isShowStandardDialog = true
    },
    /* 功能：关闭分型标准弹窗 */
    CloseStandardDialog() {
      this.isShowStandardDialog = false
    }
  }
}
</script>

<style lang="less">
  // 量测结果栏
  .result-box{
    display: flex;
    flex-direction: column;

    position: fixed;
    top: 80px;
    left: 30px;
    z-index: 10000;
    width: 25vw;
    height: 60vh;
    cursor: move;

    background-color: #FFF;
    border: 1px solid #EBEEF5;
    box-shadow: -6px 6px 20px 0px #a7a7a7;
    border-radius: 5px;
  }
  .result-box:hover{
    transition-timing-function: cubic-bezier(0.175, 0.885, 0.32, 1.275);
    transition-duration: 250ms;
    transform: scale(1.04);
    box-shadow: -10px 10px 30px 0px #a0a0a0;
    border-radius: 10px;
  }
  .header-box{
    height: 5%;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    padding: 15px 20px ;
    border-bottom: 1px solid #EBEEF5;
  }
  .header-text{
    align-self: center;
    font-size: 1.1rem;
    font-weight: bold;
    color: black;
  }
  .close-icon{
    zoom: 1.1;
    align-self: center;
    color: rgb(168, 168, 168);
  }
  .close-icon:hover{
    cursor: pointer;
    color: rgb(240, 106, 106);
  }
  .content-box{
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 95%;
    padding: 0.4rem 1.2rem;
  }

  .content-group{
    display: flex;
    flex-direction: column;
    border-bottom: 3px dotted #c7c7c7;
    padding: 0.6rem 0;
  }
  .content-group-title {
    align-self: center;
    margin-bottom: 0.2rem;
  }

  .standard-link{
    align-self: flex-end;
    margin-bottom: 1rem;
  }
</style>