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
function goToGitHub(owner, repo_name) {
    let url = 'https://github.com/'+owner+
        ((repo_name != null && typeof(repo_name) !== 'undefined')  ? ('/'+repo_name) : '');
    window.location.replace(url);
}

function populate_table(table_id, data_array) {
    let table = $(table_id);
    let tableBody = table.find('tbody');
    tableBody.empty();
    data_array.forEach(function (row_data) {
        let row = $('<tr></tr>');
        row.addClass('row');
        let owner = row_data['owner'];
        let repo_name = row_data['repo_name'];
        let owner_cell = $('<td></td>');
        let repo_cell = $('<td></td>');
        owner_cell.addAttributes({'onclick': 'goToGitHub("'+owner+'")'});
        repo_cell.addAttributes({'onclick': 'goToGitHub("'+owner+'", "'+repo_name+'")'});
        owner_cell.text(owner);
        repo_cell.text(repo_name);
        row.append(owner_cell);
        row.append(repo_cell)
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
