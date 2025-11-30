import { useApp } from '../context/AppContext.jsx';
import HomeScreen from '../screens/HomeScreen.jsx';
import TryOnScreen from '../screens/TryOnScreen.jsx';
import LoginScreen from '../screens/LoginScreen.jsx';
import OnboardingCarouselScreen from '../screens/OnboardingCarouselScreen.jsx';
import OnboardingPhotoScreen from '../screens/OnboardingPhotoScreen.jsx';

const AppContent = () => {
  const { state } = useApp();
  const { currentScreen } = state;

  // Render the appropriate screen based on navigation state
  switch (currentScreen) {
    case 'splash':
      return <HomeScreen />; // TODO: Add splash screen
    case 'login':
      return <LoginScreen />;
    case 'onboarding_carousel':
      return <OnboardingCarouselScreen />;
    case 'onboarding_photo':
      return <OnboardingPhotoScreen />;
    case 'home':
      return <HomeScreen />;
    case 'tryon':
      return <TryOnScreen />;
    case 'gallery':
      return <HomeScreen />; // TODO: Add gallery screen
    case 'camera':
      return <HomeScreen />; // TODO: Add camera screen
    case 'results':
      return <HomeScreen />; // TODO: Add results screen
    case 'profile':
      return <HomeScreen />; // TODO: Add profile screen
    default:
      return <HomeScreen />;
  }
};

export default AppContent;
