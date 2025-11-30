import { useState } from '@lynx-js/react';

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

interface OnboardingCarouselProps {
  onComplete: () => void;
}

const OnboardingCarousel = ({ onComplete }: OnboardingCarouselProps) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showTooltip, setShowTooltip] = useState(false);

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

  return (
    <view className="flex-1 w-full pt-[60px] pb-10 px-6">
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
              <text className="text-gold text-sm font-semibold">
                {currentSlide.tooltip.trigger}
              </text>
            </view>

            {showTooltip && (
              <novia-liquid-glass
                glassStyle="clear"
                tintColor="#D4AF37"
                tintAlpha={0.1}
                cornerRadius={12}
                addBorder={true}
                className="p-4 mx-4 mt-2"
              >
                <text
                  className="text-sm text-foreground text-center"
                  style={{ lineHeight: '20px' }}
                >
                  {currentSlide.tooltip.content}
                </text>
              </novia-liquid-glass>
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

      {/* Pagination Dots */}
      <view className="flex-row justify-center items-center mb-6" style={{ gap: '8px' }}>
        {SLIDES.map((_, idx) => (
          <view
            key={idx}
            bindtap={() => {
              setCurrentIndex(idx);
              setShowTooltip(false);
            }}
            className="p-1"
          >
            <view
              style={{
                width: idx === currentIndex ? '24px' : '8px',
                height: '8px',
                borderRadius: '4px',
                backgroundColor: idx === currentIndex ? '#D4AF37' : '#E5E5E5',
              }}
            />
          </view>
        ))}
      </view>

      {/* Navigation Buttons */}
      <view className="flex-row" style={{ gap: '12px' }}>
        {/* Back Button (hidden on first slide) */}
        {currentIndex > 0 ? (
          <view
            bindtap={handlePrev}
            className="flex-1 py-4 rounded-xl items-center border border-champagne"
          >
            <text className="text-muted-foreground font-semibold text-base">Back</text>
          </view>
        ) : (
          <view className="flex-1" />
        )}

        {/* Next/Complete Button */}
        <view
          bindtap={handleNext}
          className="flex-1 bg-gold py-4 rounded-xl items-center"
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
