/* Footer copyright year — rendered so it never goes stale. */
(function () {
    'use strict';
    var y = String(new Date().getFullYear());
    var nodes = document.querySelectorAll('[data-year]');
    for (var i = 0; i < nodes.length; i++) nodes[i].textContent = y;
}());
