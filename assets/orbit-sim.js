/* ============================================================
   SIM-01 — Two-body orbit sketch
   Solves the conic from four Keplerian elements, Earth at the focus.
   Mounts into every <div data-orbit-sim> on the page.
   ============================================================ */
(function () {
    'use strict';

    var MU = 398600.4418;   // km^3/s^2
    var RE = 6378.137;      // km
    var CX = 230, CY = 170; // viewBox centre

    var rad = function (d) { return d * Math.PI / 180; };

    function markup(status, note) {
        return '' +
        '<div class="telemetry">' +
            '<span class="code">TWO-BODY ORBIT · EQUATORIAL PLANE</span>' +
            '<span>' + status + '</span>' +
        '</div>' +
        (note ? '<p>' + note + '</p>' : '') +
        '<div class="sim-body">' +
            '<div class="sim-main">' +
                '<div class="sim-plot">' +
                    '<svg viewBox="0 0 460 340" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Orbit conic with Earth at the focus">' +
                        '<path data-axes stroke="#6CABDD" stroke-width="1" opacity="0.18" fill="none"></path>' +
                        '<path data-apsis stroke="#9FB0C7" stroke-width="1" stroke-dasharray="3 4" fill="none" opacity="0.7"></path>' +
                        '<polyline data-orbit fill="none" stroke="#6CABDD" stroke-width="1.6"></polyline>' +
                        '<circle data-earth fill="#1C2C5B" stroke="#6CABDD" stroke-width="1"></circle>' +
                        '<circle data-craft r="4.5" fill="#F0A63C"></circle>' +
                    '</svg>' +
                    '<span class="plot-note">EARTH AT FOCUS · VIEW AUTO-SCALED</span>' +
                '</div>' +
                '<div class="sim-readouts">' +
                    '<div>PERIAPSIS ALT <output data-hp></output> KM</div>' +
                    '<div>APOAPSIS ALT <output data-ha></output> KM</div>' +
                    '<div>PERIOD <output data-period></output> MIN</div>' +
                '</div>' +
                '<div class="sim-warn" data-warn hidden>PERIAPSIS BELOW SURFACE · CONIC INTERSECTS EARTH</div>' +
            '</div>' +
            '<div class="sim-controls">' +
                control('a', 'a · SEMI-MAJOR AXIS', 7000, 42164, 100, 14000, ' km') +
                control('e', 'e · ECCENTRICITY', 0, 0.8, 0.01, 0.35, '') +
                control('w', 'ω · ARG. OF PERIAPSIS', 0, 359, 1, 40, '°') +
                control('nu', 'ν · TRUE ANOMALY', 0, 359, 1, 120, '°') +
            '</div>' +
        '</div>';
    }

    function control(key, label, min, max, step, value, unit) {
        var id = 'orbit-' + key + '-' + Math.random().toString(36).slice(2, 8);
        return '' +
        '<div class="control">' +
            '<div class="control-head">' +
                '<label for="' + id + '">' + label + '</label>' +
                '<output data-out="' + key + '"></output>' +
            '</div>' +
            '<input id="' + id + '" type="range" data-in="' + key + '" data-unit="' + unit + '"' +
                ' min="' + min + '" max="' + max + '" step="' + step + '" value="' + value + '">' +
        '</div>';
    }

    function mount(root) {
        root.innerHTML = markup(
            root.getAttribute('data-status') || 'LIVE · IN-BROWSER SOLVER',
            root.getAttribute('data-note') || ''
        );

        var q = function (sel) { return root.querySelector(sel); };
        var inputs = {
            a: q('[data-in="a"]'), e: q('[data-in="e"]'),
            w: q('[data-in="w"]'), nu: q('[data-in="nu"]')
        };
        var out = {
            a: q('[data-out="a"]'), e: q('[data-out="e"]'),
            w: q('[data-out="w"]'), nu: q('[data-out="nu"]'),
            hp: q('[data-hp]'), ha: q('[data-ha]'), period: q('[data-period]')
        };
        var svg = {
            axes: q('[data-axes]'), apsis: q('[data-apsis]'), orbit: q('[data-orbit]'),
            earth: q('[data-earth]'), craft: q('[data-craft]')
        };
        var warn = q('[data-warn]');

        function draw() {
            var a = Number(inputs.a.value);
            var e = Number(inputs.e.value);
            var w = Number(inputs.w.value);
            var nu = Number(inputs.nu.value);

            var b = a * Math.sqrt(1 - e * e);
            var cw = Math.cos(rad(w)), sw = Math.sin(rad(w));

            // fit the whole conic plus Earth inside the frame
            var hx = Math.max(Math.hypot(a * cw, b * sw), Math.abs(a * e * cw) + RE);
            var hy = Math.max(Math.hypot(a * sw, b * cw), Math.abs(a * e * sw) + RE);
            var scale = Math.min(200 / hx, 148 / hy);

            var ex = CX + a * e * scale * cw;
            var ey = CY - a * e * scale * sw;

            var rAt = function (v) { return (a * (1 - e * e)) / (1 + e * Math.cos(rad(v))); };
            var pt = function (v) {
                var r = rAt(v), t = rad(v + w);
                return [ex + r * Math.cos(t) * scale, ey - r * Math.sin(t) * scale];
            };

            var pts = [];
            for (var v = 0; v <= 360; v += 3) {
                var p = pt(v);
                pts.push(p[0].toFixed(1) + ',' + p[1].toFixed(1));
            }
            var pp = pt(0), pa = pt(180), sc = pt(nu);
            var rp = a * (1 - e), ra = a * (1 + e);

            svg.orbit.setAttribute('points', pts.join(' '));
            svg.apsis.setAttribute('d', 'M' + pp[0].toFixed(1) + ' ' + pp[1].toFixed(1) +
                                        ' L' + pa[0].toFixed(1) + ' ' + pa[1].toFixed(1));
            svg.axes.setAttribute('d', 'M20 ' + ey.toFixed(1) + ' H440 M' + ex.toFixed(1) + ' 20 V320');
            svg.earth.setAttribute('cx', ex.toFixed(1));
            svg.earth.setAttribute('cy', ey.toFixed(1));
            svg.earth.setAttribute('r', Math.max(RE * scale, 4).toFixed(1));
            svg.craft.setAttribute('cx', sc[0].toFixed(1));
            svg.craft.setAttribute('cy', sc[1].toFixed(1));

            out.a.textContent = String(a) + ' km';
            out.e.textContent = e.toFixed(2);
            out.w.textContent = String(w) + '°';
            out.nu.textContent = String(nu) + '°';
            out.hp.textContent = Math.round(rp - RE).toLocaleString('en-US');
            out.ha.textContent = Math.round(ra - RE).toLocaleString('en-US');
            out.period.textContent = (2 * Math.PI * Math.sqrt(Math.pow(a, 3) / MU) / 60).toFixed(0);

            warn.hidden = !(rp < RE);
        }

        Object.keys(inputs).forEach(function (k) {
            inputs[k].addEventListener('input', draw);
        });
        draw();
    }

    function init() {
        var nodes = document.querySelectorAll('[data-orbit-sim]');
        for (var i = 0; i < nodes.length; i++) mount(nodes[i]);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
}());
