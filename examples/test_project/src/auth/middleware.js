const jwt = require('jsonwebtoken');
const redis = require('redis');

const redisClient = redis.createClient();
const JWT_SECRET = process.env.JWT_SECRET || 'default-secret-change-in-production';

/**
 * JWT authentication middleware
 * Validates tokens and checks against blacklist
 */
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  // Check if token is blacklisted
  redisClient.get(`blacklist:${token}`, (err, result) => {
    if (err) {
      console.error('Redis error:', err);
      return res.status(500).json({ error: 'Authentication service error' });
    }

    if (result) {
      return res.status(401).json({ error: 'Token has been revoked' });
    }

    // Verify token
    jwt.verify(token, JWT_SECRET, (err, decoded) => {
      if (err) {
        if (err.name === 'TokenExpiredError') {
          return res.status(401).json({ error: 'Token expired' });
        }
        if (err.name === 'JsonWebTokenError') {
          return res.status(401).json({ error: 'Invalid token' });
        }
        return res.status(500).json({ error: 'Token verification error' });
      }

      // Add user info to request
      req.user = {
        userId: decoded.userId,
        email: decoded.email,
        roles: decoded.roles || []
      };

      next();
    });
  });
}

/**
 * Blacklist a token (for logout/revocation)
 */
function blacklistToken(token, expiresIn = 3600) {
  redisClient.setex(`blacklist:${token}`, expiresIn, 'revoked');
}

module.exports = {
  authenticateToken,
  blacklistToken
};