import { Stack, useRouter } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useMemo, useState } from 'react';

import AuthLayout from '@/components/auth/AuthLayout';

const KEYS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '', '0', '<'];

export default function PhoneVerificationScreen() {
  const router = useRouter();
  const [code, setCode] = useState('');

  const masked = useMemo(() => {
    const chars = code.split('');
    while (chars.length < 4) chars.push('');
    return chars;
  }, [code]);

  const onKeyPress = (key: string) => {
    if (!key) return;
    if (key === '<') {
      setCode((prev) => prev.slice(0, -1));
      return;
    }
    if (code.length < 4) {
      const next = `${code}${key}`;
      setCode(next);
      if (next.length === 4) {
        router.replace('/welcome');
      }
    }
  };

  return (
    <>
      <Stack.Screen options={{ headerShown: false }} />
      <AuthLayout compactTop>
        <View style={styles.backRow}>
          <Pressable onPress={() => router.back()}>
            <Text style={styles.backText}>Back</Text>
          </Pressable>
        </View>

        <Text style={styles.title}>Verify Code</Text>

        <View style={styles.codeRow}>
          {masked.map((item, index) => (
            <View key={index} style={[styles.codeBox, item ? styles.codeBoxFilled : null]}>
              <Text style={[styles.codeText, item ? styles.codeTextFilled : null]}>{item || ' '}</Text>
            </View>
          ))}
        </View>

        <View style={styles.resendRow}>
          <Text style={styles.resendText}>Didn't receive a code? </Text>
          <Pressable>
            <Text style={styles.resendLink}>Resend Code</Text>
          </Pressable>
        </View>

        <View style={styles.keyboardWrap}>
          {KEYS.map((key, index) => (
            <Pressable key={`${key}-${index}`} onPress={() => onKeyPress(key)} style={styles.key}>
              <Text style={styles.keyText}>{key === '<' ? 'x' : key}</Text>
            </Pressable>
          ))}
        </View>
      </AuthLayout>
    </>
  );
}

const styles = StyleSheet.create({
  backRow: {
    marginTop: 2,
    marginBottom: 10,
  },
  backText: {
    color: '#1F1F3D',
    fontSize: 15,
  },
  title: {
    fontSize: 34,
    fontWeight: '800',
    color: '#1F1F3D',
    textAlign: 'center',
    marginBottom: 26,
  },
  codeRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 10,
    marginBottom: 16,
  },
  codeBox: {
    width: 52,
    height: 56,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#CAA9E2',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F0E9F8',
  },
  codeBoxFilled: {
    backgroundColor: '#662F89',
    borderColor: '#662F89',
  },
  codeText: {
    fontSize: 32,
    fontWeight: '700',
    color: '#1F1F3D',
  },
  codeTextFilled: {
    color: '#FFFFFF',
  },
  resendRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 20,
  },
  resendText: {
    color: '#6C6C80',
    fontSize: 12,
  },
  resendLink: {
    color: '#5C2D90',
    fontWeight: '700',
    fontSize: 12,
  },
  keyboardWrap: {
    marginTop: 'auto',
    marginBottom: 10,
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: 4,
  },
  key: {
    width: '31%',
    minWidth: 90,
    height: 48,
    borderRadius: 6,
    backgroundColor: '#ECECF0',
    alignItems: 'center',
    justifyContent: 'center',
  },
  keyText: {
    fontSize: 34,
    lineHeight: 36,
    color: '#1F1F3D',
  },
});
