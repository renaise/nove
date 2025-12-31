import { useState } from '@lynx-js/react';
import { useApp } from '../context/AppContext.jsx';
import { OnboardingService } from '../services/OnboardingService.js';
import { galleryPickerService } from '../services/GalleryPickerService.js';
import { SelfieIcon, GalleryIcon, CameraIcon } from '../components/Icons.jsx';

const OnboardingPhotoScreen = () => {
  const { navigateTo, setSelectedPhoto } = useApp();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGalleryPick = async () => {
    setIsLoading(true);
    setError(null);

    try {
      console.log('[OnboardingPhotoScreen] Opening gallery picker');

      // Service checks/requests permissions BEFORE opening the picker
      const media = await galleryPickerService.pickImage({
        presentationStyle: 'large',
      });

      console.log(`[OnboardingPhotoScreen] Gallery result: ${JSON.stringify(media)}`);

      if (media) {
        setSelectedPhoto(media.uri);
        OnboardingService.setPhotoProvided();
        navigateTo('home');
      } else {
        console.log('[OnboardingPhotoScreen] Gallery picker cancelled');
      }
    } catch (err) {
      console.log(`[OnboardingPhotoScreen] Gallery error: ${err}`);
      const errorMessage = err instanceof Error ? err.message : String(err);
      if (errorMessage.includes('permissions are required')) {
        setError('Please grant photo access in Settings to continue.');
      } else {
        setError('Failed to select photo. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleCameraCapture = async () => {
    setIsLoading(true);
    setError(null);

    try {
      console.log('[OnboardingPhotoScreen] Opening camera');

      // Service checks/requests permissions BEFORE opening the picker
      const media = await galleryPickerService.takePhoto({
        presentationStyle: 'fullScreen',
      });

      console.log(`[OnboardingPhotoScreen] Camera result: ${JSON.stringify(media)}`);

      if (media) {
        setSelectedPhoto(media.uri);
        OnboardingService.setPhotoProvided();
        navigateTo('home');
      } else {
        console.log('[OnboardingPhotoScreen] Camera cancelled');
      }
    } catch (err) {
      console.log(`[OnboardingPhotoScreen] Camera error: ${err}`);
      const errorMessage = err instanceof Error ? err.message : String(err);
      if (errorMessage.includes('permissions are required')) {
        setError('Please grant camera access in Settings to continue.');
      } else {
        setError('Failed to capture photo. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <view className="flex-1 w-full pt-[80px] pb-10 px-6 bg-ivory">
      {/* Icon */}
      <view className="items-center mb-8">
        <view className="w-[120px] h-[120px] rounded-full bg-blush items-center justify-center">
          <SelfieIcon size={64} color="#D4AF37" />
        </view>
      </view>

      {/* Title */}
      <text
        className="text-[28px] font-bold text-foreground text-center mb-4"
        style={{ lineHeight: '36px' }}
      >
        Capture Your True Silhouette
      </text>

      {/* Description */}
      <text
        className="text-base text-muted-foreground text-center mb-8"
        style={{ lineHeight: '24px' }}
      >
        To ensure your dream dress fits flawlessly, we need a photo of you in fitted clothing.
        Think activewear or a simple bodysuit—your blank canvas for transformation.
      </text>

      {/* Photo Options */}
      <view style={{ gap: '12px', marginBottom: '24px' }}>
        {/* Gallery Option */}
        <view
          bindtap={isLoading ? undefined : handleGalleryPick}
          className="flex-row items-center py-5 px-5 rounded-2xl bg-card"
          style={{
            opacity: isLoading ? 0.6 : 1,
            boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05)',
          }}
        >
          <view className="w-14 h-14 rounded-2xl bg-primary items-center justify-center mr-4">
            <GalleryIcon size={26} color="#FFFFFF" />
          </view>
          <view className="flex-1">
            <text className="text-base font-semibold text-foreground mb-1">
              Choose from Gallery
            </text>
            <text className="text-sm text-muted-foreground">
              Select an existing photo
            </text>
          </view>
        </view>

        {/* Camera Option */}
        <view
          bindtap={isLoading ? undefined : handleCameraCapture}
          className="flex-row items-center py-5 px-5 rounded-2xl bg-card"
          style={{
            opacity: isLoading ? 0.6 : 1,
            boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05)',
          }}
        >
          <view className="w-14 h-14 rounded-2xl bg-primary items-center justify-center mr-4">
            <CameraIcon size={26} color="#FFFFFF" />
          </view>
          <view className="flex-1">
            <text className="text-base font-semibold text-foreground mb-1">
              Take a Photo
            </text>
            <text className="text-sm text-muted-foreground">
              Capture a new silhouette shot
            </text>
          </view>
        </view>
      </view>

      {/* Error Message */}
      {error && (
        <view className="bg-rose py-4 px-4 rounded-2xl mb-4">
          <text className="text-white text-sm text-center">{error}</text>
        </view>
      )}

      {/* Loading State */}
      {isLoading && (
        <view className="items-center mb-4">
          <text className="text-muted-foreground text-sm">Loading...</text>
        </view>
      )}

      {/* Tips */}
      <view className="flex-1" />

      <view className="bg-secondary p-5 mb-4 rounded-2xl">
        <text className="text-sm font-semibold text-primary mb-3 text-center">
          Tips for the best results
        </text>
        <text
          className="text-sm text-muted-foreground text-center"
          style={{ lineHeight: '22px' }}
        >
          • Wear fitted clothing (activewear works great){'\n'}
          • Stand in good lighting{'\n'}
          • Face the camera straight on
        </text>
      </view>

      {/* Privacy Note */}
      <view className="items-center">
        <text className="text-xs text-muted-foreground text-center">
          Your photos are private and secure
        </text>
      </view>
    </view>
  );
};

export default OnboardingPhotoScreen;
