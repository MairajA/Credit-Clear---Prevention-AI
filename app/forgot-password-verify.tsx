import { Stack, useRouter } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useState } from 'react';

import AuthLayout from '@/components/auth/AuthLayout';
import { authStyles } from '@/components/auth/authStyles';

export default function ForgotPasswordVerifyScreen() {
  const router = useRouter();
  const [digits, setDigits] = useState(['', '', '', '']);

  const setDigit = (index: number, value: string) => {
    const next = [...digits];
    next[index] = value;
    setDigits(next);
  };

  return (
    <>
      <Stack.Screen options={{ headerShown: false }} />
      <AuthLayout>
        <Text style={styles.title}>Verify email</Text>
        <Text style={styles.timer}>(00:52)</Text>

        <View style={styles.digitRow}>
          {digits.map((item, index) => {
            const active = index === 0;
            return (
              <Pressable
                key={index}
                style={[styles.digitBox, active && styles.digitBoxActive]}
                onPress={() => setDigit(index, item ? '' : `${index + 2}`)}>
                <Text style={[styles.digitText, active && styles.digitTextActive]}>{item || `${index + 2}`}</Text>
              </Pressable>
            );
          })}
        </View>

        <Text style={styles.sessionText}>This session will end in 60 seconds.</Text>
        <View style={styles.resendRow}>
          <Text style={authStyles.mutedText}>Didn't receive a code? </Text>
          <Pressable>
            <Text style={authStyles.linkText}>Resend Code</Text>
          </Pressable>
        </View>

        <View style={styles.bottomZone}>
          <Pressable style={authStyles.bottomButton} onPress={() => router.push('/check-email')}>
            <Text style={authStyles.bottomButtonText}>Verify</Text>
          </Pressable>
        </View>
      </AuthLayout>
    </>
  );
}

const styles = StyleSheet.create({
  title: {
    fontSize: 34,
    fontWeight: '800',
    color: '#1F1F3D',
    textAlign: 'center',
    marginTop: 8,
  },
  timer: {
    textAlign: 'center',
    color: '#7B4F96',
    marginTop: 4,
    marginBottom: 28,
  },
  digitRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 10,
  },
  digitBox: {
    width: 60,
    height: 62,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#E4E0EC',
    backgroundColor: '#F1F2F7',
    justifyContent: 'center',
    alignItems: 'center',
  },
  digitBoxActive: {
    backgroundColor: '#662F89',
    borderColor: '#662F89',
  },
  digitText: {
    fontSize: 42,
    lineHeight: 44,
    fontWeight: '700',
    color: '#1F1F3D',
  },
  digitTextActive: {
    color: '#FFFFFF',
  },
  sessionText: {
    textAlign: 'center',
    color: '#96A0B3',
    fontSize: 12,
    marginTop: 16,
    marginBottom: 6,
  },
  resendRow: {
    flexDirection: 'row',
    justifyContent: 'center',
  },
  bottomZone: {
    flex: 1,
    justifyContent: 'flex-end',
  },
});
