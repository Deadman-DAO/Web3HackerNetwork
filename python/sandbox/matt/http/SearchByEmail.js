let winLoad = false;
let jqLoad = false;
let pageLoadedFired = false;
let forge = require('forge');
require('md');
require('baseN');
require('util');
require('md5');

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
    let md = forge.md.md5.create();
    md.update(email)
    let email_hash = md.digest().toHex();
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
