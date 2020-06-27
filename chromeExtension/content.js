chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        if(request.method == "getText"){
            sendResponse({bodyText: document.all[0].innerText, title: document.title, method: "getText"}); //same as innerText
        }
    }
);
