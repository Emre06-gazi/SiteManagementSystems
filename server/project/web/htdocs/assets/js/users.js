        function loadDarkModeFromLocalStorage() {
    const storedDarkMode = localStorage.getItem('darkMode');

    if (storedDarkMode && storedDarkMode === 'true') {
        document.body.classList.add("dark-theme");
    }
}
window.addEventListener('load', loadDarkModeFromLocalStorage);

// tıklandığında singleUser Page alanı
 function loadUserEdit(userId) {
        var userUrl = userId;
        window.location.href = userUrl;
    }

function showAddSite() {
  var panel = document.getElementsByClassName("panel")[0];
  panel.style.display = "block";
}


function hidePanel() {
  var panel = document.getElementsByClassName("panel")[0];
  panel.style.display = "none";
}

document.getElementById("add-panel-button").addEventListener("click", showAddSite);
document.getElementById("cancelButton").addEventListener("click", hidePanel);


var addUserButton = document.getElementById("add-user");
var deleteUserButton = document.getElementById("delete-user");
var addTab = document.getElementById("addTab");
var deleteTab = document.getElementById("deleteTab");

addUserButton.addEventListener("click", function() {
    addTab.style.display = "block";
    deleteTab.style.display = "none";
});

deleteUserButton.addEventListener("click", function() {
    addTab.style.display = "none";
    deleteTab.style.display = "block";
});