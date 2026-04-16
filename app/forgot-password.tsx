import { Stack, useRouter } from 'expo-router';
import { useState } from 'react';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import AuthLayout from '@/components/auth/AuthLayout';
import { authStyles } from '@/components/auth/authStyles';

export default function ForgotPasswordScreen() {
  const router = useRouter();
  const [identity, setIdentity] = useState('');

  return (
    <>
      <Stack.Screen options={{ headerShown: false }} />
      <AuthLayout>
        <Text style={authStyles.title}>Forgot Password</Text>
        <Text style={styles.infoText}>
          Please enter your <Text style={styles.bold}>email address or</Text>{'\n'}
          <Text style={styles.bold}>phone number</Text> to reset your password
        </Text>

        <View style={authStyles.field}>
          <TextInput
            value={identity}
            onChangeText={setIdentity}
            placeholder="User.name. here@mail.com"
            placeholderTextColor="#7B4F96"
            autoCapitalize="none"
            style={[authStyles.fieldInput, styles.input]}
          />
        </View>

        <View style={styles.bottomZone}>
          <Pressable style={authStyles.bottomButton} onPress={() => router.push('/forgot-password-verify')}>
            <Text style={authStyles.bottomButtonText}>Continue</Text>
          </Pressable>
        </View>
      </AuthLayout>
    </>
  );
}

const styles = StyleSheet.create({
  infoText: {
    marginTop: 8,
    textAlign: 'center',
    color: '#575772',
    lineHeight: 22,
    marginBottom: 20,
    fontSize: 15,
  },
  bold: {
    color: '#1F1F3D',
    fontWeight: '700',
  },
  input: {
    color: '#7B4F96',
    fontWeight: '600',
  },
  bottomZone: {
    flex: 1,
    justifyContent: 'flex-end',
  },
});
