# CONTENT.md — Site Structure & Content Inventory

Companion to `DESIGN.md` (visual system) and `CLAUDE.md` (working rules).
This file defines **what goes where**. `DESIGN.md` defines **what it looks like**.

Site: scipk.com · Repo: scipk/scipk.github.io · Host: GitHub Pages (serves `main`)

**Purpose of this site:** demonstrate to aerospace employers that Parham Khodadi can
do GNC engineering. Every structural decision below serves that. Content that
dilutes the GNC signal gets relocated, never deleted.

---

## 1. Navigation

```
[logo → home]   Projects · Sims · Log · SciPK · About
```

Five items, no dropdowns. The logo returns to the home page.

### Launch gating — cleared

Both Sims and Log are live in the nav.

| Item | Status |
|---|---|
| Sims | SIM-01, the two-body orbit sketch. Any further solver must be one Parham built himself — no generated simulations. |
| Log  | Three entries, authored from `log.json`. See §8. |

---

## 2. Page inventory

### Existing pages

| Path | Change |
|---|---|
| `/index.html` | Rebuild. See §4. |
| `/projects.html` | Rebuild as a 7-entry grid. See §3. |
| `/cv.pdf` | Keep. Untouched. The Résumé button on the home page links straight to it — there is no HTML résumé. |

### New pages

| Path | Contents |
|---|---|
| `/about.html` | Bio, credentials table, publications, CV download, contact. Personal interests (travel, soccer, Man City, Lakers) live here. |
| `/sims.html` | Interactive simulation index. |
| `/log.html` | Writing/updates feed, reverse chronological. Ships with an RSS feed at `/feed.xml`. |
| `/scipk.html` | Channel embed, best 4 videos, what the channel is about. |
| `/projects/GLACIER-Rendezvous.html` | **New project page — write from scratch.** See §3. |

---

## 3. Projects grid — 6 entries

Ordered by GNC relevance, not by date.

| # | Project | Path | Work needed |
|---|---|---|---|
| 1 | GLACIER Lab — Spacecraft Rendezvous Control | `/projects/GLACIER-Rendezvous.html` | **Does not exist.** Write from scratch. Currently the most relevant work on the site and it appears only as one sentence in the home page bio. Robust control for spacecraft rendezvous, GLACIER Lab, UCLA, under Prof. Shahriar Talebi. |
| 2 | BAM — Baseball Avoidance Multirotor (AE 403W) | `/projects/AE-403W.html` | Good bones. **Add quantified results:** detection latency, miss distance, success rate over N runs. The current result statement is qualitative only. |
| 3 | Spacecraft Design — AE 460 | `/projects/AE-460.html` | Foreground the **Flight Dynamics** role specifically. "Systems engineering" reads as generic; the GNC and orbit dynamics work is the point. |
| 4 | SPACE Lab Drone Autonomy | `/projects/Drone-Autonomy-SPACE-Lab.html` | **Rewrite required.** See §5. |
| 5 | Avionics Ground Systems | `/projects/RocketProject-Avionics.html` | Restyle only. Add a photo of the DAQ setup if one exists. |
| 6 | MPD Thruster | `/projects/mpd-thruster.html` | Restyle only. Earns its place by being unassigned personal work. |

**Resolved:** MATH 543 left the grid. It is listed on the About page under
Highlighted Courses; its page stays live at `/projects/MATH-543.html`.
The grid ships with 6 entries.

### Project detail page template

Every page in the grid follows the same section order:

1. **Problem** — what was being solved, with the constraint that made it hard
2. **Approach** — the method, with the governing equations where they exist
3. **My contribution** — explicit, separated from team output
4. **Result** — quantified. Numbers, plots, or a measured outcome.
5. **Code** — repo link, or an inline excerpt of the part worth reading

---

## 4. Home page

Order, top to bottom:

1. Name, one-line positioning, social links
2. **Two flagship projects** with a result image each (GLACIER + BAM)
3. Live embedded sim
4. Publications (AIAA SciTech 2026, with DOI)
5. Awards
6. One line on SciPK with a link to `/scipk.html`
7. Contact

**Removed from the home page:** YouTube video embeds (→ `/scipk.html`), personal
interests paragraph (→ `/about.html`).

**Do not** place a dated "Latest update" module in the hero. A hero reading
"Latest: March 2026" in September advertises abandonment. Recent Log entries
appear on `/log.html` only.

**Fix:** footer reads `© 2025`. Make it render the current year.

---

## 5. Relocations

Nothing is deleted. Every page below keeps its existing URL so inbound and
external links continue to resolve. Only its placement in the site changes.

### → About, "Credentials" table

Compact rows. No individual detail pages needed, though existing ones stay live.

| Item | Existing path |
|---|---|
| AGI Systems Tool Kit (STK) Level 3 | `/projects/STK.html` |
| Codecademy — C++, Python, Git, Linux, Linear Algebra | `/projects/Codecademy.html` |
| NASA L'SPACE MCA | `/projects/LSPACE-MCA.html` |
| NASA L'SPACE NPWEE | `/projects/LSPACE-NPWEE.html` |
| NASA NCAS ×3 | `/projects/NCAS.html` (site currently shows only one of the three — list all) |
| Tripoli L1 High Power Rocketry | `/projects/L1-Rocketry.html` |

### → About, "Publications"

| Item | Existing path |
|---|---|
| AIAA SDSU Student Branch History (SciTech 2026, DOI 10.2514/6.2026-2727) | `/projects/AIAA-SDSU-History.html` |

Stays prominent — it is a real conference paper. It leaves the projects grid
because it is not engineering work and dilutes a grid that should read as pure GNC.

### → SciPK page

| Item | Existing path |
|---|---|
| SciPK YouTube Channel | `/projects/SciPK-YouTube.html` |

### → About, “Highlighted Courses” table

| Item | Existing path |
|---|---|
| Experimental Aerodynamics — AE 303 | `/projects/AE-303.html` |
| Numerical Matrix Analysis — MATH 543 | `/projects/MATH-543.html` |

Name, school, and term only — no descriptions.

**Net effect:** 15 grid entries → 6. Zero pages deleted.

---

## 6. SPACE Lab page — required rewrite

The current description claims ORB-SLAM3, SLAM, and sensor fusion. The ORB-SLAM3
integration was attempted in mid-2024 and abandoned over incompatible Python
bindings. It is not working experience, and the claim will not survive a technical
interview question.

**Rewrite the description around what was actually built:** QR-fiducial detection
and relative pose estimation on a DJI Tello EDU, in Python with OpenCV.

**Handle the ORB-SLAM3 work honestly** as an integration effort that failed on
tooling incompatibility. That is a legitimate engineering account and costs nothing.

**Remove these tags:** `SLAM (Simultaneous Localization and Mapping)`, and
`sensor fusion` unless fusion was genuinely implemented.

---

## 7. Rules for implementation

- Never delete a file. Move it and leave a redirect stub.
- Never rewrite prose content on project pages except where §5 or §6 requires it.
  Restyle only.
- Never touch `/files/` or `/images/`.
- Preserve every existing URL. Nothing may 404.
- GitHub Pages has no server-side redirects. Any moved page needs a stub at the
  old path with a `<meta http-equiv="refresh">`.
- One page per commit. Commit, do not push.
- Three templates only: home, index grid, detail page. Every other page derives
  from one of them.

---

## 8. Log workflow

`log.json` is the only place a log entry exists. `log.html` and `feed.xml` are
both generated from it, so an entry is never written twice and the page and the
feed can never drift apart.

```bash
python3 tools/log.py
```

Opens a page in the browser listing every entry:

- **Add** — the form at the top. Date and message are required; title and tags optional.
- **Edit** — on any entry. Change date, title, message, or tags.
- **Delete** — on any entry, behind a confirm.

Every change writes to `log.json` and immediately rebuilds `log.html` and
`feed.xml`. Then commit and push.

`python3 tools/log.py --rebuild` regenerates both files without the browser — use
it after hand-editing `log.json`.

### Entry ids

Each entry carries a stable `id`, minted once from its title when it is created
and never changed afterwards. The id is the entry's `#anchor` on `log.html` and
its `<guid>` in the feed, so **renaming an entry later cannot break its permalink
or make RSS readers show it twice.** Do not edit an `id` by hand.

**Never edit `log.html` or `feed.xml` directly.** Everything between the
`LOG:ENTRIES` and `LOG:ITEMS` marker comments is overwritten on every rebuild.
Everything outside those markers — the page chrome, the channel metadata — is
yours to edit and is left alone.
