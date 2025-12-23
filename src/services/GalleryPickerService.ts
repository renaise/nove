import {
  GalleryPickerOptions,
  GalleryPickerResult,
  GalleryMedia,
} from '../types/native-modules.js';

class GalleryPickerService {
  private get galleryPickerModule() {
    return typeof NativeModules !== 'undefined' &&
      NativeModules.NoviaGalleryPickerModule
      ? NativeModules.NoviaGalleryPickerModule
      : undefined;
  }

  async checkPermissions(): Promise<{ camera: boolean; photos: boolean }> {
    if (!this.galleryPickerModule) {
      console.log('[GalleryPickerService] Gallery picker module not available');
      return { camera: false, photos: false };
    }

    try {
      return await this.galleryPickerModule.checkPermissions();
    } catch (error) {
      console.log(`[GalleryPickerService] Error checking permissions: ${error}`);
      return { camera: false, photos: false };
    }
  }

  async requestPermissions(): Promise<{ camera: boolean; photos: boolean }> {
    if (!this.galleryPickerModule) {
      throw new Error('Gallery picker module not available');
    }

    try {
      return await this.galleryPickerModule.requestPermissions();
    } catch (error) {
      console.log(`[GalleryPickerService] Error requesting permissions: ${error}`);
      throw error;
    }
  }

  async openGalleryPicker(
    options: Partial<GalleryPickerOptions> = {},
  ): Promise<GalleryMedia[]> {
    if (!this.galleryPickerModule) {
      throw new Error('Gallery picker module not available');
    }

    // Check permissions FIRST - before opening picker
    const permissions = await this.checkPermissions();
    console.log(`[GalleryPickerService] Current permissions: ${JSON.stringify(permissions)}`);

    if (!permissions.photos && !permissions.camera) {
      console.log('[GalleryPickerService] No permissions, requesting...');
      const requestedPermissions = await this.requestPermissions();
      console.log(`[GalleryPickerService] Requested permissions result: ${JSON.stringify(requestedPermissions)}`);

      if (!requestedPermissions.photos && !requestedPermissions.camera) {
        throw new Error('Photo and camera permissions are required');
      }
    }

    const defaultOptions: GalleryPickerOptions = {
      selectionLimit: 1,
      mediaTypes: 'images',
      allowsEditing: false,
      quality: 0.8,
      sourceType: 'gallery',
      presentationStyle: 'large',
    };

    const mergedOptions: GalleryPickerOptions = {
      ...defaultOptions,
      ...options,
    };

    try {
      console.log(`[GalleryPickerService] Opening gallery picker with options: ${JSON.stringify(mergedOptions)}`);
      const result: GalleryPickerResult =
        await this.galleryPickerModule.openGalleryPicker(mergedOptions);

      if (result.cancelled) {
        console.log('[GalleryPickerService] Gallery picker cancelled');
        return [];
      }

      return result.media || [];
    } catch (error) {
      console.log(`[GalleryPickerService] Error opening gallery picker: ${error}`);
      throw error;
    }
  }

  async pickImage(
    options: Partial<GalleryPickerOptions> = {},
  ): Promise<GalleryMedia | null> {
    const media = await this.openGalleryPicker({
      selectionLimit: 1,
      mediaTypes: 'images',
      ...options,
    });
    return media[0] || null;
  }

  async takePhoto(
    options: Partial<GalleryPickerOptions> = {},
  ): Promise<GalleryMedia | null> {
    const media = await this.openGalleryPicker({
      selectionLimit: 1,
      mediaTypes: 'images',
      sourceType: 'camera',
      ...options,
    });
    return media[0] || null;
  }
}

export const galleryPickerService = new GalleryPickerService();
