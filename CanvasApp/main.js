const { app, BrowserWindow, ipcMain, Menu, Tray, screen } = require('electron');
const { execFile } = require('child_process');
const path = require('path');

let mainWindow;
let tray = null;
let pythonChild = null;

app.whenReady().then(() => {
  const { width, height } = screen.getPrimaryDisplay().bounds;
  mainWindow = new BrowserWindow({
    x: 0,
    y: 1,
    width: width,      // 覆蓋螢幕寬度
    height: height,    // 覆蓋螢幕高度
    frame: false,
    transparent: true, // 視窗透明
    alwaysOnTop: true, // 置頂
    resizable: false, // 不可調整視窗大小
    webPreferences: {
      nodeIntegration: true, // 啟用 Node.js
      contextIsolation: false,
    },
  });

  const webContents = mainWindow.webContents;

  // 啟動 Python 程序
  const pythonPath = path.join(__dirname, 'python', 'KMeans_LiveTest.py');
  console.log('執行 Python 檔案:', pythonPath);

  pythonChild = execFile('python', ['-u', pythonPath]);

  // 處理 Python 的輸出
  pythonChild.stdout.on('data', (data) => {
    console.log('Python output:', data);
    if (mainWindow.isVisible()) {
      if (data.trim() === '1') {
        webContents.executeJavaScript("setActiveTool('eraser-tool')");
      } else if (data.trim() === '0') {
        webContents.executeJavaScript("setActiveTool('pen-tool')");
      }
    }
  });

  mainWindow.loadFile('index.html');
  mainWindow.setAlwaysOnTop(true, 'screen-saver');

  // 處理忽略滑鼠事件
  ipcMain.on('set-ignore-mouse-events', (event, ignore, boundingBox) => {
    if (ignore) {
      mainWindow.setIgnoreMouseEvents(ignore, { forward: true, ...boundingBox });
    } else {
      mainWindow.setIgnoreMouseEvents(ignore);
    }
  });

  // 視窗隱藏時停止 Python 輸入並切換回滑鼠功能
  mainWindow.on('hide', () => {
    console.log('視窗已隱藏：切換回滑鼠工具');
    webContents.executeJavaScript("setActiveTool('mouse-tool')");
  });

  // 視窗顯示時重新啟用 Python 輸入
  mainWindow.on('show', () => {
    console.log('視窗已顯示：準備接收 Python 輸入');
  });

  // 創建工作列圖示
  createTray();
});

function createTray() {
  const trayIcon = path.join(__dirname, 'assets/icon', 'icon.ico'); // 替換為你的圖示路徑
  tray = new Tray(trayIcon);

  const contextMenu = Menu.buildFromTemplate([
    {
      label: '退出',
      click: () => {
        app.quit();
      },
    },
  ]);
  tray.setToolTip('隱藏視窗');
  tray.setContextMenu(contextMenu);

  // 點擊工作列圖示，切換主窗口顯示狀態
  tray.on('click', () => {
    if (mainWindow.isVisible()) {
      mainWindow.hide();
      tray.setToolTip('顯示視窗');
    } else {
      mainWindow.show();
      tray.setToolTip('隱藏視窗');
    }
  });
}

app.on('window-all-closed', (event) => {
  if (process.platform !== 'darwin') {
    event.preventDefault();
  }
});

app.on('before-quit', () => {
  app.isQuiting = true;
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createMainWindow();
  }
});