/// App Theme - Futuristic Monochrome Design
library;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../utils/constants.dart';

class AppTheme {
  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,

      // Color Scheme
      colorScheme: ColorScheme.dark(
        primary: Color(UIConstants.electricCyan),
        onPrimary: Color(UIConstants.pureBlack),
        secondary: Color(UIConstants.offWhite),
        onSecondary: Color(UIConstants.deepBlack),
        surface: Color(UIConstants.deepBlack),
        onSurface: Color(UIConstants.offWhite),
        error: Color(UIConstants.stateListening),
      ),

      // Scaffold
      scaffoldBackgroundColor: Color(UIConstants.pureBlack),

      // AppBar
      appBarTheme: AppBarTheme(
        backgroundColor: Colors.transparent,
        elevation: 0,
        systemOverlayStyle: SystemUiOverlayStyle.light,
        iconTheme: IconThemeData(color: Color(UIConstants.offWhite)),
        titleTextStyle: TextStyle(
          color: Color(UIConstants.offWhite),
          fontSize: UIConstants.fontTitle,
          fontWeight: FontWeight.w600,
        ),
      ),

      // Text Theme
      textTheme: TextTheme(
        displayLarge: TextStyle(
          fontSize: UIConstants.fontDisplay,
          fontWeight: FontWeight.bold,
          color: Color(UIConstants.offWhite),
          letterSpacing: -0.5,
        ),
        displayMedium: TextStyle(
          fontSize: UIConstants.fontHeadline,
          fontWeight: FontWeight.w600,
          color: Color(UIConstants.offWhite),
          letterSpacing: -0.3,
        ),
        titleLarge: TextStyle(
          fontSize: UIConstants.fontTitle,
          fontWeight: FontWeight.w600,
          color: Color(UIConstants.offWhite),
        ),
        bodyLarge: TextStyle(
          fontSize: UIConstants.fontBodyLarge,
          color: Color(UIConstants.offWhite),
        ),
        bodyMedium: TextStyle(
          fontSize: UIConstants.fontBody,
          color: Color(UIConstants.offWhite),
        ),
        labelSmall: TextStyle(
          fontSize: UIConstants.fontLabel,
          fontWeight: FontWeight.w500,
          color: Color(UIConstants.lightGrey),
          letterSpacing: 0.5,
        ),
      ),

      // Icon Theme
      iconTheme: IconThemeData(
        color: Color(UIConstants.offWhite),
        size: 24,
      ),

      // Button Themes
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: Color(UIConstants.electricCyan),
          foregroundColor: Color(UIConstants.pureBlack),
          elevation: 0,
          padding: EdgeInsets.symmetric(
            horizontal: UIConstants.spacingLG,
            vertical: UIConstants.spacingMD,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),

      // Card Theme
      cardTheme: CardThemeData(
        color: Color(UIConstants.deepBlack),
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: BorderSide(
            color: Color(UIConstants.midGrey).withValues(alpha: 0.2),
            width: 1,
          ),
        ),
      ),
    );
  }

  /// Get color for AppMode
  static Color getColorForMode(AppMode mode) {
    switch (mode) {
      case AppMode.idle:
        return Color(UIConstants.offWhite).withValues(alpha: 0.3);
      case AppMode.listening:
        return Color(UIConstants.stateListening).withValues(alpha: 0.8);
      case AppMode.processing:
        return Color(UIConstants.stateProcessing).withValues(alpha: 0.8);
      case AppMode.responding:
        return Color(UIConstants.stateResponding).withValues(alpha: 0.8);
    }
  }

  /// Get icon for AppMode
  static IconData getIconForMode(AppMode mode) {
    switch (mode) {
      case AppMode.idle:
        return Icons.mic_outlined;
      case AppMode.listening:
        return Icons.mic;
      case AppMode.processing:
        return Icons.hourglass_empty;
      case AppMode.responding:
        return Icons.check_circle_outline;
    }
  }
}
