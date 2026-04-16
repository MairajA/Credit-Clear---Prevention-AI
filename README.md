# Credit Prevention AI Frontend

React Native + Expo mobile app for credit management and fraud prevention workflows.

## Tech Stack

- Expo SDK 54
- React Native 0.81
- TypeScript
- Expo Router

## Prerequisites

Install the following before running the app:

- Node.js 18 LTS or 20 LTS
- npm (comes with Node.js)
- Expo Go app on your phone (Android/iOS), or Android Studio / Xcode simulator

Check versions:

```bash
node -v
npm -v
```

## Setup

1. Clone the repository:

```bash
git clone https://github.com/ItsNabeelHussain/credit_clear_frontend.git
cd credit_clear_frontend
```

2. Install dependencies:

```bash
npm install
```

## Run the App

Start Expo dev server:

```bash
npm run start
```

Then choose one of the following:

- Press `a` for Android emulator
- Press `i` for iOS simulator (macOS only)
- Press `w` for web
- Scan the QR code in terminal using Expo Go on your phone

You can also run target-specific commands directly:

```bash
npm run android
npm run ios
npm run web
```

## Lint

```bash
npm run lint
```

## Project Structure

- `app/`: Expo Router screens and navigation routes
- `components/`: Shared UI and screen components
- `constants/`: Theme and constant values
- `hooks/`: Reusable hooks

## Troubleshooting

- If Metro cache causes issues:

```bash
npx expo start -c
```

- If dependency install fails, remove lockfile and reinstall:

PowerShell:

```powershell
Remove-Item -Recurse -Force node_modules
Remove-Item -Force package-lock.json
npm install
```

macOS/Linux:

```bash
rm -rf node_modules package-lock.json
npm install
```

## Notes

- This project is configured for cross-platform use (Android, iOS, and web).
- For iOS simulator support, run on macOS with Xcode installed.
