# OIMS

> 一款基于Electron-vue以及ElementUI开发的医学骨科影像识别系统

#### 项目配置步骤

``` bash
# install dependencies
npm install

# serve with hot reload at localhost:9080
npm run dev

# build electron application for production
npm run build

# run unit & end-to-end tests
npm test


# lint all JS/Vue component files in `src/`
npm run lint

```

---

This project was generated with [electron-vue](https://github.com/SimulatedGREG/electron-vue)@[45a3e22](https://github.com/SimulatedGREG/electron-vue/tree/45a3e224e7bb8fc71909021ccfdcfec0f461f634) using [vue-cli](https://github.com/vuejs/vue-cli). Documentation about the original structure can be found [here](https://simulatedgreg.gitbooks.io/electron-vue/content/index.html).
"# OIMS" 
"# OIMS" 



#### 完善打印功能须知

npm install jspdf

由于使用到new jsPDF()，'j'小写，与下载库中存在冲突，所以需要在/node_modules/eslint-config-standard中

修改：

```javascript
"new-cap": ["error", { "newIsCap": true, "capIsNew": false }]
```

为：

```javascript
"new-cap": ["error", { "newIsCap": false, "capIsNew": false }],
```