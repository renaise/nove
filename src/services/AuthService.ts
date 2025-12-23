// AuthService.ts - Apple Sign In authentication service for Novia

import type { AppleSignInResult } from '../types/native-modules.js';

// API Configuration - Update this with your backend URL
const API_BASE_URL = __DEV__
  ? 'http://localhost:8000'
  : 'https://api.noviaapp.com';

export interface User {
  id: string;
  email: string;
  name: string;
  appleUserId?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface AuthResponse {
  success: boolean;
  user?: User;
  token?: string;
  refreshToken?: string;
  error?: string;
}

export interface Session {
  user: User;
  token: string;
  refreshToken?: string;
}

// Storage keys
const STORAGE_KEYS = {
  SESSION: 'novia_session',
  TOKEN: 'novia_token',
  REFRESH_TOKEN: 'novia_refresh_token',
  USER: 'novia_user',
  APPLE_USER_ID: 'novia_apple_user_id',
};

export class AuthService {
  /**
   * Sign in with Apple and authenticate with backend
   */
  static async signInWithApple(): Promise<AuthResponse> {
    try {
      // Check if Sign in with Apple is available
      const isAvailable = await NativeModules.NoviaAuthModule?.isSignInWithAppleAvailable();
      if (!isAvailable) {
        return {
          success: false,
          error: 'Sign in with Apple is not available on this device',
        };
      }

      // Perform Sign in with Apple
      const result = await NativeModules.NoviaAuthModule?.signInWithApple();

      if (!result || !result.success) {
        return {
          success: false,
          error: result?.error || 'Sign in with Apple failed',
        };
      }

      console.log(
        `[AuthService] Apple Sign In successful: ${result.userIdentifier}`,
      );

      // Authenticate with backend using the Apple credentials
      const authResponse = await this.authenticateWithBackend(result);

      if (authResponse.success && authResponse.user && authResponse.token) {
        // Save session locally
        this.saveSession({
          user: authResponse.user,
          token: authResponse.token,
          refreshToken: authResponse.refreshToken,
        });

        // Save Apple User ID for credential state checks
        if (result.userIdentifier) {
          NativeModules.NativeLocalStorageModule?.setStorageItem(
            STORAGE_KEYS.APPLE_USER_ID,
            result.userIdentifier,
          );
        }
      }

      return authResponse;
    } catch (error) {
      console.log(
        `[AuthService] Error: ${error}`,
      );
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  /**
   * Authenticate with backend using Apple credentials
   */
  private static async authenticateWithBackend(
    appleCredentials: AppleSignInResult,
  ): Promise<AuthResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/graphql`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: `
            mutation AuthenticateWithApple($input: AppleAuthInput!) {
              authenticateWithApple(input: $input) {
                user {
                  id
                  email
                  name
                  appleUserId
                  createdAt
                  updatedAt
                }
                token
                refreshToken
              }
            }
          `,
          variables: {
            input: {
              identityToken: appleCredentials.identityToken,
              authorizationCode: appleCredentials.authorizationCode,
              userIdentifier: appleCredentials.userIdentifier,
              email: appleCredentials.email,
              givenName: appleCredentials.givenName,
              familyName: appleCredentials.familyName,
            },
          },
        }),
      });

      const data = await response.json();

      if (data.errors) {
        return {
          success: false,
          error: data.errors[0]?.message || 'Authentication failed',
        };
      }

      const { user, token, refreshToken } = data.data.authenticateWithApple;

      return {
        success: true,
        user,
        token,
        refreshToken,
      };
    } catch (error) {
      console.log(
        `[AuthService] Backend auth error: ${error}`,
      );
      return {
        success: false,
        error: 'Failed to connect to server',
      };
    }
  }

  /**
   * Save session to local storage
   */
  static saveSession(session: Session): void {
    try {
      NativeModules.NativeLocalStorageModule?.setStorageItem(
        STORAGE_KEYS.TOKEN,
        session.token,
      );
      NativeModules.NativeLocalStorageModule?.setStorageItem(
        STORAGE_KEYS.USER,
        JSON.stringify(session.user),
      );
      if (session.refreshToken) {
        NativeModules.NativeLocalStorageModule?.setStorageItem(
          STORAGE_KEYS.REFRESH_TOKEN,
          session.refreshToken,
        );
      }
    } catch (error) {
      console.log(
        `[AuthService] Failed to save session: ${error}`,
      );
    }
  }

  /**
   * Restore session from local storage
   */
  static restoreSession(): Session | null {
    try {
      const token = NativeModules.NativeLocalStorageModule?.getStorageItem(
        STORAGE_KEYS.TOKEN,
      );
      const userStr = NativeModules.NativeLocalStorageModule?.getStorageItem(
        STORAGE_KEYS.USER,
      );
      const refreshToken = NativeModules.NativeLocalStorageModule?.getStorageItem(
        STORAGE_KEYS.REFRESH_TOKEN,
      );

      if (!token || !userStr) {
        return null;
      }

      const user = JSON.parse(userStr) as User;
      return { user, token, refreshToken: refreshToken || undefined };
    } catch (error) {
      console.log(
        `[AuthService] Failed to restore session: ${error}`,
      );
      return null;
    }
  }

  /**
   * Clear session (logout)
   */
  static clearSession(): void {
    try {
      NativeModules.NativeLocalStorageModule?.removeStorageItem(STORAGE_KEYS.TOKEN);
      NativeModules.NativeLocalStorageModule?.removeStorageItem(STORAGE_KEYS.USER);
      NativeModules.NativeLocalStorageModule?.removeStorageItem(STORAGE_KEYS.REFRESH_TOKEN);
    } catch (error) {
      console.log(
        `[AuthService] Failed to clear session: ${error}`,
      );
    }
  }

  /**
   * Check if user is authenticated
   */
  static isAuthenticated(): boolean {
    const session = this.restoreSession();
    return session !== null && !!session.token;
  }

  /**
   * Get current user
   */
  static getCurrentUser(): User | null {
    const session = this.restoreSession();
    return session?.user || null;
  }

  /**
   * Get auth token
   */
  static getToken(): string | null {
    return NativeModules.NativeLocalStorageModule?.getStorageItem(
      STORAGE_KEYS.TOKEN,
    ) || null;
  }

  /**
   * Check Apple credential state (for app launch)
   */
  static async checkCredentialState(): Promise<boolean> {
    try {
      const appleUserId = NativeModules.NativeLocalStorageModule?.getStorageItem(
        STORAGE_KEYS.APPLE_USER_ID,
      );

      if (!appleUserId) {
        return false;
      }

      const result = await NativeModules.NoviaAuthModule?.getCredentialState(appleUserId);

      if (result?.success && result.state === 'authorized') {
        return true;
      }

      // If credential is revoked or not found, clear session
      if (result?.state === 'revoked' || result?.state === 'not_found') {
        this.clearSession();
      }

      return false;
    } catch (error) {
      console.log(
        `[AuthService] Credential check error: ${error}`,
      );
      return false;
    }
  }

  /**
   * Sign out
   */
  static async signOut(): Promise<void> {
    this.clearSession();
    NativeModules.NativeLocalStorageModule?.removeStorageItem(STORAGE_KEYS.APPLE_USER_ID);
  }
}

// Declare __DEV__ for TypeScript
declare const __DEV__: boolean;
