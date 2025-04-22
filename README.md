# Blombo

A semantic layer middleware for AI/LLM applications with a modern React + Tailwind frontend.

## Project Structure

```
blombocom/
├── backend/           # Python FastAPI backend
│   ├── blombo/       # Main backend package
│   └── tests/        # Backend tests
├── frontend/         # React + Tailwind frontend
│   ├── src/          # Frontend source code
│   └── public/       # Static assets
└── README.md         # This file
```

## Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Run the development server:
   ```bash
   poetry run uvicorn blombo.api.server:app --reload
   ```

## Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

## Development

- Backend API runs on http://localhost:8000
- Frontend development server runs on http://localhost:5173
- API documentation available at http://localhost:8000/docs

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

MIT 