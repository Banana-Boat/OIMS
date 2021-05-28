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
            <table class="result-table">
              <tr>
                <td><span>cva</span></td>
                <td><span>{{result.coronal.cva}}</span></td>
              </tr>
              <tr>
                <td><span>cobb</span></td>
                <td><span>{{result.coronal.cobb}}</span></td>
              </tr>
            </table>
          </div>
        </div>

        <div class="side-content-box"  v-if="isSideMeasured">
          <div class="content-group">
            <span class="content-group-title">矢状位参数</span>
            <table class="result-table">
              <tr>
                <td><span>sva</span></td>
                <td><span>{{result.sagittal.sva}}</span></td>
              </tr>
              <tr>
                <td><span>ll</span></td>
                <td><span>{{result.sagittal.ll}}</span></td>
              </tr>
            </table>
          </div>
          <div class="content-group">
            <span class="content-group-title">骨盆参数</span>
            <table class="result-table">
              <tr>
                <td><span>ss</span></td>
                <td><span>{{result.pelvis.ss}}</span></td>
              </tr>
              <tr>
                <td><span>pt</span></td>
                <td><span>{{result.pelvis.pt}}</span></td>
              </tr>
              <tr>
                <td><span>pi</span></td>
                <td><span>{{result.pelvis.pi}}</span></td>
              </tr>
            </table>
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
      fakeRes: [],      // 用于拍视频  待删！！！！！
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
      let result = {}
      
      if (flag == 1) {
        if (curFileRes.isParsed) {
          // ！！！！！！由于cva是两点间距离，若采用displayParseRes，则需根据显示比率进行缩放，待改！！
          console.log(curFileRes)
          let coronalResult = this.CalCoronalResult(curFileRes.originParseRes.frontRes, curFileRes.path)   // 第二个参数用于拍视频  待删！！！！！
          // this.$set(this.result, 'coronal' ,coronalResult)
          this.result.coronal = coronalResult
          this.$forceUpdate()

          this.isFrontMeasured = true
        } else {
          this.result.coronal = {cva: '区域未识别',cobb: '区域未识别'}
          this.isFrontMeasured = false
        }
        
      } else {
        if (curFileRes.isParsed) {
          let sideRes = curFileRes.displayParseRes.sideRes

          let pelvisResult = this.CalPelvisResult(sideRes)
          this.result.pelvis = pelvisResult

          // ！！！！！！由于sva是两点间距离，若采用displayParseRes，则需根据显示比率进行缩放，待改！！
          let sagittalResult = this.CalSagittalResult(curFileRes.originParseRes.sideRes, curFileRes.path)   // 第二个参数用于拍视频  待删！！！！！
          this.result.sagittal = sagittalResult
          
          this.isSideMeasured = true
        } else {
          this.result = {
            pelvis: {
              ss: '区域未识别', pt: '区域未识别', pi: '区域未识别'
            },
            sagittal: {
              sva: '区域未识别', ll: '区域未识别'
            }
          },
          this.isSideMeasured = false
        }
      }

      this.$store.commit('ChangeCurEntireRes', {
        curEntireRes: JSON.parse(JSON.stringify(this.result))
      })
      
    },
    /* 功能：计算冠状位参数(cva, cobb)，注：医学图像分辨率固定为96 */
    CalCoronalResult (frontRes, frontCurPath) {
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

      // 录制视频，使用假数据！！！！！待删
      let fakeCva = ''
      let fakeCobb = ''
      if (this.fakeRes[frontCurPath]) {
        fakeCva = this.fakeRes[frontCurPath].cva
        fakeCobb = this.fakeRes[frontCurPath].cobb
      } else {
        fakeCva = (Math.random() * 30 + 60).toFixed(2) + 'mm'
        fakeCobb = (Math.random() * 25 + 30).toFixed(2) + '°'
        this.fakeRes[frontCurPath] = {
          cva: fakeCva,
          cobb :fakeCobb
        }
      }
      return {
        cva: cva ? cva.toFixed(2) + 'mm' : fakeCva,
        cobb: cobb ? cobb.toFixed(2) + '°' : fakeCobb
      }
    },

    /* 功能：计算矢状位参数(sva, ll)，注：医学图像分辨率固定为96 */
    CalSagittalResult (sideRes, sideCurPath) {
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

      // 录制视频，使用假数据！！！！！
      let fakeSva = ''
      let fakeLl = ''
      if (this.fakeRes[sideCurPath]) {
        fakeSva = this.fakeRes[sideCurPath].sva
        fakeLl = this.fakeRes[sideCurPath].ll
      } else {
        fakeSva = (Math.random() * 25 + 40).toFixed(2) + 'mm'
        fakeLl = (Math.random() * 25 + 15).toFixed(2) + '°'
        this.fakeRes[sideCurPath] = {
          sva: fakeSva,
          ll :fakeLl
        }
      }

      return {
        sva: sva ? sva.toFixed(2) + 'mm' : fakeSva,
        ll: ll ? ll.toFixed(2) + '°' : fakeLl
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
        ss: ss ? ss.toFixed(2) + '°' : '区域未识别',
        pt: pt ? pt.toFixed(2) + '°' : '区域未识别',
        pi: pi ? pi.toFixed(2) + '°' : '区域未识别'
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
    width: 20vw;
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
    padding: 0.8rem 0;
  }
  .content-group-title {
    font-weight: bold;
    align-self: center;
    margin-bottom: 0.6rem;
  }

  .standard-link{
    align-self: flex-end;
    margin-bottom: 1rem;
  }
   
  .result-table, .result-table>tr>th, .result-table>tr>td { 
    border:1px solid #8a8a8a; 
  }
  .result-table { 
    width: 90%; 
    line-height: 1.6rem; 
    text-align: center; 
    border-collapse: collapse; 
    align-self: center;
  } 
</style>