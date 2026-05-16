# Phase 2 — Landing Page (3D Hero + Motion Design)

> A jaw-dropping landing page that showcases Yefai's AI-powered predictive maintenance. Heavy use of Three.js, Framer Motion, and scroll-driven animation.

## Page: `src/app/(landing)/page.tsx`

This is the public-facing landing page. It does NOT use the dashboard layout. It has its own full-screen layout with a transparent navbar.

## Sections

### 1. Navbar (Transparent → Glass on Scroll)

- Yefai logo (left), nav links (center): Features, How It Works, Demo, Contact
- CTA button (right): "Open Dashboard" → navigates to `/dashboard`
- On scroll: navbar background transitions from transparent to `backdrop-blur-xl bg-glass/80`
- Framer Motion: fade-in on mount, background transition on scroll

### 2. Hero Section (Full-Screen, 3D)

**Three.js Scene (React Three Fiber):**
- Dark void background with subtle star particles (using `@react-three/drei` Stars or custom Points)
- Central 3D object: a stylized CNC milling machine or industrial gear assembly
  - Wireframe + solid hybrid rendering
  - Subtle rotation animation (auto-rotate, slow)
  - Cyan and violet edge glow (using custom shader or emissive materials)
  - On mouse move: parallax tilt following cursor
- Floating data particles orbiting the machine (small glowing spheres with trails)
- Atmospheric fog with depth

**Overlay Text (HTML, positioned over canvas):**
- Headline: `"Predict Failures Before They Happen"` — staggered letter/word animation (Framer Motion)
- Subheadline: `"AI-powered predictive maintenance for manufacturing. Zero-shot anomaly detection, real-time alerts, smart spare parts management."` — fade-up with delay
- CTA buttons: "Explore Dashboard" (primary, glow) + "Watch Demo" (ghost with play icon)
- Animated stat counters scrolling in: `99.7% Detection Accuracy`, `< 2s Inference Time`, `24/7 Monitoring`

**Background Effects:**
- Gradient mesh: dark navy → deep purple → charcoal (animated, slowly shifting)
- Subtle grid pattern floor (perspective, fading into distance)
- Floating particle system (light dots drifting upward)

### 3. Features Section (Scroll-Triggered Stagger)

Three feature cards in a row (stack on mobile), each with:
- Icon (Lucide, animated on scroll enter — bounce-in)
- Title + description
- Glass card styling with hover lift + glow
- Cards stagger in from bottom on scroll with Framer Motion `whileInView`

**Cards:**
1. 🔍 **Real-Time Anomaly Detection** — "Zero-shot AI models detect tool wear from camera images instantly. No training data required."
2. 🔮 **Predictive Forecasting** — "Know exactly when a tool will reach critical wear. Plan maintenance hours ahead."
3. ⚡ **Smart Spare Parts Management** — "Automatic crisis detection, purchase order generation, and alternative supplier recommendations."

### 4. How It Works (Animated Timeline)

Vertical timeline with animated connector line that draws as you scroll:
1. **Sensor Data + Camera Feed** → "Continuous monitoring of force, vibration, acoustic, and visual data"
2. **AI Analysis** → "PatchCore anomaly detection + Jina CLIP embeddings in < 2 seconds"
3. **Crisis Assessment** → "Spare part inventory check, crisis scoring, automatic PO generation"
4. **Smart Alerts** → "Multi-channel notifications: Telegram, Email, SMS via PUQ AI"
5. **RAG Assistant** → "Ask questions about your data in natural language, get AI-powered answers"

Each step has a small icon, animates in on scroll, with a pulsing connector dot.

### 5. Live Demo Preview (Interactive)

Mock dashboard screenshot or embedded mini-dashboard showing:
- A card with anomaly score gauge (animated, counting up)
- A mini wear projection chart (Recharts, animated draw)
- A crisis alert card (flashing glow border)
- Use `perspective` CSS for 3D card tilt effect — the whole preview tilts as user moves mouse
- Floating UI elements around the preview (tooltips, badges) for depth

### 6. Stats Bar (Animated Counters)

Full-width glass bar with 4 stats counting up on scroll:
- `1,663` Images Analyzed
- `17` Machine Datasets
- `< 2s` Inference Speed
- `99.7%` Accuracy Rate

Use `AnimatedCounter` component with spring physics.

### 7. CTA Section

- Heading: "Ready to Prevent Downtime?"
- Subtext: "Start monitoring your production line with AI-powered predictive maintenance."
- Large CTA button with animated glow pulse
- Background: gradient + subtle particle system

### 8. Footer

- Yefai logo, links (Dashboard, Docs, GitHub), copyright
- Minimal, dark glass style

## Design Details

- All scroll animations use Framer Motion `whileInView` with `viewport={{ once: true, amount: 0.3 }}`
- Easing: `[0.22, 1, 0.36, 1]` for entrances
- 3D canvas uses `<Suspense>` with a beautiful loading spinner
- `prefers-reduced-motion`: disable 3D auto-rotation, use static image fallback
- Mobile: 3D scene simplifies (fewer particles, smaller model), cards stack vertically

## Mock Data Needed

None — landing page is static content. Stats are hardcoded.

## Deliverables

- [ ] Landing page layout (no sidebar)
- [ ] Three.js hero scene with 3D machine model
- [ ] Particle effects and atmospheric background
- [ ] Scroll-triggered animations for all sections
- [ ] Responsive layout (mobile stacking)
- [ ] Navbar scroll transition
- [ ] Animated counter stats
- [ ] CTA sections with glow effects
