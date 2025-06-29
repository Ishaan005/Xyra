# Organizations Page

This document describes the Organizations page implementation for the Xyra frontend application.

## Overview

The Organizations page provides a comprehensive interface for managing organizations within the Xyra system. It connects to the backend organizations API endpoints to provide full CRUD functionality.

## Features

### 1. Organization Management
- **List Organizations**: Display all organizations with pagination and filtering
- **Create Organization**: Add new organizations with complete form validation
- **Edit Organization**: Update existing organization details
- **Delete Organization**: Remove organizations with confirmation dialog

### 2. Organization Display
Each organization card shows:
- Organization name and description
- Status badge (Active/Inactive/Suspended)
- Agent count (total and active)
- Monthly revenue
- Contact information (name, email, phone)
- Creation date
- Quick action buttons (Stats, Edit, Delete)

### 3. Filtering and Search
- **Tabs**: Filter by All, Active, or Inactive organizations
- **Search**: Real-time search by name, description, or contact name
- **Real-time Updates**: Automatic refresh after CRUD operations

### 4. Statistics Dashboard
- **Summary Cards**: Total organizations, agents, costs, revenue, and margin
- **Individual Stats**: Detailed statistics modal for each organization
- **Financial Metrics**: Revenue, cost, and margin calculations

### 5. Form Management
- **Create Form**: Complete organization creation with all fields
- **Edit Form**: Update organization information
- **Validation**: Client-side validation for required fields
- **Timezone Support**: Dropdown with common timezones

## Technical Implementation

### Backend API Integration
The page uses the following API endpoints:
- `GET /api/v1/organizations` - List organizations
- `POST /api/v1/organizations` - Create organization
- `PUT /api/v1/organizations/{id}` - Update organization
- `DELETE /api/v1/organizations/{id}` - Delete organization
- `GET /api/v1/organizations/{id}/stats` - Get organization statistics

### Authentication
- Uses NextAuth.js for session management
- Automatically sets authorization headers for API requests
- Redirects to login page if not authenticated

### State Management
- React hooks for local state management
- Proper loading and error states
- Optimistic updates for better UX

### UI Components
Built using custom UI components:
- **Cards**: Organization display cards
- **Dialogs**: Create, edit, and stats modals
- **Forms**: Input fields, selects, and labels
- **Buttons**: Action buttons with loading states
- **Badges**: Status indicators
- **Skeletons**: Loading placeholders

## File Structure

```
frontend/
├── app/
│   └── organisations/
│       └── page.tsx                 # Main organizations page
├── types/
│   └── organization.ts              # TypeScript type definitions
└── utils/
    └── api.ts                       # API client (existing)
```

## Type Definitions

The page uses TypeScript interfaces defined in `/types/organization.ts`:
- `Organization`: Base organization interface
- `OrganizationWithStats`: Extended with statistics
- `OrganizationCreate`: For creating new organizations
- `OrganizationUpdate`: For updating existing organizations

## Responsive Design

The page is fully responsive with:
- Mobile-friendly card layout
- Responsive grid system (1-3 columns based on screen size)
- Mobile-optimized dialogs and forms
- Touch-friendly buttons and inputs

## Error Handling

- Comprehensive error handling for all API calls
- User-friendly error messages
- Proper loading states during operations
- Confirmation dialogs for destructive actions

## Usage

1. Navigate to `/organisations` in the application
2. View all organizations in the card layout
3. Use the search bar to find specific organizations
4. Filter by status using the tabs
5. Click "Add Organization" to create new organizations
6. Use the action buttons on each card to view stats, edit, or delete
7. View summary statistics at the top of the page

## Dependencies

The page relies on:
- Next.js 13+ App Router
- NextAuth.js for authentication
- Axios for API calls
- Radix UI components
- Tailwind CSS for styling
- Lucide React for icons
