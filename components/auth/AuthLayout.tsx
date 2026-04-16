import { LinearGradient } from 'expo-linear-gradient';
import { Image, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import type { ReactNode } from 'react';

interface AuthLayoutProps {
  children: ReactNode;
  compactTop?: boolean;
}

export default function AuthLayout({ children, compactTop = false }: AuthLayoutProps) {
  return (
    <LinearGradient
      colors={['#FFFFFF', '#ECCDF2']}
      start={{ x: 0, y: 0 }}
      end={{ x: 0, y: 1 }}
      style={styles.gradient}>
      <SafeAreaView style={styles.safeArea} edges={['top', 'left', 'right']}>
        <View style={[styles.logoWrap, compactTop && styles.logoWrapCompact]}>
          <Image
            source={require('@/assets/images/splash-logo.png')}
            style={styles.logo}
            resizeMode="contain"
          />
        </View>
        <View style={styles.content}>{children}</View>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  gradient: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
  },
  logoWrap: {
    alignItems: 'center',
    marginTop: 22,
    marginBottom: 12,
  },
  logoWrapCompact: {
    marginTop: 10,
    marginBottom: 8,
  },
  logo: {
    width: 165,
    height: 44,
  },
  content: {
    flex: 1,
    paddingHorizontal: 24,
  },
});
