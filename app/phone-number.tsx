import { Stack, useRouter } from 'expo-router';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { useState } from 'react';

import AuthLayout from '@/components/auth/AuthLayout';
import { authStyles } from '@/components/auth/authStyles';

export default function PhoneNumberScreen() {
  const router = useRouter();
  const [phone, setPhone] = useState('');

  return (
    <>
      <Stack.Screen options={{ headerShown: false }} />
      <AuthLayout compactTop>
        <Text style={authStyles.title}>Signup</Text>

        <Text style={styles.infoText}>
          Please enter <Text style={styles.bold}>your phone number,</Text>{'\n'}
          so we can verify you.
        </Text>

        <View style={styles.phoneRow}>
          <Text style={styles.flag}>US</Text>
          <TextInput
            value={phone}
            onChangeText={setPhone}
            placeholder="Enter Your Number"
            placeholderTextColor="#8A8A99"
            keyboardType="phone-pad"
            style={styles.phoneInput}
          />
          <Text style={styles.chevron}>v</Text>
        </View>

        <View style={styles.bottomZone}>
          <Pressable style={authStyles.bottomButton} onPress={() => router.push('/phone-verification')}>
            <Text style={authStyles.bottomButtonText}>Next</Text>
          </Pressable>
        </View>
      </AuthLayout>
    </>
  );
}

const styles = StyleSheet.create({
  infoText: {
    marginTop: 20,
    textAlign: 'center',
    color: '#575772',
    lineHeight: 22,
    marginBottom: 18,
    fontSize: 16,
  },
  bold: {
    color: '#1F1F3D',
    fontWeight: '700',
  },
  phoneRow: {
    height: 48,
    borderRadius: 10,
    backgroundColor: 'rgba(229, 208, 240, 0.55)',
    alignItems: 'center',
    flexDirection: 'row',
    paddingHorizontal: 14,
    gap: 10,
  },
  flag: {
    width: 26,
    color: '#1F1F3D',
    fontWeight: '700',
    fontSize: 12,
  },
  phoneInput: {
    flex: 1,
    height: 48,
    color: '#1F1F3D',
    fontSize: 14,
  },
  chevron: {
    color: '#8A8A99',
    fontSize: 11,
    fontWeight: '700',
  },
  bottomZone: {
    flex: 1,
    justifyContent: 'flex-end',
  },
});
