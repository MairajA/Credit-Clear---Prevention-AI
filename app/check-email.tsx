import { Stack, useRouter } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

import AuthLayout from '@/components/auth/AuthLayout';
import { authStyles } from '@/components/auth/authStyles';

export default function CheckEmailScreen() {
  const router = useRouter();

  return (
    <>
      <Stack.Screen options={{ headerShown: false }} />
      <AuthLayout>
        <View style={styles.iconWrap}>
          <View style={styles.iconBlobLeft} />
          <View style={styles.iconBlobRight} />
          <Ionicons name="checkmark-circle-outline" size={120} color="#662F89" />
        </View>

        <Text style={styles.title}>Check Email</Text>
        <Text style={styles.body}>
          We've shared link on email, to verify and{'\n'}continue for reset password
        </Text>

        <View style={styles.bottomZone}>
          <Pressable style={authStyles.bottomButton} onPress={() => router.replace('/login')}>
            <Text style={authStyles.bottomButtonText}>Done</Text>
          </Pressable>
        </View>
      </AuthLayout>
    </>
  );
}

const styles = StyleSheet.create({
  iconWrap: {
    marginTop: 56,
    alignItems: 'center',
    justifyContent: 'center',
    height: 220,
  },
  iconBlobLeft: {
    position: 'absolute',
    width: 130,
    height: 100,
    borderRadius: 40,
    backgroundColor: 'rgba(221, 177, 234, 0.35)',
    left: 60,
    top: 72,
  },
  iconBlobRight: {
    position: 'absolute',
    width: 130,
    height: 100,
    borderRadius: 40,
    backgroundColor: 'rgba(221, 177, 234, 0.35)',
    right: 60,
    top: 82,
  },
  title: {
    textAlign: 'center',
    fontSize: 46,
    fontWeight: '800',
    color: '#1F1F3D',
    marginTop: 8,
  },
  body: {
    textAlign: 'center',
    fontSize: 16,
    color: '#293149',
    lineHeight: 24,
    marginTop: 12,
  },
  bottomZone: {
    flex: 1,
    justifyContent: 'flex-end',
  },
});
