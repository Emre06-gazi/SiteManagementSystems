var canvas = document.getElementsByClassName("myCanvas")[0];
var img = document.querySelector("img");
var canvasWidth = window.innerWidth;
var canvasHeight = window.innerHeight;
canvas.width = window.innerWidth * 1.6;
canvas.height = window.innerHeight * 1.6;
var ctx = canvas.getContext("2d");

// Canvas üzerindeki ölçek değişkenleri
var scale = 2;

// Slayt değeri değiştiğinde çalışacak işlev
function sliderChanged() {
    var slider = document.getElementById("sliderButton");
    var value = slider.value;

    var newScale = 2 * (100 - value) / 100;

    canvas.width = canvasWidth * newScale;
    canvas.height = canvasHeight * newScale;

    scale = newScale;

    canvasObj.draw();
}

// Slayt değeri değiştiğindeki olayı dinle
var slider = document.getElementById("sliderButton");
slider.addEventListener("input", sliderChanged);

// Sayfayi Yenileme Butonu
var refreshButton = document.getElementById("refreshButton");

refreshButton.addEventListener("click", function () {
    location.reload(); // Sayfayı yenile
});

// Canvas üzerinde fare olaylarını dinle
canvas.addEventListener("mousedown", handleMouseDown);
canvas.addEventListener("mousemove", handleMouseMove);
canvas.addEventListener("mouseup", handleMouseUp);
canvas.addEventListener("mouseleave", handleMouseLeave);

var isDragging = false;
var dragStartX = 0;
var dragStartY = 0;

// Fare tıklama olayını işle
function handleMouseDown(event) {
    var rect = canvas.getBoundingClientRect(); // Canvas'in boyutlarını al
    var mouseX = event.clientX - rect.left; // Canvas içinde fare konumunu hesapla
    var mouseY = event.clientY - rect.top; // Canvas içinde fare konumunu hesapla

    isDragging = true;
    dragStartX = mouseX;
    dragStartY = mouseY;
}

// Fare hareketi olayını işle
function handleMouseMove(event) {
    if (isDragging) {
        var rect = canvas.getBoundingClientRect(); // Canvas'in boyutlarını al
        var dragEndX = event.clientX - rect.left; // Canvas içinde fare konumunu hesapla
        var dragEndY = event.clientY - rect.top; // Canvas içinde fare konumunu hesapla

        var deltaX = dragEndX - dragStartX;
        var deltaY = dragEndY - dragStartY;

        dragStartX = dragEndX;
        dragStartY = dragEndY;

        moveElements(deltaX, deltaY);
    }
}

// Fare bırakma olayını işle
function handleMouseUp() {
    isDragging = false;
}

// Fare çıkışı olayını işle
function handleMouseLeave() {
    isDragging = false;
}

// Elemanları hareket ettir
function moveElements(deltaX, deltaY) {
    for (var i = 0; i < builds.length; i++) {
        var bina = builds[i];
        bina.x += deltaX / scale;
        bina.y += deltaY / scale;
    }

    for (const [key, device] of Object.entries(devices)) {
        device.x += deltaX / scale;
        device.y += deltaY / scale;
        for (const [key2, slave] of Object.entries(device.slaves)) {
            slave.x += deltaX / scale;
            slave.y += deltaY / scale;
        }
    }

    canvasObj.background.x += deltaX / scale;
    canvasObj.background.y += deltaY / scale;

    canvasObj.draw();
}

class Device {
    constructor(x, y, slaves) {
        this.x = x;
        this.y = y;
        this.slaves = slaves;
        this.value = false;
    }

    draw() {
        ctx.save();

        if (this.value) {
            ctx.font = "20px Arial";
            ctx.fillStyle = "green";
            ctx.shadowBlur = 10;
            ctx.shadowColor = "green";
        } else {
            ctx.font = "20px Arial";
            ctx.fillStyle = "red";
            ctx.textAlign = "center";
        }

        for (const slave of this.slaves) {
            slave.color = this.value ? "green" : "red"; // slave rengini ayarla
            slave.draw();
        }

        var width = 50;
        var height = 50;
        ctx.drawImage(img, this.x, this.y, width, height);

        ctx.restore();
    }
}

class Slave {
    constructor(x, y, width, height, color) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.color = color;
    }

    draw() {
        ctx.beginPath();
        ctx.moveTo(this.x, this.y);
        ctx.rect(this.x, this.y, this.width, this.height);
        ctx.fillStyle = this.color;
        ctx.closePath();
        ctx.fill();
    }
}

class Bina {
    constructor(offset, innerColor, outerColor, label) {
        this.offset = offset;
        this.innerColor = innerColor;
        this.outerColor = outerColor;
        this.label = label;
        this.builds = [];
    }
}

class Canvas {
    constructor() {
        this.builds = [];
        this.devices = {};
        this.background = {
            x: 0,
            y: 0,
            width: 1550,
            height: 850,
            color: "lightgray",
        };
    }

    draw() {
        // Önceki konumun üzerini temizle
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Yeni arka planı çiz
        ctx.fillStyle = this.background.color;
        ctx.fillRect(
            this.background.x,
            this.background.y,
            this.background.width,
            this.background.height);

        // Diğer elemanları çiz
        for (let i = 0; i < this.builds.length; i++) {
            this.builds[i].draw();
        }

        // Devicesı çiz
        for (const [key, device] of Object.entries(devices)) {
            device.draw();
        }
    }
}

class BaseDraw {
    constructor(x, y, w, h, obj, obj2) {
        this.x = x;
        this.y = y;
        this.w = w;
        this.h = h;
        this.obj = obj;
    }

    draw() {
        ctx.fillStyle = this.obj.innerColor;
        ctx.fillRect(this.x, this.y, this.w, this.h);

        ctx.strokeStyle = this.obj.outerColor;
        ctx.lineWidth = this.obj.offset;
        ctx.strokeRect(this.x, this.y, this.w, this.h);

        ctx.fillStyle = "black";
        ctx.font = "20px Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(
            this.obj.label,
            this.x + this.w / 2,
            this.y + this.h / 2);
    }
}

class Build extends BaseDraw {
    constructor(x, y, w, h, obj) {
        super(x, y, w, h, obj);
    }
}




/////////////////////////////////////////////////////////////////////////////////////////////





function sidebarCloseFunc() {
    let canvassidebar = document.getElementById("canvasSidebar");
    let canvasTitle = document.getElementById("canvasTitle");
    let canvasContent = document.getElementById("canvasList")
        canvassidebar.classList.toggle("canvas-sidebar-open");
    canvasTitle.classList.toggle("canvas-sidebar-close");
    canvasContent.classList.toggle("canvas-sidebar-close");
    if (canvasMenuIcon.innerText === 'menu') {
        canvasMenuIcon.innerText = 'close';
    } else {
        canvasMenuIcon.innerText = 'menu';
    }
}

function loadDarkModeFromLocalStorage() {
    const storedDarkMode = localStorage.getItem('darkMode');

    if (storedDarkMode && storedDarkMode === 'true') {
        document.body.classList.add("dark-theme");
    } else {
        document.body.classList.remove("dark-theme");
    }
}
window.addEventListener('load', loadDarkModeFromLocalStorage);