// Type definitions for native modules - Novia App

import { Screen } from './index.js';

// Gallery Picker Types (for photos/videos from gallery/camera)
export interface GalleryPickerOptions {
  selectionLimit: number;
  mediaTypes: 'images' | 'videos' | 'all';
  allowsEditing?: boolean;
  quality?: number;
  sourceType?: 'gallery' | 'camera' | 'both';
  presentationStyle?: 'fullScreen' | 'pageSheet' | 'large' | 'compact';
}

export interface GalleryMedia {
  uri: string;
  type: 'image' | 'video' | 'text';
  width?: number;
  height?: number;
  duration?: number;
  fileSize?: number;
  fileName?: string;
  textContent?: string;
  mimeType: string;
  thumbnail?: string;
  assetId?: string;
}

export interface GalleryPickerResult {
  cancelled: boolean;
  media: GalleryMedia[];
  error?: string;
}

export interface ThumbnailOptions {
  assetId: string;
}

export interface ThumbnailResult {
  success: boolean;
  thumbnailUri?: string;
  mediaType?: 'image' | 'video';
  width?: number;
  height?: number;
  duration?: number;
  error?: string;
}

export interface NoviaGalleryPickerModule {
  openGalleryPicker(options: GalleryPickerOptions): Promise<GalleryPickerResult>;
  checkPermissions(): Promise<{ camera: boolean; photos: boolean }>;
  requestPermissions(): Promise<{ camera: boolean; photos: boolean }>;
  grabThumbnail(options: ThumbnailOptions): Promise<ThumbnailResult>;
}

// Text Input Module Types
export interface TextInputOptions {
  title?: string;
  message?: string;
  placeholder?: string;
  defaultValue?: string;
  keyboardType?: 'default' | 'email-address' | 'numeric' | 'phone-pad' | 'url';
  secureTextEntry?: boolean;
  autocapitalizationType?: 'none' | 'words' | 'sentences' | 'all';
  autocorrectionType?: 'default' | 'no' | 'yes';
}

export interface TextInputResult {
  text: string;
  cancelled: boolean;
}

export interface NoviaInputModule {
  showTextInput(options: TextInputOptions): Promise<TextInputResult>;
  showSecureTextInput(options: TextInputOptions): Promise<TextInputResult>;
}

// Photo Gallery Types
export interface NoviaPhotoGalleryAssetSelectedEvent {
  detail: {
    index: number;
    assetId: string;
  };
}

export interface NoviaPhotoGalleryPermissionsEvent {
  detail: {
    granted: boolean;
  };
}

export interface NoviaPhotoGalleryMediaTypeEvent {
  detail: {
    mediaType: string;
  };
}

// Video Component Types
export interface NoviaVideoLoadStartEvent {
  detail: {};
}

export interface NoviaVideoReadyEvent {
  detail: {};
}

export interface NoviaVideoEndedEvent {
  detail: {};
}

export interface NoviaVideoErrorEvent {
  detail: {
    error: string;
  };
}

// Video Player Manager Module Types
export interface NoviaVideoPlayerManager {
  pauseAll(): void;
  resumeAll(): void;
  debugPrintState(): void;
}

// Safari Module for opening URLs in SFSafariViewController
export interface NoviaSafariModule {
  openURL(url: string): void;
}

// Console provider for logging
export interface ConsoleLynxProvider {
  logToConsole(message: string): void;
  getPendingDeepLink(): Promise<string | null>;
}

// Apple Sign In Types
export interface AppleSignInResult {
  success: boolean;
  userIdentifier?: string;
  email?: string;
  givenName?: string;
  familyName?: string;
  identityToken?: string;
  authorizationCode?: string;
  realUserStatus?: number;
  error?: string;
  errorCode?: string;
}

export interface CredentialStateResult {
  success: boolean;
  state?: 'authorized' | 'revoked' | 'not_found' | 'transferred' | 'unknown';
  error?: string;
}

export interface NoviaAuthModule {
  isSignInWithAppleAvailable(): Promise<boolean>;
  signInWithApple(): Promise<AppleSignInResult>;
  getCredentialState(userIdentifier: string): Promise<CredentialStateResult>;
}

// Declare the global Native Modules object with our modules
declare global {
  interface NativeModules {
    NoviaGalleryPickerModule?: NoviaGalleryPickerModule;
    NoviaInputModule?: NoviaInputModule;
    NoviaVideoPlayerManager?: NoviaVideoPlayerManager;
    NoviaSafariModule?: NoviaSafariModule;
    ConsoleLynxProvider?: ConsoleLynxProvider;
    NoviaAuthModule?: NoviaAuthModule;
    NativeLocalStorageModule?: {
      setStorageItem(key: string, value: string): void;
      getStorageItem(key: string): string | null;
      removeStorageItem(key: string): void;
      clearStorage(): void;
    };
  }

  const NativeModules: NativeModules;
}
