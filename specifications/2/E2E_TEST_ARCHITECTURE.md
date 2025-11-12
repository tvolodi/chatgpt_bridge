# E2E Tests Architecture Overview

## File Structure

```
chat-provider-integration.e2e.test.tsx (513 lines)
├── Imports
│   ├── Vitest (describe, it, expect, beforeEach, afterEach, vi)
│   ├── React Testing Library (render, screen, waitFor, renderHook)
│   ├── User Event (for interactions)
│   ├── React Query (QueryClient, QueryClientProvider)
│   ├── MSW (http, HttpResponse, setupServer)
│   ├── Components (ChatPage)
│   ├── Stores (useProvidersStore, useUserStateStore)
│   └── API (providersAPI)
│
├── TYPE DEFINITIONS
│   ├── AIModel interface
│   │   ├── id: string
│   │   ├── name: string
│   │   ├── displayName: string
│   │   ├── description: string
│   │   ├── contextWindow: number
│   │   ├── maxTokens: number
│   │   ├── pricing?: { input: number; output: number }
│   │   └── capabilities: string[]
│   │
│   └── AIProvider interface
│       ├── id: string (UUID)
│       ├── name: string
│       ├── displayName: string
│       ├── description: string
│       ├── baseUrl: string
│       ├── models: AIModel[]
│       ├── isActive: boolean
│       ├── createdAt: string (ISO)
│       └── updatedAt: string (ISO)
│
├── MOCK DATA
│   └── MOCK_PROVIDERS: AIProvider[]
│       ├── OpenAI Provider
│       │   ├── 2 models (GPT-4, GPT-3.5 Turbo)
│       │   ├── Pricing info included
│       │   └── Real UUID format
│       │
│       └── Anthropic Provider
│           ├── 2 models (Claude 3 Opus, Claude 3 Sonnet)
│           ├── Pricing info included
│           └── Real UUID format
│
├── MSW MOCK SERVER
│   ├── setupServer()
│   ├── GET /api/ai-providers
│   │   ├── Query params support (include_inactive)
│   │   ├── Filter logic
│   │   └── Response: AIProvider[]
│   │
│   ├── GET /api/ai-providers/:provider_id
│   │   ├── Lookup provider
│   │   ├── Return 404 if not found
│   │   └── Response: AIProvider | error
│   │
│   ├── POST /api/ai-providers
│   │   ├── Parse request body
│   │   ├── Generate UUID
│   │   ├── Return 201 Created
│   │   └── Response: AIProvider (new)
│   │
│   ├── PUT /api/ai-providers/:provider_id
│   │   ├── Lookup provider
│   │   ├── Merge updates
│   │   ├── Update timestamp
│   │   └── Response: AIProvider (updated)
│   │
│   └── DELETE /api/ai-providers/:provider_id
│       ├── Lookup provider
│       ├── Return 404 if not found
│       └── Response: { message: "..." }
│
├── TEST SETUP
│   ├── beforeEach()
│   │   ├── server.listen() - Start MSW
│   │   ├── Reset store state
│   │   ├── Fetch providers via API
│   │   └── Populate store from API response
│   │
│   ├── afterEach()
│   │   ├── server.resetHandlers() - Clear overrides
│   │   └── server.close() - Stop MSW
│   │
│   └── renderWithProviders()
│       ├── Create QueryClient
│       ├── Wrap component in QueryClientProvider
│       └── Return rendered component
│
├── TEST SUITES
│   ├── Loading Providers from Backend API (3 tests)
│   │   ├── Fetch and display providers from API
│   │   ├── Include models for each provider
│   │   └── Include pricing information
│   │
│   ├── Provider Selector in Chat Header (2 tests)
│   │   ├── Display selector with active provider
│   │   └── Open dropdown showing all providers
│   │
│   ├── Real Frontend-Backend Communication (5 tests)
│   │   ├── Handle provider switching
│   │   ├── Fetch specific provider details
│   │   ├── Create new provider
│   │   ├── Update provider
│   │   └── Delete provider
│   │
│   └── Provider Availability Based on API Keys (2 tests)
│       ├── Display availability based on configuration
│       └── Handle unavailable providers
│
└── TEST DETAILS

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ TEST EXECUTION                                               │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ beforeEach() SETUP                                           │
│  1. Reset stores                                             │
│  2. Call providersAPI.listProviders()                        │
│  3. Update store with response                               │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ HTTP REQUEST (via providersAPI)                              │
│                                                              │
│  GET http://localhost:8000/api/ai-providers                 │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ MSW MOCK SERVER                                              │
│                                                              │
│  http.get('http://localhost:8000/api/ai-providers' => {     │
│    return HttpResponse.json(MOCK_PROVIDERS)                 │
│  })                                                          │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ HTTP RESPONSE                                                │
│                                                              │
│  Status: 200 OK                                              │
│  Body: [{ id, name, displayName, models, ... }]             │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ STORE UPDATE (via Zustand)                                   │
│                                                              │
│  useProvidersStore.setState({                               │
│    providers: response.data,                                │
│    currentProvider: response.data[0]                        │
│  })                                                          │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ COMPONENT RENDER                                             │
│                                                              │
│  <ChatPage />                                                │
│    └── reads from store                                      │
│        └── displays providers in UI                          │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ ASSERTIONS                                                   │
│                                                              │
│  expect(result.current.providers).toEqual(MOCK_PROVIDERS)   │
│  expect(screen.getByText('OpenAI')).toBeInTheDocument()     │
└─────────────────────────────────────────────────────────────┘
```

## API Call Flow

### 1. GET /api/ai-providers (List)
```typescript
// Frontend calls
const response = await providersAPI.listProviders()

// MSW intercepts
http.get('http://localhost:8000/api/ai-providers', ({ request }) => {
  // Check query params
  const url = new URL(request.url)
  const includeInactive = url.searchParams.get('include_inactive') === 'true'
  
  // Filter based on param
  const providers = includeInactive 
    ? MOCK_PROVIDERS 
    : MOCK_PROVIDERS.filter(p => p.isActive)
  
  // Return response
  return HttpResponse.json(providers)
})

// Store updates
useProvidersStore.setState({ providers: response.data })
```

### 2. GET /api/ai-providers/:id (Get One)
```typescript
// Frontend calls
const response = await providersAPI.getProvider(provider.id)

// MSW intercepts
http.get('http://localhost:8000/api/ai-providers/:provider_id', ({ params }) => {
  const provider = MOCK_PROVIDERS.find(p => p.id === params.provider_id)
  
  if (!provider) {
    return HttpResponse.json(
      { detail: `AI provider ${params.provider_id} not found` },
      { status: 404 }
    )
  }
  
  return HttpResponse.json(provider)
})

// Test verifies
expect(response.data.id).toBe(provider.id)
```

### 3. POST /api/ai-providers (Create)
```typescript
// Frontend calls
const response = await providersAPI.createProvider({
  name: 'google',
  displayName: 'Google AI',
  baseUrl: '...',
  models: [],
  isActive: true
})

// MSW intercepts
http.post('http://localhost:8000/api/ai-providers', async ({ request }) => {
  const body = await request.json()
  
  // Create new provider
  const newProvider: AIProvider = {
    id: `550e8400-${Date.now()}`,
    ...body,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }
  
  return HttpResponse.json(newProvider, { status: 201 })
})

// Test verifies
expect(response.status).toBe(201)
expect(response.data).toHaveProperty('id')
```

### 4. PUT /api/ai-providers/:id (Update)
```typescript
// Frontend calls
const response = await providersAPI.updateProvider(id, {
  displayName: 'Updated Name',
  description: 'Updated description'
})

// MSW intercepts
http.put('http://localhost:8000/api/ai-providers/:provider_id', async ({ params, request }) => {
  const provider = MOCK_PROVIDERS.find(p => p.id === params.provider_id)
  
  if (!provider) {
    return HttpResponse.json(
      { detail: `AI provider ${params.provider_id} not found` },
      { status: 404 }
    )
  }
  
  const updates = await request.json()
  const updated = { 
    ...provider, 
    ...updates, 
    updatedAt: new Date().toISOString() 
  }
  
  return HttpResponse.json(updated)
})

// Test verifies
expect(response.data.displayName).toBe('Updated Name')
```

### 5. DELETE /api/ai-providers/:id (Delete)
```typescript
// Frontend calls
const response = await providersAPI.deleteProvider(id)

// MSW intercepts
http.delete('http://localhost:8000/api/ai-providers/:provider_id', ({ params }) => {
  const provider = MOCK_PROVIDERS.find(p => p.id === params.provider_id)
  
  if (!provider) {
    return HttpResponse.json(
      { detail: `AI provider ${params.provider_id} not found` },
      { status: 404 }
    )
  }
  
  return HttpResponse.json({ 
    message: `AI provider ${params.provider_id} deleted successfully` 
  })
})

// Test verifies
expect(response.status).toBe(200)
expect(response.data.message).toContain('deleted successfully')
```

## Key Architectural Patterns

### 1. Real API Client Usage
```typescript
// Use real API, not mocked
import { providersAPI } from '../../services/api'

// Makes actual axios calls to mock server
const response = await providersAPI.listProviders()
```

### 2. MSW Intercepts HTTP Calls
```typescript
// MSW intercepts actual HTTP calls
const server = setupServer(
  http.get('http://localhost:8000/api/ai-providers', () => {
    return HttpResponse.json(MOCK_PROVIDERS)
  })
)

beforeEach(() => server.listen())  // Enable interception
```

### 3. Store Updated from API Response
```typescript
// Don't mock store directly - update from API
const response = await providersAPI.listProviders()
useProvidersStore.setState({
  providers: response.data
})
```

### 4. Full Test Flow
```typescript
API Call → MSW Intercept → Mock Response → Store Update → Component Render → Assertions
```

## Testing Patterns

### Pattern 1: Basic API Call Test
```typescript
it('should fetch data from API', async () => {
  const response = await providersAPI.listProviders()
  expect(response.status).toBe(200)
  expect(response.data).toEqual(MOCK_PROVIDERS)
})
```

### Pattern 2: Store Integration Test
```typescript
it('should update store from API', async () => {
  const { result } = renderHook(() => useProvidersStore())
  
  const response = await providersAPI.listProviders()
  result.current.setProviders(response.data)
  
  expect(result.current.providers).toEqual(MOCK_PROVIDERS)
})
```

### Pattern 3: Component Integration Test
```typescript
it('should render component with API data', async () => {
  renderWithProviders(<ChatPage />)
  
  await waitFor(() => {
    expect(screen.getByText('OpenAI')).toBeInTheDocument()
  })
})
```

### Pattern 4: Error Handling Test
```typescript
it('should handle errors', async () => {
  server.use(
    http.get('http://localhost:8000/api/ai-providers/:id', () => {
      return HttpResponse.json(
        { detail: 'Not found' },
        { status: 404 }
      )
    })
  )
  
  try {
    await providersAPI.getProvider('invalid-id')
    fail('Should have thrown')
  } catch (error) {
    expect(error.response?.status).toBe(404)
  }
})
```

## Summary

The rewritten E2E tests follow a clean architecture:

1. **Setup**: Reset stores, fetch data from API
2. **Execution**: Make HTTP calls through real API client
3. **Interception**: MSW mock server responds with realistic data
4. **Update**: Store updates from API response
5. **Render**: Component renders with store data
6. **Assert**: Verify correct behavior end-to-end

This simulates the exact flow that happens in production, making the tests meaningful validators of real integration.

