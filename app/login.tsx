import { Link, Stack, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useState } from 'react';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import AuthLayout from '@/components/auth/AuthLayout';
import { authStyles } from '@/components/auth/authStyles';

export default function LoginScreen() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  return (
    <>
      <Stack.Screen options={{ headerShown: false }} />
      <AuthLayout>
        <Text style={authStyles.title}>Login</Text>

        <View style={authStyles.field}>
          <TextInput
            value={email}
            onChangeText={setEmail}
            placeholder="Enter Email Address"
            placeholderTextColor="#8A8A99"
            keyboardType="email-address"
            autoCapitalize="none"
            style={authStyles.fieldInput}
          />
        </View>

        <View style={[authStyles.field, styles.passwordField]}>
          <TextInput
            value={password}
            onChangeText={setPassword}
            placeholder="Password"
            placeholderTextColor="#8A8A99"
            secureTextEntry={!showPassword}
            autoCapitalize="none"
            style={[authStyles.fieldInput, styles.passwordInput]}
          />
          <Pressable onPress={() => setShowPassword((prev) => !prev)}>
            <Ionicons name={showPassword ? 'eye-off-outline' : 'eye-outline'} size={18} color="#8A8A99" />
          </Pressable>
        </View>

        <Link href="/forgot-password" asChild>
          <Pressable style={styles.forgotWrap}>
            <Text style={styles.forgotText}>Forgot Password?</Text>
          </Pressable>
        </Link>

        <View style={styles.footerWrap}>
          <Text style={authStyles.mutedText}>Do not have account? </Text>
          <Link href="/signup" asChild>
            <Pressable>
              <Text style={[authStyles.linkText, styles.signupText]}>Sign Up</Text>
            </Pressable>
          </Link>
        </View>

        <Pressable style={authStyles.bottomButton} onPress={() => router.replace('/(tabs)')}>
          <Text style={authStyles.bottomButtonText}>Login</Text>
        </Pressable>
      </AuthLayout>
    </>
  );
}

const styles = StyleSheet.create({
  passwordField: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  passwordInput: {
    flex: 1,
  },
  forgotWrap: {
    alignSelf: 'flex-end',
    marginBottom: 18,
    marginTop: 4,
  },
  forgotText: {
    color: '#8A8A99',
    fontSize: 12,
    fontWeight: '500',
  },
  footerWrap: {
    flex: 1,
    justifyContent: 'flex-end',
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  signupText: {
    fontSize: 13,
  },
});
