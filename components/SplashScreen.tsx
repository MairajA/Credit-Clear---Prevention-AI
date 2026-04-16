import { View, Image, StyleSheet, Animated, Easing } from 'react-native';
import { useEffect, useRef } from 'react';
import { useRouter } from 'expo-router';

export default function SplashScreenComponent() {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const router = useRouter();

  useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 1200,
      easing: Easing.ease,
      useNativeDriver: true,
    }).start();

    const timer = setTimeout(() => {
      router.replace('/onboarding');
    }, 7000);

    return () => clearTimeout(timer);
  }, [fadeAnim, router]);

  return (
    <View style={styles.container}>
      {/* Background decorative shapes */}
      <View style={styles.decorativeTop} />
      <View style={styles.decorativeBottom} />
      <View style={styles.decorativeBottomLeft} />

      <Animated.View style={[styles.content, { opacity: fadeAnim }]}>
        {/* Vertical Layout - Brain Icon on top, Text below */}
        <View style={styles.logoContainer}>
          {/* Brain Icon - Top (splash-logo1) */}
          <Image
            source={require('@/assets/images/splash-logo1.png')}
            style={styles.brainIcon}
            resizeMode="contain"
          />

          {/* Text - Below (splash-logo2 - CREDIT & PREVENTION AI) */}
          <Image
            source={require('@/assets/images/splash-logo2.png')}
            style={styles.textImage}
            resizeMode="contain"
          />
        </View>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    overflow: 'hidden',
  },
  decorativeTop: {
    position: 'absolute',
    top: -100,
    right: -100,
    width: 400,
    height: 400,
    backgroundColor: 'rgba(236, 205, 242, 0.3)',
    borderRadius: 200,
  },
  decorativeBottom: {
    position: 'absolute',
    bottom: -150,
    right: -80,
    width: 350,
    height: 350,
    backgroundColor: 'rgba(220, 180, 230, 0.2)',
    borderRadius: 175,
  },
  decorativeBottomLeft: {
    position: 'absolute',
    bottom: -120,
    left: -100,
    width: 320,
    height: 320,
    backgroundColor: 'rgba(230, 200, 240, 0.25)',
    borderRadius: 160,
  },
  content: {
    justifyContent: 'center',
    alignItems: 'center',
    width: '90%',
    zIndex: 10,
  },
  logoContainer: {
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 24,
    width: '100%',
  },
  brainIcon: {
    width: 120,
    height: 120,
  },
  textImage: {
    width: 240,
    height: 120,
  },
});
