NAV
Projects · Sims · Log · SciPK · About    (logo returns home)

TEMPLATES
Only three: home, index grid, detail page. Every other page derives from one.

RESPONSIVE
Single breakpoint at 768px. Grid collapses to one column.
Telemetry headers wrap rather than truncate.

BRAND CONTEXT
Personal portfolio for an aerospace GNC engineer. Visual language comes from
MATLAB figures and ground-station telemetry, not sci-fi. No starfields, no
nebula gradients, no rocket clipart. Loosely consistent with the SciPK YouTube
channel, whose palette derives from Manchester City.

COLOR
--bg-base        #080A11   page ground
--bg-surface     #101728   cards, panels
--bg-raised      #1C2C5B   brand navy, elevated panels and active states
--accent         #6CABDD   brand sky blue — links, primary actions, data lines
--highlight      #F0A63C   amber — active nav, key figures, callouts
--text-primary   #FFFFFF
--text-secondary #9FB0C7
--hairline       rgba(108,171,221,0.20)

TYPE
Headings, labels, metadata, tags: IBM Plex Mono 600
Body: IBM Plex Sans 400
Scale (4 sizes only): 11px uppercase mono labels, +0.08em tracking / 16px body,
1.6 line-height / 24px section heads / 44px page titles

SPACING
8px base unit. Steps: 8 / 16 / 24 / 48 / 96.

COMPONENTS
1px hairline borders, 2px corner radius, no drop shadows, no gradients.
Project cards carry a monospace telemetry header:
  AE-403W · SPR 2026 · AUTONOMY · MATLAB/SIMULINK
Images get bracket-corner reticle framing and a FIG. N caption in 11px mono.
Background carries a graph-paper hairline grid at very low opacity.
Real control-theory plots (pole-zero map, root locus, Bode phase) appear as
faint section dividers and hero background elements.