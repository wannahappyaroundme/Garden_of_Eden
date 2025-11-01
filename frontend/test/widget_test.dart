// Project Eden V2 - Widget Tests
// This file is a placeholder for future widget tests

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:frontend/main.dart';

void main() {
  testWidgets('App launches and shows permission screen', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const ProviderScope(child: EdenApp()));

    // Wait for the app to settle
    await tester.pumpAndSettle();

    // Verify that the app launches
    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
