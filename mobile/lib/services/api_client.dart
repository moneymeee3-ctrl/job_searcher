import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

import '../config.dart';

/// Thrown for any non-2xx API response, carrying the server's error message.
class ApiException implements Exception {
  final int statusCode;
  final String message;
  ApiException(this.statusCode, this.message);

  @override
  String toString() => message;
}

/// Low-level HTTP client for the EMBEDHUNT API.
///
/// Persists JWTs in secure storage, injects the bearer token, and transparently
/// refreshes an expired access token once before failing.
class ApiClient {
  ApiClient({http.Client? client, FlutterSecureStorage? storage})
      : _client = client ?? http.Client(),
        _storage = storage ?? const FlutterSecureStorage();

  final http.Client _client;
  final FlutterSecureStorage _storage;

  static const _accessKey = 'access_token';
  static const _refreshKey = 'refresh_token';

  Future<String?> get accessToken => _storage.read(key: _accessKey);

  Future<void> saveTokens(String access, String refresh) async {
    await _storage.write(key: _accessKey, value: access);
    await _storage.write(key: _refreshKey, value: refresh);
  }

  Future<void> clearTokens() async {
    await _storage.delete(key: _accessKey);
    await _storage.delete(key: _refreshKey);
  }

  Future<bool> get hasSession async => (await accessToken) != null;

  Future<Map<String, String>> _headers({bool auth = true}) async {
    final headers = {'Content-Type': 'application/json'};
    if (auth) {
      final token = await accessToken;
      if (token != null) headers['Authorization'] = 'Bearer $token';
    }
    return headers;
  }

  Uri _uri(String path, [Map<String, dynamic>? query]) {
    final q = query?.map((k, v) => MapEntry(k, v.toString()));
    return Uri.parse('${AppConfig.apiV1}$path').replace(queryParameters: q);
  }

  Future<dynamic> get(String path,
      {Map<String, dynamic>? query, bool auth = true}) {
    return _send(() async => _client
        .get(_uri(path, query), headers: await _headers(auth: auth))
        .timeout(AppConfig.requestTimeout), auth: auth);
  }

  Future<dynamic> post(String path,
      {Map<String, dynamic>? body,
      Map<String, dynamic>? query,
      bool auth = true}) {
    return _send(() async => _client
        .post(_uri(path, query),
            headers: await _headers(auth: auth),
            body: body == null ? null : jsonEncode(body))
        .timeout(AppConfig.requestTimeout), auth: auth);
  }

  Future<dynamic> _send(Future<http.Response> Function() request,
      {required bool auth, bool isRetry = false}) async {
    final response = await request();

    if (response.statusCode == 401 && auth && !isRetry) {
      if (await _refresh()) {
        return _send(request, auth: auth, isRetry: true);
      }
    }
    return _decode(response);
  }

  dynamic _decode(http.Response response) {
    final body = response.body.isEmpty ? null : jsonDecode(response.body);
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return body;
    }
    final message = (body is Map && body['error'] != null)
        ? body['error'].toString()
        : (body is Map && body['detail'] != null)
            ? body['detail'].toString()
            : 'Request failed (${response.statusCode})';
    throw ApiException(response.statusCode, message);
  }

  Future<bool> _refresh() async {
    final refresh = await _storage.read(key: _refreshKey);
    if (refresh == null) return false;
    try {
      final response = await _client
          .post(_uri('/auth/refresh'),
              headers: {'Content-Type': 'application/json'},
              body: jsonEncode({'refresh_token': refresh}))
          .timeout(AppConfig.requestTimeout);
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        await saveTokens(
            data['access_token'] as String, data['refresh_token'] as String);
        return true;
      }
    } catch (_) {
      // fall through to failure
    }
    await clearTokens();
    return false;
  }
}
