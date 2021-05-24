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
    frontCurFileRes () {
      let params = this.$store.state.File.params1
      if (params.resList[params.curFilename]) 
        return JSON.parse(JSON.stringify(params.resList[params.curFilename]))
      else 
        return false
    },
    sideCurFileRes () {
      let params = this.$store.state.File.params2
      if (params.resList[params.curFilename]) 
        return JSON.parse(JSON.stringify(params.resList[params.curFilename]))
      else 
        return false
    }
  },
  watch: {
    /* 功能：监听当前打开正面图文件的量测结果信息 */
    frontCurFileRes: {
      immediate: false,
      handler: function(nv, ov) {
        if (nv)     // 未选择图片文件目录时，文件结果项不存在
          this.Refresh(1, nv)
      }
    },
    /* 功能：监听当前打开侧面图文件的量测结果信息 */
    sideCurFileRes: {
      immediate: false,
      handler: function(nv, ov) {
        if (nv)     // 未选择图片文件目录时，文件结果项不存在
          this.Refresh(2, nv)
      }
    }
  },
  methods: {
    /* 功能：刷新页面结果面板信息 */
    Refresh (flag, curFileRes) {
      
      if (flag == 1) {
        if (curFileRes.isParsed) {
          // ！！！！！！由于cva是两点间距离，若采用displayParseRes，则需根据显示比率进行缩放，待改！！
          let coronalResult = this.CalCoronalResult(curFileRes.originParseRes.frontRes)
          this.result.coronal = coronalResult

          this.isFrontMeasured = true
        } else {
          this.isFrontMeasured = false
        }
        
      } else {
        if (curFileRes.isParsed) {
          let sideRes = curFileRes.displayParseRes.sideRes

          let pelvisResult = this.CalPelvisResult(sideRes)
          this.result.pelvis = pelvisResult

          // ！！！！！！由于sva是两点间距离，若采用displayParseRes，则需根据显示比率进行缩放，待改！！
          let sagittalResult = this.CalSagittalResult(curFileRes.originParseRes.sideRes)
          this.result.sagittal = sagittalResult
          
          this.isSideMeasured = true
        } else {
          this.isSideMeasured = false
        }
      }

      if (curFileRes.isParsed) {
        this.$store.commit('ChangeCurEntireRes', {
          curEntireRes: JSON.parse(JSON.stringify(this.result))
        })
      } 
      
    },
    /* 功能：计算冠状位参数(cva, cobb)，注：医学图像分辨率固定为96 */
    CalCoronalResult (frontRes) {
      let cva = null
      let cobb = null

      // 计算需要c7和sacrum
      if (frontRes.p6 && frontRes.p7 && frontRes.p0) {
        let c7_middle_x = (frontRes.p6[0] + frontRes.p7[0]) / 2
        let sacrum_left_x = frontRes.p0[0]
        cva = ((Math.abs(c7_middle_x - sacrum_left_x)) / 96 * 25.4)
      }

      // 计算需要cobb1和cobb2
      if (frontRes.p2 && frontRes.p3 && frontRes.p4 && frontRes.p5) {
        let upper_angle = (Math.atan((frontRes.p3[1] - frontRes.p2[1]) / (frontRes.p3[0] - frontRes.p2[0])))
                          * 180 / Math.PI
        let lower_angle = (Math.atan((frontRes.p5[1] - frontRes.p4[1]) / (frontRes.p5[0] - frontRes.p4[0])))
                          * 180 / Math.PI
        cobb = upper_angle + lower_angle
      }

      return {
        cva: cva ? cva.toFixed(2) + 'mm' : '识别区域缺失，请手动量测',
        cobb: cobb ? cobb.toFixed(2) + '°' : '识别区域缺失，请手动量测'
      }
    },

    /* 功能：计算矢状位参数(sva, ll)，注：医学图像分辨率固定为96 */
    CalSagittalResult (sideRes) {
      let sva = null
      let ll = null

      // 计算需要c7和sacrum
      if (sideRes.p6 && sideRes.p7 && sideRes.p0) {
        let c7_middle_x = (sideRes.p6[0] + sideRes.p7[0]) / 2
        let sacrum_left_x = sideRes.p0[0]
        sva = ((Math.abs(c7_middle_x - sacrum_left_x)) / 96 * 25.4)
      }

      // 计算需要t12和sacrum
      if (sideRes.p8 && sideRes.p9 && sideRes.p0 && sideRes.p1 ) {
        let upper_angle = (Math.atan((sideRes.p9[1] - sideRes.p8[1]) / (sideRes.p9[0] - sideRes.p8[0])))
                          * 180 / Math.PI
        let lower_angle = (Math.atan((sideRes.p1[1] - sideRes.p0[1]) / (sideRes.p1[0] - sideRes.p0[0])))
                          * 180 / Math.PI
        ll = upper_angle + lower_angle
      }

      return {
        sva: sva ? sva.toFixed(2) + 'mm' : '识别区域缺失，请手动量测',
        ll: ll ? ll.toFixed(2) + '°' : '识别区域缺失，请手动量测'
      }
    },
    
    /* 功能：计算骨盆相关参数(ss, pt, pi) */
    CalPelvisResult (sideRes) {
      let ss = null
      let pt = null
      let pi = null

      if(sideRes.p1 && sideRes.p0)
        ss = Math.atan((sideRes.p1[1] - sideRes.p0[1]) / (sideRes.p1[0] - sideRes.p0[0])) * 180 / Math.PI
      
      if(sideRes.p5 && sideRes.p2)
        pt = 90.0 - (Math.atan((sideRes.p2[1] - sideRes.p5[1]) / (sideRes.p2[0] - sideRes.p5[0])) * 180 / Math.PI)
      
      if(sideRes.p1 && sideRes.p0 && sideRes.p5 && sideRes.p2)
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