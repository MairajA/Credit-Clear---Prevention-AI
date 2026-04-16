import { StyleSheet } from 'react-native';

export const authStyles = StyleSheet.create({
  title: {
    fontSize: 34,
    fontWeight: '800',
    color: '#1F1F3D',
    textAlign: 'center',
    marginTop: 8,
    marginBottom: 28,
  },
  field: {
    height: 48,
    borderRadius: 10,
    backgroundColor: 'rgba(229, 208, 240, 0.55)',
    paddingHorizontal: 14,
    marginBottom: 12,
    justifyContent: 'center',
  },
  fieldInput: {
    fontSize: 14,
    color: '#1F1F3D',
    height: 48,
  },
  fieldMutedText: {
    color: '#8A8A99',
    fontSize: 13,
  },
  rowBetween: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  mutedText: {
    color: '#8A8A99',
    fontSize: 12,
  },
  linkText: {
    color: '#5C2D90',
    fontWeight: '700',
    fontSize: 12,
  },
  bottomButton: {
    height: 52,
    borderRadius: 10,
    backgroundColor: '#662F89',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  bottomButtonText: {
    color: '#FFFFFF',
    fontWeight: '700',
    fontSize: 18,
  },
});
