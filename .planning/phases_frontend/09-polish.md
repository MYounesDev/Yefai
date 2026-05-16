# Phase 9 — Polish & Performance

> Final polish pass: page transitions, loading UX, responsive QA, performance optimization, accessibility, and visual refinement.

## Tasks

### 1. Page Transitions

- Wrap all page content with `PageTransition` component
- Route changes: content fades out (0.15s) → new content fades/slides in (0.3s)
- Use Framer Motion `AnimatePresence` with `mode="wait"` in the layout
- Sidebar navigation: active indicator slides smoothly between items (layout animation)

### 2. Loading States (Every Page)

Audit and ensure every data-dependent area has:
- **Initial load**: Skeleton placeholders that match the final layout shape
- **Refetch**: subtle opacity pulse (not full skeleton replacement)
- **Error state**: glass card with error icon, message, "Retry" button
- **Empty state**: illustrated empty state with message and action suggestion
- Loading skeletons for: dashboard stats, machine cards, anomaly table rows, chart areas, chat messages, notification logs

### 3. Micro-Interactions Audit

Ensure these exist throughout:
- **Buttons**: ripple effect on click, subtle scale-down on press, glow on hover
- **Cards**: 3D perspective tilt on hover (subtle, ~3deg), elevation increase
- **Links**: underline animates from left, color transition
- **Toggles**: spring animation for knob movement
- **Badges**: pulse animation for critical/danger states
- **Notification bell**: bounce animation when count changes
- **Counters**: spring animation when values update
- **Charts**: animated draw-in on first render, tooltip follows cursor smoothly
- **Modals**: backdrop blur-in, content scale from 95% to 100%
- **Toast notifications**: slide-in from right, auto-dismiss with progress bar

### 4. Responsive QA

Test and fix all breakpoints:
- **Desktop** (1280px+): full sidebar, multi-column layouts
- **Tablet** (768-1279px): collapsed sidebar (icon-only), 2-column grids, adjusted chart sizes
- **Mobile** (< 768px): sidebar becomes drawer (swipe to open), single column, stacked cards, bottom nav bar option
- Touch targets: minimum 44×44px
- Charts: readable at all sizes (Recharts responsive container)
- Tables: horizontal scroll on mobile with sticky first column
- Modals: full-screen on mobile

### 5. Performance Optimization

- **Lazy load** heavy components:
  - Three.js scene (landing page) — `dynamic(() => import(...), { ssr: false })`
  - Charts — `dynamic` import with skeleton fallback
- **Image optimization**: Next.js `<Image>` component for all images, proper `width`/`height`/`sizes`
- **Bundle splitting**: separate chunks for landing page vs dashboard
- **React Query settings**:
  - `staleTime: 30000` for dashboard data
  - `refetchInterval: 30000` for real-time-ish data
  - `refetchOnWindowFocus: false` for heavy queries
- **Animation performance**:
  - Use `transform` and `opacity` only (GPU-accelerated)
  - Avoid layout-triggering properties in animations
  - `will-change: transform` on animated elements
  - Remove particle effects on mobile (fewer GPU resources)
- **prefers-reduced-motion**:
  - Disable auto-rotating 3D scene
  - Disable particle effects
  - Reduce animation durations to near-zero
  - Keep essential transitions (page change, modal open/close)

### 6. Accessibility

- **Focus indicators**: visible cyan ring on all interactive elements
- **ARIA labels**: all buttons, icons, status indicators
- **Screen reader**: chart data available as table alternative
- **Keyboard navigation**: Tab through sidebar, Enter to activate, Escape to close modals
- **Color contrast**: ensure text meets WCAG AA on glass backgrounds
- **Skip to content**: link for keyboard users

### 7. Visual Refinement

- Consistent spacing audit (8px grid system)
- Typography hierarchy check (h1 → h6 sizes, line heights, letter spacing)
- Icon sizing consistency (all nav icons same size, all card icons same size)
- Color usage audit (no more than 5 accent colors used meaningfully)
- Gradient consistency (same gradient direction/stops across similar elements)
- Border radius consistency (rounded-2xl for cards, rounded-xl for inner elements, rounded-lg for buttons)
- Shadow consistency (all cards same elevation tier)

### 8. Error Handling

- **API error toast**: "Failed to load data. Retrying..." with auto-retry
- **Network offline**: banner at top "You are offline. Some data may be stale."
- **404 page**: custom styled with Yefai branding, "Go to Dashboard" button
- **Error boundary**: catches React errors, shows "Something went wrong" with reload button

### 9. SEO & Meta

- Unique `<title>` for each page (e.g., "Anomalies | Yefai", "Predictions | Yefai")
- Meta descriptions for landing page
- Open Graph tags for landing page (for social sharing)
- Favicon (generated or placeholder)

### 10. Final Testing Checklist

- [ ] All pages load without errors
- [ ] Mock data displays correctly on every page
- [ ] API calls fall back to mock gracefully (check console for `[DEV MOCK]` messages)
- [ ] All navigation links work
- [ ] Sidebar collapse/expand works
- [ ] All modals open/close properly
- [ ] All buttons have click feedback
- [ ] All forms validate
- [ ] Charts render and animate
- [ ] Responsive at 375px, 768px, 1024px, 1440px
- [ ] No console errors
- [ ] No layout shifts on load
- [ ] Dark theme consistent everywhere
- [ ] Animations respect prefers-reduced-motion

## Deliverables

- [ ] Page transitions on all routes
- [ ] Loading skeletons for all data areas
- [ ] Error and empty states
- [ ] Micro-interactions audit complete
- [ ] Responsive QA at all breakpoints
- [ ] Performance optimizations (lazy loading, bundle splitting)
- [ ] Accessibility audit (focus, ARIA, keyboard)
- [ ] Visual consistency audit
- [ ] Error handling (toasts, offline, 404, boundary)
- [ ] SEO meta tags
- [ ] Final testing checklist passed
