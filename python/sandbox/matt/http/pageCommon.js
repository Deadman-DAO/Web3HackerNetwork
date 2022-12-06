var LOG_VERBOSE = 4;
var LOG_LIGHT = 3;
var LOG_INFO = 2;
var LOG_ERROR = 1;
var LOG_NONE = 0;

var DEBUG_LEVEL = LOG_LIGHT;
var currentStatus = 'Unknown';
var currentPage = 'Unknown';
var userId;
var hasMessages = null;
var url = window.location.href;

if (!Date.now) {
    Date.now = function now() {
        return new Date().getTime();
    }
}
var appPresent = false;
function logAppPresent() {
    debug('appPresent set to true');
    appPresent = true;
}
function isAppPresent() {
    return appPresent;
}

const dayOfWeek = [ 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const suffix = ['??', 'st', 'nd', 'rd', 'th', 'th', 'th', 'th', 'th', 'th', 'th', 'th', 'th', 'th', 'th', 'th', 'th', 'th', 'th', 'th', 'th', 'st', 'nd', 'rd', 'th', 'th', 'th', 'th', 'th', 'th', 'th', 'st'];
function formatDateLong(d) {
    return dayOfWeek[d.getDay()]+' '+month[d.getMonth()]+' '+d.getDate()+suffix[d.getDate()]+' '+d.getFullYear();
}
function formatDate(dt) {
    return (("0"+(dt.getMonth()+1)).slice(-2)) +"/"+ (("0"+dt.getDate()).slice(-2)) +"/"+ (dt.getFullYear());
}
function formatTime(dt) {
    return (("0"+(dt.getHours())).slice(-2)) +":"+ (("0"+(dt.getMinutes())).slice(-2));
}
function formatTimeLong(dt) {
    return (("0"+(dt.getHours())).slice(-2)) +":"+ (("0"+(dt.getMinutes())).slice(-2)) + ":" + (("0")+dt.getSeconds()).slice(-2) + '.' + (("00")+(dt.getTime() % 1000)).slice(-3);
}
function formatDateTime(date) {
    return formatDate(date)+" "+formatTimeLong(date);
}
function getDate() {
    return formatDate(new Date());
}
function getTime() {
    return formatTime(new Date());
}
function getDateTime() {
    let d = new Date();
    return formatDate(d)+" "+formatTime(d);
}
function displayTime(date) {
    let e = $('#datetime');
    if (e != null && typeof(e) !== 'undefined' && e.length) {
        e.html(formatDateLong(date)+' '+formatTime(date));
        let hint = "Server time: "+formatDateTime(date)+" Local PC Time "+formatDateTime(new Date());
        // debug('Setting #datetime title to: '+hint);
        e.prop('title', hint);
    }
}

var tryCount = 0;
var maxTryCount = 20;
var waitForAppTimer;
var myCallBackStack;
function waitingForAppPresent() {
    clearTimeout(waitForAppTimer);
    if (appPresent === true) {
        debug('App found after '+tryCount+' tries (in half second delays)');
        callTheNextFunctionOnCallbackStack(myCallBackStack);
    } else {
        if (++tryCount >= maxTryCount) {
            debug("I've waited too long for the app to be present");
            callTheNextFunctionOnCallbackStack(myCallBackStack);
        } else {
            waitForAppTimer = setTimeout(waitingForAppPresent, 200);
        }
    }
}

function waitForAppPresent( callBackStack ) {
    if (appPresent === true) {
        debug('App is present!');
        callTheNextFunctionOnCallbackStack(callBackStack);
    } else {
        debug('App not found - will wait up to 10 seconds for it to appear');
        tryCount = 0;
        myCallBackStack = callBackStack;
        waitForAppTimer = setTimeout(waitingForAppPresent, 100);
    }
}

function messagePending() {
    return hasMessages;
}
function setMessagePending( newVal ) {
    if (hasMessages === null || (hasMessages ^ newVal)) {
        hasMessages = newVal;
        if (typeof(app) !== 'undefined') {
            debug('calling setMessagePending Java function ('+newVal+')');
            app.setMessagePending(newVal);
        // } else {
        //     debug('Sorry - app does not appear to be available: '+typeof(app));
        }
    } else if (newVal) {
        if (typeof(app) !== 'undefined') {
            debug('Blinking!');
            app.blink();
        // } else {
        //     debug('Sorry - app does not appear to be available: '+typeof(app));
        }

    }
}

var ipAddress;
var machineName;
function setIP( newIP ) {
    ipAddress = newIP;
    debug('IPAddress is now: '+ipAddress);
}
function setMachineName( newMachineName ) {
    machinesName = newMachineName;
    debug('machinesName is now: '+machinesName);
}
function getIPAddress() {
    return ipAddress;
}
function getMachineName() {
    return machineName;
}
var statusCallback = null;
function setStatusCallback( fcn ) {
    statusCallback = fcn;
}
function setStatus(newStatus) {
    currentStatus = newStatus;
    if (typeof(statusCallback) !== 'undefined' && statusCallback !== null) {
        statusCallback(newStatus);
    }
    debug('User status now = '+newStatus);
}
function setCurrentPage(newPage) {
    currentPage = newPage;
    debug('Current page is now: '+currentPage);
}
function getCurrentPage() {
    // debug('Getting current page');
    return currentPage;
}
function getStatus() {
    // debug('Getting status');
    return currentStatus;
}
function getPage() {
    return currentPage;
}
var userName;
var pkStationName;
var pkStationDescription;
var developer;
function setUserName( newVal ) {
    if (typeof(newVal) !== 'undefined' && newVal !== null) {
        userName = newVal;
        if (typeof(app) !== 'undefined') {
            app.setUserName(userName);
        }
    }
}
function setPKStationName( newVal ) {
    if (typeof(newVal) !== 'undefined' && newVal !== null) {
        pkStationName = newVal;
        if (typeof(app) !== 'undefined') {
            app.setPKStationName(pkStationName);
        }
    }
}
function setPKStationDescription( newVal ) {
    if (typeof(newVal) !== 'undefined' && newVal !== null) {
        pkStationDescription = newVal;
        if (typeof(app) !== 'undefined') {
            app.setPKStationDescription(pkStationDescription);
        }
    }
}
function startSecureSocket() {
    if (typeof(app) !== 'undefined' && typeof(app.startSecureSocket) !== 'undefined') {
        debug('Starting secure socket!');
        app.startSecureSocket();
        debug('Secure socket started!');
    }
}
function stopSecureSocket() {
    if (typeof(app) !== 'undefined') {
        debug('Stopping secure socket!');
        app.stopSecureSocket();
    }
}
function setDeveloper( newVal ) {

    if (typeof(app) !== 'undefined') {
        if (typeof(newVal) !== 'undefined' && newVal !== null) {
            developer = newVal;
        } else {
            developer = false;
        }
        app.setDeveloper(developer);
    }

}

function special(dude) {
    if (dude.developer) {
        $(".super").show();

    } else {
        $(".super").hide();
    }
}
function noNull(str) {
    return typeof(str) === 'undefined' || str === null ? "" : str;
}
function logEvent(eventCode, param1, param2, param3, param4, debugIt, callbackStack) {
    $.post('/asrs/other/logEvent', {
        eventCode: eventCode,
        param1: noNull(param1),
        param2: noNull(param3),
        param3: noNull(param3),
        param4: noNull(param4)
    }, function() {
        if (typeof(debugIt) !== 'undefined' && debugIt !== null) {
            debug(debugIt);
        }
        if (callbackStack !== null) {
            callTheNextFunctionOnCallbackStack(callbackStack)
        }
    });
}

var logoutTimer;
var expirationTime;
function countdownToLogout() {
    var curTime = new Date().getTime();
    var seconds = Math.round((expirationTime - curTime) / 1000);
    if (countdownStarted) {
        if (seconds < 1) {
            clearInterval(logoutTimer);
            var stack = [];
            stack.push(function() {
                logout();
                window.location.href(url);
            });

            logEvent("TIMO", "$USERID", "", "", "", "Logged Timed Out", stack);
        } else {
            $('#countdownLogout').val('Logging out in ' + seconds + ' seconds');
        }
    } else {
        debug('Resetting Countdown');
        clearInterval(logoutTimer);
    }
}
var countdownStarted = 0;
function setupCountdown() {
    debug('setupCountdown');
    countdownStarted = 1;
    expirationTime = new Date().getTime() + warnIdleTime;
    $(".countdown").show();
    logoutTimer = setInterval(countdownToLogout, 1000);
}

var maxTries = 40;
var tryCount = 0;
var maxIdleTime = 540000;
var warnIdleTime = 30000;
function setIdleTimeout(nval) {
    debug('IdleTimeout set to '+nval);
    maxIdleTime = nval;
}
function setWarningPeriod(nval) {
    debug('WarningPeriod set to '+nval);
    warnIdleTime = nval;
}
var timerId;
var restrictedIp = 0;
var thisUsersTimeout = maxIdleTime;
function initiateAutoLogout() {
    debug('Initiating Auto Logout');
    // this.addEventListener("mousemove", resetTimer, false);
    this.addEventListener("mousedown", resetTimer, false);
    this.addEventListener("keypress", resetTimer, false);
    this.addEventListener("DOMMouseScroll", resetTimer, false);
    this.addEventListener("mousewheel", resetTimer, false);
    this.addEventListener("touchmove", resetTimer, false);
    this.addEventListener("MSPointerMove", resetTimer, false);
    thisUsersTimeout = restrictedIp ? warnIdleTime : maxIdleTime;
    timerId = window.setTimeout(setupCountdown, thisUsersTimeout);
}
function resetTimer() {
    // debug('Resetting Timer!');
    countdownStarted = 0;
    window.clearTimeout(timerId);
    $(".countdown").hide();
    timerId = window.setTimeout(setupCountdown, thisUsersTimeout);
}

function callTheNextFunctionOnCallbackStack( callback ) {
    if (typeof(callback) === 'undefined' || callback === null) {
        // do Nothing
        debug("Null callback - All done");
    } else if (Array.isArray(callback)) {
        if (callback.length > 0) {
            debug('One or more folks on the callback stack');
            // debug("Array was: " + callback);
            var c = callback.pop();
            // debug("Array now: " + callback);
            c(callback);
        } else {
            debug("End of callback stack");
            debug("Versions: Launcher="+getLauncherVersion()+", HTTPClient="+getHttpVersion()+', AppServer='+getAppServer());
        }
    } else {
        debug('Calling the single callback item');
        callback();
    }
}

function getAppServer() {
    if (typeof(getLocalAppServerVersion) === 'undefined') {
        return 'Unknown';
    } else {
        return getLocalAppServerVersion();
    }
}
function getLauncherVersion() {
    if (typeof(getLocalASRSLoaderVersion) === 'undefined') {
        return 'Unknown';
    } else {
        return getLocalASRSLoaderVersion();
    }
}
function getHttpVersion() {
    if (typeof(getLocalHTTPClientVersion) === 'undefined') {
        return 'Unknown';
    } else {
        return getLocalHTTPClientVersion();
    }
}
function flashLoginHistoryButton() {
    var button = $('#loginHistoryButton');
    if (button.length > 0) {
        button.fadeTo('fast', 1.0, "linear", function() {
            button.fadeTo('slow', 0.5, 'swing', function() {
                button.fadeTo('fast', 1.0, "linear", function () {
                    button.fadeTo('slow', 0.5, 'swing', function() {
                        button.attr("style", "");
                    });
                });
            });
        });
    }

}
function displayPopup(msg) {
    debug('Popping up '+msg);
    var existing = $('#shagtag');
    if (existing.length == 0) {
        debug('Creating new shagtag');
        existing = $('<div id="shagtag"/>');
        $('body').append(existing);
        debug('shagtag appended');
    }
    existing.text(msg);
    existing.addClass('flash');
    setTimeout(function() {
        $('#shagtag').removeClass('flash');
        flashLoginHistoryButton();
    }, 5800);
}
function logLogin(callback) {
    setAppTitleDirectly('RRAD ASRS (Automated Storage Retrieval System)  -  '+currentPage);
    if (typeof(ipAddress) === 'undefined' && tryCount < maxTries) {
        debug('Delaying logLogin by two hundred milliseconds');
        tryCount++;
        setTimeout( function() {
            logLogin(callback);
        }, 200);
    } else {
        debug('Logging Login - ipAddress found');
        var xmlHttp;
        xmlHttp = new XMLHttpRequest();
        xmlHttp.onreadystatechange = function () {
            // debug("xmlHttp.readyState = "+xmlHttp.readyState);
            if (xmlHttp.readyState === 4) {
                if (xmlHttp.status === 200) {
                    var sinfo = JSON.parse(xmlHttp.response);
                    userId = sinfo.userId;
                    setUserName(sinfo.userName);
                    setPKStationName(sinfo.pkStationName);
                    setPKStationDescription(sinfo.pkStationDescription);
                    setIdleTimeout(sinfo.idleTimeout);
                    setWarningPeriod(sinfo.warningPeriod);
                    var dev = sinfo.developer;
                    debug('Login successfully captured "' + userId + '"');
                    special(sinfo);
                    setDeveloper(dev);
                    if (dev) {
                        debug('(Super User)');
                    }
                    restrictedIp = 0;
                    if (sinfo.ipRestricted) {
                        restrictedIp = 1;
                        initiateAutoLogout();
                        debug('IP Restricted - Limited login');
                    } else if (sinfo.userRestricted) {
                        debug('No can do!');
                        logout();
                    } else if (sinfo.passwordExpired) {
                        debug('Redirecting to password change screen');
                        sessionStorage.setItem("lastPage",window.location.pathname);
                        window.location.href = 'changePassword.html';
                    } else {
                        if (sinfo.autoLogout) {
                            debug("Starting Auto Logout");
                            initiateAutoLogout();
                        } else {
                            debug("This login is special and does NOT require auto logout");
                        }
                        startSecureSocket();
                    }
                    loadRoles();
                    debug('lastLogin = '+sinfo.lastLogin);
                    var lastLoginMsg = sinfo.lastLogin;
                    if (lastLoginMsg != null && typeof(lastLoginMsg) !== 'undefined') {
                        debug('Displaying last login message');
                        displayPopup("You last logged in at: "+lastLoginMsg);
                    } else {
                        flashLoginHistoryButton();
                    }


                } else {
                    debug('Error encountered capturing login event: ' + xmlHttp.status);
                }
                callTheNextFunctionOnCallbackStack(callback);
            }
        };
        var bgColor = getLocalValue('background.color', null);
        var fgColor = getLocalValue('foreground.color', null);
        debug('Your background color is: '+bgColor);
        xmlHttp.open("POST", "/asrs/other/loglogin", true);
        xmlHttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        var params = 'currentPage=' + getCurrentPage() +
                     '&currentStatus=' + getStatus() +
                     '&ip=' + getIPAddress() +
                     '&machineName=' + getMachineName()+
                     '&launcherVersion='+getLauncherVersion()+
                     '&httpVersion='+getHttpVersion()+
                     '&appServerVersion='+getAppServer()+
            (bgColor === null || fgColor === null ? '&foregroundColor=undefined&backgroundColor=undefined' :
                '&foregroundColor='+fgColor+'&backgroundColor='+bgColor);
        xmlHttp.send(params);
    }
}

$('#loginHistory').dialog( {
    autoOpen: false,
    width: 525,
    // maxHeight: 650,
    title: 'Login History',
    show: 'blind',
    hide: 'explode',
    modal: 'true',
    // },
    buttons: [
        {
            text: 'More Recent',
            icon: 'ui-icon-arrowthick-1-n',
            click: function() {
                var beforeIdx = $(this).data('beforeIdx');
                debug('Clicked up! '+beforeIdx);
                displayLoginHistory(-1, beforeIdx);
            }
        },
        {
            text: 'Earlier',
            icon: 'ui-icon-arrowthick-1-s',
            click: function() {
                var afterIdx = $(this).data('afterIdx');
                debug('Clicked down! '+afterIdx);
                displayLoginHistory(afterIdx, -1);
            }
        }
    ]


});


function displayLoginHistory(beforeIdx,afterIdx) {
    $.post('/asrs/other/getRecentLoginHistory', {
        beforeId: beforeIdx,
        afterId: afterIdx
    }, function(reply) {
        if (reply.invalidUser) {
            logout();
        } else {
            debug('Got back from getRecentLoginHistory');
            var lh = $('#loginHistory');
            // if (lh.length < 1) {
            //
            //     debug("That's strange.  #loginHistory should always be found.");
            // } else {
            //     debug("Removing previous copy of #loginHistory");
            //     lh.remove();
            // }
            // lh = $('<div id="loginHistory" class="invisible ui-dialog-content ui-widget-content" style="display: block;""/>');
            // $('body').append(lh);
            lh.empty();
            lh.data('beforeIdx', reply.minId);
            lh.data('afterIdx', reply.maxId);
            var lht = $('#loginHistoryTable');
            if (lht.length > 0) {
                debug('removing previous loginHistoryTable');
                lht.remove();
            }
            lht = $('<table id="loginHistoryTable"/>');
            lh.append(lht);
            var thead = $('<thead>');
            var row = $('<tr>');
            // row.append($('<th>Time/Date</th>').addClass('loginHistoryTimeDate'), $('<th>Result</th>').addClass('standardTable'));
            // row.append($('<th>id</th>'), $('<th>Time/Date</th>'), $('<th>Result</th>'));
            row.append($('<th>Time/Date</th>'), $('<th>Result</th>'));
            thead.append(row);
            lht.append(thead);
            var tbody = $('<tbody>');
            reply.logins.forEach( function(rslt) {
                row = $('<tr>');
                // row.append($('<td>'+rslt.id+'</td>').addClass('standardTableRightAlign'));
                row.append($('<td>'+rslt.timeString+'</td>').addClass('standardTableRightAlign'));
                // row.append($('<td>'+rslt.timeString+'</td>'));
                if (rslt.action === 'S') {
                    row.append($('<td>Successful</td>').addClass('standardTable'));
                    // row.append($('<td>Successful</td>'));
                } else {
                    row.append($('<td>FAILED</td></tr>').addClass('brightRed standardTable'));
                    // row.append($('<td>FAILED</td></tr>'));
                }
                tbody.append(row);
            });
            lht.append(tbody);
            debug('New table added');
            // copyDomToClipboard();
            // var thingy = lh.data('DataTable');
            // if (thingy == null || typeof(thingy) === 'undefined') {
                debug('Loading data table!');
                debug('DataTable is a '+typeof(lh.DataTable));
                var obj = lht.DataTable( {
                    // "scrollY":        "400px",
                    // "scrollCollapse": true,
                    // "paging":         true,
                    "order":    [],
                    "lengthMenu": [12],
                    // scrollY:        350,
                    // scrollCollapse: true,
                    // scroller:       true,
                    "initComplete" : function() {
                        lh.dialog('open');
                        // copyDomToClipboard();
                    }
                });
                debug('He returned me this: '+typeof(obj));
            //     lh.data('DataTable', obj);
            // }
            // lh.removeClass('invisible');
            // lh.dialog("widget").position({
            //     my: 'left top',
            //     at: 'left bottom',
            //     of: target
            // });
        }
    })
}
function displayMostRecentLogins() {
    var lh = $('#loginHistory');
    if (lh.length > 0) {
        lh.data('beforeIdx', -1);
        lh.data('afterIdx', -1);
        displayLoginHistory(-1,-1);
    }

}

function logout() {
    setMessagePending(false);
    stopSecureSocket();
    setDeveloper(false);
    var xmlHttp;
    xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange=function() {
        if (xmlHttp.readyState===4) {
            if (xmlHttp.status===200) {
                debug('Logout successfully captured');
            } else {
                debug('Error encountered capturing login event: '+xmlHttp.status);
            }
            if (typeof(sessionStorage) !== 'undefined' && typeof(sessionStorage.clear) !== 'undefined') {
                debug('Clearing session storage');
                sessionStorage.clear();
                debug('DONE Clearing session storage');
            } else {
                debug('sessionStorage or sessionStorage.clear() is invalid');
            }
            // if (typeof(localStorage) !== 'undefined' && typeof(localStorage.clear) !== 'undefined') {
            //     debug('Clearing local storage');
            //     localStorage.clear();
            //     debug('DONE Clearing local storage');
            // }
            // else {
            //     debug('localStorage or localStorage.clear() is invalid');
            // }
            debug('Redirecting to login screen');
            window.location.replace('../returnToLogin.html');
            debug("Probably shouldn't have gotten here");
            // window.location.href = "";
            // window.location.reload(true);
        }
    };
    var status = 'currentPage='+getCurrentPage()+
        '&currentStatus='+getStatus()+
        '&ip='+getIPAddress()+
        '&machineName='+getMachineName();
    xmlHttp.open("POST","/asrs/other/logout",true);
    xmlHttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xmlHttp.send(status);
}
function copyDomToClipboard() {
    var modal = document.getElementById("pasteyModal");
    if (modal != null && typeof(modal) !== 'undefined') {
        modal.style.display = "block";
        var clipText = document.getElementById('pasteyText');
        if (clipText != null && typeof (clipText) !== 'undefined') {
            debug('I found pasteyText');
        }
        var val = document.documentElement.outerHTML;
        debug(val.length + ' bytes found in outer HTML');
        clipText.textContent = val;
        clipText.select();
        document.execCommand("copy");
        debug("I'm itchy!  (says Rez)");
    }
    // modal.style.display = "none";
    // showDebug();
    // showDebug();
}
function showDebug() {
    var modal = document.getElementById("debugModal");
    modal.style.display = "block";
}
function hideDebug() {
    var modal = document.getElementById("debugModal");
    modal.style.display = "none";
}
function hidePastey() {
    document.getElementById("pasteyModal").style.display = "none";
}

function fixedSized( num, size ) {
    var s = num+"";
    while (s.length < size) s = "0" + s;
    return s;
}
function getTime() {
    var d =  new Date();
    return fixedSized( d.getHours(), 2 ) + ":" +
        fixedSized( d.getMinutes(), 2 ) + ":" +
        fixedSized( d.getSeconds(), 2 ) + "." +
        fixedSized( d.getMilliseconds(), 3 );
}
function log( txt ) {
    var area = document.getElementById("debugText");
    var prev = area.textContent;
    if (prev.length > 5000*DEBUG_LEVEL) {
        prev = prev.substring(0, 5000);
    }
    area.textContent = getTime()+"=>"+txt + "\n" + prev;

}
function verbose( txt ) {
    if ( DEBUG_LEVEL >= LOG_VERBOSE ) {
        log(txt);
    }
}
function debug( txt ) {
    if (DEBUG_LEVEL >= LOG_LIGHT ) {
        log(txt);
    }
}
function info( txt ) {
    if (DEBUG_LEVEL >= LOG_INFO ) {
        log(txt);
    }
}
function error(txt) {
    if (DEBUG_LEVEL >= LOG_ERROR) {
        log(txt);
    }
}
var roles = [];
function clearRoles() {
    roles = [];
    if (typeof(app) !== 'undefined') {
        app.resetRoles();
    }

}
function loadRole( role ) {
    roles.push(role);
    if (typeof(app) !== 'undefined') {
        app.addRole(role.name, role.id);
    }
}
function loadRoles() {
    $.post('/asrs/other/getUserRoles', {
    }, function(sinfo) {
        if (sinfo.invalidUser) {
            logout();
            // logout();
        } else {
            // setUserName(sinfo.userId);
            debug('Assigning roles');
            clearRoles();
            sinfo.roles.forEach(loadRole);
            roles.forEach( function(e) { debug(e.name+' -> '+e.id);});
            debug('Done assigning roles');
        }
    })
}
function heartBeat() {
    // debug('Firing heart beat');
    $.post('/asrs/other/heartBeat', {

    }, function(s) {
        if (s == null || typeof(s) === 'undefined' || typeof(s.invalidUser) === 'undefined') {
            error('heartBeat call completely failed.  Logging out!');
            logout();
        } else if (s.invalidUser === true) {
            logout();
        } else {
            verbose('Heartbeat successfully fired');
            displayTime(new Date(s.stamptime));
            // debug('Got back from heartBeat function call!');
            setTimeout(heartBeat,10000);
        }
    })
}

function setSelectedRole( roleName, roleId ) {
    debug('User selected '+roleName+'('+roleId+')');
    $.post( '/asrs/other/setSelectedRole', {
        userId: userId,
        selectedRoleId: roleId
    }, function( sinfo ) {
        if (sinfo.invalidUser) {
            logout();
        }
    });
}

function reportSecureChannelActivity() {
    debug('Observed activity within CAIL subprocess');
    resetTimer();
}

function getLocalStorage() {
    var storage = localStorage;
    if (typeof(storage) === 'undefined' || storage === null) {
        debug('localStorage still doesnt exist');
        storage = sessionStorage;
    }
    return storage;
}
function setLocalValue( key, value ) {
    var storage = getLocalStorage();
    if (typeof(storage) !== 'undefined' && storage !== null) {
        debug('Storing user selection for '+key);
        if (typeof(value) === 'undefined' || value === null) {
            storage.removeItem(key);
        } else {
            storage.setItem(key, value);
        }
    } else {
        debug('sessionStorage is not available either!');
    }
}
function getLocalValue( key, defaultValue ) {
    var storage = getLocalStorage();
    var retVal = defaultValue;
    if (typeof(storage) !== 'undefined' && storage !== null) {
        // debug('Retrieving user selection for '+key);
        retVal = storage.getItem(key);
        if (typeof(retVal) === 'undefined' || retVal === null || retVal === 'undefined') {
            retVal = defaultValue;
        }
    }
    return retVal;
}

/* New section for global "PKStation popup" data and functions. */
var globalCurrentPKStation = "";

var prevMap = {
    PK1 : 'PK4',
    PK2 : 'PK1',
    PK3 : 'PK2',
    PK4 : 'PK3'
};
var nextMap = {
    PK1 : 'PK2',
    PK2 : 'PK3',
    PK3 : 'PK4',
    PK4 : 'PK1'
};
function globalShowPrevPKStation() {
    showPKStationPopupNameChanged(prevMap[globalCurrentPKStation]);
}
function globalShowNextPKStation() {
    showPKStationPopupNameChanged(nextMap[globalCurrentPKStation]);
}
function getPKStationArray( infoServicePKArray ) {
    var newPKStationArray = {};
    for (var x = 0; x < infoServicePKArray.length; x++) {
        var pkName = infoServicePKArray[x].station;
        newPKStationArray[pkName] = infoServicePKArray[x];
    }
    return newPKStationArray;
}
var pkStationPopupCallback = null;
var pkStationButtonText = null;
var pkStationButtonTitle = null;
var pkStationFunctionToCall = null;
function showPKStationPopupWithoutCallback(pknum) {
    pkStationPopupCallback = null;
    pkStationButtonText = null;
    pkStationButtonTitle = null;
    pkStationFunctionToCall = null;
    showPKStationPopupNameChanged(pknum);
}
function showPKStationPopupWithCallback(pknum, callback, buttonText, buttonTitle, functionToCall, allowPKStationArrows) {
    pkStationPopupCallback = callback;
    pkStationButtonText = buttonText;
    pkStationButtonTitle = buttonTitle;
    pkStationFunctionToCall = functionToCall;
    if (allowPKStationArrows) {
        $('#GleftArrow').show();
        $('#GrightArrow').show();
    } else {
        $('#display').hide();
        $('#GrightArrow').hide();
    }
    showPKStationPopupNameChanged(pknum);
}
function showPKStationPopupNameChanged(pknum) {
    globalCurrentPKStation = pknum;
    var xmlHttp;
    xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange=function() {
        if (xmlHttp.readyState===4) {
            if (xmlHttp.status===200) {
                debug('Got back from call to Lite from showPKStationPopup');
                var sinfo = JSON.parse(xmlHttp.response);
                pkStation = getPKStationArray( sinfo.pickInfo.pkArray );
                renderPKStation(globalCurrentPKStation);
                if (pkStationPopupCallback !== null) {
                    pkStationPopupCallback(pkStation, sinfo, pknum);
                }
                var modal = document.getElementById("GpkstationModal");
                modal.style.display = "block";
                displayTime(new Date(sinfo.stamptime));

            }
        }
    };

    xmlHttp.open("POST","/asrs/other/lite",true);
    xmlHttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xmlHttp.send("timestamp=0&pickDetail=false&currentPKStation="+globalCurrentPKStation);
}
function globalHidePKStationPopupPlease() {
    globalCurrentPKStation = "";
    var modal = document.getElementById("GpkstationModal");
    modal.style.display = "none";
}
function globalHidePKStationPopup(event) {
    if (event.target.id === "GpkstationModal" ||
        event.target.id === "Gpkstation-label-area" ||
        event.target.id === "GPKStationLabel" ||
        event.target.id === "GhideIt") {
        globalCurrentPKStation = "";
        var modal = document.getElementById("GpkstationModal");
        modal.style.display = "none";
    }
}
function stripPKNum( pkStationName ) {
    var pk = pkStationName.toLowerCase();
    return pk.match("pk[1-4]([1-3]f|[0-9]t)") ? pk.substring(0,2)+pk.substring(3) : null;
}
function unstripPKNum( pkStation, shortPkStandName ) {
    return pkStation+shortPkStandName.substring(2).toUpperCase();
}

var palletListTable;
var palletListTableIndex = 0;
var pkStationIndexArray = ["pk1f", "pk2f", "pk3f", "pk1t", "pk2t", "pk3t", "pk4t", "pk5t", "pk6t", "pk7t", "pk8t", "pk9t", "pk0t" ];
var imageArray = {};
var pkStationStateArray = {};
function buildMultiStateStation( stateName, prefix, targetDiv ) {
    var div = document.getElementById(targetDiv);
    for ( var x = 0; x < pkStationIndexArray.length; x++) {
        var station = prefix+pkStationIndexArray[x];
        var root = pkStationStateArray[station];
        if (typeof(root) === 'undefined' || root === null) {
            root = {};
            pkStationStateArray[station] = root;
            verbose("Added station "+station);
            // Since this is the first reference to this station, add the single text element
            var textName = station+'Text';
            var textElem = document.createElement('div');
            textElem.setAttribute('id', textName);
            textElem.setAttribute('class', textName);
            textElem.textContent = '';
            div.appendChild(textElem);
            root['text'] = textElem;
            root['images'] = {};
        }
        var map = root['images'];
        var img = document.createElement('img');
        img.setAttribute('id', station+stateName);
        img.setAttribute('alt', station+stateName);
        img.setAttribute('class', 'hide-away');
        img.setAttribute('name', station);
        img.setAttribute('src', imageArray[stateName]);
        div.appendChild(img);
        map[stateName] = img;
        verbose("Added station "+station+" ("+stateName+")");
    }

}
// var loadImageCallbackStack = null;
// function setLoadImageCallbackStack( stack ) {
//     loadImageCallbackStack = stack;
// }
function globalLoadImages( targetDiv, prefix, loadImageCallbackStack ) {
    Object.keys(standStates).forEach( function (standStateKey) {

        var img = new Image();
        img.id = standStateKey;
        img.name = standStateKey;
        img.src = standStates[standStateKey];
        img.onload = function() {
            imageArray[this.name] = this.src;
            // apply this new image to the 13 instances
            debug(this.name+" image loaded");
            buildMultiStateStation(this.name, prefix, targetDiv);
            if (Object.keys(imageArray).length >= Object.keys(standStates).length) {
                debug("Images Pre-loaded - kicking off loadEverything with call-next-proc of logLogin");
                callTheNextFunctionOnCallbackStack(loadImageCallbackStack);
            }
        };
        img.onerror = function() {
            debug("Image "+img.id+" ERROR!");
        };
        img.onabort = function() {
            debug("Image "+this.id+" aborted!");
        };
        img.onstalled = function() {
            debug("Image "+this.id+" stalled!");
        };
        img.onsuspend = function() {
            debug("Image "+this.id+" suspended!");
        };
    });

}
var standStates = {
    MOVE : 'MovePending.png',
    PICK : 'PickPresent.png',
    REJECT : 'Rejectoid.png',
    EMPTY : 'Empty5.png',
    FULL : 'OccupiedStand.png',
    INV : 'Inventory.png'
};
var standStateKeys = {
    MOVE : 'MOVE',
    PICK : 'PICK',
    REJECT : 'REJECT',
    EMPTY : 'EMPTY',
    FULL : 'FULL',
    INV : 'INV'
};


function processPopupPallet( pallet ) {
    verbose("Processing pallet "+pallet.palletId);
    var row = palletListTable.insertRow(++palletListTableIndex);
    row.className = "GlerEvalAll GlerEvalRow";
    var cell = row.insertCell(0);
    cell.className = "GlerEvalAll";
    cell.innerHTML = pallet.palletId;
    cell = row.insertCell(1);
    cell.className = "GlerEvalAll";
    cell.innerHTML = pallet.shortLoc;
    cell.title = pallet.curLoc;
    cell = row.insertCell(2);
    cell.className = "GlerEvalAll";
    cell.innerHTML = pallet.status;
    var pkNum = stripPKNum(pallet.curLoc);
    if (pkNum !== null && pallet.curLoc.startsWith(globalCurrentPKStation)) {
        var root = pkStationStateArray['popup-'+pkNum];
        root.text.textContent = pallet.palletId;

        var status = standStateKeys.FULL;
        if (pallet.status === "Moving" || pallet.status.startsWith("to:")) {
            status = standStateKeys.MOVE;
        } else if (pallet.status=== "PickReady") {
            status = standStateKeys.PICK;
        } else if (pallet.status === "Inventory") {
            status = standStateKeys.INV;
        } else if (pallet.status === "Rejected") {
            status = standStateKeys.REJECT;
        } else if (pallet.status.endsWith("Empty") || pallet.palletId === "BLK") {
            status = standStateKeys.EMPTY;
        }
        root.images.EMPTY.setAttribute("class", "hide-away");
        var target = root.images[status];
        target.setAttribute('class', 'popup-'+pkNum);
    }
    // debug("Finished with pallet "+pallet.palletId);
}
function assignStandAction(x, onClick, pkName, palletId) {
    $(x).off("click"); //resets click action
    $(x).click(onClick);
    $(x).data('pkName', pkName);
    $(x).data('palletId', palletId);
}
function reallyClearIt(originalPkName, pkName, emptyStandAction) {
    verbose('Clearing it for '+pkName);
    var base = pkStationStateArray[pkName];
    base.text.textContent = "";
    Object.keys(base.images).forEach( function(key) {
        var obj = base.images[key];
        var clz = "hide-away";
        if (obj.getAttribute("id").endsWith("EMPTY")) {
            clz = obj.getAttribute("name");
            if (typeof(emptyStandAction) === 'function') {
                assignStandAction(obj, emptyStandAction, originalPkName, "");
            }
        }
        obj.setAttribute("class", clz);
    });
}
function clearPopup(pkName) {
    reallyClearIt(pkName, 'popup-'+pkName);
}
function clearPrimary(pkName, emptyStandAction) {
    reallyClearIt(pkName, 'primary-'+pkName, emptyStandAction);
}

function renderPKStation(pknum) {
    debug("Rendering PKStation "+pknum);
    var pk = pkStation[pknum];
    var loads = +pk.loadsEnroute.split(" ")[0];
    var arraySize = pk.palletArray.length;
    var calcSize = arraySize;
    document.getElementById("GPKStationLabel").textContent = pknum;
    var ler = document.getElementById("GrecalculateLoadsEnroute");
    var palletsHere = 0;
    var singleStandDiscrepancyFound = false;
    pk.palletArray.forEach( function(p) {
        if (p.palletId === 'BLOCKED') {
            singleStandDiscrepancyFound = true;
            calcSize--;
        } else if (p.shortLoc === pknum) {
            palletsHere++;
            if (p.palletId.startsWith("(")) {
                singleStandDiscrepancyFound = true;
            }
        }
    }, this );
    ler.style.fontWeight = 'bold';
    ler.disabled = false;
    if (pkStationFunctionToCall === null) {
        ler.style.backgroundColor = 'darkorange';
        ler.onclick = function () {
            recalc(pknum, loads, calcSize, singleStandDiscrepancyFound ? 1 : 0);
        };
        if (loads === calcSize) {
            if (!singleStandDiscrepancyFound) {
                clearRecalcButton();
            }
            if (calcSize > 13) {
                ler.style.backgroundColor = 'red';
                ler.title = "The system shows "+palletsHere+" stands occupied\n"+
                    "and "+(calcSize - palletsHere)+" pallets on their way.\n"+
                    "This exceeds this station's 13 stands by "+(calcSize-13)+".\n"+
                    "If vehicles are looping you may have to redirect them elsewhere."+
                    (!singleStandDiscrepancyFound ? "" : "\nPress Recalculate to fix any single stand loads en route problems.");

            } else {
                ler.title = "The system shows "+palletsHere+" stands occupied\n"+
                    "and "+(calcSize - palletsHere)+" pallets on their way.\n"+
                    (!singleStandDiscrepancyFound ?
                        "There's no need to recalculate at this time." :
                        "There are one or more individual stand Loads En Route discrepancies.\nClick to correct these.");
            }
        } else {
            ler.title = "Stand shows "+loads+" Loads En Route\n"+
                "However, the system shows "+palletsHere+" stands occupied\n"+
                "and "+(calcSize - palletsHere)+" pallets on their way.\n"+
                (!singleStandDiscrepancyFound ? "" : "There are also one or more individual stand Loads En Route discrepancies.\n")+
                "Click this button to correct the discrepancy.";
        }
    } else {
        ler.style.backgroundColor = '#4ac6a2';
        ler.value = pkStationButtonText;
        ler.title = pkStationButtonTitle;
        ler.onclick = pkStationFunctionToCall;
        ler.classList.add('clickMe');
    }

    palletListTable = document.getElementById("GPalletListTable");
    palletListTableIndex = 0;
    while (palletListTable.rows.length > 1) {
        palletListTable.deleteRow(1);
    }
    verbose('Deleted table rows.  Now on to the forEach');
    pkStationIndexArray.forEach( clearPopup );

    for (x = 0; x < pk.palletArray.length; x++) {
        processPopupPallet(pk.palletArray[x]);
    }
}

function getOrSelectBarcodePrinter() {
    return getOrSelectPrinter('BarCode');
}
function getOrSelectTicketPrinter() {
    return getOrSelectPrinter('Ticket');
}
function selectPrinter(printerType) {
    var selected = getLocalValue(printerType, null);
    debug('Printer: '+printerType+' was: '+selected);
    if (isAppPresent() && typeof(app) !== 'undefined') {
        that = $('#selectPrinter');
        that.data("printerType", printerType);
        var str = app.getPrinterList();
        var printerList = eval(str);
        var pfs = document.getElementById('printerFieldSet');
        pfs.innerHTML = ''; //eliminate any previous children
        var legend = document.createElement('legend');
        legend.setAttribute('id', 'printerSelectDescription');
        legend.setAttribute('align', 'right');
        legend.classList.add('legend-hairy');
        legend.innerText = 'Select '+printerType+' Printer';
        pfs.appendChild(legend);
        var idx = 0;
        printerList.forEach( function(printer) {
            idx++;
            var label = document.createElement('label');
            var id = 'printer'+idx;
            label.setAttribute('for', id);
            label.innerText = printer;
            that.data(id, printer);
            pfs.appendChild(label);
            var input = document.createElement("input");
            var isCurrentSelection = selected === null ? idx === 1 : selected === printer;
            if (isCurrentSelection) {
                debug('Selecting '+printer);
                input.setAttribute('checked', 'true');
            } else {
                debug( 'NOT selecting '+printer);
            }
            input.setAttribute('type', 'radio');
            input.setAttribute('name', 'printer');
            input.setAttribute('id', id);
            input.classList.add('input-spacer');
            pfs.appendChild(input);
            pfs.appendChild(document.createElement('br'));
        });
        // var pp = document.getElementById('poopyPaster');
        // pp.value = pfs.innerHTML;
        // debug("PP:"+pp.value);
        // pp.select();
        // document.execCommand("copy");

        // debug('Generated HTML: "'+pfs.innerHTML+'"');
        that.dialog('open');
    }
}
function getOrSelectPrinter(printerType) {
    var selected = getLocalValue(printerType, null);
    if (typeof(selected) === 'undefined' || selected === null) {
        debug('Selecting printer!');
        selectPrinter(printerType);
    }
    return selected;
}
$('#selectPrinter').dialog( {
    autoOpen: false,
    title: 'Select Printer',
    modal: true,
    width: 'auto',
    height: 650,
    buttons: [
        {
            text: "OK",
            click: function() {
                var msg = "Printer selected";
                var options = $("#selectPrinter input[name='printer']:checked")[0].id;
                var printer = $(this).data(options);
                if ( printer === 'None' ) {
                    debug('Setting printer to NULL');
                    printer = null;
                }
                if (isAppPresent() && typeof(app) !== 'undefined') {
                    msg = app.setSelectedPrinter(printer);
                }
                var key = $(this).data('printerType');
                setLocalValue(key,printer);
                debug(key+" is now "+printer);
                debug('Closing #selectPrinter');
                $(this).dialog('close');
                if (msg !== null) {
                    displayMessage(msg);
                }
            }

        },
        {
            text: 'Cancel',
            click: function() {
                $(this).dialog('close');
            }
        }
    ]
});

$('#displayGenericMessage').dialog( {
    autoOpen: false,
    modal: true,
    width: 600,
    maxHeight: 650,
    overflow: 'auto',
    open: function() {
        var it = $('#displayGenericMessage');
        var tit = it.data('title');
        it.dialog('option', 'title', typeof(tit) === 'undefined' ? 'Info' : tit);
    },
    buttons: [
        {
            text: "OK",
            click: function() {
                $(this).dialog('close');
            }
        }
    ]
});
function displayMessage(message, title) {
    $('#genericMessage').html(message);
    var it = $('#displayGenericMessage');
    it.data('title', title);
    it.dialog('open');
}
function setAppTitleDirectly(str) {
    if (typeof(app) !== 'undefined' &&
        typeof(app.setTitle !== 'undefined')) {
        app.setTitle(str);
    }

}
const displayErrorTag = $('#displayError');
displayErrorTag.dialog( {
    autoOpen: false,
    title: 'Error Encountered',
    modal: true,
    buttons: [
        {
            text: 'OK',
            click: function() {
                $(this).dialog('close');
            }
        }
    ]
});

function displayError(shortMessage, detailed) {
    if (displayErrorTag.length) {
        let ems = $('#errorMessageShort');
        if (ems.length) {
            ems.val(shortMessage);
        }
        let emd = $('#errorMessageDetail');
        if (emd.length) {
            emd.val(detailed);
        }
        displayErrorTag.dialog('open');
    }
}