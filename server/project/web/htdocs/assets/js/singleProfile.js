function loadDarkModeFromLocalStorage() {
    const storedDarkMode = localStorage.getItem('darkMode');

    if (storedDarkMode && storedDarkMode === 'true') {
        document.body.classList.add("dark-theme");
    }
}
window.addEventListener('load', loadDarkModeFromLocalStorage);

var loadFile = function (event) {
    var image = document.getElementById("output");
    image.src = URL.createObjectURL(event.target.files[0]);
};

const edit_button = document.getElementById("edit-button");
const password = document.getElementById("passwordChange");
const visibleBtn = document.getElementById("visible");
const role = document.getElementById("role");
const save = document.getElementById("save");

console.log(save)

let editable = false;
password.disabled = true;

function visiblePassword() {
    if (password.type === "password") {
        password.type = "text";
        visibleBtn.innerText = "visibility_off"
    }
    else {
        password.type = "password";
        visibleBtn.innerText = "visibility"
    }
}

visibleBtn.addEventListener("click", visiblePassword);



function editableParagraph() {
    editable = !editable;
    password.disabled = !editable;

    var paragraphs = document.getElementsByTagName("p");
    for (var i = 0; i < paragraphs.length; i++) {
        paragraphs[i].contentEditable = editable;
        paragraphs[i].classList.toggle("editable");
    }

    if (editable) {
        visibleBtn.style.display = "block";
        save.style.display = "flex";
    }
    else {
        visibleBtn.style.display = "none";
        save.style.display = "none";
    }
};

edit_button.addEventListener("click", editableParagraph);


