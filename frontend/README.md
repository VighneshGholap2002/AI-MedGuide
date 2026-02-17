# Frontend README

## React Clinical Note Summarizer UI

React + TypeScript frontend application for the Clinical Note Summarizer system.

### Requirements

- Node.js 18+
- npm or yarn

### Setup

1. **Install dependencies**

   ```bash
   npm install
   ```

2. **Configure API endpoint** (optional)
   - Edit `src/services/api.ts` if backend is running on different port
   - Default: `http://localhost:8080/api`

3. **Start development server**
   ```bash
   npm start
   ```

The application will open at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

Output will be in `build/` directory.

### Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── CaseForm.tsx         # Form for creating new cases
│   │   ├── CaseList.tsx         # List of patient cases
│   │   └── CaseDetail.tsx       # Detailed case view and results
│   ├── services/
│   │   └── api.ts               # API service client
│   ├── App.tsx                  # Main application component
│   ├── App.css                  # Application styles
│   ├── index.tsx                # React entry point
│   └── index.css                # Global styles
├── public/
│   └── index.html               # HTML template
├── package.json                 # Dependencies
└── tsconfig.json                # TypeScript configuration
```

### Features

#### Case Management

- Create new patient cases with clinical notes
- View list of all cases
- Delete cases
- Real-time case list updates

#### Clinical Note Submission

Form includes:

- Case Title
- Patient Age
- Gender (Male/Female/Other)
- Clinical Notes (textarea for pasting notes)

#### Summarization Results Display

- Chief Complaint extraction
- Key Findings summary
- Clinical Assessment
- Risk Words highlighting (red for CRITICAL, orange for HIGH)
- Risk Factors list
- Follow-up Recommendations
- ICD Code suggestions
- Confidence Score with progress bar

### Styling

The application uses **Tailwind CSS** for styling:

- Responsive grid layout
- Three-column design: Form | List | Details
- Color-coded risk levels
- Smooth transitions and hover effects

### API Integration

All API calls are handled by `src/services/api.ts`:

```typescript
// Create case
caseService.createCase(caseData);

// Get all cases
caseService.getAllCases();

// Get specific case
caseService.getCaseById(id);

// Summarize case
caseService.summarizeCase(id);

// Update case
caseService.updateCase(id, caseData);

// Delete case
caseService.deleteCase(id);
```

### Error Handling

- Network errors display user-friendly messages
- Validation errors shown in forms
- Cases list shows error state if API fails
- Auto-retry not implemented (manual refresh recommended)

### Performance

- Lazy loading of case details
- Efficient state management with React hooks
- Debounced API calls
- Optimized re-renders

### Browser Compatibility

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

### Environment Variables

Create `.env` file for customization:

```
REACT_APP_API_URL=http://localhost:8080/api
```

### Deployment

#### Docker

```bash
docker build -t clinical-frontend:latest .
docker run -p 3000:3000 clinical-frontend:latest
```

#### Nginx (Production)

```bash
npm run build
# Serve 'build' directory with Nginx
```

### Troubleshooting

1. **API connection refused**
   - Ensure backend is running on port 8080
   - Check CORS configuration in backend

2. **Styled elements not loading**
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Run `npm run build` for production

3. **Cases not updating**
   - Refresh the browser
   - Check MongoDB connection in backend logs

### Development

### Available Scripts

- `npm start` - Start development server with hot reload
- `npm build` - Build production bundle
- `npm test` - Run test suite
- `npm eject` - Expose configuration (cannot be undone)
