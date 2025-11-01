# Design: Testing and Feedback

## Objective
Comprehensive testing and user feedback collection.

## Test Strategy

### Backend Testing
- **Unit Tests**: pytest for individual functions
- **Integration Tests**: Test complete workflows
- **Fixtures**: Shared test data

### UI Testing
- **Framework**: Playwright or Cypress
- **Tests**: Search, rendering, pins, download

### Feedback Collection
- **API**: POST /api/feedback
- **Storage**: Database or JSON files
- **Schema**: {rating, comment, query, answer_id}

## Out of Scope
- Performance testing
- Load testing
- A/B testing
