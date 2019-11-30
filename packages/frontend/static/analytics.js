'use strict';

// Make the actual CORS request.
function mcr(track_id) {
    if (!track_id) {
        console.error("Undefined ML key!");
    }

    const method = 'GET';
    const presentable_data = {
        url: window.location.href,
        origin: window.location.origin,
        track_id: track_id,
    }
    const url = 'https://actstylo.ngrok.io/traffic/?json=' + encodeURIComponent(JSON.stringify(presentable_data));

    let xhr = new XMLHttpRequest();
    if ("withCredentials" in xhr) {
        // with creds
        // XHR for Chrome/Firefox/Opera/Safari.
        xhr.open(method, url, true);
    } else if (typeof XDomainRequest != "undefined") {
        // XDomainRequest for IE.
        xhr = new XDomainRequest();
        xhr.open(method, url);
    } else {
        // CORS not supported.
        return null;
    }
    xhr.send();
}
