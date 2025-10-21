# Multiple Filters Documentation

## Overview

The Article Library now features an advanced **Multiple Filters** system that allows users to apply, combine, and manage multiple filters simultaneously. Users can easily add, remove, and track active filters through an intuitive visual interface featuring interactive filter chips.

## Features

### 1. **Filter Types**

The system supports three main filter types:

- **Author Filter**: Search articles by author name (partial matching)
- **Date Range Filter**: Filter articles by publication date (from/to)
- **Website Filter**: Filter articles by source website (partial matching)

### 2. **Active Filter Chips**

When filters are applied, they appear as visual chips/tags below the search controls:

- **Visual Representation**: Each chip displays an icon, filter label, and remove button
- **Individual Removal**: Click the X button on any chip to remove that specific filter
- **Smooth Animations**: Chips animate in when added and out when removed
- **Responsive Design**: Chips adapt to different screen sizes

### 3. **Filter Management**

#### Adding Filters

1. Enter values in the filter input fields:
   - Type an author name in the "Author" field
   - Select a date range using "Date From" and "Date To" fields
   - Type a website URL in the "Website" field

2. Click the **"Search"** button to apply the filters

3. Active filters will appear as chips below the search controls

#### Removing Filters

There are multiple ways to remove filters:

1. **Individual Removal**: Click the X button on any filter chip
2. **Clear All**: Click the "Clear" button to remove all filters at once
3. **Manual Editing**: Edit the input field and click "Search" again to replace the filter

#### Replacing Filters

When you apply a new filter of the same type:
- The old filter is automatically replaced with the new one
- Only one filter per type can be active at a time
- For date ranges, both "From" and "To" are considered part of the same filter

## User Interface

### Filter Control Section

```html
<div class="filters-section">
  <div class="filters-container">
    <!-- Author Filter Input -->
    <div class="filter-group">
      <label for="authorInput">Author</label>
      <input type="text" id="authorInput" placeholder="Type author name..." />
    </div>

    <!-- Date Range Inputs -->
    <div class="filter-group">
      <label for="dateFromInput">Date From</label>
      <input type="date" id="dateFromInput" />
    </div>

    <div class="filter-group">
      <label for="dateToInput">Date To</label>
      <input type="date" id="dateToInput" />
    </div>

    <!-- Website Filter Input -->
    <div class="filter-group">
      <label for="websiteInput">Website</label>
      <input type="text" id="websiteInput" placeholder="Type website URL..." />
    </div>

    <!-- Per Page Selector -->
    <div class="filter-group">
      <label for="perPageSelector">Per Page</label>
      <select id="perPageSelector">
        <option value="5">5 Items</option>
        <option value="10" selected>10 Items</option>
        <option value="20">20 Items</option>
      </select>
    </div>
  </div>

  <!-- Action Buttons -->
  <div class="filter-actions">
    <button id="searchBtn" class="btn btn-search">
      <i class="fas fa-search"></i> Search
    </button>
    <button id="clearFiltersBtn" class="btn btn-filter-clear">
      <i class="fas fa-times-circle"></i> Clear
    </button>
  </div>
</div>
```

### Active Filter Chips Section

```html
<div id="filterChipsContainer" class="filter-chips-container">
  <div class="filter-chips-label">
    <i class="fas fa-filter"></i> Active Filters:
  </div>
  <div id="filterChips" class="filter-chips">
    <!-- Filter chips are rendered here dynamically -->
  </div>
</div>
```

## CSS Styling

### Filter Chips Classes

- `.filter-chips-container`: Main container for filter chips display
- `.filter-chips-label`: Label text with icon
- `.filter-chips`: Flex container for individual chips
- `.filter-chip`: Individual filter chip with styling
- `.filter-chip-icon`: Icon display within chip
- `.filter-chip-text`: Text label with ellipsis for overflow
- `.filter-chip-remove`: Remove button within chip

### Animations

- **Slide Down**: Filter chips section animates in from top when filters are applied
- **Chip Appear**: Individual chips scale and fade in when added
- **Hover Effect**: Remove button expands on hover for better UX
- **Active State**: Remove button has visual feedback when clicked

## JavaScript Implementation

### Core Functions

#### `addFilter(type, value, label, icon, apiParam)`

Adds a new filter to the active filters list.

**Parameters:**
- `type` (string): Filter type ('author', 'date_range', 'website')
- `value` (string|object): Filter value (string for most, object for date_range)
- `label` (string): Display label for the chip
- `icon` (string): FontAwesome icon class
- `apiParam` (string): API parameter name

**Behavior:**
- Generates unique filter ID
- Replaces existing filter of the same type
- Re-renders filter chips
- Resets to page 1
- Loads filtered articles

**Example:**
```javascript
addFilter(
  'author',
  'John Doe',
  'Author: "John Doe"',
  'fas fa-pen-fancy',
  'author'
);
```

#### `removeFilter(filterId)`

Removes a specific filter by its ID.

**Parameters:**
- `filterId` (string): Unique filter ID

**Behavior:**
- Finds and removes the filter from active filters
- Clears the corresponding input field
- Re-renders filter chips
- Resets to page 1
- Loads filtered articles

#### `clearAllFilters()`

Clears all active filters and resets the UI.

**Behavior:**
- Empties the active filters array
- Clears all input fields
- Resets pagination to page 1
- Re-renders filter chips (hides container)
- Loads all articles

#### `renderFilterChips()`

Renders the visual filter chips based on active filters.

**Behavior:**
- Creates chip elements for each active filter
- Adds remove buttons with click handlers
- Shows/hides the chips container based on filter count
- Applies animations for smooth transitions

### Data Structure

Active filters are stored as an array of filter objects:

```javascript
const filterObject = {
  id: 'author-1234567890',           // Unique identifier
  type: 'author',                    // Filter type
  label: 'Author: "John Doe"',      // Display label
  icon: 'fas fa-pen-fancy',         // Icon class
  value: 'John Doe',                // Filter value
  apiParam: 'author'                // API parameter name
};

const dateFilterObject = {
  id: 'date_range-1234567890',
  type: 'date_range',
  label: 'Date: 2024-01-01 to 2024-12-31',
  icon: 'fas fa-calendar-alt',
  value: {
    from: '2024-01-01',
    to: '2024-12-31'
  },
  apiParam: 'date_range'
};
```

## API Integration

### Query Parameters

The API endpoint `/api/articles` accepts the following query parameters:

- `author` (string, optional): Filter by author name (partial match)
- `date_from` (string, optional): Start date in YYYY-MM-DD format
- `date_to` (string, optional): End date in YYYY-MM-DD format
- `website` (string, optional): Filter by website URL (partial match)
- `page` (integer, default: 1): Page number for pagination
- `per_page` (integer, default: 10): Items per page (5, 10, or 20)

### Example API Calls

**Single Filter:**
```
GET /api/articles?author=John%20Doe&page=1&per_page=10
```

**Multiple Filters:**
```
GET /api/articles?author=John%20Doe&website=medium.com&date_from=2024-01-01&page=1&per_page=10
```

**Filter with Pagination:**
```
GET /api/articles?date_from=2024-01-01&date_to=2024-12-31&page=2&per_page=20
```

## Usage Examples

### Example 1: Filter by Author

1. Type "Jane Smith" in the Author field
2. Click "Search"
3. A filter chip appears showing "Author: Jane Smith"
4. The grid updates to show only articles by Jane Smith
5. To remove, click the X on the chip

### Example 2: Filter by Date Range

1. Select "2024-01-01" in the "Date From" field
2. Select "2024-12-31" in the "Date To" field
3. Click "Search"
4. A filter chip appears showing "Date: 2024-01-01 to 2024-12-31"
5. The grid shows articles from that date range

### Example 3: Multiple Filters

1. Type "Sarah Johnson" in Author field
2. Type "techblog.com" in Website field
3. Click "Search"
4. Two filter chips appear
5. The grid shows articles by Sarah Johnson from techblog.com
6. Click X on either chip to remove that specific filter

### Example 4: Replace a Filter

1. "Author: John Doe" filter is active
2. Type "Jane Smith" in Author field
3. Click "Search"
4. The chip updates to "Author: Jane Smith"
5. Results update accordingly

### Example 5: Clear All Filters

1. Multiple filters are active
2. Click "Clear" button
3. All input fields clear
4. Filter chips disappear
5. All articles are displayed again

## Responsive Design

### Desktop (1024px and above)

- Filter controls display in a compact horizontal layout
- Filter chips display inline with wrapping
- Full-width labels and spacing

### Tablet (768px - 1024px)

- Filter controls stack slightly with adjusted spacing
- Filter chips wrap as needed
- Smaller font sizes for space efficiency

### Mobile (640px - 768px)

- Filter controls stack vertically
- Filter chips display with reduced padding
- Adjusted icon sizes and font sizes
- Remove buttons remain easy to tap

### Small Mobile (below 640px)

- Maximum spacing optimization
- Full-width filter inputs
- Stacked filter chips
- Optimized for touch interaction

## Browser Compatibility

- **Chrome/Edge**: Full support
- **Firefox**: Full support
- **Safari**: Full support (iOS 12+)
- **Mobile Browsers**: Full support with touch-friendly interactions

## Performance Considerations

- **Debouncing**: Filter searches directly update results (no debounce needed as search is explicit)
- **Pagination Reset**: Automatically resets to page 1 when filters change
- **Lazy Rendering**: Filter chips are only rendered when needed
- **Animation Performance**: CSS animations use GPU acceleration (transform, opacity)

## Accessibility

- **ARIA Labels**: All interactive elements have proper aria-labels
- **Keyboard Navigation**: All buttons are keyboard accessible
- **Color Contrast**: Filter chips meet WCAG AA standards
- **Focus States**: Clear focus indicators on all interactive elements
- **Screen Readers**: Filter status is conveyed through semantic HTML and aria-labels

## Troubleshooting

### Filters Not Applying

**Issue**: Filter chip appears but articles don't filter
- Ensure the API endpoint is properly configured
- Check browser console for JavaScript errors
- Verify the search button was clicked

### Filters Disappearing

**Issue**: Filter chips disappear after page reload
- This is expected behavior (filters are session-based)
- Filters are not persisted across page refreshes
- To persist filters, implement localStorage

### Chip Remove Button Not Working

**Issue**: Clicking X on chip doesn't remove filter
- Check that JavaScript is enabled
- Verify no JavaScript errors in console
- Try using the "Clear" button instead

## Future Enhancements

Possible improvements for future versions:

1. **Filter Presets**: Save and load filter combinations
2. **Filter History**: Quick access to recently used filters
3. **Advanced Filters**: More complex filtering options (AND/OR logic)
4. **Filter Persistence**: Save filters using localStorage
5. **Export Filters**: Export filtered results to CSV/JSON
6. **Filter Suggestions**: Auto-complete for author/website filters
7. **Filter Analytics**: Track which filters are most used

## Code Examples

### Example: Adding a Custom Filter Type

To add a new filter type, modify the search button event listener:

```javascript
searchBtn.addEventListener("click", () => {
  // ... existing code ...

  // Add new filter type
  const statusValue = statusInput.value.trim();
  if (statusValue) {
    addFilter(
      'status',
      statusValue,
      `Status: "${statusValue}"`,
      'fas fa-flag',
      'status'
    );
  }

  // ... rest of code ...
});
```

### Example: Programmatic Filter Addition

```javascript
// Add filters programmatically
addFilter(
  'author',
  'Jane Doe',
  'Author: "Jane Doe"',
  'fas fa-pen-fancy',
  'author'
);

// Add date range
addFilter(
  'date_range',
  { from: '2024-01-01', to: '2024-06-30' },
  'Date: 2024-01-01 to 2024-06-30',
  'fas fa-calendar-alt',
  'date_range'
);
```

## Maintenance Notes

- Filter chip animations are defined in `grid.css` with `@keyframes`
- Active filters are managed in memory (reset on page load)
- API filtering is handled server-side in `/api/articles` endpoint
- All DOM references are cached at script load for performance

## See Also

- [Grid Enhancement Summary](../GRID_ENHANCEMENT_SUMMARY.md)
- [UI Changes Summary](../UI_CHANGES_SUMMARY.md)
- [Quick Reference](../QUICK_REFERENCE.md)