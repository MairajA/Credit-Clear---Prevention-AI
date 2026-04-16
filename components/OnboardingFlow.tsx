import React, { useRef, useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Text,
  Dimensions,
  NativeScrollEvent,
  NativeSyntheticEvent,
  Image,
} from 'react-native';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';

const { width } = Dimensions.get('window');

const ONBOARDING_SCREENS = [
  {
    id: 1,
    title: 'Watch your score climb,\nautomatically.',
    description:
      "Credit Clear's AI disputes errors, builds your history, and optimizes your profile.",
    illustration: require('@/assets/images/Group 4.png'),
  },
  {
    id: 2,
    title: 'Never miss a payment again.',
    description:
      "Credit Clear's AI disputes errors, builds your history, and optimizes your profile.",
    illustration: require('@/assets/images/Group 6.png'),
  },
  {
    id: 3,
    title: 'Your credit, fixed in 90 days.',
    description:
      'A personalized month-by-month roadmap built from your actual credit report. Disputes, debt strategy, and credit building.',
    illustration: require('@/assets/images/bro1.png'),
  },
];

export default function OnboardingFlow() {
  const router = useRouter();
  const scrollViewRef = useRef<ScrollView>(null);
  const [currentIndex, setCurrentIndex] = useState(0);

  const handleScroll = (event: NativeSyntheticEvent<NativeScrollEvent>) => {
    const contentOffsetX = event.nativeEvent.contentOffset.x;
    const index = Math.round(contentOffsetX / width);
    setCurrentIndex(index);
  };

  const handleNext = () => {
    if (currentIndex < ONBOARDING_SCREENS.length - 1) {
      scrollViewRef.current?.scrollTo({
        x: (currentIndex + 1) * width,
        animated: true,
      });
    } else {
      router.replace('/login');
    }
  };

  const handleSkip = () => {
    router.replace('/login');
  };

  return (
    <LinearGradient
      colors={['#FFFFFF', '#ECCDF2']}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.container}>
      <TouchableOpacity
        style={styles.skipButton}
        onPress={handleSkip}>
        <Text style={styles.skipButtonText}>Skip</Text>
      </TouchableOpacity>

      <ScrollView
        ref={scrollViewRef}
        horizontal
        pagingEnabled
        scrollEventThrottle={16}
        onScroll={handleScroll}
        showsHorizontalScrollIndicator={false}
        scrollEnabled={true}>
        {ONBOARDING_SCREENS.map((screen) => (
          <View key={screen.id} style={styles.slide}>
            {/* Illustration */}
            <View style={styles.illustrationContainer}>
              <Image
                source={screen.illustration}
                style={styles.illustration}
                resizeMode="contain"
              />
            </View>

            {/* Content */}
            <View style={styles.content}>
              <Text style={styles.title}>{screen.title}</Text>
              <Text style={styles.description}>{screen.description}</Text>
            </View>
          </View>
        ))}
      </ScrollView>

      {/* Indicators */}
      <View style={styles.indicatorsContainer}>
        {ONBOARDING_SCREENS.map((_, index) => (
          <View
            key={index}
            style={[
              styles.indicator,
              currentIndex === index && styles.indicatorActive,
            ]}
          />
        ))}
      </View>

      {/* Next Button */}
      <TouchableOpacity
        style={styles.nextButton}
        onPress={handleNext}>
        <Text style={styles.nextButtonText}>
          {currentIndex === ONBOARDING_SCREENS.length - 1 ? 'Get Started' : 'Next'}
        </Text>
      </TouchableOpacity>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  skipButton: {
    position: 'absolute',
    top: 50,
    right: 20,
    zIndex: 10,
  },
  skipButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F1F3D',
  },
  slide: {
    width: width,
    flex: 1,
    paddingHorizontal: 20,
    justifyContent: 'space-between',
    paddingTop: 60,
    paddingBottom: 120,
  },
  illustrationContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 30,
  },
  illustration: {
    width: '100%',
    height: 300,
  },
  content: {
    paddingHorizontal: 10,
  },
  title: {
    fontSize: 28,
    fontWeight: '800',
    color: '#1F1F3D',
    marginBottom: 12,
    lineHeight: 36,
  },
  description: {
    fontSize: 14,
    fontWeight: '500',
    color: '#999999',
    lineHeight: 20,
  },
  indicatorsContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 8,
    marginBottom: 20,
    marginTop: -30,
  },
  indicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#E0D4F7',
  },
  indicatorActive: {
    width: 24,
    backgroundColor: '#662F89',
  },
  nextButton: {
    marginHorizontal: 20,
    marginBottom: 40,
    backgroundColor: '#662F89',
    paddingVertical: 14,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  nextButtonText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#FFFFFF',
  },
});
