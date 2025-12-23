// OnboardingService.ts - Persistence layer for onboarding state

const STORAGE_KEYS = {
  CAROUSEL_COMPLETE: 'novia_onboarding_carousel_complete',
  PHOTO_PROVIDED: 'novia_onboarding_photo_provided',
};

export const OnboardingService = {
  /**
   * Check if user has completed the onboarding carousel
   */
  isCarouselComplete(): boolean {
    const value = NativeModules.NativeLocalStorageModule?.getStorageItem(
      STORAGE_KEYS.CAROUSEL_COMPLETE,
    );
    return value === 'true';
  },

  /**
   * Mark the carousel as complete
   */
  setCarouselComplete(): void {
    NativeModules.NativeLocalStorageModule?.setStorageItem(
      STORAGE_KEYS.CAROUSEL_COMPLETE,
      'true',
    );
    console.log(
      '[OnboardingService] Carousel marked complete',
    );
  },

  /**
   * Check if user has provided their silhouette photo
   */
  isPhotoProvided(): boolean {
    const value = NativeModules.NativeLocalStorageModule?.getStorageItem(
      STORAGE_KEYS.PHOTO_PROVIDED,
    );
    return value === 'true';
  },

  /**
   * Mark that user has provided their photo
   */
  setPhotoProvided(): void {
    NativeModules.NativeLocalStorageModule?.setStorageItem(
      STORAGE_KEYS.PHOTO_PROVIDED,
      'true',
    );
    console.log(
      '[OnboardingService] Photo marked as provided',
    );
  },

  /**
   * Check if full onboarding is complete (carousel + photo)
   */
  isOnboardingComplete(): boolean {
    return this.isCarouselComplete() && this.isPhotoProvided();
  },

  /**
   * Reset onboarding state (for testing/debugging)
   */
  reset(): void {
    NativeModules.NativeLocalStorageModule?.removeStorageItem(
      STORAGE_KEYS.CAROUSEL_COMPLETE,
    );
    NativeModules.NativeLocalStorageModule?.removeStorageItem(
      STORAGE_KEYS.PHOTO_PROVIDED,
    );
    console.log(
      '[OnboardingService] Onboarding state reset',
    );
  },
};
