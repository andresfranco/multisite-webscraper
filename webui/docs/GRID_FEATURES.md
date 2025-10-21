# Grid Search Features Documentation

## Overview

The Article Library grid has been enhanced with powerful filtering, search, and pagination capabilities. Users can now search the database in real-time with multiple filters applied simultaneously, and navigate through results with flexible pagination options.

## Features

### 1. Real-Time Search
- **Search Input**: Search articles by title or author name
- **Database Search**: Every keystroke queries the database for instant results
- **Case-Insensitive**: Search is case-insensitive for better user experience
- **Live Results**: Results update immediately as you type

### 2. Multiple Filters

#### Author Filter
- Filter articles by specific authors
- Dropdown populated with all unique authors from the database
- Works in combination with other filters

#### Date Filter
- Filter articles by publication date
- Shows all available dates in the database
- Dates displayed in ISO format (YYYY-MM-DD)
- Sorted in reverse chronological order (newest first)

#### Website Filter
- Filter articles by source website
- Dropdown shows all unique websites in the database
- Helps identify articles from specific sources
- Useful for comparing content across sources

#### Clear Filters Button
- One-click button to reset all filters
- Clears search input and all dropdown selections
- Resets pagination to page 1
- Resets items per page to default (10)

### 3. Pagination

#### Page Size Selector
- Choose how many items to display per page
- Options: **5**, **10** (default), or **20** items
- Change page size while maintaining current filters

#### Pagination Controls
- **Previous Button**: Navigate to the previous page (disabled on page 1)
- **Next Button**: Navigate to the next page (disabled on last page)
- **Page Numbers**: Interactive page number buttons
  - Current page highlighted in orange accent color
  - Shows up to 5 page numbers at a time
  - Ellipsis (...) used to indicate skipped pages
  - Quick navigation with "First" and "Last" page buttons

#### Results Information
- Displays current page range (e.g., "Showing 1–10 of 47 articles")
- Shows total number of articles matching filters
- Updates dynamically based on applied filters

#### Filter Status Indicator
- Shows active filters in a visual indicator
- Lists all currently applied filters
- Format: `Filters applied: Search: "term" • Author: "name" • Date: "date" • Website: "url"`
- Hidden when no filters are applied

## Usage Examples

### Example 1: Find articles by a specific author
1. Open the Article Library
2. Click on the "Author" dropdown
3. Select an author name
4. Results update automatically
5. Navigate through pages using pagination controls

### Example 2: Search with multiple filters
1. Type a search term in the search box (e.g., "python")
2. Select an author from the Author dropdown
3. Select a date from the Date dropdown
4. Change "Per Page" to 20 to see more results
5. All filters work together - only articles matching ALL criteria are shown

### Example 3: Reset and start over
1. Click the "Clear Filters" button
2. All filters are reset to defaults
3. Search input is cleared
4. Pagination returns to page 1
5. All articles are shown again

## Technical Implementation

### Backend Changes

#### New API Endpoint: `/api/article-filters`
**Method**: GET

**Response**:
```json
{
  "success": true,
  "filters": {
    "authors": ["Author 1", "Author 2", ...],
    "dates": ["2024-01-15", "2024-01-14", ...],
    "websites": ["https://example.com", ...]
  }
}
```

#### Enhanced API Endpoint: `/api/articles`
**Method**: GET

**Query Parameters**:
- `search` (optional): Search term for title/author
- `author` (optional): Filter by author name
- `date` (optional): Filter by publication date
- `website` (optional): Filter by website URL
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page - 5, 10, or 20 (default: 10)

**Response**:
```json
{
  "success": true,
  "articles": [...],
  "count": 10,
  "total_count": 47,
  "page": 1,
  "per_page": 10,
  "total_pages": 5,
  "has_next": true,
  "has_prev": false
}
```

### Frontend Components

#### HTML Elements
- Filter dropdowns for Author, Date, Website
- Page size selector (5, 10, 20 items)
- Search input with icon
- Clear filters button
- Results information display
- Filter status indicator
- Pagination controls with page numbers

#### CSS Styling
- Consistent with current design system
- Uses existing color variables (accent color: orange)
- Responsive design for mobile devices
- Hover and active states for all interactive elements
- Smooth transitions and animations

#### JavaScript Functions
- `loadFilters()`: Fetch available filter options
- `populateFilterSelect()`: Fill dropdown menus
- `loadArticles()`: Query API with current filters
- `updatePagination()`: Update pagination controls
- `generatePageNumbers()`: Create page number buttons
- `updateFilterStatus()`: Display active filters
- Event listeners for all interactive elements

## Design Consistency

### Colors
- **Accent Color**: Orange (#f97316) - Used for icons, active states, and highlights
- **Border Color**: Light gray for input fields
- **Background**: White cards with subtle shadows
- **Text**: Primary and secondary text colors from design system

### Icons
- **Search**: `fa-search`
- **Author**: `fa-pen-fancy`
- **Date**: `fa-calendar-alt`
- **Website**: `fa-globe`
- **Clear**: `fa-times-circle`
- **Pagination**: `fa-chevron-left`, `fa-chevron-right`

### Layout
- Grid-based card layout (unchanged)
- Filters positioned above grid
- Pagination controls positioned below grid
- Responsive layout for mobile devices
- Flexible spacing using CSS variables

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES6 JavaScript features used
- CSS Grid and Flexbox for layout
- Fetch API for HTTP requests

## Performance Considerations

- Database queries are efficient with proper filtering
- Pagination reduces DOM elements for large result sets
- Client-side rendering of page numbers
- Lazy loading of filter options on page load
- Debounced search updates (if needed in future)

## Future Enhancements

Potential improvements for future versions:
- Advanced search with operators (AND, OR, NOT)
- Custom date range filters
- Save/bookmark filter combinations
- Export filtered results
- Sort options (date, title, relevance)
- Filter by content length or reading time
- Tag-based filtering
- Full-text search on article content

## Troubleshooting

### Filters not updating?
- Clear browser cache
- Refresh the page (F5)
- Check browser console for errors

### Pagination not working?
- Ensure `per_page` value is 5, 10, or 20
- Check that page number is within valid range

### No filter options showing?
- Ensure articles exist in the database
- Check that `/api/article-filters` endpoint is responding
- Verify database connection

## Keyboard Navigation

All interactive elements are accessible via keyboard:
- Tab: Move between filters and buttons
- Enter: Activate buttons and dropdowns
- Arrow Keys: Navigate dropdown options
- Escape: Close dropdowns (if applicable)