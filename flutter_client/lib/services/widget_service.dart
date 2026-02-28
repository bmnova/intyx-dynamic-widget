/// Service for communicating with the backend API.
library;

import 'dart:convert';

import 'package:http/http.dart' as http;

import '../core/intyx_init.dart';
import '../models/trigger_context.dart';
import '../models/widget_response.dart';
import 'widget_cache.dart';

class WidgetService {
  final String baseUrl;
  final http.Client _client;

  /// Optional offline cache. When provided, successful responses are stored
  /// locally and returned if a subsequent network request fails.
  final WidgetCache? cache;

  WidgetService({required this.baseUrl, http.Client? client, this.cache})
      : _client = client ?? http.Client();

  /// Returns headers for JSON POST requests, including Authorization when available.
  Map<String, String> get _postHeaders => {
        'Content-Type': 'application/json',
        if (IntyxDynamicWidget.apiKey != null)
          'Authorization': 'Bearer ${IntyxDynamicWidget.apiKey}',
      };

  /// Returns headers for GET requests, including Authorization when available.
  Map<String, String> get _getHeaders => {
        if (IntyxDynamicWidget.apiKey != null)
          'Authorization': 'Bearer ${IntyxDynamicWidget.apiKey}',
      };

  /// Fetch all widgets, optionally filtered by user.
  ///
  /// On network failure, returns the last cached response for this [userId]
  /// when a [cache] has been configured. Throws if there is no cache fallback.
  Future<List<WidgetEntry>> getWidgets({String? userId}) async {
    final cacheKey = 'getWidgets_${userId ?? 'all'}';
    try {
      final uri = Uri.parse('$baseUrl/api/widgets').replace(
        queryParameters: userId != null ? {'user_id': userId} : null,
      );
      final response = await _client.get(uri, headers: _getHeaders);
      _checkResponse(response);
      await cache?.save(cacheKey, response.body);
      return WidgetResponse.fromJson(
              json.decode(response.body) as Map<String, dynamic>)
          .widgets;
    } catch (_) {
      final cached = await cache?.load(cacheKey);
      if (cached != null) return cached;
      rethrow;
    }
  }

  /// Evaluate triggers and get matching widgets.
  ///
  /// On network failure, returns the last cached trigger evaluation when a
  /// [cache] has been configured. Throws if there is no cache fallback.
  ///
  /// When the license's MAU quota is exceeded the server returns
  /// `{"widgets": [], "fallback": true}`. In that case this method returns
  /// the last cached result so the user still sees content, or an empty list
  /// if no cache is available.
  Future<List<WidgetEntry>> evaluateTriggers(TriggerContext context) async {
    const cacheKey = 'evaluateTriggers';
    try {
      final uri = Uri.parse('$baseUrl/api/widgets/evaluate');
      final response = await _client.post(
        uri,
        headers: _postHeaders,
        body: json.encode(context.toJson()),
      );
      _checkResponse(response);
      final body = json.decode(response.body) as Map<String, dynamic>;
      // Quota exceeded — serve cached content instead of an empty screen
      if (body['fallback'] == true) {
        final cached = await cache?.load(cacheKey);
        return cached ?? [];
      }
      await cache?.save(cacheKey, response.body);
      return WidgetResponse.fromJson(body).widgets;
    } catch (_) {
      final cached = await cache?.load(cacheKey);
      if (cached != null) return cached;
      rethrow;
    }
  }

  /// Ask AI to suggest widgets for a context.
  Future<WidgetResponse> suggestWidgets(Map<String, dynamic> context) async {
    final uri = Uri.parse('$baseUrl/api/ai/suggest-widget');
    final response = await _client.post(
      uri,
      headers: _postHeaders,
      body: json.encode(context),
    );
    _checkResponse(response);

    final data = json.decode(response.body) as Map<String, dynamic>;
    return WidgetResponse.fromJson(data);
  }

  /// Dismiss a widget for a user.
  Future<void> dismissWidget(String widgetId, String userId) async {
    final uri = Uri.parse('$baseUrl/api/widgets/$widgetId/dismiss');
    final response = await _client.post(
      uri,
      headers: _postHeaders,
      body: json.encode({'user_id': userId}),
    );
    _checkResponse(response);
  }

  /// Record a widget interaction.
  Future<void> recordInteraction(
    String widgetId,
    String userId, {
    String action = 'tap',
  }) async {
    final uri = Uri.parse('$baseUrl/api/widgets/$widgetId/interact');
    final response = await _client.post(
      uri,
      headers: _postHeaders,
      body: json.encode({'user_id': userId, 'action': action}),
    );
    _checkResponse(response);
  }

  /// Record a user action for trigger evaluation.
  Future<void> recordUserAction(
    String userId,
    String action, {
    Map<String, dynamic>? metadata,
  }) async {
    final uri = Uri.parse('$baseUrl/api/widgets/user/action');
    final response = await _client.post(
      uri,
      headers: _postHeaders,
      body: json.encode({
        'user_id': userId,
        'action': action,
        if (metadata != null) 'metadata': metadata,
      }),
    );
    _checkResponse(response);
  }

  void dispose() => _client.close();

  void _checkResponse(http.Response response) {
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw WidgetServiceException(
        'API error: ${response.statusCode}',
        statusCode: response.statusCode,
        body: response.body,
      );
    }
  }
}

class WidgetServiceException implements Exception {
  final String message;
  final int statusCode;
  final String body;

  WidgetServiceException(this.message, {required this.statusCode, required this.body});

  @override
  String toString() => 'WidgetServiceException($statusCode): $message';
}
