// Project Eden V2 - Widget Tests
// This file is a placeholder for future widget tests

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:frontend/main.dart';

void main() {
  testWidgets('App launches successfully', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const ProviderScope(child: EdenApp()));

    // Pump a frame to render the app
    await tester.pump();

    // Verify that the app launches with MaterialApp
    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
