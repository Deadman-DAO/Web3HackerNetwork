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
    $.get('/api/searchByEmail/?email_hash='+email_hash, function (rslt) {
        pastReposTable = $('#beenthere')[0]; /* deref the jquery container object with [0]*/
        while (pastReposTable.rows.length > 1) {
            pastReposTable.deleteRow(1);
        }
        pastReposTable.append('<thead><tr><th>Repo Owner</th><th>Repo Name</th></tr></thead>');
        rslt.projects.forEach(function (project) {
            let row = pastReposTable.append('<tr><td>'+project.owner+'</td><td>'+project.name+'</td></tr>');
        });
        pastReposTable.removeClass('hidden');
        pastReposTable.addClass('visible');
        debug(rslt);
    });
}

debug("Registering trigger for window.onload and jquery.document.read");
window.onload = winLoaded;
$(document).ready(function () {
    debug("jQuery document ready reporting SIR!");
    jqLoaded();
});
