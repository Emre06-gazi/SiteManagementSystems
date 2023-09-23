function saatEkle() {
      var saatlerDiv = document.getElementById("saatler");

      var saatGrubuDiv = document.createElement("div");

      var baslangicLabel = document.createElement("label");
      baslangicLabel.innerHTML = "Başlangıç Saati:";

      var baslangicInput = document.createElement("input");
      baslangicInput.type = "time";
      baslangicInput.name = "startTime[]";

      var bitisLabel = document.createElement("label");
      bitisLabel.innerHTML = "Bitiş Saati:";

      var bitisInput = document.createElement("input");
      bitisInput.type = "time";
      bitisInput.name = "endTime[]";

      var kaldirButton = document.createElement("button");
      kaldirButton.innerHTML = "x";
      kaldirButton.type = "button";
      kaldirButton.onclick = function() {
        saatlerDiv.removeChild(saatGrubuDiv);
      };

      saatGrubuDiv.appendChild(baslangicLabel);
      saatGrubuDiv.appendChild(baslangicInput);
      saatGrubuDiv.appendChild(document.createElement("br"));
      saatGrubuDiv.appendChild(bitisLabel);
      saatGrubuDiv.appendChild(bitisInput);
      saatGrubuDiv.appendChild(document.createElement("br"));
      saatGrubuDiv.appendChild(kaldirButton);

      saatlerDiv.appendChild(saatGrubuDiv);
      }

        // EKLEME BUTONLARI ============================

        let mainPage = document.getElementById("yonetimEmbed");
        let senaryoPage = document.getElementById("senaryoPage");
        let grupPage = document.getElementById("gruplaPage");

        function senaryoEkle() {
            mainPage.classList.add("closePage");
            mainPage.classList.remove("openAdd");
            grupPage.classList.add("closePage");
            grupPage.classList.remove("openAdd");
            senaryoPage.classList.remove("closePage");
            senaryoPage.classList.add("openAdd");
        }

        function grupEkle() {
            mainPage.classList.add("closePage");
            mainPage.classList.remove("openAdd");
            senaryoPage.classList.add("closePage");
            senaryoPage.classList.remove("openAdd");
            grupPage.classList.remove("closePage");
            grupPage.classList.add("openAdd");
        }

        function goBack() {
            mainPage.classList.remove("closePage");
            mainPage.classList.add("openAdd");
            senaryoPage.classList.add("closePage");
            senaryoPage.classList.remove("openAdd");
            grupPage.classList.add("closePage");
            grupPage.classList.remove("openAdd");
        }
        function goBackNormal() {
            mainPage.classList.remove("closePage");
            mainPage.classList.add("openAdd");
            senaryoPage.classList.add("closePage");
            senaryoPage.classList.remove("openAdd");
            grupPage.classList.add("closePage");
            grupPage.classList.remove("openAdd");
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