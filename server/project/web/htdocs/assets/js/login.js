    function login() {
        var username = document.getElementById("username").value;
        var password = document.getElementById("password").value;

        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/api/login/" + username + "/" + password, true);
        xhr.setRequestHeader("Content-Type", "application/json");

        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.success) {
                    window.location.href = "http://" + server_ip;
                } else {
                    alert(response.desc);
                }
            }
        };
        xhr.send();
    }

function loadDarkModeFromLocalStorage() {
    const storedDarkMode = localStorage.getItem('darkMode');

    if (storedDarkMode && storedDarkMode === 'true') {
        document.getElementById("loginPage").classList.add("dark-theme");
    }
}
window.addEventListener('load', loadDarkModeFromLocalStorage);