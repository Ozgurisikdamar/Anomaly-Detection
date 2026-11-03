# StoreGuard Netlify — Current Deployment Recovery

**Repository:** `Ozgurisikdamar/Anomaly-Detection`  
**Production URL:** `https://store-guard.netlify.app/`  
**Checked:** 2026-11-03  
**Purpose:** Force Netlify to publish the current `main` revision and distinguish a stale deploy from a backend/API configuration issue.

## Repository findings

The repository's default branch is `main`. The latest commit checked is `e5c2ce3e0a3cbfe68e295426fe1bb36473be3e57` (2026-10-31), whose changes are documentation-only. The recent UI theme commit is `35c9ce07091cc2bae5814eaba04f0d74f1a91d7f` (2026-10-31); it adds the Gündüz/Gece theme toggle and updates theme tokens. The production page screenshot supplied on 2026-11-03 displays the dark theme, but this alone does not prove a stale deploy: dark mode remains the documented default and user preference is stored in browser localStorage under `sg-theme`.

The app is a Next.js 14 SSR app under `apps/web`, not a static Vite SPA. Root `netlify.toml` already specifies:
- Base directory: `apps/web`
- Build command: `npm run build`
- Publish directory: `.next` (resolved relative to base)
- Node 22
- `@netlify/plugin-nextjs`

Do **not** replace this with a static `dist` configuration or add SPA catch-all rewrites. The app uses `force-dynamic` server components and Next server runtime.

## Correct Netlify configuration

In Netlify project configuration, verify:
- Repository: `Ozgurisikdamar/Anomaly-Detection`
- Production branch: `main`
- Base directory: `apps/web`
- Build command: `npm run build` (or inherit from `netlify.toml`)
- Publish directory: leave empty so the committed config's `.next` is applied. If the UI requires a value, use root-relative `apps/web/.next`.
- Package directory: empty
- Node version: 22 (already declared in `netlify.toml`)

A stale UI publish/package value can override or conflict with the file-based configuration. Clear it before redeploying.

## Recovery steps

1. In Netlify → StoreGuard site → Site configuration, verify the repository and production branch.
2. Check the latest Production deploy's commit SHA. It should be `e5c2ce3e0a3cbfe68e295426fe1bb36473be3e57` or a newer commit from `main`.
3. If it is older, trigger **Deploys → Trigger deploy → Clear cache and deploy site**.
4. Inspect the resulting build log. Confirm it checks out the expected commit, detects base `apps/web`, runs `npm run build`, and uses the Next.js plugin/runtime.
5. If the build fails with a base/publish collision, clear the Netlify UI Publish directory and Package directory as described above, save, then clear-cache deploy again.
6. Verify the deployed UI in a private/incognito window to avoid stale browser assets/localStorage. The theme defaults to dark; the screenshot's dark theme is not by itself evidence of an old build.

## Frontend vs backend status

A successful Netlify deployment only hosts the Next.js dashboard. It does not deploy the FastAPI backend or the vision process.

The frontend reads `NEXT_PUBLIC_API_BASE` at build time. Set it in Netlify to the public HTTPS API origin. The API must include `https://store-guard.netlify.app` in its allowed CORS origins (the settings support `STOREGUARD_CORS_ORIGINS_EXTRA`).

If `NEXT_PUBLIC_API_BASE` is absent or the backend is unreachable, the dashboard intentionally falls back to the bundled SIMULATED sample data and the source pill should indicate sample/offline. This is expected fallback behavior, not proof of a stale frontend deploy.

## Verification checklist

- [ ] Production deploy commit SHA matches current `main`.
- [ ] Netlify log shows base `apps/web`.
- [ ] Next.js build completes and `@netlify/plugin-nextjs` runs successfully.
- [ ] Production site loads in private window.
- [ ] Theme preference is checked independently of deploy freshness.
- [ ] Source pill reads live API only when a valid reachable API is configured.
- [ ] Browser network panel confirms API requests target the configured HTTPS API origin and succeed.
- [ ] API CORS permits the Netlify origin.

## Limits of this recovery

Repository configuration is verified from GitHub. The Netlify account's site settings, deploy history/logs, environment variables and actual deploy status are not accessible through this repository inspection. Do not claim the site has been redeployed successfully until the Netlify Deploys page confirms the latest deployment is Published and serves the intended commit.
