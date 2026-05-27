


### Prompt 1 — create \"Platform Capabilities\" Section Exactly

Write a React component named `Capabilities` using TypeScript, TailwindCSS, and Framer Motion (`motion` and `useInView`). Import `useState` and `useRef` from React.

Define a const array `capabilities` with exactly 3 objects in this exact order:

1. `{ title: 'Anomaly Detection', description: 'Real-time sub-millisecond anomaly detection across every sensor stream. Identifies deviations before they propagate.', image: 'https://readdy.ai/api/search-image?query=Close-up of industrial CNC machine sensors and monitoring equipment with glowing cyan LED indicators in a dark high-tech factory environment, cinematic lighting, dark background with subtle grid lines, ultra-premium manufacturing aesthetic&width=600&height=800&seq=1&orientation=portrait', status: 'LIVE' }`

2. `{ title: 'Wear Prediction', description: 'Predictive modeling that forecasts tool degradation, surface finish decay, and optimal replacement windows.', image: 'https://readdy.ai/api/search-image?query=Macro photography of precision cutting tool tip with microscopic wear patterns visible, dark industrial background with cyan and violet accent lighting, ultra sharp detail, premium manufacturing aesthetic, cinematic depth of field&width=600&height=800&seq=2&orientation=portrait', status: 'PREDICTIVE' }`

3. `{ title: 'Crisis Scoring', description: 'Intelligent spare-parts inventory scoring that predicts supply-chain disruptions and flags critical shortage risks.', image: 'https://readdy.ai/api/search-image?query=Industrial crisis management dashboard interface with glowing red and amber alert indicators on dark background, holographic data overlays, supply chain visualization nodes connected by light lines, premium dark UI aesthetic&width=600&height=800&seq=3&orientation=portrait', status: 'CRITICAL' }`

The component default-export function uses `useState(0)` for `activeIndex` and `useRef(null)` for `ref`. Then `useInView(ref, { once: true, margin: '-80px' })` for `inView`.

The returned JSX root is a `<section>` with `id=\"capabilities\"`, `ref={ref}`, and classes: `relative w-full py-28 md:py-36 bg-yefai-black overflow-hidden`. The exact background color must be `#050508` (mapped as `bg-yefai-black` in Tailwind config).

Inside the section, first place a `<div>` with classes `absolute inset-0 grid-bg opacity-15`. This is a CSS grid pattern background at 15% opacity.

Then place an ambient glow `<div>` with classes `absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-cyan-500/[0.015] rounded-full blur-[150px]`.

Then a content wrapper `<div>` with classes `relative z-10 max-w-7xl mx-auto px-6 md:px-10`.

Inside that wrapper, place a `<motion.div>` with these exact props:
- `initial={{ opacity: 0, y: 30 }}`
- `animate={inView ? { opacity: 1, y: 0 } : {}}`
- `transition={{ duration: 0.7 }}`
- `className=\"mb-16 md:mb-20\"`

Inside this motion.div, place an `<h2>` with class `text-3xl md:text-5xl lg:text-6xl font-bold text-white leading-tight`. Its text content is exactly: `Platform Capabilities`. Immediately after the text (no space, inline), append a `<span>` with class `inline-block ml-3 text-cyan-400 text-2xl md:text-4xl align-middle`. Inside that span, place an `<i>` with className `ri-focus-3-line`.

Below the h2, place a `<p>` with class `mt-4 text-base md:text-lg text-white/35 max-w-xl font-light`. Its exact text is: `Three core pillars of autonomous manufacturing intelligence. Each deployed at machine speed, each trained on industrial-scale telemetry.`

Below the header motion.div, create a flex container `<div>` with class `flex flex-col md:flex-row gap-4 md:gap-5`. Map over the `capabilities` array. For each `cap` and `index`:

Return a `<motion.div>` with:
- `key={cap.title}`
- `initial={{ opacity: 0, y: 40 }}`
- `animate={inView ? { opacity: 1, y: 0 } : {}}`
- `transition={{ duration: 0.6, delay: 0.15 * index }}`
- `onMouseEnter={() => setActiveIndex(index)}`
- `className={`relative rounded-2xl overflow-hidden cursor-pointer transition-all duration-700 ease-out ${isActive ? 'md:flex-[2]' : 'md:flex-1'}`}` where `isActive = activeIndex === index`
- `style={{ minHeight: '420px' }}`

Inside each card, place these children in this exact order:

1. **Background Image container:** `<div className=\"absolute inset-0\">` containing an `<img>` with `src={cap.image}`, `alt={cap.title}`, `className=\"w-full h-full object-cover transition-transform duration-700 ease-out\"`, and inline style `style={{ transform: isActive ? 'scale(1.05)' : 'scale(1)' }}`.

2. **Gradient Overlay 1:** `<div className=\"absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent\" />`

3. **Gradient Overlay 2:** `<div className=\"absolute inset-0 bg-gradient-to-r from-black/30 to-transparent\" />`

4. **Status Badge:** `<div className=\"absolute top-5 right-5 z-20\">` containing a `<span>` with inline-flex, gap-1.5, px-3 py-1, rounded-full, text-[10px], tracking-widest, uppercase, font-semibold, border, backdrop-blur-sm. The conditional classes must be exactly:
- If `cap.status === 'LIVE'`: `bg-emerald-500/10 border-emerald-400/30 text-emerald-400`
- Else if `cap.status === 'PREDICTIVE'`: `bg-cyan-500/10 border-cyan-400/30 text-cyan-400`
- Else: `bg-amber-500/10 border-amber-400/30 text-amber-400`

Inside the badge span, place a small dot `<span>` with `w-1.5 h-1.5 rounded-full` and conditional classes:
- If `cap.status === 'LIVE'`: `bg-emerald-400 animate-pulse`
- Else if `cap.status === 'PREDICTIVE'`: `bg-cyan-400 animate-pulse`
- Else: `bg-amber-400 animate-pulse`

Then the status text `{cap.status}`.

5. **Content container:** `<div className=\"absolute bottom-0 left-0 right-0 p-6 md:p-8 z-20\">` containing:
   - An `<h3>` with conditional class: if `isActive` then `text-2xl md:text-3xl`, else `text-xl md:text-2xl`. Both have `font-bold text-white transition-all duration-500`. Content: `{cap.title}`.
   - A `<motion.p>` with `initial={false}`, `animate={{ opacity: isActive ? 1 : 0.5, height: isActive ? 'auto' : '48px' }}`, class `mt-3 text-sm md:text-base text-white/50 font-light leading-relaxed overflow-hidden`. Content: `{cap.description}`.
   - If `isActive` is true, render a `<motion.div>` with `initial={{ opacity: 0, y: 10 }}`, `animate={{ opacity: 1, y: 0 }}`, `transition={{ duration: 0.4 }}`, class `mt-5 flex items-center gap-2`. Inside it: a `<span>` with text `Learn more` and class `text-sm font-medium text-cyan-400`, followed by an `<i>` with class `ri-arrow-right-line text-cyan-400 text-sm`.

Export the component as default.

---

### Prompt 2 — create \"Dashboard Preview\" Section Exactly

Write a React component named `DashboardPreview` using TypeScript, TailwindCSS, and Framer Motion (`motion` and `useInView`). Import `useRef` and `useState` from React.

Define a const array `dashboards` with exactly 4 objects in this exact order:

1. `{ title: 'Live Telemetry', subtitle: 'Real-time spindle temperature, vibration, and load monitoring across all active units.', image: 'https://readdy.ai/api/search-image?query=Industrial telemetry dashboard UI with real-time sensor data charts in dark mode, glowing cyan line graphs and gauges on deep navy background, premium futuristic manufacturing control panel aesthetic, holographic data overlays&width=700&height=500&seq=4&orientation=landscape', status: 'LIVE' }`

2. `{ title: 'Predictive Analytics', subtitle: 'Wear trajectory modeling with confidence intervals and replacement scheduling.', image: 'https://readdy.ai/api/search-image?query=Predictive analytics dashboard with forecast curves and probability charts in dark futuristic UI, violet and cyan gradient data visualization, manufacturing intelligence platform interface, deep navy background&width=700&height=500&seq=5&orientation=landscape', status: 'PREDICTIVE' }`

3. `{ title: 'Tool Wear Monitor', subtitle: 'Microscopic degradation tracking with automated alert thresholds and wear-rate scoring.', image: 'https://readdy.ai/api/search-image?query=Tool wear monitoring dashboard with microscopic surface analysis visualization, dark industrial UI with amber and red alert zones, precision manufacturing quality control interface, futuristic dark mode design&width=700&height=500&seq=6&orientation=landscape', status: 'CRITICAL' }`

4. `{ title: 'Crisis Overview', subtitle: 'Supply-chain disruption scoring, inventory gaps, and emergency procurement pipeline.', image: 'https://readdy.ai/api/search-image?query=Crisis management dashboard with supply chain network map visualization, red alert indicators on dark background, inventory shortage warnings, industrial operations command center UI, premium dark theme&width=700&height=500&seq=7&orientation=landscape', status: 'CRITICAL' }`

The component uses `useRef<HTMLDivElement>(null)` for `scrollRef`, `useRef(null)` for `sectionRef`. `useInView(sectionRef, { once: true, margin: '-80px' })` for `inView`. `useState(false)` for `canScrollLeft`, `useState(true)` for `canScrollRight`.

Define a `checkScroll` function that, if `scrollRef.current` exists, destructures `{ scrollLeft, scrollWidth, clientWidth }` from it, then calls `setCanScrollLeft(scrollLeft > 10)` and `setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 10)`.

Define a `scroll(dir: 'left' | 'right')` function that, if `scrollRef.current` exists, computes `const amount = scrollRef.current.clientWidth * 0.8`, then calls `scrollRef.current.scrollBy({ left: dir === 'left' ? -amount : amount, behavior: 'smooth' })`, then `setTimeout(checkScroll, 400)`.

The returned JSX root is a `<section>` with `id=\"dashboard\"`, `ref={sectionRef}`, and classes: `relative w-full py-28 md:py-36 bg-yefai-navy overflow-hidden`. The exact background color must be `#0a0a12` (mapped as `bg-yefai-navy` in Tailwind config).

Inside the section, place `<div className=\"absolute inset-0 grid-bg opacity-15\" />`.

Then a content wrapper `<div>` with classes `relative z-10 max-w-7xl mx-auto px-6 md:px-10`.

Inside that wrapper, place a `<motion.div>` with:
- `initial={{ opacity: 0, y: 30 }}`
- `animate={inView ? { opacity: 1, y: 0 } : {}}`
- `transition={{ duration: 0.7 }}`
- `className=\"flex flex-col md:flex-row md:items-end justify-between mb-12 md:mb-16 gap-4\"`

Inside this header motion.div:
- First, a `<div>` containing an `<h2>` with class `text-3xl md:text-5xl lg:text-6xl font-bold text-white leading-tight`. Its exact text is `Dashboard Preview`.
- As a sibling to that inner `<div>`, place a `<p>` with class `text-sm md:text-base text-white/35 font-light max-w-sm`. Its exact text is: `Real-time plant telemetry and control — every metric, every alert, every decision surface.`

Below the header, create a relative wrapper `<div className=\"relative\">`. Inside it, a scroll container `<div>` with `ref={scrollRef}`, `onScroll={checkScroll}`, and classes: `flex gap-5 overflow-x-auto scrollbar-hide snap-x snap-mandatory pb-4`.

Map over `dashboards` array. For each `dash` and `index`:

Return a `<motion.div>` with:
- `key={dash.title}`
- `initial={{ opacity: 0, y: 40 }}`
- `animate={inView ? { opacity: 1, y: 0 } : {}}`
- `transition={{ duration: 0.6, delay: 0.1 * index }}`
- `className=\"snap-start flex-shrink-0 w-[320px] md:w-[400px] lg:w-[460px] rounded-2xl overflow-hidden relative group cursor-pointer\"`
- `style={{ minHeight: '320px' }}`

Inside each card, place these children in this exact order:

1. **Image container:** `<div className=\"absolute inset-0\">` containing an `<img>` with `src={dash.image}`, `alt={dash.title}`, `className=\"w-full h-full object-cover transition-transform duration-700 group-hover:scale-105\"`.

2. **Gradient overlay:** `<div className=\"absolute inset-0 bg-gradient-to-t from-black/85 via-black/20 to-transparent\" />`

3. **Status badge:** `<div className=\"absolute top-4 right-4 z-20\">` containing a `<span>` with inline-flex, gap-1.5, px-2.5 py-1, rounded-full, text-[10px], tracking-widest, uppercase, font-semibold, border, backdrop-blur-sm. The conditional classes must be exactly:
- If `dash.status === 'LIVE'`: `bg-emerald-500/10 border-emerald-400/25 text-emerald-400`
- Else if `dash.status === 'PREDICTIVE'`: `bg-cyan-500/10 border-cyan-400/25 text-cyan-400`
- Else: `bg-amber-500/10 border-amber-400/25 text-amber-400`

Inside the badge span, place a small dot `<span>` with `w-1.5 h-1.5 rounded-full` and conditional classes:
- If `dash.status === 'LIVE'`: `bg-emerald-400 animate-pulse`
- Else if `dash.status === 'PREDICTIVE'`: `bg-cyan-400 animate-pulse`
- Else: `bg-amber-400 animate-pulse`

Then the status text `{dash.status}`.

4. **Bottom info container:** `<div className=\"absolute bottom-0 left-0 right-0 p-5 md:p-6 z-20\">` containing:
   - An `<h3>` with class `text-lg md:text-xl font-bold text-white`. Content: `{dash.title}`.
   - A `<p>` with class `mt-1.5 text-sm text-white/40 font-light leading-relaxed`. Content: `{dash.subtitle}`.

After the scroll container (still inside the relative wrapper), place a scroll controls `<div>` with class `hidden md:flex items-center justify-between mt-8`.

Inside it, place two `<button>` elements:

**Left button:**
- `onClick={() => scroll('left')}`
- `disabled={!canScrollLeft}`
- Conditional className: if `canScrollLeft` is true, use `w-10 h-10 rounded-full border flex items-center justify-center transition-all duration-300 border-white/15 text-white/60 hover:border-cyan-400/30 hover:text-cyan-400 cursor-pointer`. If false, use `w-10 h-10 rounded-full border flex items-center justify-center transition-all duration-300 border-white/5 text-white/15 cursor-default`.
- Inside: `<i className=\"ri-arrow-left-line text-lg\" />`

**Right button:**
- `onClick={() => scroll('right')}`
- `disabled={!canScrollRight}`
- Conditional className: if `canScrollRight` is true, use `w-10 h-10 rounded-full border flex items-center justify-center transition-all duration-300 border-white/15 text-white/60 hover:border-cyan-400/30 hover:text-cyan-400 cursor-pointer`. If false, use `w-10 h-10 rounded-full border flex items-center justify-center transition-all duration-300 border-white/5 text-white/15 cursor-default`.
- Inside: `<i className=\"ri-arrow-right-line text-lg\" />`

Export the component as default.

---

### Prompt 3 — create \"Deploy the RAG Assistant\" Section Exactly

Write a React component named `RAGAssistant` using TypeScript, TailwindCSS, and Framer Motion (`motion` and `useInView`). Import `useRef` from React.

The component uses `useRef(null)` for `ref`. Then `useInView(ref, { once: true, margin: '-80px' })` for `inView`.

The returned JSX root is a `<section>` with `id=\"rag\"`, `ref={ref}`, and class `relative w-full overflow-hidden`.

Inside the section, place a flex container `<div>` with class `flex flex-col md:flex-row min-h-[600px] md:min-h-[700px]`.

**Left Half:**

Place a `<motion.div>` with:
- `initial={{ opacity: 0, x: -40 }}`
- `animate={inView ? { opacity: 1, x: 0 } : {}}`
- `transition={{ duration: 0.8 }}`
- `className=\"relative w-full md:w-1/2 bg-yefai-dark-charcoal overflow-hidden\"`

The exact background color is `#0f0f14` (mapped as `bg-yefai-dark-charcoal` in Tailwind config).

Inside this left motion.div, place these children in this exact order:

1. **Cyan ambient glow:** `<div className=\"absolute top-1/4 left-1/4 w-80 h-80 bg-cyan-500/[0.04] rounded-full blur-[120px]\" />`

2. **Image container:** `<div className=\"absolute inset-0 flex items-end\">` containing an `<img>` with:
   - `src=\"https://readdy.ai/api/search-image?query=AI conversational assistant interface for industrial factory, dark chat UI with glowing cyan message bubbles and holographic data overlays, manufacturing diagnostics conversation, futuristic dark mode interface design, premium tech aesthetic&width=800&height=900&seq=14&orientation=portrait\"`
   - `alt=\"RAG Assistant Interface\"`
   - `className=\"w-full h-full object-cover object-top opacity-80\"`

3. **Left-to-right gradient overlay:** `<div className=\"absolute inset-0 bg-gradient-to-r from-black/70 via-black/30 to-transparent\" />`

4. **Bottom-to-top gradient overlay:** `<div className=\"absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/40\" />`

5. **Content overlay:** `<div className=\"relative z-10 h-full flex flex-col justify-end p-8 md:p-12 lg:p-16\">` containing:
   - A `<motion.p>` with `initial={{ opacity: 0, y: 20 }}`, `animate={inView ? { opacity: 1, y: 0 } : {}}`, `transition={{ duration: 0.6, delay: 0.3 }}`, class `text-xs tracking-[0.2em] uppercase text-cyan-400/70 font-medium mb-4`. Its exact text is `Conversational Intelligence`.
   - A `<motion.h2>` with `initial={{ opacity: 0, y: 30 }}`, `animate={inView ? { opacity: 1, y: 0 } : {}}`, `transition={{ duration: 0.7, delay: 0.4 }}`, class `text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-[1.05]`. Its exact text is three lines with manual `<br />` between each: `Ask` / `Your` / `Factory`.

**Right Half — \"Deploy the RAG Assistant\":**

Place a `<motion.div>` with:
- `initial={{ opacity: 0, x: 40 }}`
- `animate={inView ? { opacity: 1, x: 0 } : {}}`
- `transition={{ duration: 0.8, delay: 0.2 }}`
- `className=\"relative w-full md:w-1/2 bg-yefai-black flex flex-col items-center justify-center p-8 md:p-12 lg:p-20 text-center\"`

The exact background color is `#050508` (mapped as `bg-yefai-black` in Tailwind config).

Inside this right motion.div, place these children in this exact order:

1. **Violet ambient glow:** `<div className=\"absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-violet-500/[0.02] rounded-full blur-[120px]\" />`

2. **Content wrapper:** `<div className=\"relative z-10 max-w-md\">` containing:
   - An `<h2>` with class `text-3xl md:text-4xl lg:text-5xl font-bold text-white leading-tight`. Its exact text is two lines with a manual `<br />` between: `Deploy the` / `RAG Assistant`.
   - A `<p>` with class `mt-6 text-base md:text-lg text-white/35 font-light leading-relaxed`. Its exact text is: `Your entire plant history, manuals, sensor logs, and maintenance records — accessible through natural language. Ask why a spindle vibrates. Ask when to schedule replacement. Ask what happened during the March outage. Your factory answers.`
   - A `<motion.button>` with `initial={{ opacity: 0, y: 20 }}`, `animate={inView ? { opacity: 1, y: 0 } : {}}`, `transition={{ duration: 0.6, delay: 0.6 }}`, class `mt-10 inline-flex items-center gap-3 px-8 py-4 rounded-full bg-yefai-charcoal border border-white/[0.08] text-white font-medium text-sm hover:bg-white/[0.08] hover:border-cyan-400/20 transition-all duration-300 cursor-pointer group`. The exact background color for `bg-yefai-charcoal` is `#141418`. Inside the button:
     - A `<span>` with text `Request Access`
     - An `<i>` with class `ri-arrow-right-line text-cyan-400 group-hover:translate-x-1 transition-transform`

Export the component as default.

---