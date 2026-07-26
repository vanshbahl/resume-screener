# UI / UX Design Document

## Revision History
| Date       | Version | Description                   |
| ---------- | ------- | ----------------------------- |
| 2026-07-23 | 1.0     | Initial MVP Document Creation |
| 2026-07-26 | 2.0     | Redesign for Resume Intelligence Platform |

## 1. Design Philosophy
The user interface should feel highly professional, clean, and empowering. The application is a B2C productivity and intelligence tool for job seekers; therefore, utility, clarity, and explainability take precedence over flashy animations. 

## 2. Color System
- **Background**: Neutral Light (`#F8FAFC`) / Dark Mode (`#0F172A`)
- **Primary**: Indigo (`#4F46E5`) - Used for CTAs and primary actions.
- **Success**: Emerald (`#10B981`) - Used for high resume scores.
- **Warning**: Amber (`#F59E0B`) - Used for missing skills or weak areas.
- **Text**: Slate (`#334155` for light mode, `#CBD5E1` for dark mode).

## 3. Typography
- **Primary Font**: `Inter` (sans-serif) for high legibility in data tables and UI elements.
- **Monospace Font**: `Fira Code` or `JetBrains Mono` for viewing raw JSON or extracted code snippets.

## 4. Components
We rely on **shadcn/ui** for accessible, headless components:
- Data Visualizations (for resume benchmarking).
- Modals / Dialogs (for AI Follow-up questions).
- Drag-and-Drop Zones (for resume uploads).
- Progress Bars / Gauges (for visualizing overall scores).
- Badges (for displaying extracted skills and strengths).

## 5. Layout
- **Sidebar Navigation**: Fixed left-hand sidebar for navigating between "Dashboard", "My Resumes", "Insights", and "Settings".
- **Main Content Area**: Flexible width, max-width constrained on ultra-wide monitors.
- **Sticky Headers**: Essential for long scrolling reports.

## 6. Responsive Design
- The dashboard is primarily designed for **Desktop** usage (tablet and above), as users evaluate and edit their resumes on larger screens.
- Mobile views will stack charts and reports into cards, but mobile is not a P1 priority.

## 7. Accessibility (a11y)
- All shadcn/ui components are ARIA-compliant out of the box.
- Strict adherence to WCAG AA contrast ratios for text and background colors.
- Keyboard navigability for all reports and forms.

## 8. User Journey
1. **Login**: User accesses the dashboard.
2. **Upload**: User uses a Drag-and-Drop zone to upload their PDF resume.
3. **Processing**: System shows a loading state as the backend parses the document.
4. **AI Follow-up (Conditional)**: System asks intelligent follow-up questions if critical information is missing.
5. **Review**: User is presented with a Resume Intelligence Report showing their overall score, strengths, weaknesses, and industry benchmark ranking.
6. **Action**: User reviews actionable recommendations to optimize their resume.

## 9. Page Breakdown
- `/` - Main Dashboard (Upload zone + Resume History).
- `/resumes/{id}` - Resume Intelligence Report (Score Visualization, Benchmarks, AI Feedback).
- `/insights` - Career insights and dataset rankings.

## 10. Design Inspiration
- Modern AI productivity tools like Perplexity or Notion AI.
- Clean, minimalist aesthetic utilizing vast whitespace to emphasize data clarity.
