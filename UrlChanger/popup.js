document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('start-rotation').addEventListener('click', function() {
    chrome.runtime.sendMessage({ action: 'startRotation' });
  });
});

