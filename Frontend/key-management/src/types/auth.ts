export interface LoginFormTypes {
  username?: string;
  password?: string;
  remember?: boolean;
  providerName?: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken?: string;
}

export interface AuthResponse {
  success: boolean;
  tokens?: AuthTokens;
  error?: string;
} 