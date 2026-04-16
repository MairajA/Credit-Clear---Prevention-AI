import { Stack } from 'expo-router';
import SplashScreenComponent from '@/components/SplashScreen';

export default function SplashScreen() {
  return (
    <>
      <Stack.Screen options={{ headerShown: false }} />
      <SplashScreenComponent />
    </>
  );
}
