import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';

export default function CreditAnalysisScreen() {
  const [selectedPhase, setSelectedPhase] = useState(0);

  const phases = [
    {
      id: 1,
      period: 'Days 1-30',
      title: 'Fix Errors',
      tasks: [
        'Dispute inaccurate accounts',
        'Remove fraudulent inquiries',
        'Get payment history errors fixed',
      ],
      progress: 100,
      icon: '🔍',
    },
    {
      id: 2,
      period: 'Days 31-60',
      title: 'Build History',
      tasks: [
        'Secure credit cards',
        'Become authorized user',
        'Keep low utilization',
      ],
      progress: 45,
      icon: '📈',
    },
    {
      id: 3,
      period: 'Days 61-90',
      title: 'Optimize',
      tasks: [
        'Optimize credit mix',
        'Request increases',
        'Final review',
      ],
      progress: 0,
      icon: '✨',
    },
  ];

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>90-Day Credit Roadmap</Text>
        <Text style={styles.subtitle}>Your personalized credit improvement plan</Text>
      </View>

      {/* Roadmap Timeline */}
      <View style={styles.timeline}>
        {phases.map((phase, index) => (
          <TouchableOpacity
            key={phase.id}
            style={[
              styles.phaseButton,
              selectedPhase === index && styles.activePhaseButton,
            ]}
            onPress={() => setSelectedPhase(index)}
          >
            <View
              style={[
                styles.phaseCircle,
                selectedPhase === index && styles.activePhaseCircle,
              ]}
            >
              <Text style={styles.phaseIcon}>{phase.icon}</Text>
            </View>
            <Text style={styles.phasePeriod}>{phase.period}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Selected Phase Details */}
      <View style={styles.phaseDetails}>
        <View style={styles.phaseHeader}>
          <Text style={styles.phaseTitle}>{phases[selectedPhase].title}</Text>
          <View style={styles.progressBadge}>
            <Text style={styles.progressText}>{phases[selectedPhase].progress}%</Text>
          </View>
        </View>

        {/* Progress Bar */}
        <View style={styles.progressBar}>
          <View
            style={[
              styles.progressFill,
              { width: `${phases[selectedPhase].progress}%` },
            ]}
          />
        </View>

        {/* Tasks */}
        <View style={styles.tasksContainer}>
          {phases[selectedPhase].tasks.map((task, index) => (
            <View key={index} style={styles.taskItem}>
              <View style={styles.taskCheckbox}>
                <Text style={styles.taskCheckmark}>
                  {phases[selectedPhase].progress > 30 * index ? '✓' : ' '}
                </Text>
              </View>
              <Text style={styles.taskText}>{task}</Text>
            </View>
          ))}
        </View>
      </View>

      {/* Key Metrics */}
      <View style={styles.metricsSection}>
        <Text style={styles.metricsTitle}>Key Metrics</Text>
        <View style={styles.metricsGrid}>
          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>720</Text>
            <Text style={styles.metricLabel}>Current Score</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>+40</Text>
            <Text style={styles.metricLabel}>Projected Gain</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>28%</Text>
            <Text style={styles.metricLabel}>Utilization</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>0</Text>
            <Text style={styles.metricLabel}>Late Payments</Text>
          </View>
        </View>
      </View>

      <View style={{ height: 20 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9F3FF',
    paddingHorizontal: 16,
    paddingTop: 12,
  },
  header: {
    marginBottom: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#1F1F3D',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: '#999',
  },
  timeline: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 8,
    marginBottom: 24,
  },
  phaseButton: {
    flex: 1,
    alignItems: 'center',
  },
  activePhaseButton: {},
  phaseCircle: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#E0D4F7',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  activePhaseCircle: {
    backgroundColor: '#7C3AED',
  },
  phaseIcon: {
    fontSize: 28,
  },
  phasePeriod: {
    fontSize: 11,
    fontWeight: '600',
    color: '#666',
    textAlign: 'center',
  },
  phaseDetails: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
  },
  phaseHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  phaseTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#1F1F3D',
  },
  progressBadge: {
    backgroundColor: '#E0D4F7',
    borderRadius: 20,
    paddingHorizontal: 12,
    paddingVertical: 4,
  },
  progressText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#7C3AED',
  },
  progressBar: {
    height: 6,
    backgroundColor: '#E0D4F7',
    borderRadius: 3,
    overflow: 'hidden',
    marginBottom: 16,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#7C3AED',
  },
  tasksContainer: {
    gap: 12,
  },
  taskItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  taskCheckbox: {
    width: 24,
    height: 24,
    borderRadius: 6,
    backgroundColor: '#E0D4F7',
    justifyContent: 'center',
    alignItems: 'center',
  },
  taskCheckmark: {
    color: '#7C3AED',
    fontWeight: '700',
    fontSize: 14,
  },
  taskText: {
    fontSize: 14,
    color: '#1F1F3D',
    fontWeight: '500',
  },
  metricsSection: {
    marginBottom: 20,
  },
  metricsTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1F1F3D',
    marginBottom: 12,
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  metricCard: {
    width: '48%',
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  metricValue: {
    fontSize: 24,
    fontWeight: '700',
    color: '#7C3AED',
    marginBottom: 4,
  },
  metricLabel: {
    fontSize: 12,
    color: '#999',
    textAlign: 'center',
  },
});
