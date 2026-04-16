import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Switch } from 'react-native';

export default function SettingsScreen() {
  const [notifEnabled, setNotifEnabled] = React.useState(true);
  const [emailEnabled, setEmailEnabled] = React.useState(true);

  const settingsGroups = [
    {
      title: 'Notifications',
      items: [
        {
          id: 1,
          label: 'Push Notifications',
          value: notifEnabled,
          onToggle: () => setNotifEnabled(!notifEnabled),
        },
        {
          id: 2,
          label: 'Email Alerts',
          value: emailEnabled,
          onToggle: () => setEmailEnabled(!emailEnabled),
        },
      ],
    },
    {
      title: 'Account',
      items: [
        { id: 3, label: 'Edit Profile', icon: '👤', action: true },
        { id: 4, label: 'Change Password', icon: '🔐', action: true },
        { id: 5, label: 'Linked Accounts', icon: '🔗', action: true },
      ],
    },
    {
      title: 'Support',
      items: [
        { id: 6, label: 'Help Center', icon: '❓', action: true },
        { id: 7, label: 'Contact Support', icon: '📧', action: true },
        { id: 8, label: 'Give Feedback', icon: '⭐', action: true },
      ],
    },
    {
      title: 'Legal',
      items: [
        { id: 9, label: 'Privacy Policy', icon: '📋', action: true },
        { id: 10, label: 'Terms of Service', icon: '⚖️', action: true },
      ],
    },
  ];

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Settings</Text>
      </View>

      {/* Profile Section */}
      <View style={styles.profileSection}>
        <View style={styles.profileAvatar}>
          <Text style={styles.avatarText}>👤</Text>
        </View>
        <View style={styles.profileInfo}>
          <Text style={styles.profileName}>John Doe</Text>
          <Text style={styles.profileEmail}>john@example.com</Text>
        </View>
      </View>

      {/* Settings Groups */}
      {settingsGroups.map((group) => (
        <View key={group.title} style={styles.settingGroup}>
          <Text style={styles.groupTitle}>{group.title}</Text>
          {group.items.map((item, index) => (
            <View key={item.id}>
              <View style={styles.settingItem}>
                {'value' in item ? (
                  <>
                    <Text style={styles.settingLabel}>{item.label}</Text>
                    <Switch
                      value={item.value}
                      onValueChange={() => {
                        if ('onToggle' in item) {
                          item.onToggle();
                        }
                      }}
                      trackColor={{ false: '#E0D4F7', true: '#7C3AED' }}
                      thumbColor="#FFF"
                    />
                  </>
                ) : (
                  <>
                    <View style={styles.settingLabelRow}>
                      <Text style={styles.settingIcon}>{'icon' in item ? item.icon : ''}</Text>
                      <Text style={styles.settingLabel}>{item.label}</Text>
                    </View>
                    <Text style={styles.arrowIcon}>›</Text>
                  </>
                )}
              </View>
              {index < group.items.length - 1 && <View style={styles.divider} />}
            </View>
          ))}
        </View>
      ))}

      {/* Logout Button */}
      <TouchableOpacity style={styles.logoutButton}>
        <Text style={styles.logoutText}>Log Out</Text>
      </TouchableOpacity>

      {/* Version */}
      <Text style={styles.version}>App Version 1.0.0</Text>

      <View style={{ height: 30 }} />
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
  },
  profileSection: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
    marginBottom: 24,
  },
  profileAvatar: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#E0D4F7',
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    fontSize: 32,
  },
  profileInfo: {
    flex: 1,
  },
  profileName: {
    fontSize: 16,
    fontWeight: '700',
    color: '#1F1F3D',
  },
  profileEmail: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
  },
  settingGroup: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    marginBottom: 16,
    overflow: 'hidden',
  },
  groupTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: '#7C3AED',
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 8,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  settingLabelRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  settingIcon: {
    fontSize: 20,
  },
  settingLabel: {
    fontSize: 15,
    fontWeight: '500',
    color: '#1F1F3D',
  },
  arrowIcon: {
    fontSize: 24,
    color: '#999',
  },
  divider: {
    height: 1,
    backgroundColor: '#E0D4F7',
    marginHorizontal: 16,
  },
  logoutButton: {
    backgroundColor: '#FF6B6B',
    borderRadius: 12,
    padding: 14,
    alignItems: 'center',
    marginTop: 12,
  },
  logoutText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFF',
  },
  version: {
    fontSize: 12,
    color: '#999',
    textAlign: 'center',
    marginTop: 16,
  },
});
