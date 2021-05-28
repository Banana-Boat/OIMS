const fs = require('fs')

const state = {
  // 正面图的相关变量
  params1: {
    'dirPath': '', // 文件夹路径
    'compressDirPath': './tmp/img/front_compress/', // 图片压缩后的保存路径
    'preprocessDirPath': './tmp/img/front_preprocess/', // 图片预处理后的保存路径
    'fileList': {}, // 文件列表（用于维护文件列表栏）
    'resList': {}, // 量测结果列表（用于维护图片的量测结果，包含每一项）
    'curFilename': null, // 当前打开的文件文件名
    'canvasData': null, // 画布
    'resXmlPath': './tmp/xml/front_result.xml',
  },
  // 侧面图的相关变量
  params2: {
    'dirPath': '',
    'compressDirPath': './tmp/img/side_compress/',
    'preprocessDirPath': './tmp/img/side_preprocess/',
    'fileList': {},
    'resList': {},
    'curFilename': null,
    'canvasData': null,
    'resXmlPath': './tmp/xml/side_result.xml'
  },
  selectedImgBox: 1, // 当前选中的图片框
  isMeasuring: false, // 是否在量测中
  curEntireRes: null, // 当前文件整体量测结果（用于打印输出）
  isShowResultBox: false, //是否显示结果面板
  preprocessScale: 5 // 预处理图片缩放倍率
}

const mutations = {
  // 清空state
  clear(state){
    for(let i in state){
      delete state[i]
    }
  },
  // 修改图片目录的路径。flag=1：正面图，flag=2：侧面图
  ChangeDirPath (state, payload) {
    var params = payload.flag === 1 ? state.params1 : state.params2
    params.dirPath = payload.path
  },
  // 修改整个文件列表
  ChangeFileList (state, payload) {
    var params = payload.flag === 1 ? state.params1 : state.params2
    params.fileList = payload.fileList
  },
  // 修改整个量测结果列表
  ChangeResList (state, payload) {
    var params = payload.flag === 1 ? state.params1 : state.params2
    params.resList = payload.resList
  },
  // 修改当前打开的图片
  ChangeCurFilename (state, payload) {
    var params = payload.flag === 1 ? state.params1 : state.params2
    params.curFilename = payload.curFilename
  },
  // 修改画布内容（base64）
  ChangeCanvasData (state, payload) {
    var params = payload.flag === 1 ? state.params1 : state.params2
    params.canvasData = payload.canvasData
  },
  // 切换选中的图片框
  ChangeSelectedImgBox (state, payload) {
    if (state.selectedImgBox !== payload.flag) {
      state.selectedImgBox = payload.flag
    }
  },
  // 修改当前正侧图的综合健康数据
  ChangeCurEntireRes (state, payload) {
    state.curEntireRes = payload.curEntireRes
  },
  // 改变量测状态
  ChangeMeasureState (state, payload) {
    state.isMeasuring = payload.isMeasuring
  },
  // 改变显示结果面板的状态
  ChangeIsShowResultBoxState (state, payload) {
    state.isShowResultBox = payload.isShowResultBox
  }
}

const actions = {
  /* 功能：修改curFilename为列表第一项 */
  ChangeCurFilenameToTheFirst (context, payload) {
    let params = payload.flag === 1 ? context.state.params1 : context.state.params2
    if (Object.keys(params.fileList).length !== 0) {
      context.commit('ChangeCurFilename', {
        flag: payload.flag,
        curFilename: Object.keys(params.fileList)[0]
      })
    } else {
      context.commit('ChangeCurFilename', {
        flag: payload.flag,
        curFilename: null
      })
    }
  },
  /* 功能：读取文件目录，修改文件列表（读文件为异步操作）。flag=1：正面图，flag=2：侧面图 */ 
  LoadDir (context, payload) {
    return new Promise((resolve, reject) => {
      fs.readdir(payload.path, (err, files) => {
        if (err)
          reject()
        
        let tempFileList = {}
        let fileType = ['jpg', 'jpeg']
        let tempResList = {}
        files.forEach((file) => {
          if (fileType.includes(file.split('.').pop().toLowerCase())) {
            tempFileList[file] = {
              'path': payload.path + '\\' + file,
              'isMeasured': false
            }
            tempResList[file] = {
              'path': payload.path + '\\' + file,
              'isParsed': false,
              'isScaled': false, // 解析结果是否被缩放过
              'originParseRes': {}, // 原图尺寸对应的解析结果（点集）
              'displayParseRes': {} // 当前显示尺寸对应的解析结果（点集）
            }
          }
        })
        context.commit('ChangeFileList', {
          flag: payload.flag,
          fileList: tempFileList
        })
        context.commit('ChangeResList', {
          flag: payload.flag,
          resList: tempResList
        })
        
        resolve()
      })
    })
    
  }
}

export default {
  state,
  mutations,
  actions
}
