# Web Scraper - Design & Style Guide

## Overview

This document outlines the design principles, color palette, typography, and component guidelines for the Multisite Web Scraper application. The design follows a **flat, elegant, and modern** aesthetic with a focus on readability and user experience.

---

## Design Principles

### 1. **Flat Design**
- Minimalist approach with subtle shadows and depth
- Clean lines and simple shapes
- Avoid skeuomorphism and unnecessary gradients
- Focus on clarity and content

### 2. **Elegant Simplicity**
- Every element has a purpose
- Generous whitespace for breathing room
- Consistent visual hierarchy
- Professional and approachable

### 3. **Accessibility First**
- High contrast ratios for text
- Keyboard navigation support
- Font Awesome icons with text labels
- Clear focus states

### 4. **Responsive Design**
- Mobile-first approach
- Flexible layouts using CSS Grid and Flexbox
- Touch-friendly interactive elements (min 44px height)
- Optimized for all screen sizes

---

## Color Palette

### Primary Colors

```
Primary Dark: #2d3748
Primary Light: #1a202c
Background: #f9fafb
White: #ffffff
```

### Accent Colors

```
Accent Orange: #f97316
Accent Dark: #ea580c
Accent Light: #fed7aa
```

### Semantic Colors

```
Success: #10b981
Success Light: #d1fae5
Error/Danger: #ef4444
Error Light: #fee2e2
Warning: #f59e0b
Warning Light: #fef3c7
Info: #3b82f6
Info Light: #dbeafe
```

### Neutral Colors

```
Gray 50: #f9fafb
Gray 100: #f3f4f6
Gray 200: #e5e7eb
Gray 300: #d1d5db
Gray 400: #9ca3af
Gray 500: #6b7280
Gray 600: #4b5563
Gray 700: #374151
Gray 800: #1f2937
Gray 900: #111827
```

---

## Typography

### Font Family

**Primary Font**: System fonts stack
```
-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif
```

### Font Sizes

```
XS: 12px
SM: 13px
Base: 14px
MD: 16px
LG: 18px
XL: 24px
2XL: 28px
3XL: 32px
4XL: 36px
```

### Font Weights

```
Light: 300
Normal: 400
Medium: 500
Semibold: 600
Bold: 700
Extrabold: 800
```

### Line Heights

```
Tight: 1.25
Normal: 1.5
Relaxed: 1.625
Loose: 1.75
```

### Heading Styles

```
H1: 32px, Bold, Letter-spacing: -1px
H2: 28px, Bold, Letter-spacing: -0.5px
H3: 24px, Bold, Letter-spacing: 0
H4: 18px, Semibold
```

---

## Spacing System

Consistent spacing using an 8px base unit:

```
XS: 4px
SM: 8px
MD: 12px
LG: 16px
XL: 20px
2XL: 24px
3XL: 32px
4XL: 40px
5XL: 48px
```

---

## Border Radius

```
SM: 4px (small elements)
MD: 6px (inputs, buttons)
LG: 8px (cards, containers)
XL: 12px (large cards, modals)
2XL: 16px (prominent containers)
Full: 9999px (badges, pills)
```

---

## Shadows

### Elevation Levels

```
Shadow SM: 0 1px 2px 0 rgba(0, 0, 0, 0.05)

Shadow MD: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
           0 2px 4px -1px rgba(0, 0, 0, 0.06)

Shadow LG: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
           0 4px 6px -2px rgba(0, 0, 0, 0.05)

Shadow XL: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
           0 10px 10px -5px rgba(0, 0, 0, 0.04)

Shadow Hover: 0 12px 24px rgba(0, 0, 0, 0.15)
```

---

## Components

### Buttons

#### Primary Button
- **Background**: Accent Orange (#f97316)
- **Text Color**: White
- **Padding**: 12px 16px
- **Border Radius**: 8px
- **Font Weight**: Semibold
- **Height**: 44px (mobile-friendly)
- **Hover**: Darker shade (#ea580c)
- **Shadow**: Subtle elevation

```css
.btn-primary {
    background: var(--color-accent);
    color: var(--color-white);
    padding: 12px var(--spacing-lg);
    border-radius: var(--radius-lg);
    font-weight: var(--font-weight-semibold);
    box-shadow: 0 2px 8px rgba(249, 115, 22, 0.25);
    transition: all var(--transition-base);
}

.btn-primary:hover {
    background: var(--color-accent-dark);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(249, 115, 22, 0.35);
}
```

#### Secondary Button
- **Background**: White
- **Border**: 1.5px solid border color
- **Text Color**: Primary
- **Padding**: 12px 16px
- **Border Radius**: 8px

```css
.btn-secondary {
    background: var(--color-white);
    color: var(--color-text-primary);
    border: 1.5px solid var(--color-border);
    padding: 12px var(--spacing-lg);
    border-radius: var(--radius-lg);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.btn-secondary:hover {
    background: var(--color-background-secondary);
    border-color: var(--color-text-secondary);
}
```

### Cards

- **Background**: White
- **Border Radius**: 8-12px
- **Shadow**: Subtle, elevates on hover
- **Padding**: 16-24px
- **Border**: 1px solid light border

### Form Elements

#### Input Fields
- **Background**: White
- **Border**: 1px solid #e5e7eb
- **Border Radius**: 6px
- **Padding**: 12px 16px
- **Focus**: Accent color border + subtle shadow

```css
input:focus {
    outline: none;
    border-color: var(--color-accent);
    box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.08);
}
```

#### Checkboxes
- **Custom styled** with accent color
- **Size**: 18x18px
- **Checked**: Filled with accent color
- **Focus**: Visible outline

### Status Messages

#### Success
- **Background**: Light green with gradient
- **Border Left**: 4px solid green
- **Icon**: Check circle (Font Awesome)
- **Text Color**: Dark green

#### Error
- **Background**: Light red with gradient
- **Border Left**: 4px solid red
- **Icon**: Exclamation circle
- **Text Color**: Dark red

#### Loading
- **Background**: Light accent with gradient
- **Border Left**: 4px solid accent
- **Icon**: Spinner (animated)
- **Text Color**: Primary

---

## Icons

### Icon Library: Font Awesome 6.4.0

All icons use Font Awesome with semantic meaning:

```
Navigation:
- fa-arrow-left: Back navigation
- fa-sync-alt: Refresh/reload
- fa-search: Search/find
- fa-link: Links/URLs

Content:
- fa-newspaper: Articles/news
- fa-bookmark: Saved items
- fa-book: Library/collection
- fa-pen-fancy: Author/writing
- fa-file-alt: Document/file

UI:
- fa-check-circle: Success
- fa-exclamation-circle: Error
- fa-exclamation-triangle: Warning
- fa-lightbulb: Tip/help
- fa-cog: Settings
- fa-list: List view
- fa-th: Grid view

Actions:
- fa-trash-alt: Delete
- fa-plus-circle: Add/create
- fa-sliders-h: Controls/settings
```

### Icon Usage Guidelines

1. **Always pair with text** for clarity
2. **Consistent sizing** (typically 16-20px)
3. **Maintain sufficient contrast** (minimum 4.5:1)
4. **Use semantic icons** that clearly represent the action
5. **Animate sparingly** (only for loading states)

---

## Animations & Transitions

### Transition Times

```
Fast: 0.15s ease
Base: 0.3s ease
Slow: 0.5s ease
```

### Animations

#### Slide Up (Page Load)
```css
@keyframes slideUp {
    from {
        transform: translateY(20px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}
```

#### Fade In
```css
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
```

#### Spin (Loading)
```css
@keyframes spin {
    to { transform: rotate(360deg); }
}
```

### Guidelines

- Use animations to guide attention and provide feedback
- Keep animations under 500ms for responsiveness
- Respect `prefers-reduced-motion` for accessibility
- Use transforms for performance (GPU accelerated)

---

## Responsive Breakpoints

```
Mobile: < 640px
Tablet: 640px - 1024px
Desktop: 1024px+

Specific Breakpoints:
SM: 640px
MD: 768px
LG: 1024px
XL: 1280px
2XL: 1536px
```

### Mobile-First Approach

1. Design for mobile first
2. Progressively enhance for larger screens
3. Use mobile-friendly touch targets (min 44x44px)
4. Stack layouts vertically on mobile
5. Use single column on mobile, multi-column on desktop

---

## Component Specifications

### Navigation Bar
- **Height**: 56-64px
- **Background**: White
- **Border**: 1px bottom border
- **Sticky**: Yes, on scroll
- **Z-index**: 100

### Container
- **Max Width**: 1200px
- **Padding**: 16px (mobile), 32px+ (desktop)
- **Centered**: Yes, with margin auto

### Cards Grid
- **Columns**: 
  - Mobile: 1 column
  - Tablet: 2 columns
  - Desktop: 3+ columns
- **Gap**: 16-32px
- **Min Width**: 280px per card

---

## Accessibility Checklist

- [ ] Color contrast ratio: minimum 4.5:1 for text
- [ ] Focus states clearly visible
- [ ] Keyboard navigation fully supported
- [ ] Icons have text labels or ARIA labels
- [ ] Form inputs have associated labels
- [ ] Error messages clearly visible
- [ ] Loading states have spinner animation
- [ ] Touch targets minimum 44x44px
- [ ] Semantic HTML structure
- [ ] ARIA roles and attributes where needed

---

## Performance Tips

1. **CSS Variables** for theming and consistency
2. **CSS Grid** for layout (native performance)
3. **Flexbox** for components
4. **GPU-accelerated** transforms for animations
5. **Minimal shadows** - computed carefully
6. **System fonts** stack for fast loading
7. **Lazy load** images where applicable

---

## Development Standards

### CSS Organization

```
1. Variables (colors, sizing, spacing)
2. Base styles (html, body, typography)
3. Layout components
4. Form elements
5. Buttons
6. Cards and containers
7. Status messages
8. Responsive media queries
9. Animations and transitions
```

### Naming Conventions

- Use BEM (Block Element Modifier) for CSS classes
- Prefixes: `.btn-`, `.card-`, `.status-`
- Modifiers: `.is-active`, `.is-disabled`

### Component Structure

```html
<div class="component">
  <div class="component__header">
    <!-- Header content -->
  </div>
  <div class="component__body">
    <!-- Main content -->
  </div>
  <div class="component__footer">
    <!-- Footer content -->
  </div>
</div>
```

---

## Future Enhancements

- Dark mode support (CSS custom properties ready)
- Animation preferences for reduced motion
- Additional color themes
- Expanded icon library
- Advanced component library

---

## References

- [Font Awesome Icons](https://fontawesome.com)
- [Web Content Accessibility Guidelines (WCAG)](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN Web Docs](https://developer.mozilla.org/)
- [CSS-Tricks](https://css-tricks.com/)

---

**Document Version**: 1.0  
**Last Updated**: 2025  
**Status**: Active