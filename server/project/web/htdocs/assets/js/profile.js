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
const save_button = document.getElementById("save-changes-btn");
const password = document.getElementById("passwordChange");
const visibleBtn = document.getElementById("visible");
const role = document.getElementById("role");
const save = document.getElementById("save");
const cancel_button = document.getElementById("cancel-btn");

cancel_button.addEventListener("click", function() {
    var paragraphs = document.getElementsByClassName("edits");
    for (var i = 0; i < paragraphs.length; i++) {
        var originalValue = paragraphs[i].getAttribute("data-original");
        paragraphs[i].textContent = originalValue;
    }
});


console.log(save)

let editable = false;

function editableParagraph() {
    editable = !editable;

    var paragraphs = document.getElementsByClassName("edits");
    for (var i = 0; i < paragraphs.length; i++) {
        paragraphs[i].contentEditable = editable;
        paragraphs[i].classList.toggle("editable");
    }

    if (editable) {
        save.style.display = "flex";
    }
    else {
        visibleBtn.style.display = "none";
        save.style.display = "none";
    }
};

edit_button.addEventListener("click", editableParagraph);

function saveChanges() {
  var id = document.getElementById("userId").value;
  var firstname = document.getElementById("firstname").textContent;
  var username = document.getElementById("username").textContent;
  var lastname = document.getElementById("lastname").textContent;
  var tagname = document.getElementById("tagname").textContent;

  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/api/users/" + id + "/" + firstname + "/" + lastname + "/" + tagname + "/" + username, true);
  xhr.onreadystatechange = function () {
    if (xhr.readyState === 4 && xhr.status === 200) {
      var response = JSON.parse(xhr.responseText);
      if (response.ret === "POSTLANDI") {
        alert("Bilgileriniz başarıyla güncellenmiştir.");

        var updatedData = JSON.parse(xhr.responseText);
        var sessionData = updatedData.session;
        for (var key in sessionData) {
          if (sessionData.hasOwnProperty(key)) {
            session[key] = sessionData[key];
          }
        }
      } else {
        alert("Bilgilerinizi güncellerken bir hata meydana geldi.");
      }
    }
  };
  xhr.send(JSON.stringify({
    "id": id,
    "firstname": firstname,
    "lastname": lastname,
    "tagname": tagname,
    "username": username
  }));
}
save_button.addEventListener("click", saveChanges);