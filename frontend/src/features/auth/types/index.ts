// Auth is not wired in this MVP (public demo). These types document the shape a
// real implementation would use. See ./README.md.
export interface AuthUser {
  id: string;
  name: string;
  email: string;
}

export interface AuthSession {
  user: AuthUser;
  token: string;
}
