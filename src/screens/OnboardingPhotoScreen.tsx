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
      <novia-liquid-glass
        glassStyle="clear"
        tintColor="#FFFFFF"
        tintAlpha={0.2}
        cornerRadius={24}
        addBorder={true}
        className="p-6 mb-6"
      >
        {/* Gallery Option */}
        <view
          bindtap={isLoading ? undefined : handleGalleryPick}
          className="flex-row items-center py-4 px-4 rounded-xl mb-3"
          style={{
            backgroundColor: '#F8E8E8',
            opacity: isLoading ? 0.6 : 1,
          }}
        >
          <view className="w-12 h-12 rounded-full bg-gold items-center justify-center mr-4">
            <GalleryIcon size={24} color="#FFFFFF" />
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
          className="flex-row items-center py-4 px-4 rounded-xl"
          style={{
            backgroundColor: '#F7E7CE',
            opacity: isLoading ? 0.6 : 1,
          }}
        >
          <view className="w-12 h-12 rounded-full bg-gold items-center justify-center mr-4">
            <CameraIcon size={24} color="#FFFFFF" />
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
      </novia-liquid-glass>

      {/* Error Message */}
      {error && (
        <view className="bg-rose/20 py-3 px-4 rounded-lg mb-4">
          <text className="text-rose text-sm text-center">{error}</text>
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

      <novia-liquid-glass
        glassStyle="clear"
        tintColor="#D4AF37"
        tintAlpha={0.05}
        cornerRadius={16}
        addBorder={false}
        className="p-4 mb-4"
      >
        <text className="text-sm font-semibold text-gold mb-2 text-center">
          Tips for the best results
        </text>
        <text
          className="text-xs text-muted-foreground text-center"
          style={{ lineHeight: '18px' }}
        >
          • Wear fitted clothing (activewear works great){'\n'}
          • Stand in good lighting{'\n'}
          • Face the camera straight on
        </text>
      </novia-liquid-glass>

      {/* Privacy Note */}
      <view className="items-center">
        <text className="text-xs text-muted-foreground text-center">
          🔒 Your photos are strictly private and never shared
        </text>
      </view>
    </view>
  );
};

export default OnboardingPhotoScreen;
