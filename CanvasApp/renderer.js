const canvas = document.getElementById('drawing-canvas');
const ctx = canvas.getContext('2d');
const { ipcRenderer } = require('electron');

let drawing = false;
let pc = '#000000';
let sc = '#000000';
let ps = 5;
let es = 5;
let ss = 5;
let mouseEventsIgnored = false;
let selectedShape = 'line';
let undoStack = [];
let redoStack = [];

toggle_mouse_event();
setActiveTool('mouse-tool');
updateShapeTool();
window.addEventListener('resize', resizeCanvas);
resizeCanvas();
const tools = [
    { toolId: 'pen-tool', settingsId: 'pen-settings', arrowId: 'pen-settings-toggle' },
    { toolId: 'shape-tool', settingsId: 'shape-settings', arrowId: 'shape-settings-toggle' },
    { toolId: 'eraser-tool', settingsId: 'eraser-settings', arrowId: 'eraser-settings-toggle' },
];
tools.forEach(tool => createToolHandler(tool.toolId, tool.settingsId, tool.arrowId));

function resizeCanvas() { // 調整畫布大小
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;
}

function showSettingsArrow(toolId) { // 顯示設定箭頭
    if (toolId === 'pen-tool') {
        document.getElementById('pen-settings-toggle').style.display = 'inline-block';
        document.getElementById('pen-color').setAttribute('data-tool', 'pen-tool');
        document.getElementById('pen-size').setAttribute('data-tool', 'pen-tool');
    } else if (toolId === 'shape-tool') {
        document.getElementById('shape-settings-toggle').style.display = 'inline-block';
        document.getElementById('shape-color').setAttribute('data-tool', 'shape-tool');
        document.getElementById('shape-size').setAttribute('data-tool', 'shape-tool');
    } else if (toolId === 'eraser-tool') {
        document.getElementById('eraser-settings-toggle').style.display = 'inline-block';
        document.getElementById('eraser-size').setAttribute('data-tool', 'eraser-tool');
    }
}

function setActiveTool(toolId) { // 設定工具
    document.querySelectorAll('.tool-button').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tools-settings').forEach(panel => panel.classList.remove('active'));
    document.querySelectorAll('.arrow-button').forEach(arrow => arrow.style.display = 'none');
    document.querySelectorAll('.arrow-button').forEach(arrow => arrow.innerHTML = '<i class="fas fa-chevron-right"></i>');

    document.getElementById(toolId).classList.add('active');
    showSettingsArrow(toolId);

    mouseEventsIgnored = toolId !== 'mouse-tool';
    toggle_mouse_event();

    switch (toolId) {
        case 'pen-tool':
        case 'shape-tool':
            canvas.style.cursor = 'url("./assets/cursors/pen-cursor.png")0 20, auto';
            break;
        case 'eraser-tool':
            canvas.style.cursor = 'url("./assets/cursors/eraser-cursor.png")10 10, auto';
            break;
        default:
            canvas.style.cursor = 'default';
    }
}

function updateArrowDirection(arrowButton, settingsPanel) { // 更新箭頭方向
    if (toolbar.classList.contains('toolbar-left')) {
        if (settingsPanel.classList.contains('active')) {
            arrowButton.innerHTML = '<i class="fas fa-chevron-left"></i>';
        } else {
            arrowButton.innerHTML = '<i class="fas fa-chevron-right"></i>';
        }
    } else if (toolbar.classList.contains('toolbar-right')) {
        if (settingsPanel.classList.contains('active')) {
            arrowButton.innerHTML = '<i class="fas fa-chevron-right"></i>';
        } else {
            arrowButton.innerHTML = '<i class="fas fa-chevron-left"></i>';
        }
    } else if (toolbar.classList.contains('toolbar-center')) {
        if (settingsPanel.classList.contains('active')) {
            arrowButton.innerHTML = '<i class="fas fa-chevron-up"></i>';
        } else {
            arrowButton.innerHTML = '<i class="fas fa-chevron-down"></i>';
        }
    }
}

function createToolHandler(toolId, settingsId, arrowId) { // 創建工具處理程序
    const toolButton = document.getElementById(toolId); 
    const settingsPanel = document.getElementById(settingsId);
    const arrowButton = document.getElementById(arrowId);

    arrowButton.setAttribute('data-sp', settingsId);

    toolButton.addEventListener('click', () => {
        setActiveTool(toolId);
        arrowButton.style.display = 'inline-block';
        updateArrowDirection(arrowButton, settingsPanel);
    });

    arrowButton.addEventListener('click', () => {
        settingsPanel.classList.toggle('active');
        arrowButton.classList.toggle('active');
        updateArrowDirection(arrowButton, settingsPanel);
    });
}

function updateShapeTool() { // 更新形狀工具
    const shapeToolButton = document.getElementById('shape-tool');
    const shapeSettings = document.getElementById('shape-settings');
    shapeSettings.innerHTML = '';

    const shapes = ['line', 'rect', 'circle'];
    const icons = {
        'line': '<i class="fas fa-slash"></i>',
        'rect': '<i class="far fa-square"></i>',
        'circle': '<i class="far fa-circle"></i>'
    };

    shapeToolButton.innerHTML = icons[selectedShape];

    shapes.forEach(shape => {
        if (shape !== selectedShape) {
            const button = document.createElement('button');
            button.className = 'tool-button';
            button.innerHTML = icons[shape];
            button.addEventListener('click', () => {
                selectedShape = shape;
                updateShapeTool();
            });
            shapeSettings.appendChild(button);
        }
    });

    const colorLabel = document.createElement('label');
    colorLabel.innerHTML = 'Color: <input type="color" id="shape-color" value="' + sc + '">';
    shapeSettings.appendChild(colorLabel);

    const sizeLabel = document.createElement('label');
    sizeLabel.innerHTML = 'Size: <input type="range" id="shape-size" min="1" max="20" value="' + ss + '">';
    shapeSettings.appendChild(sizeLabel);

    document.getElementById('shape-color').addEventListener('change', (e) => {
        sc = e.target.value;
    });

    document.getElementById('shape-size').addEventListener('input', (e) => {
        ss = e.target.value;
    });
}

document.getElementById('mouse-tool').addEventListener('click', () => {
    setActiveTool('mouse-tool');
});

document.getElementById('toolbar-close').addEventListener('click', () => {
    toolbar.classList.toggle('active');
    document.querySelectorAll('.arrow-button').forEach(arrow => arrow.style.display = 'none');
    toggle_toolbar();
});

document.getElementById('toolbar-open').addEventListener('click', () => {
    toolbar.classList.toggle('active');
    showSettingsArrow(document.querySelector('.tool-button.active').id);
    toggle_toolbar();
});

function toggle_toolbar() { // 切換工具欄
    if (toolbar.classList.contains('active')) {
        (toolbar.classList.contains('toolbar-left')) ? toolbar.style.left = '-55px' : toolbar.style.left = '100%';
        document.getElementById('toolbar-open').style.display = 'block';
    } else {
        (toolbar.classList.contains('toolbar-left')) ? toolbar.style.left = '0' : toolbar.style.left = 'calc(100% - 55px)';
        document.getElementById('toolbar-open').style.display = 'none';
    }
}

function toggle_mouse_event() { // 切換滑鼠事件
    const rect = canvas.getBoundingClientRect();
    if (!mouseEventsIgnored) {
        ipcRenderer.send('set-ignore-mouse-events', true, {
            forward: true,
            region: {
                x: rect.x,
                y: rect.y,
                width: rect.width,
                height: rect.height
            }
        });
        const normalArea = document.getElementById('toolbar');
        normalArea.addEventListener('mouseenter', () => {
            ipcRenderer.send('set-ignore-mouse-events', false);
        });
        normalArea.addEventListener('mousemove', () => {
            ipcRenderer.send('set-ignore-mouse-events', false);
        });
        normalArea.addEventListener('mouseleave', () => {
            ipcRenderer.send('set-ignore-mouse-events', true, {
                forward: true,
                region: {
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height
                }
            });
        });
    } else {
        const normalArea = document.getElementById('toolbar');
        normalArea.addEventListener('mouseenter', () => {
            ipcRenderer.send('set-ignore-mouse-events', false);
        });
        normalArea.addEventListener('mouseleave', () => {
            ipcRenderer.send('set-ignore-mouse-events', false);
        });
    }
}

let startX = 0;
let startY = 0;

canvas.addEventListener('mousedown', (e) => { // 畫布滑鼠按下事件
    const currentTool = document.querySelector('.tool-button.active').id;

    if (currentTool !== 'mouse-tool') {
        drawing = true;
        startX = e.offsetX;
        startY = e.offsetY;
        if (currentTool === 'pen-tool') {
            ctx.beginPath();
            ctx.moveTo(startX, startY);
        } else if (currentTool === 'shape-tool') {
            savedCanvasImage = ctx.getImageData(0, 0, canvas.width, canvas.height);
        } else if (currentTool === 'eraser-tool') {
            ctx.clearRect(startX - es, startY - es, es, es);
        }
    }
});

canvas.addEventListener('mousemove', (e) => { // 畫布滑鼠移動事件
    const currentTool = document.querySelector('.tool-button.active').id;

    if (drawing) {
        const mouseX = e.offsetX;
        const mouseY = e.offsetY;
        switch (currentTool) {
            case 'pen-tool':
                ctx.lineTo(mouseX, mouseY);
                ctx.strokeStyle = pc;
                ctx.lineWidth = ps;
                ctx.stroke();
                break;
            case 'shape-tool':
                ctx.putImageData(savedCanvasImage, 0, 0);
                ctx.strokeStyle = sc;
                ctx.lineWidth = ss;
                if (selectedShape === 'line') {
                    ctx.beginPath();
                    ctx.moveTo(startX, startY);
                    ctx.lineTo(mouseX, mouseY);
                    ctx.stroke();
                } else if (selectedShape === 'rect') {
                    ctx.strokeRect(startX, startY, mouseX - startX, mouseY - startY);
                } else if (selectedShape === 'circle') {
                    const radius = Math.hypot(mouseX - startX, mouseY - startY);
                    ctx.beginPath();
                    ctx.arc(startX, startY, radius, 0, Math.PI * 2);
                    ctx.stroke();
                }
                break;
            case 'eraser-tool':
                ctx.clearRect(mouseX - es, mouseY - es, es * 2, es * 2);
                break;
        }
    }
});

canvas.addEventListener('mouseup', () => { // 畫布滑鼠放開事件
    const currentTool = document.querySelector('.tool-button.active').id;

    if (drawing) {
        drawing = false;
        if (currentTool === 'pen-tool') {
            ctx.closePath();
            saveCanvasState();
        }
        if (currentTool === 'shape-tool') {
            saveCanvasState();
        }
        if (currentTool === 'eraser-tool') {
            saveCanvasState();
        }
    }
});

function saveCanvasState() { // 儲存畫布狀態
    const canvasData = canvas.toDataURL();
    undoStack.push(canvasData);
    redoStack = [];
}

const toolbar = document.getElementById('toolbar');
const toolbarDivider = document.getElementById('toolbar-divider');

let isDragging = false;
let dragOffsetX = 0;
let dragOffsetY = 0;

toolbarDivider.addEventListener('mousedown', (e) => { // 工具欄分隔線滑鼠按下事件
    isDragging = true;
    dragOffsetX = e.clientX - toolbar.offsetLeft;
    dragOffsetY = e.clientY - toolbar.offsetTop;
    document.body.style.userSelect = 'none';
});

document.addEventListener('mousemove', (e) => { // 滑鼠移動事件
    if (isDragging) {
        toolbar.style.left = (e.clientX - dragOffsetX) + 'px';
        toolbar.style.top = (e.clientY - dragOffsetY) + 'px';
        arrowpos();
    }
});

document.addEventListener('mouseup', () => { // 滑鼠放開事件
    if (isDragging) {
        isDragging = false;
        document.body.style.userSelect = '';

        const windowWidth = window.innerWidth;
        const toolbarRect = toolbar.getBoundingClientRect();
        if (toolbarRect.left + toolbarRect.width / 2 < windowWidth / 2) {
            toolbar.style.left = '0px';
            changeToolbarPosition('left');
        } else {
            toolbar.style.left = (windowWidth - toolbarRect.width) + 'px';
            changeToolbarPosition('right');
        }
    }
});

function arrowpos() { //收合視窗箭頭位置
    const windowWidth = window.innerWidth;
    const arrowop = document.getElementById('toolbar-open');
    const arrowcl = document.getElementById('toolbar-close');
    console.log(toolbar.style.left, windowWidth);
    console.log(parseInt(toolbar.style.left, 10), windowWidth);
    if (parseInt(toolbar.style.left, 10) < windowWidth / 2 + 55) {
        arrowop.innerHTML = '<i class="fas fa-chevron-right"></i>';
        arrowcl.innerHTML = '<i class="fas fa-chevron-left"></i>';
    } else {
        arrowop.innerHTML = '<i class="fas fa-chevron-left"></i>';
        arrowcl.innerHTML = '<i class="fas fa-chevron-right"></i>';
    }
}

//=======================================================
document.getElementById('pen-color').addEventListener('change', (e) => {pc = e.target.value;});

document.getElementById('pen-size').addEventListener('input', (e) => {ps = e.target.value;});

document.getElementById('shape-color').addEventListener('change', (e) => {sc = e.target.value;});

document.getElementById('shape-size').addEventListener('input', (e) => {ss = e.target.value;});

document.getElementById('eraser-size').addEventListener('input', (e) => {es = e.target.value * 3;});

document.getElementById('pen-type').addEventListener('change', (e) => {
    const penType = e.target.value;
    if (penType === 'marker') {
        ctx.globalCompositeOperation = 'source-over';
    } else {
        ctx.globalCompositeOperation = 'source-over';
    }
});

//=======================================================
function changeToolbarPosition(position) { // 改變工具欄位置
    const toolbar = document.getElementById('toolbar');
    toolbar.classList.remove('toolbar-left', 'toolbar-right', 'toolbar-center');

    toolbar.classList.add(`toolbar-${position}`);

    const arrowButtons = document.querySelectorAll('.arrow-button');
    arrowButtons.forEach(arrowButton => {
        const settingsPanelId = arrowButton.getAttribute('data-sp');
        const settingsPanel = document.getElementById(settingsPanelId);
        updateArrowDirection(arrowButton, settingsPanel);
    });
}

document.getElementById('left-position').addEventListener('click', () => changeToolbarPosition('left'));
document.getElementById('right-position').addEventListener('click', () => changeToolbarPosition('right'));
document.getElementById('center-position').addEventListener('click', () => changeToolbarPosition('center'));