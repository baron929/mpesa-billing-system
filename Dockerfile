# Stage 1: Dependencies (production only)
FROM node:20.10.0-alpine AS deps
WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Builder (with dev dependencies for Prisma generation)
FROM node:20.10.0-alpine AS builder
WORKDIR /app

COPY package*.json ./
COPY prisma ./prisma
RUN npm ci && npx prisma generate

# Stage 3: Production Runtime
FROM node:20.10.0-alpine AS production
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=5000

# Copy production dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy Prisma client from builder stage
COPY --from=builder /app/node_modules/.prisma ./node_modules/.prisma
COPY --from=builder /app/prisma ./prisma

# Copy application source code
COPY package*.json ./
COPY server.js ./
COPY api ./api
COPY billing_system ./billing_system
COPY config ./config
COPY hotspot ./hotspot
COPY middleware ./middleware
COPY models ./models
COPY routes ./routes
COPY services ./services
COPY public ./public

EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD node -e "require('http').get('http://127.0.0.1:5000/health', (res) => {if (res.statusCode !== 200) throw new Error('Health check failed');})"

CMD ["node", "server.js"]
