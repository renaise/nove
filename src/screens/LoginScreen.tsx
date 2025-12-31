import { useState } from '@lynx-js/react';
import { useApp } from '../context/AppContext.jsx';
import { AuthService } from '../services/AuthService.js';
import { OnboardingService } from '../services/OnboardingService.js';
import { HeartIcon } from '../components/Icons.jsx';

const LoginScreen = () => {
  const { navigateTo, setUser } = useApp();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSignInWithApple = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await AuthService.signInWithApple();

      if (result.success && result.user) {
        console.log(
          `[LoginScreen] Sign in successful: ${result.user.email}`,
        );
        setUser({
          id: result.user.id,
          name: result.user.name,
          email: result.user.email,
        });

        // Check onboarding progress and navigate accordingly
        if (!OnboardingService.isCarouselComplete()) {
          console.log(
            '[LoginScreen] Navigating to onboarding carousel',
          );
          navigateTo('onboarding_carousel');
        } else if (!OnboardingService.isPhotoProvided()) {
          console.log(
            '[LoginScreen] Navigating to photo capture',
          );
          navigateTo('onboarding_photo');
        } else {
          console.log(
            '[LoginScreen] Onboarding complete, navigating to home',
          );
          navigateTo('home');
        }
      } else {
        setError(result.error || 'Sign in failed');
      }
    } catch (err) {
      console.log(
        `[LoginScreen] Sign in error: ${err}`,
      );
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <view className="flex-1 w-full items-center justify-center px-8">
      {/* Logo/Branding */}
      <view className="items-center mb-16">
        <view className="w-[100px] h-[100px] rounded-full bg-blush items-center justify-center mb-8">
          <HeartIcon size={52} color="#E6B88A" />
        </view>
        <text className="text-[44px] font-bold text-foreground mb-3">
          Nove
        </text>
        <text className="text-base text-muted-foreground text-center" style={{ lineHeight: '24px' }}>
          Your wedding vision, beautifully realized
        </text>
      </view>

      {/* Sign In Section */}
      <view className="w-full items-center">
        {/* Sign in with Apple Button */}
        <view
          bindtap={isLoading ? undefined : handleSignInWithApple}
          className="w-full bg-foreground py-4 px-6 rounded-2xl flex flex-row items-center justify-center mb-4"
          style={{ opacity: isLoading ? 0.6 : 1 }}
        >
          {/* Apple Logo */}
          <novia-svg
            content='<svg viewBox="0 0 24 24"><path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/></svg>'
            tintColor="#FFFFFF"
            className="w-5 h-5 mr-3"
          />
          <text className="text-white font-semibold text-base">
            {isLoading ? 'Signing in...' : 'Continue with Apple'}
          </text>
        </view>

        {/* Error Message */}
        {error && (
          <view className="w-full bg-rose py-3 px-4 rounded-2xl mb-4">
            <text className="text-white text-sm text-center">
              {error}
            </text>
          </view>
        )}
      </view>

      {/* Terms */}
      <view className="absolute bottom-12 left-8 right-8">
        <text className="text-muted-foreground text-xs text-center" style={{ lineHeight: '20px' }}>
          By continuing, you agree to our Terms of Service and Privacy Policy
        </text>
      </view>
    </view>
  );
};

export default LoginScreen;
