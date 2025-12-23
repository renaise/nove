import { useEffect, useState } from '@lynx-js/react';
import { AppProvider, useApp } from './context/AppContext.jsx';
import AppContent from './components/AppContent.jsx';
import { AuthService } from './services/AuthService.js';
import { OnboardingService } from './services/OnboardingService.js';
import './App.css';

/**
 * AppInitializer handles session restoration and initial navigation.
 * Must be inside AppProvider to access navigation context.
 */
const AppInitializer = () => {
  const { navigateTo, setUser } = useApp();
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    const initializeApp = () => {
      console.log(
        '[App] Initializing app, checking session...',
      );

      // Try to restore existing session
      const session = AuthService.restoreSession();

      if (session && session.user) {
        console.log(
          `[App] Session restored for: ${session.user.email}`,
        );
        setUser(session.user);

        // Check onboarding progress
        const carouselComplete = OnboardingService.isCarouselComplete();
        const photoProvided = OnboardingService.isPhotoProvided();

        console.log(
          `[App] Onboarding status - carousel: ${carouselComplete}, photo: ${photoProvided}`,
        );

        if (!carouselComplete) {
          navigateTo('onboarding_carousel');
        } else if (!photoProvided) {
          navigateTo('onboarding_photo');
        } else {
          navigateTo('home');
        }
      } else {
        console.log(
          '[App] No session found, staying on login',
        );
        // Stay on login (default screen)
      }

      setIsInitialized(true);
    };

    initializeApp();
  }, []);

  if (!isInitialized) {
    // Show minimal loading state while checking session
    return (
      <view className="flex-1 bg-ivory items-center justify-center">
        <text className="text-gold text-2xl font-bold">Novia</text>
      </view>
    );
  }

  return <AppContent />;
};

export const App = () => {
  return (
    <AppProvider>
      <view className="App">
        <AppInitializer />
      </view>
    </AppProvider>
  );
};
