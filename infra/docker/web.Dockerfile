# StoreGuard web dashboard image. Build context is the repo root.
FROM node:22-alpine

WORKDIR /app

# The web app imports shared types from packages/contracts (externalDir).
COPY packages/contracts ./packages/contracts
COPY apps/web ./apps/web

WORKDIR /app/apps/web
RUN npm install --no-audit --no-fund
RUN npm run build

EXPOSE 3000
CMD ["npm", "run", "start"]
