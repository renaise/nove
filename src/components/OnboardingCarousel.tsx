import { useState, useRef } from '@lynx-js/react';

// Import onboarding images
import step1Image from '../assets/onboarding/step1-silhouette.png';
import step2Image from '../assets/onboarding/step2-filter.png';
import step3Image from '../assets/onboarding/step3-tryon.png';
import step4Image from '../assets/onboarding/step4-nextstep.png';

// Carousel slide data from BRAND.md
const SLIDES = [
  {
    id: 'silhouette',
    image: step1Image,
    title: "Let's Capture Your True Silhouette",
    body: 'To ensure your dream dress fits flawlessly, our AI needs to see your natural shape. We recommend wearing fitted activewear or a simple bodysuit—think of it as a blank canvas for your transformation.',
    tooltip: {
      trigger: 'Why fitted?',
      content:
        'Loose clothing changes the dress shape. A true silhouette ensures the "Yes" dress looks just as good virtually as it will in the boutique.',
    },
    privacyNote: 'Strictly Private. Your photos are processed securely and never shared.',
  },
  {
    id: 'filter',
    image: step2Image,
    title: 'The Dream Filter',
    body: 'Endless Love, Zero Effort: Swipe through thousands of styles, effortlessly. Filter by Fairy-tale, Modern, Lace, Flowy—and discover dresses you never knew you needed.',
  },
  {
    id: 'truth',
    image: step3Image,
    title: 'The Moment of Truth',
    body: "Is It The One? Your dream dress, flawlessly fitted for this moment. Our AI creates a stunning visualization that feels real—because this is your special journey.",
  },
  {
    id: 'nextstep',
    image: step4Image,
    title: 'The Next Step',
    body: 'Ready to Feel the Fabric? Your journey continues with your local boutique. Share your favorites, chat with stylists, and book fittings—all from the app.',
    ctaText: 'Start Your Joyful Discovery',
  },
];

// Minimum swipe distance to trigger slide change
const SWIPE_THRESHOLD = 50;

interface OnboardingCarouselProps {
  onComplete: () => void;
}

const OnboardingCarousel = ({ onComplete }: OnboardingCarouselProps) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showTooltip, setShowTooltip] = useState(false);
  const touchStartRef = useRef<number>(0);

  const currentSlide = SLIDES[currentIndex];
  const isLastSlide = currentIndex === SLIDES.length - 1;

  const handleNext = () => {
    if (isLastSlide) {
      onComplete();
    } else {
      setCurrentIndex(currentIndex + 1);
      setShowTooltip(false);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setShowTooltip(false);
    }
  };

  // Swipe gesture handlers
  const handleTouchStart = (e: any) => {
    const touches = e.detail?.touches || e.touches || [];
    const touch = touches[0];
    if (touch) {
      touchStartRef.current = touch.clientX ?? touch.pageX ?? touch.x ?? 0;
    }
  };

  const handleTouchEnd = (e: any) => {
    const touches = e.detail?.changedTouches || e.changedTouches || [];
    const touch = touches[0];
    if (touch) {
      const endX = touch.clientX ?? touch.pageX ?? touch.x ?? 0;
      const diff = touchStartRef.current - endX;

      if (Math.abs(diff) > SWIPE_THRESHOLD) {
        if (diff > 0) {
          // Swipe left - go next
          if (currentIndex < SLIDES.length - 1) {
            setCurrentIndex(currentIndex + 1);
            setShowTooltip(false);
          }
        } else {
          // Swipe right - go prev
          if (currentIndex > 0) {
            setCurrentIndex(currentIndex - 1);
            setShowTooltip(false);
          }
        }
      }
    }
  };

  return (
    <view
      className="flex-1 w-full pt-[60px] pb-10 px-6"
      bindtouchstart={handleTouchStart}
      bindtouchend={handleTouchEnd}
    >
      {/* Image Container */}
      <view className="items-center mb-6">
        <view
          className="rounded-2xl overflow-hidden"
          style={{ width: '280px', height: '280px' }}
        >
          <image
            src={currentSlide.image}
            className="w-full h-full"
            style={{ objectFit: 'cover' }}
          />
        </view>
      </view>

      {/* Content */}
      <view className="flex-1">
        {/* Title */}
        <text
          className="text-[28px] font-bold text-foreground text-center mb-4"
          style={{ lineHeight: '36px' }}
        >
          {currentSlide.title}
        </text>

        {/* Body */}
        <text
          className="text-base text-muted-foreground text-center mb-4"
          style={{ lineHeight: '24px' }}
        >
          {currentSlide.body}
        </text>

        {/* Tooltip (for first slide) */}
        {currentSlide.tooltip && (
          <view className="items-center mb-4">
            <view
              bindtap={() => setShowTooltip(!showTooltip)}
              className="py-2 px-4"
            >
              <text className="text-primary text-sm font-semibold">
                {currentSlide.tooltip.trigger}
              </text>
            </view>

            {showTooltip && (
              <view
                className="p-4 mx-4 mt-2 bg-secondary rounded-2xl"
                style={{
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05)',
                }}
              >
                <text
                  className="text-sm text-foreground text-center"
                  style={{ lineHeight: '22px' }}
                >
                  {currentSlide.tooltip.content}
                </text>
              </view>
            )}
          </view>
        )}

        {/* Privacy Note (for first slide) */}
        {currentSlide.privacyNote && (
          <view className="items-center mt-4">
            <text className="text-xs text-muted-foreground text-center">
              🔒 {currentSlide.privacyNote}
            </text>
          </view>
        )}
      </view>

      {/* Pagination Dots - Horizontal row */}
      <view className="items-center mb-6">
        <view style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', gap: '8px' }}>
          <view
            bindtap={() => { setCurrentIndex(0); setShowTooltip(false); }}
            style={{ padding: '4px' }}
          >
            <view
              style={{
                width: currentIndex === 0 ? '28px' : '8px',
                height: '8px',
                borderRadius: '4px',
                backgroundColor: currentIndex === 0 ? '#E6B88A' : '#E5E5EA',
              }}
            />
          </view>
          <view
            bindtap={() => { setCurrentIndex(1); setShowTooltip(false); }}
            style={{ padding: '4px' }}
          >
            <view
              style={{
                width: currentIndex === 1 ? '28px' : '8px',
                height: '8px',
                borderRadius: '4px',
                backgroundColor: currentIndex === 1 ? '#E6B88A' : '#E5E5EA',
              }}
            />
          </view>
          <view
            bindtap={() => { setCurrentIndex(2); setShowTooltip(false); }}
            style={{ padding: '4px' }}
          >
            <view
              style={{
                width: currentIndex === 2 ? '28px' : '8px',
                height: '8px',
                borderRadius: '4px',
                backgroundColor: currentIndex === 2 ? '#E6B88A' : '#E5E5EA',
              }}
            />
          </view>
          <view
            bindtap={() => { setCurrentIndex(3); setShowTooltip(false); }}
            style={{ padding: '4px' }}
          >
            <view
              style={{
                width: currentIndex === 3 ? '28px' : '8px',
                height: '8px',
                borderRadius: '4px',
                backgroundColor: currentIndex === 3 ? '#E6B88A' : '#E5E5EA',
              }}
            />
          </view>
        </view>
      </view>

      {/* Navigation Buttons - Horizontal row */}
      <view className="flex-row" style={{ gap: '12px' }}>
        {/* Back Button (hidden on first slide) */}
        {currentIndex > 0 ? (
          <view
            bindtap={handlePrev}
            className="flex-1 py-4 rounded-2xl items-center bg-secondary"
          >
            <text className="text-foreground font-semibold text-base">Back</text>
          </view>
        ) : (
          <view className="flex-1" />
        )}

        {/* Next/Complete Button */}
        <view
          bindtap={handleNext}
          className="flex-1 bg-primary py-4 rounded-2xl items-center"
        >
          <text className="text-white font-semibold text-base">
            {isLastSlide ? (currentSlide.ctaText || "Let's Begin") : 'Next'}
          </text>
        </view>
      </view>
    </view>
  );
};

export default OnboardingCarousel;
