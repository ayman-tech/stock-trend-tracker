let urls = [];
let currentIndex = 0;
let tabId = null;
let rotationStarted = false;

// Fetch URLs from the local text file
fetch(chrome.runtime.getURL('urls.txt'))
  .then(response => response.text())
  .then(text => {
    urls = text.split(/\s+/).filter(Boolean);
    openNewTab();
  });

function openNewTab() {
  if (urls.length === 0 || rotationStarted) return;
  rotationStarted = true;
  chrome.tabs.create({ url: urls[currentIndex] }, (tab) => {
    tabId = tab.id;
    setTimeout(changeUrl, 15000);
  });
  rotationStarted = false;
}

function changeUrl() {
  currentIndex = (currentIndex + 1) % urls.length;
  chrome.tabs.update(tabId, { url: urls[currentIndex] });
  if(currentIndex == urls.length-1) return;
  setTimeout(changeUrl, 15000);
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'startRotation') {
    openNewTab();
  }
});
