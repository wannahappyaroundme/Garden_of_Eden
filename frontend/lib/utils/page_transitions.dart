/// Custom page transitions for smooth navigation
library;

import 'package:flutter/material.dart';
import '../screens/profile_screen.dart';
import '../screens/settings_screen.dart';

enum SlideDirection {
  fromRight,
  fromLeft,
  fromBottom,
  fromTop,
}

/// Slide page route with custom direction
class SlidePageRoute<T> extends PageRouteBuilder<T> {
  final Widget page;
  final SlideDirection direction;
  final Duration duration;

  SlidePageRoute({
    required this.page,
    this.direction = SlideDirection.fromRight,
    this.duration = const Duration(milliseconds: 300),
  }) : super(
          pageBuilder: (context, animation, secondaryAnimation) => page,
          transitionDuration: duration,
          reverseTransitionDuration: duration,
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            Offset begin;
            switch (direction) {
              case SlideDirection.fromRight:
                begin = const Offset(1.0, 0.0);
                break;
              case SlideDirection.fromLeft:
                begin = const Offset(-1.0, 0.0);
                break;
              case SlideDirection.fromBottom:
                begin = const Offset(0.0, 1.0);
                break;
              case SlideDirection.fromTop:
                begin = const Offset(0.0, -1.0);
                break;
            }

            const end = Offset.zero;
            final tween = Tween(begin: begin, end: end);
            final offsetAnimation = animation.drive(
              tween.chain(CurveTween(curve: Curves.easeInOut)),
            );

            return SlideTransition(
              position: offsetAnimation,
              child: child,
            );
          },
        );
}

/// Fade page route
class FadePageRoute<T> extends PageRouteBuilder<T> {
  final Widget page;
  final Duration duration;

  FadePageRoute({
    required this.page,
    this.duration = const Duration(milliseconds: 300),
  }) : super(
          pageBuilder: (context, animation, secondaryAnimation) => page,
          transitionDuration: duration,
          reverseTransitionDuration: duration,
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            return FadeTransition(
              opacity: animation,
              child: child,
            );
          },
        );
}

/// Scale and fade page route
class ScaleFadePageRoute<T> extends PageRouteBuilder<T> {
  final Widget page;
  final Duration duration;

  ScaleFadePageRoute({
    required this.page,
    this.duration = const Duration(milliseconds: 300),
  }) : super(
          pageBuilder: (context, animation, secondaryAnimation) => page,
          transitionDuration: duration,
          reverseTransitionDuration: duration,
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            const begin = 0.9;
            const end = 1.0;
            final tween = Tween(begin: begin, end: end);
            final scaleAnimation = animation.drive(
              tween.chain(CurveTween(curve: Curves.easeInOut)),
            );

            return FadeTransition(
              opacity: animation,
              child: ScaleTransition(
                scale: scaleAnimation,
                child: child,
              ),
            );
          },
        );
}

/// Navigation helpers with custom transitions
class AppNavigation {
  /// Navigate to Profile screen with slide from bottom
  static Future<T?> toProfile<T>(BuildContext context, String userId) {
    return Navigator.push<T>(
      context,
      SlidePageRoute(
        page: _buildProfileScreen(userId),
        direction: SlideDirection.fromBottom,
      ),
    );
  }

  /// Navigate to Settings screen with slide from right
  static Future<T?> toSettings<T>(BuildContext context, String userId) {
    return Navigator.push<T>(
      context,
      SlidePageRoute(
        page: _buildSettingsScreen(userId),
        direction: SlideDirection.fromRight,
      ),
    );
  }

  /// Navigate with fade
  static Future<T?> fadeTo<T>(BuildContext context, Widget page) {
    return Navigator.push<T>(
      context,
      FadePageRoute(page: page),
    );
  }

  /// Navigate with scale and fade
  static Future<T?> scaleFadeTo<T>(BuildContext context, Widget page) {
    return Navigator.push<T>(
      context,
      ScaleFadePageRoute(page: page),
    );
  }

  // Private helpers
  static Widget _buildProfileScreen(String userId) {
    return ProfileScreen(userId: userId);
  }

  static Widget _buildSettingsScreen(String userId) {
    return SettingsScreen(userId: userId);
  }
}
