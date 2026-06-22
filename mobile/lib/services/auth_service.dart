import '../models/user.dart';
import 'api_client.dart';

/// Auth API: register, login, session bootstrap.
class AuthService {
  AuthService(this._api);
  final ApiClient _api;

  Future<User> login(String email, String password) async {
    final data = await _api.post('/auth/login',
        body: {'email': email, 'password': password}, auth: false) as Map<String, dynamic>;
    await _api.saveTokens(
        data['access_token'] as String, data['refresh_token'] as String);
    return User.fromJson(data['user'] as Map<String, dynamic>);
  }

  Future<User> register({
    required String email,
    required String username,
    required String password,
    required String firstName,
    required String lastName,
  }) async {
    final data = await _api.post('/auth/register', auth: false, body: {
      'email': email,
      'username': username,
      'password': password,
      'first_name': firstName,
      'last_name': lastName,
    }) as Map<String, dynamic>;
    await _api.saveTokens(
        data['access_token'] as String, data['refresh_token'] as String);
    return User.fromJson(data['user'] as Map<String, dynamic>);
  }

  /// Returns the current user if a stored session is still valid, else null.
  Future<User?> currentUser() async {
    if (!await _api.hasSession) return null;
    try {
      final data = await _api.get('/auth/me') as Map<String, dynamic>;
      return User.fromJson(data);
    } on ApiException {
      return null;
    }
  }

  Future<void> logout() => _api.clearTokens();
}
