
function resuToogleDarkMode(_document, isDarkMode){
  const iframe = _document.querySelector('iframe');

    if (!iframe){
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

let isDarkMode;
function toggleDarkModeOnLoading() {
    if (isDarkMode) {
        document.body.classList.add('dark-theme');
    } else {
        document.body.classList.remove('dark-theme');
    }
    resuToogleDarkMode(document, isDarkMode)
}

function loadDarkModeFromLocalStorage() {
    const storedDarkMode = localStorage.getItem('darkMode');

    if (storedDarkMode && storedDarkMode === 'true') {
      isDarkMode = true
      toggleDarkModeOnLoading();
      return
    }
    isDarkMode =false
}
