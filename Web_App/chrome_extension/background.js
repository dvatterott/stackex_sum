// background.js

//listen for extension button press
chrome.browserAction.onClicked.addListener(function(tab) {
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    var activeTab = tabs[0];
    var url = tabs[0].url;
  chrome.tabs.sendMessage(activeTab.id, {"message": "clicked_browser_action","url": url});
  });
});

// open new tab!
chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
    if( request.message === "open_new_tab" ) {
      //chrome.tabs.update({"url": "http://127.0.0.1:5000/output?url=" + request.url});
      //chrome.tabs.update({"url": "http://34.198.227.154:5000/output?url=" + request.url});
      chrome.tabs.update({"url": "http://siftingtheoverflow.com/output?url=" + request.url});
    }
  }
);
