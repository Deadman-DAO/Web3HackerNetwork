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
function populate_table(table_id, data_array, columns) {
    let table = $(table_id);
    let tableBody = table.find('tbody');
    tableBody.empty();
    data_array.forEach(function (row_data) {
        let row = $('<tr></tr>');
        row.addClass('row');
        columns.forEach(function (cell_name) {
            let cell_data = row_data[cell_name];
            let cell = $('<td></td>');
            cell.text(cell_data);
            let link = $('<a></a>').attr('href', 'https://github.com/'+row_data.owner+'/'+row_data.repo_name);
            cell.append(link);
            row.append(cell);
        });
        tableBody.append(row);
    });
    table.removeClass('invisible');
    table.addClass('visible')
}
function search_by_email() {
    let email = document.getElementById("email").value;
    let email_hash = hex_md5(email);
    debug('Searching for '+email);
    $.get('/api/searchByEmail/?email_hash='+email_hash, function (rslt) {
        populate_table('#beenthere', rslt.projects, ['owner', 'repo_name'])
    });
}

debug("Registering trigger for window.onload and jquery.document.read");
window.onload = winLoaded;
$(document).ready(function () {
    debug("jQuery document ready reporting SIR!");
    jqLoaded();
});
