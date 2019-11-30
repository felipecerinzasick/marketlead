function createCORSRequest(method, url) {
    var xhr = new XMLHttpRequest();
    if ("withCredentials" in xhr) {
        console.log("with cred");
        // XHR for Chrome/Firefox/Opera/Safari.
        xhr.open(method, url, true);
    } else if (typeof XDomainRequest != "undefined") {
        console.log("IE");
        // XDomainRequest for IE.
        xhr = new XDomainRequest();
        xhr.open(method, url);
    } else {
        console.log("cors not supported");
        // CORS not supported.
        xhr = null;
    }
    return xhr;
}

// Make the actual CORS request.
function makeCorsRequest() {
    // This is a sample server that supports CORS.
    var url = 'https://actstylo.ngrok.io/traffic/?website=something-sssssss';

    var xhr = createCORSRequest('GET', url);
    if (!xhr) {
        alert('CORS not supported');
        return;
    }

    // Response handlers.
    xhr.onload = function () {
        alert('Response from CORS request to ' + url + ': title');
    };

    xhr.onerror = function () {
        alert('Whoops, there was an error making the request.');
    };

    xhr.send();
}

makeCorsRequest();