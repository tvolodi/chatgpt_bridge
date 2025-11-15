# REQ-301: Header Bar at Top

**Registry Entry:** See `docs/01_requirements_registry.md` (Line 54)  
**Functionality Reference:** `specifications/functionality.md` Section 3.1.1, 3.2  
**Document Version:** 1.0  
**Last Updated:** November 15, 2025  
**Status:** implemented  

---

## 1. Overview

### 1.1 Brief Description
Implement a fixed navigation header bar at the top of the application (~80px height) containing application branding, search capability, AI provider selector, settings access, and user menu - providing quick access to all major application functions.

### 1.2 Business Value
- **Discoverability:** All major functions immediately visible (search, settings, provider choice)
- **Context:** Always shows current provider and app state
- **Navigation:** Single source of truth for switching providers and accessing settings
- **Professional:** Modern UI pattern that users expect

### 1.3 Scope & Boundaries

**In Scope:**
- ✅ Fixed-height header bar (80px) at application top
- ✅ Application title/logo (top-left)
- ✅ Search bar with dropdown results
- ✅ AI provider selector with status
- ✅ Settings button linking to settings page
- ✅ User menu dropdown (basic in single-user mode)
- ✅ Status indicators for providers
- ✅ Responsive layout on different screen sizes

**Out of Scope:**
- ❌ Mobile-specific header variations (Phase 2)
- ❌ Header customization/themes (Phase 2)
- ❌ Advanced user profile features (out of scope - single user)
- ❌ Notifications in header (Phase 2)
- ❌ Header collapse on scroll (Phase 2)

---

## 2. Functional Requirements

### 2.1 Core Requirements

#### REQ-301-A: Fixed Header Bar Structure
- **Description:** 80px fixed height header spanning full application width
- **Layout:** Flex container with left, center, and right sections
- **Position:** Fixed to top with z-index above all content
- **Background:** Dark theme (slate-800) matching application
- **Sections:**
  - Left: Logo + Application title
  - Center: Search bar (takes available space)
  - Right: Provider selector, Settings, User menu
- **Acceptance Criteria:**
  - ✓ Header is exactly 80px tall
  - ✓ Stays visible during scrolling
  - ✓ Content below header doesn't overlap
  - ✓ Responsive on different screen widths

#### REQ-301-B: Application Title and Logo
- **Description:** Display app branding and title
- **Implementation:**
  - Logo image or icon (placeholder available)
  - Text "AI Chat Assistant" in header font
  - Location: Top-left of header
  - Spacing: 16px padding from left edge
  - Click behavior: Optional - can navigate to home
- **CSS Classes:** Using Tailwind
  ```html
  <div className="flex items-center gap-4 px-4">
    <div className="w-8 h-8 bg-blue-600 rounded" /> {/* Logo placeholder */}
    <h1 className="text-xl font-bold text-white">AI Chat Assistant</h1>
  </div>
  ```
- **Acceptance Criteria:**
  - ✓ Logo visible and properly sized
  - ✓ Title text clear and readable
  - ✓ Consistent with app theming
  - ✓ No overflow on narrow screens

#### REQ-301-C: Search Bar with Dropdown Results
- **Description:** Search input for finding messages and files
- **Implementation:**
  - Input field with placeholder "Search messages and files..."
  - Minimum width: 300px when screen space allows
  - Dropdown appears below input on focus
  - Shows matching messages and files
  - Keyboard navigation (arrow keys to select, Enter to open)
- **Features:**
  - Real-time search as user types
  - Debounced API calls (300ms delay)
  - Results grouped by type (Messages | Files)
  - Click to open result
  - Escape to close dropdown
- **API Integration:**
  - GET `/api/search?q={query}` - Search messages and files
  - Returns: `{ messages: [...], files: [...] }`
- **Acceptance Criteria:**
  - ✓ Search input visible and functional
  - ✓ Dropdown shows results when typing
  - ✓ Can click result to navigate
  - ✓ Keyboard navigation works
  - ✓ Debouncing prevents excessive API calls

#### REQ-301-D: AI Provider Selector Dropdown
- **Description:** Dropdown showing available providers and allowing quick selection
- **Display:**
  - Current provider name and icon
  - Dropdown arrow indicating expandable menu
  - Configuration status indicator (✓ configured or ✗ not configured)
- **Dropdown Content:**
  - List of all available providers
  - Shows provider name, description, model count
  - Green checkmark for currently selected
  - Red warning icon for unconfigured providers (disabled)
  - Visual distinction for configured vs unconfigured
- **Behavior:**
  - Click to toggle dropdown
  - Click provider to select (only if configured)
  - Unconfigured providers show tooltip: "Configure in Settings"
  - Selection persists across sessions (localStorage)
  - Invalid selection falls back to first configured provider
- **CSS Styling:**
  ```html
  <div className="relative">
    <button className="flex items-center gap-2 px-3 py-2 rounded bg-slate-700">
      <Settings size={16} />
      <span>{selectedProvider?.name}</span>
      <ChevronDown size={16} />
    </button>
    {isOpen && (
      <div className="absolute top-full right-0 mt-1 bg-slate-800 border border-slate-700 rounded shadow-lg w-64">
        {/* Dropdown items */}
      </div>
    )}
  </div>
  ```
- **Acceptance Criteria:**
  - ✓ Current provider always visible
  - ✓ Dropdown shows all available providers
  - ✓ Can switch providers with one click
  - ✓ Configuration status clearly shown
  - ✓ Dropdown closes after selection
  - ✓ Selection persists on page reload

#### REQ-301-E: Settings Button
- **Description:** Button linking to application settings page
- **Implementation:**
  - Icon: Gear/cog icon (lucide-react `Settings` component)
  - Position: Header right section, before user menu
  - Behavior: Click navigates to `/settings` route
  - Hover effect: Background highlight
  - Accessibility: aria-label="Settings", keyboard accessible
- **CSS:**
  ```html
  <button 
    onClick={() => navigate('/settings')}
    aria-label="Settings"
    className="p-2 rounded hover:bg-slate-700 transition-colors"
  >
    <Settings size={20} />
  </button>
  ```
- **Acceptance Criteria:**
  - ✓ Button visible and clickable
  - ✓ Clicking navigates to settings
  - ✓ Settings page loads correctly
  - ✓ Back button returns to chat
  - ✓ Accessibility attributes present

#### REQ-301-F: User Menu Dropdown
- **Description:** User profile menu in header (minimal for single-user)
- **Current Implementation:**
  - Shows "User" or profile indicator
  - Dropdown with: Profile info, Logout option
  - Limited features (single-user application)
- **Future Expansion:**
  - User preferences quick access
  - Theme toggle
  - Help/About
- **CSS:**
  ```html
  <div className="relative">
    <button className="flex items-center gap-2 px-3 py-2 rounded hover:bg-slate-700">
      <User size={20} />
    </button>
    {isOpen && (
      <div className="absolute top-full right-0 mt-1 bg-slate-800 rounded shadow-lg">
        <div className="px-4 py-2 text-sm">Local User</div>
        <button className="w-full text-left px-4 py-2 hover:bg-slate-700">Logout</button>
      </div>
    )}
  </div>
  ```
- **Acceptance Criteria:**
  - ✓ Menu accessible from header
  - ✓ Shows user indicator
  - ✓ Logout functionality works
  - ✓ Menu closes after action

### 2.2 Technical Constraints

- **Fixed Height:** Exactly 80px (no flexibility for content below)
- **Z-index:** Must be above all page content (z-50 or higher)
- **Performance:** All dropdown interactions must be < 100ms
- **Accessibility:** All interactive elements must be keyboard navigable
- **Responsive:** Must work from 768px screen width upward
- **Search Debounce:** 300ms minimum delay between API calls

### 2.3 User Interactions

```
User Journey:
1. App loads → Header appears with logo, search, provider, settings
2. User sees current provider selected (e.g., "OpenAI")
3. User types in search → Dropdown with results appears
4. User clicks result → Navigates to that message/file
5. User clicks provider dropdown → List of providers appears
6. User clicks different provider → Selected provider updates
7. User clicks settings gear → Settings page opens
8. User clicks back → Returns to chat with same header
```

---

## 3. Implementation Details

### 3.1 Backend Implementation

**No direct backend implementation** - Header is purely frontend with API calls for search and provider data.

**API Endpoints Used:**
- GET `/api/search?q={query}` - Provides search results
- GET `/api/ai-providers` - List available providers
- PUT `/api/ai-providers/{id}/select` - Update selected provider

### 3.2 Frontend Implementation

**Components Affected:**
- `MainLayout.tsx` - Contains header component (lines 20-150)
- `Header.tsx` - Dedicated header component
- `ProviderSelector.tsx` - Provider dropdown logic
- `SearchBar.tsx` - Search input with results

**Key Components:**

```typescript
// Header.tsx (lines 1-80)
export const Header: React.FC = () => {
  const navigate = useNavigate()
  const { selectedProvider, setSelectedProvider } = useProvidersStore()
  const [searchQuery, setSearchQuery] = useState('')
  
  return (
    <header className="fixed top-0 left-0 right-0 h-20 bg-slate-800 border-b border-slate-700 flex items-center px-6 gap-6 z-50">
      {/* Left: Logo and title */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-blue-600 rounded" />
        <h1 className="text-lg font-bold text-white">AI Chat Assistant</h1>
      </div>
      
      {/* Center: Search bar */}
      <div className="flex-1">
        <SearchBar value={searchQuery} onChange={setSearchQuery} />
      </div>
      
      {/* Right: Controls */}
      <div className="flex items-center gap-4">
        <ProviderSelector 
          selectedProviderId={selectedProvider?.id}
          onProviderChange={setSelectedProvider}
        />
        <button 
          onClick={() => navigate('/settings')}
          className="p-2 rounded hover:bg-slate-700"
        >
          <Settings size={20} className="text-slate-300" />
        </button>
        <UserMenu />
      </div>
    </header>
  )
}
```

```typescript
// ProviderSelector.tsx (lines 30-120)
export const ProviderSelector: React.FC<ProviderSelectorProps> = ({
  selectedProviderId,
  onProviderChange
}) => {
  const { providers, getActiveProviders, getProviderConfig } = useProvidersStore()
  const [isOpen, setIsOpen] = useState(false)
  
  const activeProviders = getActiveProviders()
  const selectedProvider = providers.find(p => p.id === selectedProviderId)
  
  const handleSelect = (providerId: string) => {
    onProviderChange(providerId)
    setIsOpen(false)
  }
  
  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded bg-slate-700 hover:bg-slate-600"
      >
        <Settings size={16} className="text-slate-300" />
        <span className="text-sm text-slate-100">{selectedProvider?.name || 'Select'}</span>
        <ChevronDown size={16} className="text-slate-400" />
      </button>
      
      {isOpen && (
        <div className="absolute right-0 top-full mt-1 bg-slate-800 border border-slate-700 rounded shadow-lg w-64 z-50">
          {activeProviders.map(provider => (
            <button
              key={provider.id}
              onClick={() => handleSelect(provider.id)}
              className={`w-full text-left px-4 py-2 hover:bg-slate-700 flex items-center justify-between
                ${selectedProvider?.id === provider.id ? 'bg-slate-700 text-blue-400' : 'text-slate-200'}
              `}
            >
              <span>{provider.name}</span>
              {selectedProvider?.id === provider.id && <Check size={16} />}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
```

```typescript
// SearchBar.tsx (lines 1-100)
export const SearchBar: React.FC<SearchBarProps> = ({
  value,
  onChange
}) => {
  const [results, setResults] = useState<SearchResults | null>(null)
  const [isOpen, setIsOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  
  const debouncedSearch = useMemo(
    () => debounce(async (query: string) => {
      if (!query.trim()) {
        setResults(null)
        return
      }
      setIsLoading(true)
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`)
      const data = await response.json()
      setResults(data)
      setIsLoading(false)
    }, 300),
    []
  )
  
  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value
    onChange(newValue)
    setIsOpen(true)
    debouncedSearch(newValue)
  }
  
  return (
    <div className="relative flex-1 max-w-md">
      <input
        type="text"
        value={value}
        onChange={handleChange}
        onFocus={() => setIsOpen(true)}
        placeholder="Search messages and files..."
        className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      
      {isOpen && results && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-slate-800 border border-slate-700 rounded shadow-lg z-50 max-h-96 overflow-y-auto">
          {isLoading && <div className="px-4 py-2 text-slate-400">Searching...</div>}
          {/* Results grouped by type */}
          {results.messages?.length > 0 && (
            <div>
              <div className="px-4 py-2 text-xs font-semibold text-slate-400">Messages</div>
              {results.messages.map(msg => (
                <SearchResult key={msg.id} result={msg} type="message" />
              ))}
            </div>
          )}
          {results.files?.length > 0 && (
            <div>
              <div className="px-4 py-2 text-xs font-semibold text-slate-400">Files</div>
              {results.files.map(file => (
                <SearchResult key={file.id} result={file} type="file" />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
```

### 3.3 API Endpoints

- **GET** `/api/search?q={query}` - Search messages and files
  - Response: `{ messages: Message[], files: File[] }`
  - Usage: SearchBar component

- **GET** `/api/ai-providers` - List available providers
  - Response: `[{ id, name, description, modelCount, isConfigured }]`
  - Usage: ProviderSelector component

- **PUT** `/api/ai-providers/{id}/select` - Set selected provider
  - Request: `{ providerId: string }`
  - Response: `{ selectedProvider: Provider }`
  - Persists to localStorage on frontend

---

## 4. Testing Strategy

### 4.1 Unit Tests

**Test File:** `tests/frontend/components/Header.test.tsx`

- **test_header_renders:** Header component renders without errors
- **test_logo_displays:** Logo and title visible
- **test_search_input_visible:** Search input present and functional
- **test_provider_selector_dropdown:** Dropdown shows providers
- **test_settings_button_navigates:** Settings button navigates to /settings

### 4.2 Functional Tests

**Test File:** `tests/frontend/functional/test_header_interactions.tsx`

- **test_provider_switch:** User can switch providers from dropdown
- **test_search_dropdown_opens:** Search dropdown appears on input
- **test_search_results_display:** Results show in grouped list
- **test_responsive_layout:** Header adapts to screen width

### 4.3 Test Coverage

- **Target:** 85% coverage for header components
- **Critical paths:** Search, provider selection, settings navigation

---

## 5. Dependencies & Relationships

### 5.1 Depends On

| REQ-ID | Title | Reason |
|--------|-------|--------|
| REQ-305 | Application title and logo | Displayed in header |
| REQ-306 | Search bar with results | Core header component |
| REQ-307 | AI provider selector | Core header component |
| REQ-308 | Settings button | Core header component |

### 5.2 Enables / Unblocks

| REQ-ID | Title | How |
|--------|-------|-----|
| REQ-302-309 | All header-related requirements | Implemented as part of header |
| REQ-506 | Provider status display | Shown in provider dropdown |
| REQ-507 | Provider selector in header | Implemented here |

---

## 6. Known Issues & Notes

- Status bar below header (REQ-302) currently minimal
- Mobile responsiveness deferred to Phase 2
- User menu features limited by single-user design

---

## 7. Acceptance Checklist

- [x] Header fixed at 80px height
- [x] All elements visible and functional
- [x] Search works with debouncing
- [x] Provider selection persists
- [x] Settings navigation works
- [x] Responsive on standard widths
- [x] Keyboard navigation supported
- [x] Tests passing

---

## Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-15 | Development Team | Initial detailed specification |

---

**Status:** Ready for team use
