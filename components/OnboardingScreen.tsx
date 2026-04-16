import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  ScrollView,
  TouchableOpacity,
  Image,
} from 'react-native';

const { width } = Dimensions.get('window');

interface OnboardingScreen {
  id: number;
  title: string;
  subtitle: string;
  icon: string;
}

const onboardingData: OnboardingScreen[] = [
  {
    id: 1,
    title: 'Watch your score climb,\nautomatically.',
    subtitle:
      "Credit Clear's AI displays errors, builds your history, and optimizes your profile.",
    icon: 'climb',
  },
  {
    id: 2,
    title: 'Never miss a payment again.',
    subtitle: "Credit Clear's AI displays errors, builds your history, and optimizes your profile.",
    icon: 'payment',
  },
  {
    id: 3,
    title: 'Your credit, fixed in 90 days.',
    subtitle:
      'A personalized month-by-month roadmap built from your actual credit report. Disputes, debt strategy, and credit building.',
    icon: 'roadmap',
  },
  {
    id: 4,
    title: 'Your credit, fixed in 90 days.',
    subtitle:
      'A personalized month-by-month roadmap built from your actual credit report. Disputes, debt strategy, and credit building.',
    icon: 'calendar',
  },
];

export default function OnboardingScreen() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const scrollRef = useRef<ScrollView>(null);

  const handleNext = () => {
    if (currentIndex < onboardingData.length - 1) {
      const newIndex = currentIndex + 1;
      setCurrentIndex(newIndex);
      scrollRef.current?.scrollTo({
        x: newIndex * width,
        animated: true,
      });
    }
  };

  const handleSkip = () => {
    // Navigate to main app
    console.log('Skip onboarding');
  };

  const handleScroll = (event: any) => {
    const contentOffsetX = event.nativeEvent.contentOffset.x;
    const currentPageIndex = Math.round(contentOffsetX / width);
    setCurrentIndex(currentPageIndex);
  };

  const renderScreen = (screen: OnboardingScreen) => (
    <View key={screen.id} style={styles.screen}>
      <View style={styles.header}>
        <TouchableOpacity onPress={handleSkip}>
          <Text style={styles.skipText}>Skip</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.content}>
        {/* Placeholder for illustration */}
        <View style={styles.illustrationContainer}>
          <View
            style={[
              styles.illustration,
              { backgroundColor: `hsl(${Math.random() * 360}, 70%, 85%)` },
            ]}
          />
        </View>

        <Text style={styles.title}>{screen.title}</Text>
        <Text style={styles.subtitle}>{screen.subtitle}</Text>
      </View>

      <View style={styles.footer}>
        {/* Dots indicator */}
        <View style={styles.dotsContainer}>
          {onboardingData.map((_, index) => (
            <View
              key={index}
              style={[styles.dot, currentIndex === index && styles.activeDot]}
            />
          ))}
        </View>

        <TouchableOpacity style={styles.nextButton} onPress={handleNext}>
          <Text style={styles.nextButtonText}>
            {currentIndex === onboardingData.length - 1 ? 'Get Started' : 'Next'}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <ScrollView
      ref={scrollRef}
      horizontal
      pagingEnabled
      scrollEventThrottle={16}
      onScroll={handleScroll}
      scrollEnabled={false}
      style={styles.container}
    >
      {onboardingData.map((screen) => renderScreen(screen))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9F3FF',
  },
  screen: {
    width,
    paddingTop: 16,
    paddingHorizontal: 24,
    paddingBottom: 40,
    justifyContent: 'space-between',
    backgroundColor: '#F9F3FF',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
  },
  skipText: {
    fontSize: 14,
    color: '#7C3AED',
    fontWeight: '600',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  illustrationContainer: {
    height: 280,
    width: '100%',
    marginBottom: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  illustration: {
    width: 200,
    height: 240,
    borderRadius: 16,
    opacity: 0.7,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#1F1F3D',
    textAlign: 'center',
    marginBottom: 16,
    lineHeight: 32,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    lineHeight: 20,
  },
  footer: {
    alignItems: 'center',
    gap: 24,
  },
  dotsContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 8,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#E0D4F7',
  },
  activeDot: {
    backgroundColor: '#7C3AED',
    width: 24,
  },
  nextButton: {
    width: '100%',
    paddingVertical: 16,
    backgroundColor: '#7C3AED',
    borderRadius: 12,
    alignItems: 'center',
  },
  nextButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFF',
  },
});
