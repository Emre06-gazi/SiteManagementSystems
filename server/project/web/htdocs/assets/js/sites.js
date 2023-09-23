        function loadDarkModeFromLocalStorage() {
    const storedDarkMode = localStorage.getItem('darkMode');

    if (storedDarkMode && storedDarkMode === 'true') {
        document.body.classList.add("dark-theme");
    }
}
window.addEventListener('load', loadDarkModeFromLocalStorage);

 function loadSiteEdit(siteId) {
        var siteUrl = siteId;
        window.location.href = siteUrl;
    }

function showAddSite() {
  var panel = document.getElementsByClassName("panel")[0];
  panel.style.display = "block";
}


function hidePanel() {
  var panel = document.getElementsByClassName("panel")[0];
  panel.style.display = "none";
}

function addArea() {
  const areasContainer = document.getElementById('areasContainer');
  const areaDiv = document.createElement('div');
  areaDiv.className = 'area';
  areaDiv.innerHTML = `
    <input type="text" name="areaName[]" placeholder="Bölge Adı" />
    <input type="text" name="areaSystems[]" placeholder="Sistemler" />
    <button type="button" class="removeAreaButton" onclick="removeArea(this)">X</button>
  `;
  areasContainer.appendChild(areaDiv);
}

function removeArea(button) {
  const areaDiv = button.parentNode;
  areaDiv.parentNode.removeChild(areaDiv);
}

document.getElementById("addNewSite").addEventListener("click", showAddSite);
document.getElementById("cancelButton").addEventListener("click", hidePanel);

var addSiteButton = document.getElementById("add-site-button");
var deleteSiteButton = document.getElementById("remove-site-button");
var addTab = document.getElementById("addTab");
var deleteTab = document.getElementById("removeTab");

addSiteButton.addEventListener("click", function() {
    addTab.style.display = "block";
    deleteTab.style.display = "none";
});

deleteSiteButton.addEventListener("click", function() {
    addTab.style.display = "none";
    deleteTab.style.display = "block";
});