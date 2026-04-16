import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import 'react-native-reanimated';

import { useColorScheme } from '@/hooks/use-color-scheme';

export const unstable_settings = {
  anchor: '(tabs)',
};

export default function RootLayout() {
  const colorScheme = useColorScheme();

  return (
    <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
      <Stack>
        <Stack.Screen name="splash" options={{ headerShown: false }} />
        <Stack.Screen name="onboarding" options={{ headerShown: false }} />
        <Stack.Screen name="login" options={{ headerShown: false }} />
        <Stack.Screen name="signup" options={{ headerShown: false }} />
        <Stack.Screen name="phone-number" options={{ headerShown: false }} />
        <Stack.Screen name="phone-verification" options={{ headerShown: false }} />
        <Stack.Screen name="forgot-password" options={{ headerShown: false }} />
        <Stack.Screen name="forgot-password-verify" options={{ headerShown: false }} />
        <Stack.Screen name="check-email" options={{ headerShown: false }} />
        <Stack.Screen name="welcome" options={{ headerShown: false }} />
        <Stack.Screen name="connect-accounts" options={{ headerShown: false }} />
        <Stack.Screen name="connect-bank" options={{ headerShown: false }} />
        <Stack.Screen name="bank-list" options={{ headerShown: false }} />
        <Stack.Screen name="connect-bank-selected" options={{ headerShown: false }} />
        <Stack.Screen name="sign-in-bank" options={{ headerShown: false }} />
        <Stack.Screen name="sign-in-chase" options={{ headerShown: false }} />
        <Stack.Screen name="waiting-verification" options={{ headerShown: false }} />
        <Stack.Screen name="connected" options={{ headerShown: false }} />
        <Stack.Screen name="connected-banks" options={{ headerShown: false }} />
        <Stack.Screen name="detected-cards" options={{ headerShown: false }} />
        <Stack.Screen name="loans-bills" options={{ headerShown: false }} />
        <Stack.Screen name="analyzing" options={{ headerShown: false }} />
        <Stack.Screen name="scanned" options={{ headerShown: false }} />
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="modal" options={{ presentation: 'modal', title: 'Modal' }} />
      </Stack>
      <StatusBar style="auto" />
    </ThemeProvider>
  );
}
