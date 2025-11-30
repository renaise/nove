import { useState } from '@lynx-js/react';
import { useApp } from '../context/AppContext.jsx';
import { GalleryIcon, SelfieIcon, BackIcon, DressIcon, HeartIcon } from '../components/Icons.jsx';

const TryOnScreen = () => {
  const { goBack, state, setSelectedPhoto } = useApp();
  const [showWhyTooltip, setShowWhyTooltip] = useState(false);

  const handleBackPress = () => {
    goBack();
  };

  const handleSelectPhoto = () => {
    NativeModules.ConsoleLynxProvider?.logToConsole('Select photo tapped');
    // TODO: Open gallery picker
  };

  const handleTakeSelfie = () => {
    NativeModules.ConsoleLynxProvider?.logToConsole('Take selfie tapped');
    // TODO: Open camera
  };

  const toggleWhyTooltip = () => {
    setShowWhyTooltip(!showWhyTooltip);
  };

  return (
    <view className="flex-1 w-full App">
      {/* Header */}
      <novia-liquid-glass
        glassStyle="clear"
        tintColor="#FFFFFF"
        tintAlpha={0.5}
        addBorder={false}
        className="flex-row items-center pt-[60px] pb-4 px-5 border-b border-white/20"
      >
        <view bindtap={handleBackPress} className="p-2 mr-2">
          <BackIcon size={24} color="#2D2D2D" />
        </view>
        <text className="flex-1 text-xl font-semibold text-foreground text-center mr-10">
          Your Journey to "Yes"
        </text>
      </novia-liquid-glass>

      {/* Content */}
      <scroll-view className="flex-1" scroll-y={true}>
        <view className="py-6 px-5">
          {/* Step 1: Capture Your True Silhouette */}
          <novia-liquid-glass
            glassStyle="clear"
            tintColor="#FFFFFF"
            tintAlpha={0.2}
            cornerRadius={24}
            addBorder={true}
            className="p-5 mb-4"
          >
            <view className="flex-row items-center mb-3">
              <view className="w-8 h-8 rounded-full bg-gold items-center justify-center mr-3">
                <text className="text-white font-bold">1</text>
              </view>
              <text className="text-lg font-semibold text-foreground">
                Capture Your True Silhouette
              </text>
            </view>

            <text className="text-sm text-muted-foreground mb-2" style={{ lineHeight: '20px' }}>
              To ensure your dream dress fits flawlessly, our AI needs to see your natural shape.
            </text>

            <text className="text-sm text-foreground mb-3" style={{ lineHeight: '20px' }}>
              Wear fitted activewear or a simple bodysuit—think of it as a blank canvas for your transformation.
            </text>

            {/* Why Fitted? Tooltip */}
            <view bindtap={toggleWhyTooltip} className="mb-4">
              <text className="text-sm text-gold underline">Why fitted clothing?</text>
            </view>

            {showWhyTooltip && (
              <view className="bg-champagne p-3 rounded-lg mb-4">
                <text className="text-sm text-foreground" style={{ lineHeight: '18px' }}>
                  Loose clothing changes the dress shape. A true silhouette ensures the "Yes" dress looks just as good virtually as it will in the boutique.
                </text>
              </view>
            )}

            <view className="flex flex-row" style={{ gap: '12px' }}>
              <view
                bindtap={handleSelectPhoto}
                className="flex-1 bg-blush py-4 rounded-xl items-center"
              >
                <view className="mb-2">
                  <GalleryIcon size={28} color="#D4AF37" />
                </view>
                <text className="text-sm font-semibold text-foreground">
                  From Gallery
                </text>
              </view>
              <view
                bindtap={handleTakeSelfie}
                className="flex-1 bg-blush py-4 rounded-xl items-center"
              >
                <view className="mb-2">
                  <SelfieIcon size={28} color="#D4AF37" />
                </view>
                <text className="text-sm font-semibold text-foreground">
                  Take Photo
                </text>
              </view>
            </view>

            {/* Privacy Note */}
            <view className="mt-4 flex-row items-center justify-center">
              <text className="text-xs text-muted-foreground">
                🔒 Strictly Private. Your photos are processed securely and never shared.
              </text>
            </view>
          </novia-liquid-glass>

          {/* Step 2: The Dream Filter */}
          <novia-liquid-glass
            glassStyle="clear"
            tintColor="#FFFFFF"
            tintAlpha={0.2}
            cornerRadius={24}
            addBorder={true}
            className="p-5 mb-4"
            style={{ opacity: state.selectedPhoto ? 1 : 0.5 }}
          >
            <view className="flex-row items-center mb-3">
              <view
                className="w-8 h-8 rounded-full items-center justify-center mr-3"
                style={{ backgroundColor: state.selectedPhoto ? '#D4AF37' : '#E5E5E5' }}
              >
                <text className="text-white font-bold">2</text>
              </view>
              <text className="text-lg font-semibold text-foreground">
                The Dream Filter
              </text>
            </view>

            <text className="text-sm text-muted-foreground mb-2" style={{ lineHeight: '20px' }}>
              Endless Love, Zero Effort.
            </text>

            <text className="text-sm text-foreground mb-4" style={{ lineHeight: '20px' }}>
              Swipe through stunning styles—Fairy-tale, Modern, Lace, or Flowy.
            </text>

            {/* Dress Style Tags */}
            <view className="flex flex-row flex-wrap mb-4" style={{ gap: '8px' }}>
              {['Fairy-tale', 'Modern', 'Lace', 'Flowy', 'Classic'].map((style) => (
                <view key={style} className="px-3 py-1 bg-blush rounded-full">
                  <text className="text-xs text-foreground">{style}</text>
                </view>
              ))}
            </view>

            {/* Dress Grid Preview */}
            <view className="flex flex-row" style={{ gap: '8px' }}>
              {[1, 2, 3].map((i) => (
                <view
                  key={i}
                  className="flex-1 bg-ivory rounded-lg items-center justify-center border border-champagne"
                  style={{ aspectRatio: 0.75 }}
                >
                  <DressIcon size={32} color="#D4AF37" />
                </view>
              ))}
            </view>
          </novia-liquid-glass>

          {/* Step 3: The Moment of Truth */}
          <novia-liquid-glass
            glassStyle="clear"
            tintColor="#FFFFFF"
            tintAlpha={0.2}
            cornerRadius={24}
            addBorder={true}
            className="p-5 mb-4"
            style={{ opacity: state.selectedPhoto && state.selectedDress ? 1 : 0.3 }}
          >
            <view className="flex-row items-center mb-3">
              <view
                className="w-8 h-8 rounded-full items-center justify-center mr-3"
                style={{ backgroundColor: state.selectedPhoto && state.selectedDress ? '#D4AF37' : '#E5E5E5' }}
              >
                <text className="text-white font-bold">3</text>
              </view>
              <text className="text-lg font-semibold text-foreground">
                The Moment of Truth
              </text>
            </view>

            <text className="text-sm text-foreground italic" style={{ lineHeight: '20px' }}>
              "Is It The One?"
            </text>

            <text className="text-sm text-muted-foreground mt-2" style={{ lineHeight: '20px' }}>
              See yourself in your dream dress, flawlessly fitted by our AI.
            </text>
          </novia-liquid-glass>

          {/* Generate CTA Button */}
          <view
            className="py-4 rounded-xl items-center flex-row justify-center"
            style={{
              backgroundColor: state.selectedPhoto && state.selectedDress ? '#D4AF37' : '#E5E5E5',
            }}
          >
            <HeartIcon
              size={20}
              color={state.selectedPhoto && state.selectedDress ? '#FFFFFF' : '#737373'}
            />
            <text
              className="font-semibold text-lg ml-2"
              style={{
                color: state.selectedPhoto && state.selectedDress ? '#FFFFFF' : '#737373',
              }}
            >
              Discover My Silhouette
            </text>
          </view>

          {/* Bottom spacing */}
          <view className="h-8" />
        </view>
      </scroll-view>
    </view>
  );
};

export default TryOnScreen;
