<template>
  <div v-draggable class="result-box" v-if="isShowResultBox">
    <div class="header-box">
      <span class="header-text">量测结果</span>
      <i class="fa fa-close close-icon" @click="Close"></i>
    </div>
    <div class="content-box" v-if="isParsed2">
      <div>ss: {{result.ss}}</div>
      <div>pt: {{result.pt}}</div>
      <div>pi: {{result.pi}}</div>
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
      result: {
        'ss': '',
        'pt': '',
        'pi': ''
      }
    }
  },
  computed: {
    isParsed2 () {
      let curFilename = this.$store.state.File.params2.curFilename
      let isParsed = null
      if (this.$store.state.File.params2.resList[curFilename]) {
        isParsed = this.$store.state.File.params2.resList[curFilename].isParsed
      }
      if (isParsed) {
        let parseRes = this.$store.state.File.params2.resList[curFilename].parseRes
        let result = this.CalResult(parseRes)
        this.result = result
        this.$store.commit('ChangeCurEntireRes', {
          curEntireRes: result
        })
        return true
      } else {
        this.result = {
          'ss': '',
          'pt': '',
          'pi': ''
        }
        // 待改整合（正侧）
        this.$store.commit('ChangeCurEntireRes', {
          curEntireRes: null
        })
        return false
      }
    }
  },
  watch: {
  },
  methods: {
    CalResult (parseRes) {
      let ss = null
      let pt = null
      let pi = null
      if(parseRes.p1 && parseRes.p0 && parseRes.p5 && parseRes.p2){
        ss = Math.atan((parseRes.p1[1] - parseRes.p0[1]) / (parseRes.p1[0] - parseRes.p0[0])) *
                  180 / Math.PI
        pt = 90.0 - (Math.atan((parseRes.p2[1] - parseRes.p5[1]) / (parseRes.p2[0] - parseRes.p5[0])) *
                  180 / Math.PI)
        pi = ss + pt
      }
      return {
        'ss': ss ? ss.toFixed(2) : '(识别区域缺失，无法计算)',
        'pt': pt ? pt.toFixed(2) : '(识别区域缺失，无法计算)',
        'pi': pi ? pi.toFixed(2) : '(识别区域缺失，无法计算)'
      }
    },
    Close () {
      this.$emit('CloseResultBox')
    }
  }
}
</script>

<style lang="less">
  // 量测结果栏
  .result-box{
    z-index: 100;
    width: 20vw;
    height: 50vh;
    cursor: move;

    background-color: #FFF;
    border: 1px solid #EBEEF5;
    box-shadow: 6px 6px 20px 0px #dddddd;
    border-radius: 5px;
  }
  .result-box:hover{
    transition-timing-function: cubic-bezier(0.175, 0.885, 0.32, 1.275);
    transition-duration: 250ms;
    transform: scale(1.04);
    box-shadow: 10px 10px 30px 0px #cfcfcf;
    border-radius: 10px;
  }
  .header-box{
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    padding: 15px 20px ;
    border-bottom: 1px solid #EBEEF5;
  }
  .header-text{
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
    padding: 20px;
  }
</style>