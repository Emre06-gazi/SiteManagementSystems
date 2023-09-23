let icon = document.getElementById("darkicon");
const darkModeToggle = document.getElementById('darkTheme');


function resuToogleDarkMode(_document, isDarkMode) {
  const iframe = _document.querySelector('iframe');

  if (!iframe) {
    return
  }
  const innerIframeDoc = iframe.contentDocument ?? iframe.contentWindow.document

  if (isDarkMode) {
    innerIframeDoc.body.classList.add('dark-theme');
  } else {
    innerIframeDoc.body.classList.remove('dark-theme');
  }

  resuToogleDarkMode(innerIframeDoc, isDarkMode)
}

function toggleDarkMode() {
  isDarkMode = !isDarkMode;
  localStorage.setItem('darkMode', isDarkMode.toString());

  if (isDarkMode) {
    icon.innerText = "light_mode"
    icon.classList.add("dark-theme-animation");
    document.body.classList.add('dark-theme');
  } else {
    icon.innerText = "nightlight"
    icon.classList.remove("dark-theme-animation");
    document.body.classList.remove('dark-theme');
  }
  resuToogleDarkMode(document, isDarkMode)
}

darkModeToggle.addEventListener('click', toggleDarkMode);

// window.addEventListener('load', loadDarkModeFromLocalStorage);
loadDarkModeFromLocalStorage()

let menuicon = document.getElementById("menuicon");
menuicon.onclick = function () {
  let sidebar = document.getElementById("sideBar");
  let title = document.getElementById("sidebarTitle");
  let content = document.getElementById("sidebarContent");
  let user = document.getElementById("sidebarUser");
  let embed = document.getElementById("embedContent");
  sidebar.classList.toggle("sidebar-open");
  title.classList.toggle("sidebarClose");
  content.classList.toggle("sidebarClose");
  user.classList.toggle("sidebarClose");
  embed.classList.toggle("embedOpen");
  if (menuicon.innerText == 'menu') {
    menuicon.innerText = 'close';
  } else {
    menuicon.innerText = 'menu';
  }
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////

async function postData(_api = "", _data = {}) {
  // Default options are marked with *
  try {
    const response = await fetch(`http://${server_ip}/api/${_api}`, {
      method: "POST", // *GET, POST, PUT, DELETE, etc.
      mode: "cors", // no-cors, *cors, same-origin
      cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
      credentials: "same-origin", // include, *same-origin, omit
      headers: {
        "Content-Type": "application/json",
        // 'Content-Type': 'application/x-www-form-urlencoded',
      },
      redirect: "follow", // manual, *follow, error
      referrerPolicy: "no-referrer", // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
      body: JSON.stringify(_data), // body data type must match "Content-Type" header
    });
    return response.json(); // parses JSON response into native JavaScript objects
  } catch (error) {
    console.error("Error:", error);
    return null
  }
}


///////////////////////////////////////////////////////////////////////////////////////////////////////////


class TreeBase{
  constructor(parent, id, dictName, text, className) {
    this.inside = null
    this.parent = parent
    this.id = id
    this.text = text
    this.dictName = dictName
    this.className = className
    this.details = $('<details>')
    this.ul = $('<ul>')
    this.dom = $('<li>').append(this.details.append($('<summary>').addClass(this.className).text(this.text))).append(this.ul);
    this.dom.addClass('loaded');
    this.objects = [];
  }

  setup(){
    const me = this
    this.details.on('toggle', function (e) {
      e.stopPropagation();
      me.update(e);
    })
  }

  _update(data) {
    data.forEach((systemData) => {
      const _newObject = new this.inside(this, systemData)
      this.ul.append(_newObject.dom);
      this.objects.push(_newObject)
    });
  }

  
  createRequest(obj, data){   

    if (typeof obj.dictName === 'undefined'){
      return {}
    }

    data = {
      ...data,
      ...{[obj.dictName] : obj.id},
      ...obj.createRequest(obj.parent, data)
    }

    return data
  }

  sendData(){
    return postData("test", this.createRequest(this, {}))
  }

  update(e) {
    if (!e.currentTarget.open) {
      this.ul.empty();
      this.objects = [];
      return
    }
    this.sendData().then((data) => {
      this._update(data);
    });
  }

}


class Devices extends TreeBase {
  constructor(parent, siteData) {
    super(undefined, siteData.device_id, undefined, siteData.device_name, undefined);
    this.device_id = siteData.device_id
    this.device_name = siteData.device_name
    this.connected = siteData.connected
    this.setup()
    this.draw()
  }

  draw(){
    if (this.connected){

    }
    else{

    }
    
  }

  update(e) {
    $('.content .main-canvas').attr('src', `/canvas/${this.device_id}`);
    this.draw()
  }
}

function getSummaryClass2(content) {
  if (content === 0) {
    return ['energyName', "Elektrik"];
  } else if (content === 1) {
    return ['waterName', "Sulama"];
  } else if (content === 2) {
    return ['heatName', "Isıtma"];
  } else if (content === 3) {
    return ['poolName', "Havuz"];
  }
  // Varsayılan sınıf
  return '';
}

class System extends TreeBase {
  constructor(parent, siteData) {
    const [className, text] = getSummaryClass2(siteData)
    super(parent, siteData, "system_id", text, className);
    this.inside = Devices
    this.setup()

  }
}

class Area extends TreeBase {
  constructor(parent, areaData) {
    super(parent, areaData.id, "block_id", areaData.name, "areaName");
    this.inside = System
    this.setup()

  }
}

class Site extends TreeBase {
  constructor(parent, siteData) {
    super(parent, siteData.id, "site_id", siteData.site_name, "siteName");
    this.inside = Area
    this.setup()
  }
}



class TreeView extends TreeBase {
  constructor(parent, areaData) {
    super(undefined, undefined, undefined, undefined, undefined);
    this.inside = Site

    this.ul = $('.tree');
    this.dom = this.ul;
    this.details = $('details.contentListItem');

    this.setup()

  }
}


const treeView = new TreeView()


///////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function () {
  $.ajax({
    url: 'http://' + server_ip + '/api/treeView/',
    type: 'GET',
    dataType: 'json',
    success: function (response) {
      var treeData = response;
      buildTreeView(treeData);
    },
    error: function (xhr, status, error) {
      console.error(error);
    }
  });

  function buildTreeView(data) {
    var tree = $('.tree');
    tree.empty();

    for (var i = 0; i < data.length; i++) {
      var site = data[i];
      var siteItem = $('<li>').append($('<details>').append($('<summary>').addClass('siteName').text(site))).append($('<ul>'));

      siteItem.on('click', function () {
        var siteElement = $(this);
        var siteName = siteElement.find('.siteName').text();

        if (!siteElement.hasClass('loaded')) {
          loadBolge(siteName, siteElement);
          siteElement.addClass('loaded');
        } else {
          siteElement.find('ul').toggle();
        }
      });

      tree.append(siteItem);
    }
  }

  function loadBolge(siteName, siteElement) {
    var encodedSite = encodeURIComponent(siteName);
    var siteUrl = 'http://' + server_ip + '/api/treeView/' + encodedSite;

    $.ajax({
      url: siteUrl,
      type: 'GET',
      dataType: 'json',
      success: function (response) {
        var bolgeData = response;
        var childNode = $('<ul>');

        for (var i = 0; i < bolgeData.length; i++) {
          var bolge = bolgeData[i];
          var bolgeItem = $('<li>').append($('<details>').append($('<summary>').addClass('areaName').text(bolge))).append($('<ul>'));

          bolgeItem.on('click', function (e) {
            e.stopPropagation();

            var bolgeElement = $(this);
            var bolgeName = bolgeElement.find('summary').text();

            if (!bolgeElement.hasClass('loaded')) {
              loadSistem(siteName, bolgeName, bolgeElement);
              bolgeElement.addClass('loaded');
            } else {
              bolgeElement.find('ul').toggle();
            }
          });

          childNode.append(bolgeItem);
        }

        siteElement.find('ul').remove();
        siteElement.append(childNode);
      },
      error: function (xhr, status, error) {
        console.error(error);
      }
    });
  }

  function getSummaryClass(content) {
    if (content === 'Elektrik') {
      return 'energyName';
    } else if (content === 'Sulama') {
      return 'waterName';
    } else if (content === 'Isıtma') {
      return 'heatName';
    } else if (content === 'Havuz') {
      return 'poolName';
    }
    // Varsayılan sınıf
    return '';
  }


  function loadSistem(siteName, bolgeName, bolgeElement) {
    var encodedSite = encodeURIComponent(siteName);
    var encodedBolge = encodeURIComponent(bolgeName);
    var bolgeUrl = 'http://' + server_ip + '/api/treeView/' + encodedSite + '/' + encodedBolge;

    $.ajax({
      url: bolgeUrl,
      type: 'GET',
      dataType: 'json',
      success: function (response) {
        var bolgeData = response;
        var bolgeNode = $('<ul>');

        for (var i = 0; i < bolgeData.length; i++) {
          var bolgeDataNew = bolgeData[i];
          var bolgeItem = $('<li>').append($('<details>').append($('<summary>').addClass(getSummaryClass(bolgeDataNew)).text(bolgeDataNew)));

          bolgeItem.on('click', function (e) {
            e.stopPropagation();

            var clickedEfendiElement = $(this);
            var sistem = clickedEfendiElement.find('summary').text();

            if (!clickedEfendiElement.hasClass('loaded')) {
              var encodedSistem = bolgeUrl + '/' + sistem;
              loadEfendi(encodedSistem, clickedEfendiElement);
              clickedEfendiElement.addClass('loaded');
            } else {
              clickedEfendiElement.find('ul').toggle();
            }
          });

          bolgeNode.append(bolgeItem);
        }

        var efendiList = $('<ul>').append(bolgeNode);
        bolgeElement.append(efendiList);
      },
      error: function (xhr, status, error) {
        console.error(error);
      }
    });
  }

  function loadEfendi(sistem, clickedElement) {
    $.ajax({
      url: sistem,
      type: 'GET',
      dataType: 'json',
      success: function (response) {
        var extractedValue = Object.keys(response)[0];

        if (clickedElement.find('[data-name="' + extractedValue + '"]').length === 0) {
          var clickedSrc = $('<li>').append($('<details>').append($('<summary>').text(extractedValue))).attr('data-name', extractedValue);
          var efendiList = $('<ul>').append(clickedSrc);
          clickedElement.append(efendiList);

          clickedSrc.on('click', function (e) {
            e.stopPropagation();
            var clickedEfendiElement = $(this);
            var clickedEfendi = clickedEfendiElement.attr('data-name');

            var newSrc = '/canvas/' + clickedEfendi;
            $('.content .main-canvas').attr('src', newSrc);
          });
        }
      },
      error: function (xhr, status, error) {
        console.error(error);
      }
    });
  }
});

const mainCanvas = document.querySelector(".main-canvas");

// Site Ekle Sayfa
var siteEkleButton = document.getElementById("siteEkle");
siteEkleButton.addEventListener("click", function () {
  mainCanvas.src = "/sites";
});

// Kullanici Ekle Sayfa
var kullanicilarButton = document.getElementById("kullanicilar");
kullanicilarButton.addEventListener("click", function () {
  mainCanvas.src = "/users";
});

// Profil Sayfa
var profileButton = document.getElementById("profile");
profileButton.addEventListener("click", function () {
  mainCanvas.src = "/profile";
});