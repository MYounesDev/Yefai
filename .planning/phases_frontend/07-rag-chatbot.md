# Phase 7 — RAG Chatbot

> AI-powered chatbot page with streaming responses, image cards, and session history. The core "smart assistant" feature.
> 
> **Role Access:** Accessible to Manager, Operator, Technician only. Procurement and Viewer CANNOT access (RoleGuard → 403 page). Chat sessions are org-scoped — each org has its own chat history.

## Page: `src/app/(dashboard)/chat/page.tsx`

**API calls:** `sendChatMessage()`, `getChatSessions()`, `getChatSessionById()`, `searchHybrid()`

## Layout (2-panel)

### Left Panel — Session Sidebar (25%, collapsible)

- "New Chat" button (top, prominent, cyan)
- Session list from `getChatSessions()`:
  - Each session: title (first message truncated), date, message count
  - Active session highlighted with cyan left border
  - Click to load session history
  - Delete button (hover reveal, ghost red icon)
- Animated transition on session switch

### Right Panel — Chat Interface (75%)

#### Chat Header

- Session title (editable on click)
- "Clear Chat" button
- "Export" button (download as text — mock)

#### Message Area (scrollable, auto-scroll to bottom)

Message bubbles with clear visual distinction:

**User Messages:**
- Right-aligned
- Glass card with cyan-tinted border
- User avatar (placeholder initials)
- Timestamp on hover

**AI Messages:**
- Left-aligned
- Glass card with violet-tinted border
- Yefai AI avatar (bot icon)
- Markdown rendered content (bold, lists, code blocks)
- **Image Cards**: when response includes images (from RAG search results):
  - Inline image thumbnails in a horizontal scroll row
  - Each image: glass-card frame, click to enlarge (modal with zoom)
  - Below each image: metadata (Set, wear level, machine ID, anomaly score)
  - Hover effect: slight lift + border glow
- **Data Tables**: when response includes tabular data:
  - Rendered as glass-styled table within the message
- **Source Citations**: at the bottom of AI response:
  - "Sources: Set 5 / Image 23 (similarity: 0.92), Set 12 / Image 7 (similarity: 0.87)"
  - Clickable → link to anomaly detail page
- Streaming effect: text appears character by character (simulated in mock with setTimeout)

**System Messages:**
- Center-aligned, muted text
- "Session started", "Context loaded", etc.

#### Input Area (bottom, sticky)

- Large textarea with glass styling
- Placeholder: "Ask about tool wear, anomalies, spare parts..."
- Send button (cyan, arrow icon) — disabled when empty
- Keyboard shortcut: Ctrl+Enter to send
- Loading state: pulsing dots animation while waiting for response
- Quick suggestion chips above input (on empty chat):
  - "Which tools have the highest wear?"
  - "Show me critical anomalies from today"
  - "What spare parts are out of stock?"
  - "Compare flank wear vs adhesive wear patterns"

## Mock Data (`src/services/mock/chat.ts`)

**Chat Sessions** (5 mock sessions):
- "Tool Wear Analysis — Set 5"
- "Critical Anomaly Investigation"
- "Spare Parts Inventory Check"
- "Weekly Report Summary"
- "Flank Wear Pattern Research"

**Mock Responses**: For common queries, return realistic AI-style responses with:
- Markdown formatted text
- Referenced images (mock URLs/placeholders)
- Source citations with similarity scores
- Some responses with data tables

**Streaming Simulation**: `mockSendMessage` returns response with a small delay (500ms) simulating streaming.

**Hybrid Search Results**: Return 5 mock search results with:
- Image reference, Set, wear level, metadata
- Similarity score

## Key Interactions

1. User types message → send → loading dots appear
2. AI response streams in (mock: appears after 500ms delay)
3. If response has images → image cards render inline
4. Source citations link to anomaly detail pages
5. Session auto-saves to sidebar
6. Quick suggestions disappear after first message

## Deliverables

- [ ] Chat page with session sidebar + chat interface
- [ ] User/AI message bubbles with distinct styling
- [ ] Inline image cards with metadata
- [ ] Source citations with links
- [ ] Message input with suggestions and keyboard shortcut
- [ ] Simulated streaming text effect
- [ ] Session management (create, switch, delete)
- [ ] Mock chat data with realistic AI responses
- [ ] Scroll management (auto-scroll, scroll-to-bottom button)
- [ ] Loading states (pulsing dots, skeleton for session list)
- [ ] Responsive (sidebar collapses to drawer on mobile)
