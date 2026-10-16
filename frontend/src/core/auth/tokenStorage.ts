/** The only module allowed to touch localStorage for tokens — everything
 * else (the axios client, AuthContext) goes through these functions so the
 * storage mechanism can change later (e.g. httpOnly cookies) in one place. */

const ACCESS_TOKEN_KEY = "ai_fte_access_token";
const REFRESH_TOKEN_KEY = "ai_fte_refresh_token";

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setTokens(accessToken: string, refreshToken: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}
