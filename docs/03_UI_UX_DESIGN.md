# UI / UX Design Document

## Revision History
| Date       | Version | Description                   |
| ---------- | ------- | ----------------------------- |
| 2026-07-23 | 1.0     | Initial MVP Document Creation |

## 1. Design Philosophy
The user interface should feel highly professional, clean, and data-dense. The application is a B2B productivity tool; therefore, utility, clarity, and speed take precedence over flashy animations. 

## 2. Color System
- **Background**: Neutral Light (`#F8FAFC`) / Dark Mode (`#0F172A`)
- **Primary**: Indigo (`#4F46E5`) - Used for CTAs and primary actions.
- **Success**: Emerald (`#10B981`) - Used for high candidate match scores.
- **Warning**: Amber (`#F59E0B`) - Used for missing skills.
- **Text**: Slate (`#334155` for light mode, `#CBD5E1` for dark mode).

## 3. Typography
- **Primary Font**: `Inter` (sans-serif) for high legibility in data tables and UI elements.
- **Monospace Font**: `Fira Code` or `JetBrains Mono` for viewing raw JSON or extracted code snippets.

## 4. Components
We rely on **shadcn/ui** for accessible, headless components:
- Data Tables (for candidate rankings).
- Modals / Dialogs (for Job Creation).
- Drag-and-Drop Zones (for resume uploads).
- Progress Bars (for visualizing match scores).
- Badges (for displaying extracted skills).

## 5. Layout
- **Sidebar Navigation**: Fixed left-hand sidebar for navigating between "Jobs", "Candidates", and "Settings".
- **Main Content Area**: Flexible width, max-width constrained on ultra-wide monitors.
- **Sticky Headers**: Essential for long tables of candidates.

## 6. Responsive Design
- The dashboard is primarily designed for **Desktop** usage (tablet and above), as recruiters evaluate resumes on larger screens.
- Mobile views will stack tables into cards, but mobile is not a P1 priority.

## 7. Accessibility (a11y)
- All shadcn/ui components are ARIA-compliant out of the box.
- Strict adherence to WCAG AA contrast ratios for text and background colors.
- Keyboard navigability for all tables and forms.

## 8. User Journey
1. **Login**: User accesses the dashboard.
2. **Job Creation**: User clicks "New Job", inputs title and required skills.
3. **Ingestion**: User clicks into the Job, uses a Drag-and-Drop zone to upload 50 PDF resumes.
4. **Processing**: System shows a loading state/progress bar as backend processes documents.
5. **Review**: Table populates with Candidates sorted by Match Score. User clicks a candidate to see score breakdown (Hard Skills vs Semantic Similarity).

## 9. Page Breakdown
- `/` - Main Dashboard (List of active Jobs).
- `/jobs/{id}` - Job Detail View (Upload zone + Candidate Ranking Table).
- `/candidates/{id}` - Deep dive into a specific parsed resume and raw text.

## 10. Design Inspiration
- Modern ATS (Applicant Tracking Systems) like Greenhouse or Ashby.
- Vercel's clean, minimalist dashboard aesthetic.
