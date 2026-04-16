import { Stack, useRouter } from 'expo-router';
import { Pressable, StyleSheet, Text, View, Image } from 'react-native';

import AuthLayout from '@/components/auth/AuthLayout';

export default function WelcomeScreen() {
  const router = useRouter();

  return (
    <>
      <Stack.Screen options={{ headerShown: false }} />
      <AuthLayout>
        <Pressable onPress={() => router.back()} style={styles.backWrap}>
          <Text style={styles.backText}>Back</Text>
        </Pressable>

        <View style={styles.content}>
          <Image
            source={require('@/assets/images/splash-logo1.png')}
            style={styles.mark}
            resizeMode="contain"
          />

          <Text style={styles.title}>Welcome Bilal!</Text>
          <Text style={styles.body}>
            It seems everything went well and your app is ready to work with you
          </Text>
        </View>

        <Pressable style={styles.cta} onPress={() => router.replace('/connect-accounts')}>
          <Text style={styles.ctaText}>Continue</Text>
        </Pressable>
      </AuthLayout>
    </>
  );
}

const styles = StyleSheet.create({
  backWrap: {
    marginTop: 6,
  },
  backText: {
    color: '#1F1F3D',
    fontSize: 15,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 10,
  },
  mark: {
    width: 160,
    height: 160,
    marginBottom: 24,
  },
  title: {
    fontSize: 45,
    fontWeight: '800',
    color: '#1F1F3D',
    marginBottom: 12,
    textAlign: 'center',
  },
  body: {
    textAlign: 'center',
    color: '#293149',
    fontSize: 17,
    lineHeight: 24,
  },
  cta: {
    height: 52,
    borderRadius: 10,
    backgroundColor: '#662F89',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  ctaText: {
    color: '#FFFFFF',
    fontWeight: '700',
    fontSize: 18,
  },
});
