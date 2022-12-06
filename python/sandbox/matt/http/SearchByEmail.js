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
function populate_table(table_id, data_array) {
    let table = $(table_id);
    let tableBody = table.find('tbody');
    tableBody.empty();
    data_array.forEach(function (row_data) {
        let row = $('<tr></tr>');
        row_data.forEach(function (cell_data) {
            let cell = $('<td></td>');
            cell.text(cell_data);
            row.append(cell);
        });
        tableBody.append(row);
    });
}
function search_by_email() {
    let email = document.getElementById("email").value;
    let email_hash = hex_md5(email);
    debug('Searching for '+email);
    $.get('/api/searchByEmail/?email_hash='+email_hash, function (rslt) {
        populate_table('#beenthere', rslt.projects)
    });
}

debug("Registering trigger for window.onload and jquery.document.read");
window.onload = winLoaded;
$(document).ready(function () {
    debug("jQuery document ready reporting SIR!");
    jqLoaded();
});
