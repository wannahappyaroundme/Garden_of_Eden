import 'package:uuid/uuid.dart';

/// Generates unique user IDs for identification
///
/// Format: user_{timestamp}_{uuid}
/// Example: user_1699123456_a1b2c3d4-e5f6-7890-abcd-ef1234567890
class UserIdGenerator {
  static const _uuid = Uuid();

  /// Generate a new unique user ID
  ///
  /// This creates a globally unique identifier combining:
  /// - Current timestamp (for temporal ordering)
  /// - UUID v4 (for uniqueness guarantee)
  static String generate() {
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final uuid = _uuid.v4();
    return 'user_${timestamp}_$uuid';
  }

  /// Validate if a string is a valid user ID format
  static bool isValid(String userId) {
    // Check format: user_{timestamp}_{uuid}
    final pattern = RegExp(r'^user_\d+_[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$');
    return pattern.hasMatch(userId);
  }
}
