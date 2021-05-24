'use strict'

import { app, BrowserWindow, Menu } from 'electron'
/**
 * Set `__static` path to static files in production
 * https://simulatedgreg.gitbooks.io/electron-vue/content/en/using-static-assets.html
 */
if (process.env.NODE_ENV !== 'development') {
  global.__static = require('path').join(__dirname, '/static').replace(/\\/g, '\\\\')
}

let mainWindow = null

const winURL = process.env.NODE_ENV === 'development'
  ? `http://localhost:9080`
  : `file://${__dirname}/index.html`

function createWindow () {
  mainWindow = new BrowserWindow({
    useContentSize: true,
    show: false,
    resizable: false,
    webPreferences: {
      webSecurity: false
    },
    icon: '../../static/ai_bone_ruler.ico'
  })
  // 打开调试窗口！！！
  //mainWindow.webContents.openDevTools()

  Menu.setApplicationMenu(null)
  mainWindow.maximize()
  mainWindow.show()

  mainWindow.loadURL(winURL)

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

app.on('ready', () => {
  createWindow()
  // 创建临时文件夹
  var fs = require('fs')
  try {
    fs.mkdirSync('./tmp', (err) => { throw err })
    fs.mkdirSync('./tmp/img', (err) => { throw err })
    fs.mkdirSync('./tmp/xml', (err) => { throw err })
    fs.mkdirSync('./tmp/img/front_compress', (err) => { throw err })
    fs.mkdirSync('./tmp/img/side_compress', (err) => { throw err })
    fs.mkdirSync('./tmp/img/front_preprocess', (err) => { throw err })
    fs.mkdirSync('./tmp/img/side_preprocess', (err) => { throw err })
  } catch (error) {
    console.log('临时文件夹创建失败')
  }
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow()
  }
})

/**
 * Auto Updater
 *
 * Uncomment the following code below and install `electron-updater` to
 * support auto updating. Code Signing with a valid certificate is required.
 * https://simulatedgreg.gitbooks.io/electron-vue/content/en/using-electron-builder.html#auto-updating
 */

/*
import { autoUpdater } from 'electron-updater'

autoUpdater.on('update-downloaded', () => {
  autoUpdater.quitAndInstall()
})

app.on('ready', () => {
  if (process.env.NODE_ENV === 'production') autoUpdater.checkForUpdates()
})
 */
