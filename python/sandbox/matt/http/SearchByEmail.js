var winLoad = false;
var jqLoad = false;
var pageLoadedFired = false;

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
    var email = document.getElementById("email").value;
    debug('Searching for '+email);
    $.post('/api/searchByEmail', {
        email: email
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
