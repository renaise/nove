import { createContext, useContext, useState, useCallback, ReactNode } from '@lynx-js/react';

// Screen types for the wedding app
export type Screen =
  | 'splash'
  | 'login'              // Sign in with Apple
  | 'onboarding_carousel' // Onboarding: 4-page intro carousel
  | 'onboarding_photo'   // Onboarding: Photo capture
  | 'home'
  | 'marketplace'        // Dress marketplace/gallery
  | 'tryon'              // Try-on preview for selected dress
  | 'gallery'            // Browse dresses/venues (legacy)
  | 'camera'             // Take/select photos
  | 'results'            // View try-on results
  | 'profile';

export interface User {
  id: string;
  name: string;
  email: string;
}

interface AppState {
  currentScreen: Screen;
  previousScreen?: Screen;
  user: User | null;
  selectedPhoto: string | null;  // URI of selected bride photo
  selectedDress: string | null;  // ID of selected dress
}

interface AppContextType {
  state: AppState;
  navigateTo: (screen: Screen, data?: Partial<AppState>) => void;
  goBack: () => void;
  setUser: (user: User | null) => void;
  setSelectedPhoto: (uri: string | null) => void;
  setSelectedDress: (id: string | null) => void;
}

const initialState: AppState = {
  currentScreen: 'login',
  user: null,
  selectedPhoto: null,
  selectedDress: null,
};

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider = ({ children }: { children: ReactNode }) => {
  const [state, setState] = useState<AppState>(initialState);

  const navigateTo = useCallback((screen: Screen, data?: Partial<AppState>) => {
    setState((prev) => ({
      ...prev,
      ...data,
      previousScreen: prev.currentScreen,
      currentScreen: screen,
    }));
  }, []);

  const goBack = useCallback(() => {
    setState((prev) => ({
      ...prev,
      currentScreen: prev.previousScreen || 'home',
      previousScreen: undefined,
    }));
  }, []);

  const setUser = useCallback((user: User | null) => {
    setState((prev) => ({ ...prev, user }));
  }, []);

  const setSelectedPhoto = useCallback((uri: string | null) => {
    setState((prev) => ({ ...prev, selectedPhoto: uri }));
  }, []);

  const setSelectedDress = useCallback((id: string | null) => {
    setState((prev) => ({ ...prev, selectedDress: id }));
  }, []);

  return (
    <AppContext.Provider
      value={{
        state,
        navigateTo,
        goBack,
        setUser,
        setSelectedPhoto,
        setSelectedDress,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = (): AppContextType => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
