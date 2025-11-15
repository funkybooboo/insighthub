# Test Expansion Plan - Client

## Current Status (✅ Excellent)
- **Unit Tests**: 319 tests passing (100%)
- **Coverage**: 97% statements, 94.28% branches, 100% functions
- **Code Quality**: 0 lint errors, 0 type errors

## Test Gaps Identified

### 1. 🎭 Missing Storybook Stories (High Priority)

**Components without stories:**
- [ ] `ChatBot.tsx` - Main chat interface component
- [ ] `ChatSidebar.tsx` - Session management sidebar
- [ ] `ProtectedRoute.tsx` - Auth guard component
- [ ] `DocumentManager.tsx` - Document upload/list manager
- [ ] `SignupForm.stories.tsx` - Needs to be created

**Benefits:**
- Visual documentation for developers
- Interactive component playground
- Visual regression testing base
- Design system reference

### 2. 🔄 Integration Tests (High Priority)

**User Flows to Test:**
- [ ] Complete signup → login → chat flow
- [ ] Document upload → chat with context flow
- [ ] Session creation → message exchange → session switch flow
- [ ] Multi-tab authentication state sync
- [ ] WebSocket reconnection scenarios

**Test File Structure:**
```
tests/integration/
├── auth-flow.integration.test.tsx
├── chat-flow.integration.test.tsx
├── document-flow.integration.test.tsx
├── session-management.integration.test.tsx
└── websocket.integration.test.tsx
```

### 3. 🎯 E2E Tests with Playwright (High Priority)

**Critical User Journeys:**
- [ ] New user signup and first chat
- [ ] Returning user login and session restoration
- [ ] Document upload and RAG query
- [ ] Multi-session chat management
- [ ] Mobile responsive behavior

**Test File Structure:**
```
e2e/
├── auth/
│   ├── signup.spec.ts
│   ├── login.spec.ts
│   └── logout.spec.ts
├── chat/
│   ├── new-conversation.spec.ts
│   ├── session-management.spec.ts
│   └── message-history.spec.ts
├── documents/
│   ├── upload.spec.ts
│   ├── list-view.spec.ts
│   └── delete.spec.ts
└── responsive/
    ├── mobile.spec.ts
    └── tablet.spec.ts
```

### 4. 📡 Additional Bruno API Tests (Medium Priority)

**Missing API Test Scenarios:**
- [ ] Rate limiting tests
- [ ] Concurrent request handling
- [ ] Large file upload scenarios
- [ ] WebSocket connection edge cases
- [ ] Database transaction rollback scenarios
- [ ] API version compatibility tests

**Test File Structure:**
```
bruno/
├── Documents/
│   ├── Upload_Large_File.bru (>15MB)
│   ├── Upload_Concurrent.bru
│   ├── Upload_Invalid_Type.bru
│   └── List_Pagination.bru
├── Chat/
│   ├── Streaming_Response.bru
│   ├── Rate_Limit.bru
│   └── Concurrent_Messages.bru
└── System/
    ├── Health_Check.bru
    └── Version_Info.bru
```

### 5. 🎨 Visual Regression Tests (Medium Priority)

**Using Playwright + Percy/Chromatic:**
- [ ] Component visual snapshots
- [ ] Responsive design breakpoints
- [ ] Theme variations (if applicable)
- [ ] Accessibility contrast checks

### 6. ⚡ Performance Tests (Medium Priority)

**Areas to Test:**
- [ ] Component render performance
- [ ] Large message list virtualization
- [ ] WebSocket message throughput
- [ ] Bundle size monitoring
- [ ] Core Web Vitals (LCP, FID, CLS)

**Test File Structure:**
```
tests/performance/
├── component-render.perf.test.ts
├── message-list.perf.test.ts
└── bundle-size.test.ts
```

### 7. ♿ Accessibility Tests (Medium Priority)

**Using @axe-core/playwright:**
- [ ] Keyboard navigation tests
- [ ] Screen reader compatibility
- [ ] ARIA labels verification
- [ ] Color contrast checks
- [ ] Focus management tests

**Test File Structure:**
```
tests/accessibility/
├── keyboard-navigation.a11y.test.ts
├── screen-reader.a11y.test.ts
└── aria-labels.a11y.test.ts
```

## Implementation Priority

### Phase 1: Critical Path (Week 1)
1. **Storybook stories** for missing components
2. **E2E tests** for core user journeys
3. **Integration tests** for auth and chat flows

### Phase 2: Quality Enhancement (Week 2)
4. **Bruno API tests** for edge cases
5. **Visual regression** baseline
6. **Accessibility audits**

### Phase 3: Optimization (Week 3)
7. **Performance benchmarks**
8. **Load testing**
9. **Test infrastructure improvements**

## Estimated Test Count After Expansion

| Test Type | Current | Target | Increase |
|-----------|---------|--------|----------|
| Unit Tests | 319 | 350 | +31 |
| Storybook Stories | 7 | 12 | +5 |
| Integration Tests | 0 | 15 | +15 |
| E2E Tests | 0 | 25 | +25 |
| Bruno API Tests | ~20 | 40 | +20 |
| A11y Tests | 0 | 10 | +10 |
| **TOTAL** | **346** | **452** | **+106** |

## Success Metrics

- ✅ 95%+ code coverage maintained
- ✅ All critical user paths covered by E2E tests
- ✅ 100% of components have Storybook stories
- ✅ All API endpoints have happy + sad path tests
- ✅ Zero accessibility violations
- ✅ Performance budgets enforced

## Next Steps

1. Review and approve this plan
2. Set up Playwright configuration
3. Create test templates and helpers
4. Begin Phase 1 implementation
