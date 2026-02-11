/// Initialization and license validation for the Intyx Dynamic Widget SDK.
library;

import 'dart:convert';

import 'package:http/http.dart' as http;

class IntyxDynamicWidget {
  IntyxDynamicWidget._();

  static String? _apiKey;
  static String? _plan;
  static int _widgetLimit = 0;
  static bool _initialized = false;
  static String _baseUrl = 'https://api.intyx.dev';

  /// Whether the SDK has been initialized and the license is valid.
  static bool get isInitialized => _initialized;

  /// Current plan name (starter, pro, enterprise).
  static String? get plan => _plan;

  /// Max widget types allowed by the current plan (-1 = unlimited).
  static int get widgetLimit => _widgetLimit;

  /// The API key currently in use.
  static String? get apiKey => _apiKey;

  /// Initialize the SDK with the purchased API key.
  ///
  /// ```dart
  /// await IntyxDynamicWidget.init(apiKey: 'intyx_pro_abc123...');
  /// ```
  static Future<void> init({
    required String apiKey,
    String? baseUrl,
  }) async {
    _apiKey = apiKey;
    if (baseUrl != null) _baseUrl = baseUrl;

    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/api/licenses/validate'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'api_key': apiKey}),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body) as Map<String, dynamic>;
        if (data['valid'] == true) {
          _plan = data['plan'] as String?;
          _widgetLimit = data['widget_limit'] as int? ?? 0;
          _initialized = true;
          return;
        }
      }

      // Validation failed but don't crash — allow offline/demo usage
      _initialized = true;
      _plan = 'offline';
      _widgetLimit = 3;
    } catch (_) {
      // Network error — still allow the app to run with limited features
      _initialized = true;
      _plan = 'offline';
      _widgetLimit = 3;
    }
  }

  /// Reset the SDK state (useful for testing or logout).
  static void reset() {
    _apiKey = null;
    _plan = null;
    _widgetLimit = 0;
    _initialized = false;
  }
}
