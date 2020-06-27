chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    chrome.tabs.sendMessage(tabs[0].id, {method: "getText"}, function(response) {
        if(response.method=="getText"){
            alltext = response.bodyText;
            title = response.title;
            console.log(title);
            console.log(alltext);

            var request = new XMLHttpRequest()
            request.open('GET', 'http://127.0.0.1:5000/api/summarizetext?text='+alltext+'&headline='+title, true);
            request.onload = function () {
              console.log(this.response);
              document.all[0].innerText = this.response;
            }
            request.send();

        }
    });
});
