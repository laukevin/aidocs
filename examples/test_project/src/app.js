const express = require('express');
const jwt = require('jsonwebtoken');
const authRoutes = require('./auth/routes');
const apiRoutes = require('./api/routes');
const { authenticateToken } = require('./auth/middleware');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());

// Public routes
app.use('/auth', authRoutes);

// Protected routes
app.use('/api', authenticateToken, apiRoutes);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Error handling
app.use((error, req, res, next) => {
  console.error('Unhandled error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = app;