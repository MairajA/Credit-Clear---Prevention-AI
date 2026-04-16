import { Link, Stack, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useState } from 'react';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import AuthLayout from '@/components/auth/AuthLayout';
import { authStyles } from '@/components/auth/authStyles';

export default function SignUpScreen() {
  const router = useRouter();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [acceptedTerms, setAcceptedTerms] = useState(false);

  return (
    <>
      <Stack.Screen options={{ headerShown: false }} />
      <AuthLayout>
        <Text style={authStyles.title}>Signup</Text>

        <View style={authStyles.field}>
          <TextInput
            value={fullName}
            onChangeText={setFullName}
            placeholder="Full name"
            placeholderTextColor="#8A8A99"
            style={authStyles.fieldInput}
          />
        </View>

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

        <View style={[authStyles.field, styles.passwordField]}>
          <TextInput
            value={confirmPassword}
            onChangeText={setConfirmPassword}
            placeholder="Confirm Password"
            placeholderTextColor="#8A8A99"
            secureTextEntry={!showConfirmPassword}
            autoCapitalize="none"
            style={[authStyles.fieldInput, styles.passwordInput]}
          />
          <Pressable onPress={() => setShowConfirmPassword((prev) => !prev)}>
            <Ionicons name={showConfirmPassword ? 'eye-off-outline' : 'eye-outline'} size={18} color="#8A8A99" />
          </Pressable>
        </View>

        <Pressable style={styles.termsRow} onPress={() => setAcceptedTerms((prev) => !prev)}>
          <View style={[styles.checkbox, acceptedTerms && styles.checkboxChecked]} />
          <Text style={styles.termsText}>
            I've read and agree to the <Text style={authStyles.linkText}>terms</Text> if{' '}
            <Text style={authStyles.linkText}>privacy policy</Text>
          </Text>
        </Pressable>

        <View style={styles.bottomZone}>
          <Link href="/login" asChild>
            <Pressable>
              <Text style={styles.hasAccountText}>Already have an account? Login</Text>
            </Pressable>
          </Link>
          <Pressable style={authStyles.bottomButton} onPress={() => router.push('/phone-number')}>
            <Text style={authStyles.bottomButtonText}>Next</Text>
          </Pressable>
        </View>
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
  termsRow: {
    marginTop: 6,
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 8,
  },
  checkbox: {
    width: 16,
    height: 16,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: '#A7A7B5',
    marginTop: 2,
  },
  checkboxChecked: {
    backgroundColor: '#662F89',
    borderColor: '#662F89',
  },
  termsText: {
    flex: 1,
    color: '#8A8A99',
    fontSize: 11,
    lineHeight: 16,
  },
  bottomZone: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  hasAccountText: {
    fontSize: 12,
    color: '#8A8A99',
    textAlign: 'center',
    marginBottom: 10,
  },
});
