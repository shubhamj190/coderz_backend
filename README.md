# Backend Service

This is the backend service for the Coding Platform application.

## Project Structure

```
Backend/
├── controllers/     # Request handlers
├── models/         # Database models
├── routes/         # API routes
├── middleware/     # Custom middleware
├── config/         # Configuration files
└── server.js       # Main application entry
```

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
- Create a `.env` file
- Add necessary environment variables

3. Start the server:
```bash
npm start
```

## API Routes

- `/api/auth` - Authentication routes
- `/api/users` - User management
- `/api/problems` - Coding problems
- `/api/submissions` - Code submissions

## Technologies Used

- Node.js
- Express.js
- MongoDB
- JWT Authentication

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request