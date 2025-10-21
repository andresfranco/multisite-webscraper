# Grid Search - Quick Reference Card

## 🔍 Search
**How:** Type in the search box at the top
**Searches:** Article titles and author names
**Case:** Insensitive (type "python" or "Python")
**Speed:** Instant results

```
Search Example:
Search term: "machine learning"
Results: All articles mentioning machine learning in title or by authors with that phrase
```

## 🎯 Filters

### Author Filter
- Click dropdown → Select author → Results update
- Works with other filters

### Date Filter
- Click dropdown → Select date → Results update
- Dates sorted newest first

### Website Filter
- Click dropdown → Select source → Results update
- Helps compare sources

### Combining Filters
```
Filter 1: Author = "John Smith"
Filter 2: Date = "2024-01-15"
Filter 3: Website = "example.com"
Result: Shows ONLY articles by John from that date on that website
```

## 📖 Pagination

### Page Size
- Click "Per Page" dropdown
- Choose: 5, 10 (default), or 20 items
- Grid updates immediately

### Navigate Pages
- **Previous Button**: Go back one page (disabled on page 1)
- **Next Button**: Go forward one page (disabled on last page)
- **Page Numbers**: Click any number to jump there
- Current page highlighted in **orange**

### Page Info
Displays: `Page 1 of 5`
Displays: `Showing 1–10 of 47 articles`

## 🔄 Clear Everything
**Button:** "Clear Filters"
**Does:** Resets search, all filters, and pagination
**When to use:** Start fresh or remove all restrictions

## 📊 Active Filters Display
Shows what you've applied:
```
Filters applied: Search: "python" • Author: "John" • Date: "2024-01-15"
```
Hidden when no filters active

## ⚡ Quick Tips

### Fast Search
- Type just a few letters for instant results
- Works on title and author

### Narrow Results
- Use all 4 filters together for precise results
- Each filter narrows down results more

### Explore Collection
- Change page size to see more at once
- Use pagination to browse everything

### Change Mind
- Clear Filters button resets everything in one click
- Start over anytime

## 🎨 Visual Cues

| Icon | Means |
|------|-------|
| 🔍 Search | Search articles |
| ✍️ Pen | Filter by author |
| 📅 Calendar | Filter by date |
| 🌐 Globe | Filter by website |
| 📄 List | Choose items per page |
| ✕ Clear | Reset all filters |
| ◀ Prev | Previous page |
| ▶ Next | Next page |

## 📱 Mobile
- All filters work on phones/tablets
- Touch-friendly buttons
- Filters stack vertically on small screens

## ❓ No Results?
1. **Check filters** - Might be too restrictive
2. **Try simpler search** - Use fewer words
3. **Click Clear Filters** - Reset and start over
4. **Check article count** - Make sure database has articles

## ⌨️ Keyboard Shortcuts
- **Tab** - Move between controls
- **Enter** - Click buttons
- **Arrow Keys** - Navigate dropdown options

## 🚀 Common Workflows

### Find All by One Author
1. Click Author dropdown
2. Select author name
3. Done!

### Search Topic + Date
1. Type topic in search (e.g., "AI")
2. Click Date dropdown
3. Select date
4. Results filtered to that topic and date

### Browse One Website
1. Click Website dropdown
2. Select website
3. Use pagination to browse all
4. Change page size if needed

### See Everything Again
1. Click "Clear Filters"
2. All restrictions removed

## 📈 Understanding Numbers

**Results Display:**
```
Showing 1–10 of 47 articles
   ↑       ↑      ↑
   |       |      |
 Start   End    Total
```

**Pagination:**
```
Page 1 of 5
   ↑     ↑
Current  Total
Pages
```

## 🔧 Not Working?

| Issue | Solution |
|-------|----------|
| Filters empty | May have no articles (try scraping more) |
| No results | Filters too restrictive - clear them |
| Slow loading | Try smaller page size |
| Not updating | Refresh page (F5) |

## ⭐ Pro Tips

1. **Combine filters** - Use multiple at once for best results
2. **Start broad** - Search without filters, then narrow down
3. **Adjust page size** - Use 20 items to see more at once
4. **Page numbers** - Click directly instead of using Previous/Next
5. **Check filter status** - Always visible, shows what's applied

## 📚 For More Information

- User Guide: See GRID_QUICKSTART.md
- Full Features: See GRID_FEATURES.md
- System Info: See docs/README.md

---

**Quick Tip:** All filters work together with AND logic.  
Select multiple filters to narrow results further.
