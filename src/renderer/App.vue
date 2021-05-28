<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>
import { ipcRenderer } from "electron"

export default {
  name: 'oims',
  created() {
    ipcRenderer.send("close-loading-window")
  }
}
</script>

<style>
  body{
    margin: 0;
    height: 100vh;
    font-family: "Microsoft YaHei";
  }
  #app{
    height: 100%;
  }

  button{
    font-family: "Microsoft YaHei";
  }
  
  .el-card__header {
    padding: 15px 20px !important;
  }
  .el-card__body{
    padding: 0.8rem !important;
  }
  
  .el-divider{
    width: auto !important;
    margin: 8px 16px !important;
  }

  .cell{
    text-overflow: unset !important;
  }

  .el-dialog__body{
    padding: 15px 20px !important;
  }
  
</style>
