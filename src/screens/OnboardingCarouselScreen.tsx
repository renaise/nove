import { useApp } from '../context/AppContext.jsx';
import OnboardingCarousel from '../components/OnboardingCarousel.jsx';
import { OnboardingService } from '../services/OnboardingService.js';

const OnboardingCarouselScreen = () => {
  const { navigateTo } = useApp();

  const handleComplete = () => {
    NativeModules.ConsoleLynxProvider?.logToConsole(
      '[OnboardingCarouselScreen] Carousel complete, navigating to photo capture',
    );
    OnboardingService.setCarouselComplete();
    navigateTo('onboarding_photo');
  };

  return (
    <view className="flex-1 bg-ivory">
      <OnboardingCarousel onComplete={handleComplete} />
    </view>
  );
};

export default OnboardingCarouselScreen;
