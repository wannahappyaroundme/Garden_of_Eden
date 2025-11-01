/// User Profile Provider using Riverpod
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/chat_models.dart';
import '../services/api_service.dart';
import 'service_providers.dart';

/// Profile State Notifier
class ProfileNotifier extends StateNotifier<AsyncValue<UserProfile?>> {
  final ApiService _apiService;
  String? _currentUserId;

  ProfileNotifier(this._apiService) : super(const AsyncValue.data(null));

  /// Load profile for user
  Future<void> loadProfile(String userId) async {
    _currentUserId = userId;
    state = const AsyncValue.loading();

    try {
      final profile = await _apiService.getProfile(userId);
      state = AsyncValue.data(profile);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }

  /// Update profile
  Future<void> updateProfile({
    String? oneThing,
    String? coreIdentity,
    String? coreMotivation,
  }) async {
    if (_currentUserId == null) return;

    state = const AsyncValue.loading();

    try {
      final profile = await _apiService.updateProfile(
        userId: _currentUserId!,
        oneThing: oneThing,
        coreIdentity: coreIdentity,
        coreMotivation: coreMotivation,
      );
      state = AsyncValue.data(profile);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }

  /// Refresh profile
  Future<void> refresh() async {
    if (_currentUserId != null) {
      await loadProfile(_currentUserId!);
    }
  }
}

/// Provider
final profileProvider =
    StateNotifierProvider<ProfileNotifier, AsyncValue<UserProfile?>>((ref) {
  final apiService = ref.watch(apiServiceProvider);
  return ProfileNotifier(apiService);
});
