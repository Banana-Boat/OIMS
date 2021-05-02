const fs = require('fs')

const state = {
  // 正面图的相关变量
  params1: {
    'dirPath': '', // 文件夹路径
    'compressDirPath': './tmp/img/front_compress/', // 对比度调整后的保存路径
    'fileList': {}, // 文件列表（用于维护文件列表栏）
    'resList': {}, // 量测结果列表（用于维护图片的量测结果，包含每一项）
    'curFilename': '', // 当前打开的文件文件名
    'canvasData': null, // 画布
    'testx':'',
    'testy':'',
    'testList':{}  //绘制直线参数
  },
  // 侧面图的相关变量
  params2: {
    'dirPath': '',
    'compressDirPath': './tmp/img/side_compress/',
    'fileList': {},
    'resList': {},
    'curFilename': '',
    'canvasData': null,
    'testList':{}
  },
  selectedImgBox: 1, // 当前选中的图片框
  isMeasuring: false, // 是否在量测中
  curEntireRes: null // 当前文件整体量测结果（正+侧）
}

const mutations = {
  ChangTest(state,payload){
    //alert(payload.testList[payload.curFilename].x1)
    var params = payload.flag == 1? state.params1 : state.params2
    params.testx=payload.testx
    params.testy=payload.testy
    params.testList=payload.testList
    //alert(payload.testList[payload.curFilename].x1)
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
  // 修改当前正侧图的综合健康数据
  ChangeCurEntireRes (state, payload) {
    state.curEntireRes = payload.curEntireRes
  },
  // 切换选中的图片框
  ChangeSelectedImgBox (state, payload) {
    if (state.selectedImgBox !== payload.flag) {
      state.selectedImgBox = payload.flag
    }
  },
  // 改变量测状态
  ChangeMeasureState (state, payload) {
    state.isMeasuring = payload.isMeasuring
  }
}

const actions = {
  // 公用操作。读取文件目录，修改文件列表（读文件为异步操作）。flag=1：正面图，flag=2：侧面图
  LoadDir (context, payload) {
    fs.readdir(payload.path, (err, files) => {
      if (err) {
        return console.error(err)
      }
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
            'isMeasured': false,
            'isParsed': false,
            'measureRes': {}, // 量测结果
            'parseRes': {} // 解析结果（点集、参数）
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
      if (Object.keys(tempFileList).length !== 0) {
        context.commit('ChangeCurFilename', {
          flag: payload.flag,
          curFilename: Object.keys(tempFileList)[0]
        })
      } else {
        context.commit('ChangeCurFilename', {
          flag: payload.flag,
          curFilename: ''
        })
      }
    })
  }
}

export default {
  state,
  mutations,
  actions
}
