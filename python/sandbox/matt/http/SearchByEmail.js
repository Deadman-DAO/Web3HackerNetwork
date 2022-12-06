let winLoad = false;
let jqLoad = false;
let pageLoadedFired = false;

debug('Loading SearchByEmail.js');
function firePageLoaded() {
    if (winLoad && jqLoad && !pageLoadedFired) {
        debug("Both winLoad and jqLoad are set - Firing pageLoaded");
        pageLoadedFired = true;
    }
}


function winLoaded() {
    winLoad = true;
    debug("window.onload fired");
    firePageLoaded();
}

function jqLoaded() {
    jqLoad = true;
    debug("jQuery Loaded");
    firePageLoaded();
}

function search_by_email() {
    let email = document.getElementById("email").value;
    let email_hash = hex_md5(email);
    debug('Searching for '+email);
    $.post('/api/searchByEmail/', {
        email_hash: email_hash
    }, function (rslt) {
        debug(rslt);
    });
}

debug("Registering trigger for window.onload and jquery.document.read");
window.onload = winLoaded;
$(document).ready(function () {
    debug("jQuery document ready reporting SIR!");
    jqLoaded();
});
